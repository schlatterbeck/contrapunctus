#!/usr/bin/python3
# Copyright (C) 2017-2025
# Magdalena Schlatterbeck
# Dr. Ralf Schlatterbeck Open Source Consulting.
# Reichergasse 131, A-3411 Weidling.
# Web: http://www.runtux.com Email: office@runtux.com
# ****************************************************************************
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
# ****************************************************************************

import sys
import pga
import random
import itertools
from   .tune      import Tune, Bar, Tone
from   .gregorian import gregorian_modes
from   .checks    import checks
from   .rhythm    import *
from   argparse   import ArgumentParser
from   copy       import deepcopy
# Backwards compatibility:
from   rsclib.iter_recipes import batched

class File_Handler:
    def __init__ (self, filename):
        self.filename = filename
    # end def __init__

    def __exit__ (self, exc_type, exc_val, exc_tb):
        if self.filename:
            self.f.close ()
    # end def __exit__
# end def File_Handler

class Outfile (File_Handler):
    def __enter__ (self):
        if self.filename:
            self.f = open (self.filename, 'a')
        else:
            self.f = sys.stdout
        return self.f
    # end def __enter__
# end class Outfile

class Infile (File_Handler):
    def __enter__ (self):
        if self.filename and self.filename != '-':
            self.f = open (self.filename)
        else:
            self.f = sys.stdin
            self.filename = None
        return self.f
    # end def __enter__
# end class Infile

class Fake_PGA:
    """ This just has a single gene copy and emulates the allele
        accessor methods.
    """
    def __init__ (self):
        self.gene = []
        for i in self.init:
            self.gene.append (0)
    # end def __init__

    def __len__ (self):
        return len (self.gene)
    # end def len

    def get_allele (self, p, pop, i):
        return self.gene [i]
    # end def get_allele

    def set_allele (self, p, pop, i, v):
        self.gene [i] = v
    # end def set_allele

    def fix_gene_length (self):
        li = len (self.init)
        lg = len (self.gene)
        if li != lg:
            if lg > li:
                self.gene = self.gene [:li]
            else:
                self.gene.extend ([0] * (li - lg))
    # end def fix_gene_length

# end class Fake_PGA

