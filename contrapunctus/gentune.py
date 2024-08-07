#!/usr/bin/python3
# Copyright (C) 2017-2024
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
from   .tune      import Tune, Voice, Bar, Meter, Tone, halftone, sgn
from   .gregorian import dorian, hypodorian
from   .checks    import *
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
            self.f = open (self.filename, 'w')
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
        Length of the automatically-generated voices
        Now that we allow up to 1/8 notes the gene for the first voice
        is longer.
        A bar can contain at most 14 notes:
        - A 'heavy' position must not contain 1/8
        - so we have at least 2*1/4 for the heavy position
        - and the rest 1/8 makes 16/8 - 2*1/4 = 12/8
        We have for each note in a bar:
        - length of note (or pause, for now we do not generate a pause)
        - the length can only be 16, 12, 8, 6, 4, 3, 2, 1
        But we only use one bar (8/8) and we bind the second note if
        it is the same pitch (maybe with some probability). The gene
        coding is:
        - log_2 of the length (left out if there is only 1 possibility)
        - pitch for each note
        Thats 7 pairs of genes (where the length is sometimes left out):
        - 1-3 (8, 4, 2)/8, the heavy position has at least 1/4
        - pitch 0-7
        - 0-1 (2 or 1)/8 for first 1/4 light position
        - pitch 0-7
        - pitch 0-7 (1/8 light can only be 1/8, so no length)
        - 1-2 (4, 2)/8, the half-heavy position has at least 1/4
        - pitch 0-7
        - UNUSED pitch 0-7 (1/8 light can only be 1/8)
        - 0-1 (2 or 1)/8
        - pitch 0-7
        - pitch 0-7 (1/8 light can only be 1/8)
        if the previous note is longer some of the genes are not used
    """

    pop_default = (10, 500)
    # These should always be printed when printing options:
    necessary_options = ['--random-seed', '--tune-length']
    # And these should always be removed:
    remove_options    = ['--output-file']

    # These need to call reset before each eval:
    melody_history_checks = \
        [c for c in melody_checks_cp + melody_checks_cf if hasattr (c, 'reset')]
    harmony_history_checks = [c for c in harmony_checks if hasattr (c, 'reset')]

    def __init__ (self, cmd, args):
        self.cmd           = cmd
        self.args          = args
        self.orig_args     = None
        self.do_explain    = False
        self.explanation   = []
        self.tune          = None # for given cantus firmus
        self.cantus_firmus = None
        self._tunelength   = args.tune_length
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
                self.tune = Tune.from_iterator (f)
            # Now set the option to '+' so that next time we read from abc file
            args.cantus_firmus = '+'
            for v in self.tune.voices:
                if v.id == 'CantusFirmus':
                    self.cantus_firmus = v
                    break
                else:
                    raise ValueError ('No CantusFirmus voice found')
            self.tunelength = len (self.cantus_firmus.bars)
        if not getattr (self, 'init', None):
            self.set_init ()
    # end def __init__

    @property
    def tunelength (self):
        return self._tunelength
    # end def tunelength

    @tunelength.setter
    def tunelength (self, tl):
        self._tunelength = tl
        self.set_init ()
        if getattr (self, 'gene', None):
            self.fix_gene_length ()
    # end def tunelength

    def args_from_gene (self, iter):
        argv = []
        for line in iter:
            line = line.strip ()
            line = line.split ('%') [-1]
            if not line:
                break
            argv.extend (line.split ())
        self.orig_args = self.cmd.parse_args (argv)
        # Set tune length accordingly
        if self.orig_args.tune_length == self.args.tune_length:
            self.tunelength = self.orig_args.tune_length
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
                raise NotImplementedError ('nargs>1 not supported')
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
                if not opt.startswith ('--'):
                    c = ' '
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
        for cf, cp in zip (tune.iter (0), tune.iter (1)):
            assert cp.voice.id == 'Contrapunctus'
            assert cf.voice.id == 'CantusFirmus'
            cf_obj = cf.objects [0]
            # For now a bar in the cantus firmus only
            # contains one single note, the 0th object in bar
            assert len (cf.objects) == 1

            for check in melody_checks_cf:
                b, u = check.check (cf_obj)
                if b:
                    badness *= b
                ugliness += u
                self.explain (check)
            bsum = usum = 0
            for cp_obj in cp.objects:
                for check in melody_checks_cp:
                    b, u = check.check (cp_obj)
                    bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                    usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                    self.explain (check)
                for check in harmony_checks:
                    b, u = check.check (cf_obj, cp_obj)
                    bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                    usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                    self.explain (check)

                # 1.4: Avoid moving in parallel fourths (In practice
                # Palestrina and others frequently allowed themselves such
                # progressions, especially if they do not involve the lowest
                # of the parts)

                # Don't get carried away :-)
                # 0.2.5: "The interval of a tenth should not be exceeded
                # between two adjacent parts unless by necessity." We limit
                # this to a ninth.

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

    def from_allele (self, v, i):
        v = int (v)
        if v > self.init [i][1]:
            return self.init [i][1]
        return v
    # end def from_allele

    def from_gene_lines (self, iter):
        idx = 0
        c   = 0
        if self.args.best_eval:
            for n, line in enumerate (iter):
                if ('Command-line options:' in line):
                    self.args_from_gene (iter)
                    continue
                if line.startswith ('The Best String:'):
                    c = n
                    break
        started = False
        for n, line in enumerate (iter):
            if ('Command-line options:' in line):
                self.args_from_gene (iter)
                continue
            ln = n + 1 + c
            start = '#', '%#', 'Text: #'
            for s in start:
                if line.startswith (s):
                    break
            else:
                if not started:
                    continue
                else:
                    yield idx
            i, l = line.split ('#', 1)[-1].split (':')
            i = int (i)
            if i != idx:
                raise ValueError ("Line %s: Invalid gene-file format" % ln)
            for offs, a in enumerate (l.split (',')):
                a = float (a.strip ().lstrip ('[').rstrip (']').strip ())
                a = int (a)
                if idx + offs >= len (self):
                    self.tunelength = 2 * self.tunelength
                    assert len (self) > idx + offs
                self.set_allele (1, pga.PGA_NEWPOP, idx + offs, a)
            idx += offs + 1
        if idx > 0:
            yield idx
    # end def from_gene_lines

    def _fix_gene (self):
        for i in range (len (self.init)):
            a = self.get_allele (1, pga.PGA_NEWPOP, i)
            v = self.from_allele (a, i)
            self.set_allele (1, pga.PGA_NEWPOP, i, v)
    # end def _fix_gene

    def _from_gene (self, f):
        iter = f
        if self.cantus_firmus == '+':
            self.tune = Tune.from_iterator (f)
            iter = self.tune.comment
        for genelength in self.from_gene_lines (iter):
            if not self.orig_args or not self.orig_args.tune_length:
                tunelength = (genelength + 25) / 12
                assert int (tunelength) == tunelength
                tunelength = int (tunelength)
            else:
                tunelength = self.orig_args.tune_length
            if genelength != len (self.init):
                self.tunelength = tunelength
            if self.args.fix_gene:
                self._fix_gene ()
    # end def _from_gene

    def from_gene (self):
        with Infile (self.args.gene_file) as f:
            self._from_gene (f)
    # end def from_gene

    def phenotype (self, p, pop, maxidx = None):
        tune = Tune \
            ( number = 1
            , meter  = Meter (4, 4)
            , Q      = '1/4=200'
            , key    = 'DDor'
            , unit   = 8
            , score  = '(Contrapunctus) (CantusFirmus)'
            )
        if self.cantus_firmus:
            cf = self.cantus_firmus.copy ()
            assert self.cflength == 0
        else:
            cf = Voice (id = 'CantusFirmus', name = 'Cantus Firmus')
            b  = Bar (8, 8)
            b.add (Tone (hypodorian.finalis, 8))
            cf.add (b)
        tune.add (cf)
        for i in range (self.cflength):
            if maxidx is not None and i > maxidx:
                return tune
            a = self.get_allele (p, pop, i)
            if self.args.fix_gene:
                a = self.from_allele (a, i)
            b = Bar (8, 8)
            b.add (Tone (hypodorian [a], 8))
            cf.add (b)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the step2 for
        # the cantus firmus
        # 1.1: "The counterpoint must begin and end on a perfect
        # consonance" is also achived by hard-coding the last tone.
        if not self.cantus_firmus:
            b  = Bar (8, 8)
            b.add (Tone (hypodorian.step2, 8))
            cf.add (b)
            b  = Bar (8, 8)
            b.add (Tone (hypodorian.finalis, 8))
            cf.add (b)
        cp  = Voice (id = 'Contrapunctus', name = 'Contrapunctus')
        tune.add (cp)
        for i in range (self.cplength):
            off  = i * 11 + self.cflength
            boff = 0 # offset in bar
            v = []
            for j in range (11):
                idx = j + off
                a = self.get_allele (p, pop, idx)
                if self.args.fix_gene:
                    a = self.from_allele (a, idx)
                v.append (a)
            b = Bar (8, 8)
            cp.add (b)
            if maxidx is not None and off + 1 > maxidx:
                return tune
            l = 1 << v [0]
            assert 2 <= l <= 8
            b.add (Tone (dorian [v [1]], l))
            boff += l
            if boff == 2:
                if maxidx is not None and off + 3 > maxidx:
                    return tune
                l = 1 << v [2]
                assert 1 <= l <= 2
                b.add (Tone (dorian [v [3]], l))
                boff += l
            if boff == 3:
                if maxidx is not None and off + 4 > maxidx:
                    return tune
                b.add (Tone (dorian [v [4]], 1))
                boff += 1
            if boff == 4:
                if maxidx is not None and off + 6 > maxidx:
                    return tune
                l = 1 << v [5]
                assert 2 <= l <= 4
                b.add (Tone (dorian [v [6]], l))
                boff += l
            if boff == 5:
                # Probably never reached, prev tone may not be len 1
                if maxidx is not None and off + 7 > maxidx:
                    return tune
                b.add (Tone (dorian [v [7]], 1))
                boff += 1
            if boff == 6:
                if maxidx is not None and off + 9 > maxidx:
                    return tune
                l = 1 << v [8]
                assert 1 <= l <= 2
                b.add (Tone (dorian [v [9]], l))
                boff += l
            if boff == 7:
                if maxidx is not None and off + 10 > maxidx:
                    return tune
                b.add (Tone (dorian [v [10]], 1))
                boff += 1
        b  = Bar (8, 8)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the
        # subsemitonium for the contrapunctus.
        b.add (Tone (dorian.subsemitonium, 8))
        cp.add (b)
        b  = Bar (8, 8)
        b.add (Tone (dorian [7], 8))
        cp.add (b)
        return tune
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
            nbar.add (Tone (dorian [a], bd.tone_idx (b, t)))
            #print (bd.tune)
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
                #print ('\n'.join (self.explanation))
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
        cp.bars [-2].add (Tone (dorian.subsemitonium, 8))
        cp.bars [-1].add (Tone (dorian [7], 8))
        off = self.cplength - 1
        pos = -22 + 1
        seq = range (self.init [pos][0], self.init [pos][1] + 1)

        bd = Bardata (tune, seq)
        bd.add_bar (-4, (8,))
        bd.add_bar (-3, (4, 2, 2))
        return self._run_cf_end_check (bd)
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
        for c in melody_checks_cp:
            if hasattr (c, 'reset'):
                c.reset ()
            for bcp in tune.voices [1].bars [start:end]:
                for cp_obj in bcp.objects:
                    b, u = c.check (cp_obj)
                    if b or u:
                        self.explain (c)
                        return False
        for c in harmony_checks:
            if hasattr (c, 'reset'):
                c.reset ()
            for bcf, bcp in zip (*(v.bars [start:end] for v in tune.voices)):
                assert len (bcf.objects) == 1
                for cp_obj in bcp.objects:
                    b, u = c.check (bcf.objects [0], cp_obj)
                    if b or u:
                        self.explain (c)
                        return False
        return True
    # end def run_cp_checks

    def set_init (self):
        if self.cantus_firmus is None:
            self.cflength = self.tunelength - 3
        else:
            self.cflength = 0
        self.cplength   = self.tunelength - 2
        init            = []
        # Can't use '[[0, 7]] * cflength' due to aliasing
        for i in range (self.cflength):
            init.append ([0, 7])
        for i in range (self.cplength):
            init.append ([1,  3]) # duration heavy
            init.append ([0,  7]) # pitch
            init.append ([0,  1]) # duration light 1/4
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8
            init.append ([1,  2]) # duration half-heavy 1/4 or 1/2
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8
            init.append ([0,  1]) # duration light 1/4
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8
        self.init = init
    # end def set_init

    def verify_cantus_firmus (self):
        if not self.cantus_firmus:
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
            , stopping_rule_types = [pga.PGA_STOP_MAXITER]
            , max_GA_iter   = args.max_generations
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

    @tunelength.setter
    def tunelength (self, tl):
        if getattr (self, 'init', None):
            raise ValueError ('Not possible to set tunelength after init')
        self._tunelength = tl
    # end def tunelength

    def print_string (self, file, p, pop):
        if not self.prefix_printed or self.stop_reached:
            print (self.as_args (force = True), file = file)
            self.prefix_printed = True
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
            assert 0
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
            if not result:
                print ('No Cantus Firmus found')
                return
        else:
            if not self.verify_cantus_firmus ():
                print ('No valid Contrapunctus for this Cantus Firmus')
                return
        result = self.find_contrapunctus (0, 0)
        if not result:
            # This should never be reached unless we have rules or a CF
            # that make it fail early. Otherwise the user will interrupt
            # before we ever get here :-)
            print ('No Contrapunctus found')
            return
        r = []
        with Outfile (self.args.output_file) as f:
            print (self.as_complete_tune (force = True), file = f)
    # end def run

    def run_cf_checks (self, tune, idx):
        self.explanation = []
        for c in melody_checks_cf:
            if hasattr (c, 'reset'):
                c.reset ()
            # Check up to idx + 1 because first bar is hardcoded
            end = idx + 2
            # Check last two hardcoded bars if at end
            if idx >= self.cflength - 1:
                end = 3 + self.cflength
            for bar in tune.voices [0].bars [max (idx - 1, 0):end]:
                assert len (bar.objects) == 1
                b, u = c.check (bar.objects [0])
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
        )
    cmd.add_argument \
        ( "--do-not-fix-gene"
        , help    = "During gene reading do limit maximum of read values"
        , dest    = 'fix_gene'
        , action  = 'store_false'
        , default = True
        )
    cmd.add_argument \
        ( "-g", "--gene-file"
        , help    = "Read gene-file and output phenotype, no searching"
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
        ( "-R", "--random-seed"
        , help    = "Random seed initialisation for reproduceable results"
                    " default=%(default)s"
        , type    = int
        , default = 23
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
    >>> args = ['--de-variant', 'unknown']
    >>> r = main (args)
    Invalid --de-variant, use one of best, rand, either-or
    >>> r
    1
    >>> args = ['-c+']
    >>> r = main (args)
    --cantus-firmus=+ needs --gene-file option
    >>> r
    1
    """
    de_variants = ['best', 'rand', 'either-or']
    cmd  = contrapunctus_cmd ()
    args = cmd.parse_args (argv)
    if args.cantus_firmus == '+' and not args.gene_file:
        print ('--cantus-firmus=+ needs --gene-file option')
        return 1
    if args.de_variant not in de_variants:
        print ('Invalid --de-variant, use one of %s' % ', '.join (de_variants))
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

if __name__ == '__main__':
    main (sys.argv [1:]) # pragma: no cover