class Contrapunctus:
    """ The rules for counterpoint are taken partly from wikipedia
        "Counterpoint" article (in particular "species counterpoint"),
        partly from Magdalenas notes on counterpoint.
        The numbering in the comments is as follows:
        - Wikipedia section "Considerations for all species" has two
          enumerations appear, the first titled "The following rules
          apply to melodic writing in each species, for each part", the
          second titled "And, in all species, the following rules govern
          the combination of parts". We number the first with
          0.1.1--0.1.7, the second 0.2.1--0.2.6.
        - Wikipedia section "First species" has an enumeration with 9
          points, they are numbered 1.1--1.9 in the following.

        The first voice in the gene is the cantus firmus, the second
        voice is the contrapunctus.
        The length of notes in a bar are now factored into Rhythm
        modules. See rhythm.py.
    """

    pop_default = (10, 500)
    # These should always be printed when printing options:
    necessary_options = ['--random-seed', '--tune-length']
    # And these should always be removed:
    remove_options    = ['--output-file']

    def __init__ (self, cmd, args):
        self.cmd           = cmd
        self.args          = args
        self.mode          = gregorian_modes [args.gregorian_mode]
        self.orig_args     = None
        self.do_explain    = False
        self.explanation   = []
        self._tune         = None # for given cantus firmus
        self.cantus_firmus = None
        self.rhythm        = Rhythm_Semibreve (self, args.tune_length)
        assert args.tune_length > 3
        if not args.pop_size and not args.optimize_depth_first:
            if args.use_de:
                args.pop_size = self.pop_default [0]
            else:
                args.pop_size = self.pop_default [1]
        # Force verbose when searching
        if args.optimize_depth_first or not args.gene_file:
            if args.verbose < 2:
                args.verbose = 2
        if args.cantus_firmus:
            assert args.cantus_firmus != '+'
            with Infile (args.cantus_firmus) as f:
                tune = Tune.from_iterator (f)
            if args.transpose_cf:
                tune = tune.transpose (args.transpose_cf)
            self.tune = tune
        if not getattr (self, 'init', None):
            self.init = self.rhythm.compute_init ()
        self.get_checks ()
    # end def __init__

    @property
    def cflength (self):
        return self.rhythm.cflength
    # end def cflength

    @property
    def cplength (self):
        return self.rhythm.cplength
    # end def cplength

    @property
    def tune (self):
        return self._tune
    # end def tune

    @tune.setter
    def tune (self, tune):
        # Convert unit if necessary
        tune.unit = 8
        # Now set the option to '+' so that next time we read from abc file
        self.args.cantus_firmus = '+'
        if len (tune.voices) == 1:
            self.cantus_firmus = tune.voices [0]
        else:
            for v in tune.voices:
                if v.id == 'CantusFirmus':
                    self.cantus_firmus = v
                    break
            else:
                raise ValueError ('No CantusFirmus voice found')
        if not getattr (self.cantus_firmus, 'id', None):
            self.cantus_firmus.id = 'CantusFirmus'
        if not getattr (self.cantus_firmus, 'name', None):
            self.cantus_firmus.properties ['name'] = 'Cantus Firmus'
        self._tune = tune
        self.tunelength = len (self.cantus_firmus.bars)
    # end def tune

    @property
    def tunelength (self):
        return self.rhythm.tunelength
    # end def tunelength

    @tunelength.setter
    def tunelength (self, tl):
        self.rhythm.tunelength = tl
        self.init = self.rhythm.compute_init ()
        if getattr (self, 'gene', None):
            self.fix_gene_length ()
    # end def tunelength

    def args_from_gene (self, itr):
        argv = []
        for n, line in enumerate (itr):
            line = line.strip ()
            if line == 'Command-line options:':
                continue
            line = line.split ('%') [-1]
            if not line:
                break
            argv.extend (line.split ())
        self.orig_args = self.cmd.parse_args (argv)
        # Set tune length accordingly
        if self.orig_args.tune_length == self.args.tune_length:
            self.tunelength = self.orig_args.tune_length
        return n
    # end def args_from_gene

    def as_args (self, prefix = None, force = False):
        """ Output command line arguments
        """
        r = []
        r.append ('Command-line options:')
        # For formatting, longest value
        max_argval_len = 6
        dest_dict = dict ((x.dest, x) for x in self.cmd._actions)
        args  = self.args
        if self.orig_args:
            args = self.orig_args
        if not self.orig_args and not force:
            return ''
        by_dest = {}
        for k in args.__dict__:
            opts   = dest_dict [k].option_strings
            minopt = opts [-1]
            for opt in opts:
                if opt.startswith ('--') and len (opt) < len (minopt):
                    minopt = opt
            by_dest [k] = minopt

        # Determine options that need printing
        maxl  = 0
        valid = []
        for k in args.__dict__:
            opt = by_dest [k]
            if opt in self.remove_options:
                continue
            v   = args.__dict__ [k]
            act = dest_dict [k]
            if act.nargs and act.nargs > 1:
                raise NotImplementedError ('nargs>1 not supported') \
                    # pragma: no cover
            if act.nargs == 0:
                # can also be None, explicitly check for True/False
                if act.const is True and not v:
                    continue
                if act.const is False and v:
                    continue
            else:
                if act.type is None and not v:
                    continue
            if act.default is not None and v == act.default:
                if opt not in self.necessary_options:
                    continue
            if act.default is None and v is None:
                continue
            if act.__class__.__name__ == '_CountAction':
                for i in range (v):
                    valid.append (k)
            else:
                valid.append (k)
            if len (opt) > maxl:
                maxl = len (opt)

        maxl += max_argval_len +  1 # + delimiting space
        cols = 77 // maxl or 1
        for b in batched (sorted (valid), cols):
            rb = []
            for k in b:
                v   = args.__dict__ [k]
                opt = by_dest [k]
                act = dest_dict [k]
                c   = '='
                # Currently there is no option with only a single '-'.
                if not opt.startswith ('--'):
                    c = ' ' # pragma: no cover
                if act.nargs == 0:
                    s = opt
                else:
                    s = '%s=%s' % (opt, v)
                rb.append (('%%-%ds' % maxl) % s)
            if rb:
                r.append (' '.join (rb).rstrip ())
        # empty line at end
        r.append ('')
        if prefix is not None:
            r = [(prefix + x).rstrip () for x in r]
        return '\n'.join (r)
    # end def as_args

    def as_complete_tune (self, p = 1, pop = pga.PGA_NEWPOP, force = False):
        r = []
        r.append (self.as_tune (p, pop))
        a = self.as_args ('% ', force = force)
        if a:
            r.append (a)
        if self.args.verbose:
            self.do_explain = True
            r.append ('%% Eval: %g' % self.evaluate (p, pop))
            exp = '\n'.join (self.explanation)
            r.append ('% '+ exp.replace ('\n', '\n% '))
        if self.args.verbose > 1:
            r.append (self.as_tune_gene (p, pop))
        return '\n'.join (r)
    # end def as_complete_tune

    def as_tune (self, p = 1, pop = pga.PGA_NEWPOP):
        tune = self.phenotype (p, pop)
        if self.args.transpose:
            tune = tune.transpose (self.args.transpose)
        return str (tune)
    # end def as_tune

    def as_tune_gene (self, p = 1, pop = pga.PGA_NEWPOP):
        r = []
        al = lambda x: self.get_allele (p, pop, x)
        g  = ['[%d]' % al (i) for i in range (len (self.init))]
        for i, b in enumerate (batched (g, 16)):
            r.append ('%%# %4d: %s' % ((i * 16), ','.join (b)))
        return '\n'.join (r)
    # end def as_tune_gene

    def evaluate (self, p, pop):
        tune       = self.phenotype (p, pop)
        badness    = 1.0
        ugliness   = 1.0
        dir        = (-1, 1)
        # Reset history
        for check in self.melody_history_checks:
            check.reset ()
        for check in self.harmony_history_checks:
            check.reset ()

        self.explanation = []

        # A tune contains two (or theoretically more) voices. We can
        # iterate over the bars of a voice via tune.iter (N) where N is
        # the voice index (starting with 0).
        # A bar contains many Bar_Object objects. These can either be a
        # Tone or a Pause. A tone contains a Halftone object in the
        # attribute halftone.
        # Each bar has a .prev and .next bar which can be None (prev is
        # None for the first bar while next is None for the last).
        # We iterate over the bars in each tune.
        # cf: Cantus Firmus (Object of class 'Bar')
        # cp: Contrapunctus (Object of class 'Bar')
        last_cf_obj = last_cp_obj = last_bar_obj = None
        bsum = usum = 0
        for cf_obj, cp_obj in tune.voices_iter ():
            cf = cf_obj.bar
            cp = cp_obj.bar
            assert cp.voice.id == 'Contrapunctus'
            assert cf.voice.id == 'CantusFirmus'
            assert cf.idx == cp.idx

            if last_bar_obj is not cp:
                ugliness += usum
                if bsum:
                    assert bsum > 1
                    badness *= bsum
                bsum = usum = 0
                last_bar_obj = cp
            if not self.args.no_check_cf and last_cf_obj is not cf_obj:
                last_cf_obj = cf_obj
                for check in self.melody_checks_cf:
                    b, u = check.check (cf_obj)
                    if b:
                        badness *= b
                    ugliness += u
                    self.explain (check)
            if last_cp_obj is not cp_obj:
                last_cp_obj = cp_obj
                for check in self.melody_checks_cp:
                    b, u = check.check (cp_obj)
                    bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                    usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                    self.explain (check)
            for check in self.harmony_checks:
                b, u = check.check (cf_obj, cp_obj)
                bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                self.explain (check)

        ugliness += usum
        if bsum:
            assert bsum > 1
            badness *= bsum
        return ugliness * badness
    # end def evaluate

    def explain (self, check):
        if self.do_explain:
            ex = str (check)
            if ex:
                self.explanation.append (ex)
    # end def explain

    def fix_gene (self):
        for i in range (len (self.init)):
            a = self.get_fixed_allele (1, pga.PGA_NEWPOP, i)
            self.set_allele (1, pga.PGA_NEWPOP, i, a)
    # end def fix_gene

    def from_gene (self):
        with Infile (self.args.gene_file) as f:
            next (self.from_gene_lines (f))
    # end def from_gene

    def _from_gene_lines (self, itr):
        idx  = 0
        c    = 0
        tune = None
        if self.args.best_eval:
            for n, line in enumerate (itr):
                if ('Command-line options:' in line):
                    c += self.args_from_gene (itr)
                    continue
                if line.startswith ('The Best String:'):
                    c += n
                    break
        for n, line in enumerate (itr):
            line = line.lstrip ()
            if line.startswith ('X:') or line.startswith ('M:'):
                tmp_iter  = iter ([line])
                tune = Tune.from_iterator \
                    (itertools.chain (tmp_iter, itr), True)
                c += tune.nlines - 1 # first line already counted
                line = getattr (tune, 'lastline', None)
                # When reading abc file the abc parser has picked up the
                # gene, too
                if tune.comment:
                    i, t = next (self._from_gene_lines (tune.comment))
                    yield i, tune
                    tune = None
                if line is None:
                    continue
            if ('Command-line options:' in line):
                c += self.args_from_gene (itr)
                continue
            ln = n + 1 + c
            start = '#', '%#', 'Text: #'
            for s in start:
                if line.startswith (s):
                    break
            else:
                if idx > 0:
                    yield idx, tune
                idx = 0
                continue
            i, l = line.split ('#', 1)[-1].split (':')
            i = int (i)
            if i != idx:
                raise ValueError ("Line %s: Invalid gene-file format" % ln) \
                    # pragma: no cover
            for offs, a in enumerate (l.split (',')):
                a = float (a.strip ().lstrip ('[').rstrip (']').strip ())
                a = int (a)
                if idx + offs >= len (self):
                    self.tunelength = 2 * self.tunelength
                    assert len (self) > idx + offs
                self.set_allele (1, pga.PGA_NEWPOP, idx + offs, a)
            idx += offs + 1
        if idx > 0:
            yield idx, tune
    # end def _from_gene_lines

    def from_gene_lines (self, itr):
        for genelength, tune in self._from_gene_lines (itr):
            if self.orig_args and self.orig_args.cantus_firmus:
                assert self.orig_args.cantus_firmus == '+'
                self.tune = tune
                if self.args.fix_gene:
                    self.fix_gene ()
                yield genelength
            if not self.orig_args or not self.orig_args.tune_length:
                # tunelength with CF doesn't include the gene part for the
                # CF and is thus shorter.
                # With CF we have:
                # genelength = (tunelength - 3) + 11 * (tunelength - 2)
                # Without CF we have:
                # genelength = (tunelength - 2) * 11
                tunelength = (genelength + 25) / 12
                args = self.orig_args or self.args
                if tunelength != int (tunelength):
                    tunelength = (genelength + 22) / 11
                    assert int (tunelength) == tunelength
                    assert tune is not None
                    self.tune = tune
                    args.cantus_firmus = '+'
                    assert tunelength == len (self.cantus_firmus.bars)
                assert int (tunelength) == tunelength
                tunelength = int (tunelength)
                args.tune_length = tunelength
            else:
                tunelength = self.orig_args.tune_length
            if genelength != len (self.init):
                self.tunelength = tunelength
            if self.args.fix_gene:
                self.fix_gene ()
            yield genelength
    # end def from_gene_lines

    def get_checks (self):
        ch = checks [self.args.checks]
        self.melody_checks_cf, self.melody_checks_cp, self.harmony_checks = ch
        # These need to call reset before each eval:
        melody_checks = self.melody_checks_cp + self.melody_checks_cf
        self.melody_history_checks = \
            [c for c in melody_checks if hasattr (c, 'reset')]
        self.harmony_history_checks = \
            [c for c in self.harmony_checks if hasattr (c, 'reset')]
    # end def get_checks

    def get_fixed_allele (self, p, pop, idx):
        v = int (self.get_allele (p, pop, idx))
        if self.args.fix_gene and v > self.init [idx][1]:
            return self.init [idx][1]
        return v
    # end def get_fixed_allele

    def phenotype (self, p, pop, maxidx = None):
        return self.rhythm.phenotype (p, pop, maxidx)
    # end def phenotype

    def _run_cf_end_check (self, bd, bar = None, b = 0, t = 0):
        if b >= len (bd.bars):
            return True
        cp = bd.tune.voices [-1]
        for a in bd.seq:
            if bar is None:
                nbar = Bar (8, 8)
            else:
                nbar = bar.copy ()
            cp.replace (bd.bar_idx (b), nbar)
            nbar.add (Tone (self.mode [0][a], bd.tone_idx (b, t)))
            tsum = sum (bd.tone_idx (b, x) for x in range (t))
            assert nbar.objects [-1].offset == tsum
            sidx = cp.bars [bd.bar_idx (0)].idx
            eidx = cp.bars [bd.bar_idx (b)].idx + 1
            if eidx == self.cplength and t == bd.tone_idx_len (b) - 1:
                eidx = self.tunelength
            assert sidx < eidx
            #print ('CHECK RANGE %d to %d' % (sidx, eidx))
            # Beware, sidx is optional and is *last*
            if not self.run_cp_checks (bd.tune, eidx, sidx):
                if self.explanation:
                    with Outfile (self.args.output_file) as f:
                        print ('\n'.join (self.explanation), file = f)
                        for v in bd.tune.voices:
                            print (v.as_abc (), file = f)
                continue
            n_t = t + 1
            n_b = b
            if n_t >= bd.tone_idx_len (b):
                n_t   = 0
                n_b  += 1
                nbar = None
            if self._run_cf_end_check (bd, nbar, n_b, n_t):
                return True
        return False
    # end def _run_cf_end_check

    def run_cf_end_checks (self, tune):
        """ Here we check if for the last 4 bars for the given CF we can
            find a valid CP.
            This asumes an empty Contrapunctus voice in tune.
        """
        self.explanation = []
        assert len (tune.voices) == 2
        assert len (tune.voices [1].bars) == 1
        assert len (tune.voices [1].bars [0].objects) == 0
        # Preparation
        cp = tune.voices [1]
        for k in range (self.tunelength - 1):
            b  = Bar (8, 8)
            cp.add (b)
        cp.bars [-2].add (Tone (self.mode [0].subsemitonium, 8))
        cp.bars [-1].add (Tone (self.mode [0][7], 8))
        off = self.cplength - 1
        pos = -22 + 1
        seq = range (self.init [pos][0], self.init [pos][1] + 1)

        if self.args.explain_cp_cf:
            self.do_explain = True
        for b in (((8,), (4, 2, 2)), ((8,), (2, 1, 1, 2, 1, 1))):
            bd = Bardata (tune, seq)
            bd.add_bar (-4, b [0])
            bd.add_bar (-3, b [1])
            if self._run_cf_end_check (bd):
                if self.args.explain_cp_cf:
                    with Outfile (self.args.output_file) as f:
                        print \
                            ('Feasibility: Found CP for last 4 bars', file = f)
                return True
    # end def run_cf_end_checks

    def run_cp_checks (self, tune, idx, startidx = None):
        """ Run Contrapunctus checks
            Note that if the startidx is given the caller asumes
            responsibility for start = startidx / end = idx.
        """
        self.explanation = []
        if startidx is None:
            start = max (idx - 2, 0)
            end   = idx + 1
            # Check last two hardcoded bars if at end
            if idx >= self.cplength - 1:
                end = self.tunelength
        else:
            # Explicit specification of start/end
            start = startidx
            end   = idx
        for c in self.melody_checks_cp:
            if hasattr (c, 'reset'):
                c.reset ()
            for bcp in tune.voices [1].bars [start:end]:
                for cp_obj in bcp.objects:
                    b, u = c.check (cp_obj)
                    if b or (not self.args.allow_ugliness and u):
                        self.explain (c)
                        return False
        for c in self.harmony_checks:
            if hasattr (c, 'reset'):
                c.reset ()
            for bcf, bcp in zip (*(v.bars [start:end] for v in tune.voices)):
                for cp_obj in bcp.objects:
                    if not bcf.objects [0].overlaps (cp_obj):
                        continue
                    b, u = c.check (bcf.objects [0], cp_obj)
                    if b or (not self.args.allow_ugliness and u):
                        self.explain (c)
                        return False
        return True
    # end def run_cp_checks

    def verify_cantus_firmus (self):
        if not self.cantus_firmus:
            return True
        if self.args.no_cf_feasibility:
            return True
        tune  = self.phenotype (1, pga.PGA_NEWPOP, 0)
        if not self.run_cf_end_checks (tune):
            return False
        return True
    # end def verify_cantus_firmus

# end class Contrapunctus

class Contrapunctus_PGA (Contrapunctus, pga.PGA):

    def __init__ (self, cmd, args):
        Contrapunctus.__init__ (self, cmd, args)
        self.prefix_printed = False
        self.stop_reached   = False
        init = deepcopy (self.init)
        if args.use_de:
            for item in init:
                item [-1] += 1
        d = dict \
            ( maximize      = False
            , init          = init
            , random_seed   = self.args.random_seed
            , pop_size      = args.pop_size
            , num_replace   = args.pop_size * 9 // 10
            , print_options = [pga.PGA_REPORT_STRING]
            , max_GA_iter   = args.max_generations
            , print_frequency     = args.print_frequency
            , stopping_rule_types = [pga.PGA_STOP_MAXITER]
            )
        typ = int
        if args.use_de:
            typ = float
            variant = args.de_variant.upper ().replace ('-', '_')
            variant = getattr (pga, 'PGA_DE_VARIANT_' + variant)
            d.update \
                ( num_replace          = args.pop_size
                , pop_replace_type     = pga.PGA_POPREPL_PAIRWISE_BEST
                , select_type          = pga.PGA_SELECT_LINEAR
                , mutation_only        = True
                , mutation_bounce_back = True
                , mutation_type        = pga.PGA_MUTATION_DE
                , DE_variant           = variant
                , DE_crossover_prob    = args.de_crossover_prob
                , DE_jitter            = args.de_jitter
                , DE_scale_factor      = args.de_scale_factor
                , DE_crossover_type    = pga.PGA_DE_CROSSOVER_BIN
                )
        if self.args.output_file:
            d.update (output_file = args.output_file)
        pga.PGA.__init__ (self, typ, len (init), **d)
    # end def __init__

    tunelength = Contrapunctus.tunelength
    tune       = Contrapunctus.tune

    @tunelength.setter
    def tunelength (self, tl):
        if getattr (self, 'init', None):
            raise ValueError \
                ('Not possible to set tunelength after init') # pragma: no cover
        self.rhythm.tunelength = tl
    # end def tunelength

    @tune.setter
    def tune (self, tune):
        if getattr (self, 'init', None):
            raise ValueError \
                ('Not possible to set tunelength after init') # pragma: no cover
        Contrapunctus.tune.fset (self, tune)
    # end def tune

    def print_string (self, file, p, pop):
        if not self.prefix_printed or self.stop_reached:
            print (self.as_args (force = True), file = file)
            self.prefix_printed = True
        bestidx = self.get_best_index (pga.PGA_OLDPOP)
        eval    = self.get_evaluation (bestidx, pga.PGA_OLDPOP)
        print ('Best index: %d: %.11e' % (bestidx, eval), file = file)
        evalstr = 'Iter: %s Evals: %s' % (self.GA_iter, self.eval_count)
        print (evalstr, file = file)
        print (self.as_tune (p, pop), file = file)
        if self.stop_reached:
            self.do_explain = True
            self.evaluate (p, pop)
            print ('\n'.join (self.explanation), file = file)
        file.flush ()
        super ().print_string (file, p, pop)
    # end def print_string

    def stop_cond (self):
        best = self.get_best_report_index (pga.PGA_OLDPOP, 0)
        eval = self.get_evaluation (best, pga.PGA_OLDPOP)
        if eval == 1:
            self.stop_reached = True
            return True
        if self.eval_count >= self.args.max_evals:
            self.stop_reached = True
            return True
        self.stop_reached = self.check_stopping_conditions ()
        return self.stop_reached
    # end def stop_cond

# end class Contrapunctus_PGA

class Bardata:
    """ Data structures for recursive bar checking
    """
    def __init__ (self, tune, seq):
        self.tune = tune
        self.seq  = seq
        self.bars = []
    # end def __init__

    def __str__ (self):
        return 'Bardata: %s' % str (self.bars)
    # end def __str

    def add_bar (self, bar_idx, tone_lengths):
        self.bars.append ((bar_idx, tone_lengths))
    # end def add_bar

    def bar_idx (self, idx):
        return self.bars [idx][0]
    # end def bar_idx

    def tone_idx (self, bidx, tidx):
        return self.bars [bidx][1][tidx]
    # end def tone_idx

    def tone_idx_len (self, idx):
        return len (self.bars [idx][1])
    # end def tone_idx_len

# end class Bardata

class Contrapunctus_Depth_First (Fake_PGA, Contrapunctus):

    def __init__ (self, cmd, args):
        Contrapunctus.__init__ (self, cmd, args)
        Fake_PGA.__init__ (self)
        random.seed (self.args.random_seed)
    # end def __init__

    def find_cantus_firmus (self, idx):
        if idx == self.cflength:
            return True
        for a in self.randrange (idx):
            self.set_allele (1, 1, idx, a)
            tune  = self.phenotype (1, 1, idx)
            if not self.run_cf_checks (tune, idx):
                continue
            r = self.find_cantus_firmus (idx + 1)
            if r:
                return True
        return False
    # end def find_cantus_firmus

    boff_lut = (0, None, 2, 4, 5, None, 8, 10)

    def find_contrapunctus (self, off, boff):
        if off >= self.cplength:
            return True
        aidx = self.cflength + 11 * off + self.boff_lut [boff]
        if boff in (0, 2, 4, 6):
            for a1 in self.randrange (aidx):
                self.set_allele (1, 1, aidx, a1)
                for a2 in self.randrange (aidx + 1):
                    self.set_allele (1, 1, aidx + 1, a2)
                    tune = self.phenotype (1, 1, aidx + 1)
                    if not self.run_cp_checks (tune, off):
                        continue
                    noff  = off
                    nboff = boff + (1 << a1)
                    assert nboff <= 8
                    if nboff > 7:
                        noff += 1
                        nboff = 0
                    r = self.find_contrapunctus (noff, nboff)
                    if r:
                        return True
        elif boff in (3, 5, 7):
            for a in self.randrange (aidx):
                self.set_allele (1, 1, aidx, a)
                tune = self.phenotype (1, 1, aidx)
                if not self.run_cp_checks (tune, off):
                    continue
                noff  = off
                nboff = boff + 1
                if nboff > 7:
                    noff += 1
                    nboff = 0
                r = self.find_contrapunctus (noff, nboff)
                if r:
                    return True
        else:
            assert 0 # pragma: no cover
        return False
    # end def find_contrapunctus

    def randrange (self, idx):
        rn = list (range (self.init [idx][0], self.init [idx][1] + 1))
        random.shuffle (rn)
        return rn
    # end def randrange

    def run (self):
        if not self.cantus_firmus:
            result = self.find_cantus_firmus (0)
            # This should not happen: It is only possible if the rules
            # forbid enough so that we cannot find a CF, and this may
            # take *ages*.
            if not result: # pragma no cover
                with Outfile (self.args.output_file) as f:
                    print ('No Cantus Firmus found', file = f)
                return
        else:
            if not self.verify_cantus_firmus ():
                with Outfile (self.args.output_file) as f:
                    msg = 'No valid Contrapunctus for this Cantus Firmus'
                    print (msg, file = f)
                return
        result = self.find_contrapunctus (0, 0)
        if not result:
            with Outfile (self.args.output_file) as f:
                print ('No Contrapunctus found', file = f)
            return
        r = []
        with Outfile (self.args.output_file) as f:
            print (self.as_complete_tune (force = True), file = f)
    # end def run

    def run_cf_checks (self, tune, idx):
        self.explanation = []
        for c in self.melody_checks_cf:
            if hasattr (c, 'reset'):
                c.reset ()
            # Check up to idx + 1 because first bar is hardcoded
            end = idx + 2
            # Check last two hardcoded bars if at end
            if idx >= self.cflength - 1:
                end = 3 + self.cflength
            for bar in tune.voices [0].bars [max (idx - 1, 0):end]:
                for obj in bar.objects:
                    b, u = c.check (obj)
                    if b or u:
                        self.explain (c)
                        return False
        if idx >= self.cflength - 1:
            return self.run_cf_end_checks (tune)
        return True
    # end def run_cf_checks

# end class Contrapunctus_Depth_First

def contrapunctus_cmd (argv = None):
    cmd = ArgumentParser ()
    cmd.add_argument \
        ( "-a", "--allow-ugliness"
        , help    = "Allow ugliness with DF search and for given cantus"
                    " firmus (with --cantus-firmus option)"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "-b", "--best-eval"
        , help    = "Asume a search trace for -g option and output best"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "-c", "--cantus-firmus"
        , help    = "Read Cantus Firmus from file, '-' reads from standard"
                    " input, '+' reads from gene file given with -g"
        )
    cmd.add_argument \
        ( "--checks"
        , help    = "Name of checks to use, default=%(default)s"
        , default = 'default'
        , choices = checks.keys ()
        )
    cmd.add_argument \
        ( "-d", "--use-differential-evolution", "--use-de"
        , dest    = 'use_de'
        , help    = "Use Differential Evolution"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "--de-crossover-prob"
        , help    = "Differential Evolution crossover probability,"
                    " default=%(default)s"
        , default = 0.05
        , type    = float
        )
    cmd.add_argument \
        ( "--de-jitter"
        , help    = "Differential Evolution jitter, default=%(default)s"
        , default = 0.001
        , type    = float
        )
    cmd.add_argument \
        ( "--de-scale-factor"
        , help    = "Differential Evolution scale factor, default=%(default)s"
        , default = 0.85
        , type    = float
        )
    cmd.add_argument \
        ( "--de-variant"
        , help    = "Differential Evolution variant, default=%(default)s"
        , default = 'best'
        , choices = ('best', 'rand', 'either-or')
        )
    cmd.add_argument \
        ( "--do-not-fix-gene"
        , help    = "During gene reading do limit maximum of read values"
        , dest    = 'fix_gene'
        , action  = 'store_false'
        , default = True
        )
    cmd.add_argument \
        ( "--explain-cp-cf"
        , help    = "Explain results when checking if a Contrapunctus"
                    " exists for a given Cantus Firmus"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "-g", "--gene-file"
        , help    = "Read gene-file and output phenotype, no searching"
        )
    cmd.add_argument \
        ( "--gregorian_mode"
        , help    = "Gregorian mode, default=%(default)s"
        , default = 'dorian'
        , choices = gregorian_modes.keys ()
        )
    cmd.add_argument \
        ( "-l", "--tune-length"
        , help    = "Length of generated tune, default=%(default)s"
        , type    = int
        , default = 12
        )
    cmd.add_argument \
        ( "--max-evals"
        , help    = "Maximum number of evaluations, default=%(default)s"
        , type    = int
        , default = 100000
        )
    cmd.add_argument \
        ( "--max-generations"
        , help    = "Maximum number of generations, default=%(default)s"
        , type    = int
        , default = 10000
        )
    cmd.add_argument \
        ( "--no-check-cf", "--no-check-cantus-firmus"
        , help    = "Do not check cantus firmus melody during search,"
                    " applies only to explicit cantus firmus with"
                    " --cantus-firmus option and only for EA searching"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "--no-cf-feasibility", "--no-cantus-firmus-feasibility"
        , help    = "Do not check cantus firmus melody prior to search,"
                    " applies only to explicit cantus firmus with"
                    " --cantus-firmus option and only for EA searching"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "--optimize-depth-first", "--df"
        , help    = "Optimize using depth first search"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "-O", "--output-file"
        , help    = "Output file for progress information"
        )
    cmd.add_argument \
        ( "-p", "--pop-size"
        , help    = "Population size default for DE: %d for GA: %d"
                  % Contrapunctus.pop_default
        , type    = int
        )
    cmd.add_argument \
        ( "--print-frequency"
        , help    = "Print frequency, default=%(default)s"
        , type    = int
        , default = 10
        )
    cmd.add_argument \
        ( "-R", "--random-seed"
        , help    = "Random seed initialisation for reproduceable results"
                    " default=%(default)s"
        , type    = int
        , default = 23
        )
    cmd.add_argument \
        ( "-T", "--transpose-cf", "--transpose-cantus-firmus"
        , help    = "Number of halftones to transpose cantus firmus when"
                    " read from a file"
        , type    = int
        , default = 0
        )
    cmd.add_argument \
        ( "-t", "--transpose"
        , help    = "Number of halftones to transpose resulting tune"
        , type    = int
        , default = 0
        )
    cmd.add_argument \
        ( "-v", "--verbose"
        , help    = "Verbose output of gene string with -g"
        , action  = 'count'
        , default = 0
        )
    return cmd
# end def contrapunctus_cmd

def main (argv = None):
    """ Document some common error cases here and test them
    >>> args = ['-c+']
    >>> r = main (args)
    --cantus-firmus=+ needs --gene-file option
    >>> r
    1
    >>> args = '--df -c test/test/zacconi.abc --no-check-cf'.split ()
    >>> r = main (args)
    CF checking can not be turned off for depth first search
    >>> r
    1
    >>> args = '--df --no-cf-feasibility'.split ()
    >>> r = main (args)
    CF checking can be turned off only for --cantus-firmus
    >>> r
    1
    """
    cmd  = contrapunctus_cmd ()
    args = cmd.parse_args (argv)
    if args.cantus_firmus == '+' and not args.gene_file:
        print ('--cantus-firmus=+ needs --gene-file option')
        return 1
    if args.no_check_cf or args.no_cf_feasibility:
        if not args.cantus_firmus:
            print ('CF checking can be turned off only for --cantus-firmus')
            return 1
        if args.optimize_depth_first:
            print ('CF checking can not be turned off for depth first search')
            return 1
    if args.gene_file or args.optimize_depth_first:
        cp = Contrapunctus_Depth_First (cmd, args)
        if args.gene_file:
            cp.from_gene ()
            with Outfile (args.output_file) as f:
                print (cp.as_complete_tune (), file = f)
        else:
            cp.run ()
    else:
        cp = Contrapunctus_PGA (cmd, args)
        if not cp.verify_cantus_firmus ():
            errmsg = 'No valid Contrapunctus for this Cantus Firmus'
            with Outfile (args.output_file) as f:
                print (errmsg, file = f)
            return 1
        cp.run ()
# end def main

def transpose_tune (argv = None):
    cmd = ArgumentParser ()
    cmd.add_argument \
        ( 'filename'
        , nargs = 1
        )
    cmd.add_argument \
        ( "-t", "--transpose"
        , help    = "Number of halftones to transpose resulting tune"
        , type    = int
        , default = 0
        )
    cmd.add_argument \
        ( "-O", "--output-file"
        , help    = "Output file for progress information"
        )
    args = cmd.parse_args (argv)
    tune = Tune.from_file (args.filename [0])
    tune = tune.transpose (args.transpose)
    with Outfile (args.output_file) as f:
        print (tune.as_abc (), file = f)
# end def transpose_tune

if __name__ == '__main__':
    main (sys.argv [1:]) # pragma: no cover
