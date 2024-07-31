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
from   .tune      import Tune, Voice, Bar, Meter, Tone, halftone, sgn
from   .gregorian import dorian, hypodorian
from   .checks    import *
from   argparse   import ArgumentParser
from   copy       import deepcopy

class Create_Contrapunctus (pga.PGA):

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
    """

    # 0.1.2: "Permitted melodic intervals are the perfect fourth, fifth,
    # and octave, as well as the major and minor second, major and minor
    # third, and ascending minor sixth. The ascending minor sixth must
    # be immediately followed by motion downwards." This means we allow
    # the following halftone intervals: 1, 2, 3, 4, 5, 7, 8, 9, 12 and
    # forbid the following: 0, 6, 10, 11
    # We currently allow sixth in both directions
    # We allow unison in the second voice but not several in a series.
    melody_checks_cf = \
        [ Check_Melody_Interval
            ( "0.1.2: no seventh (Septime)"
            , interval = (10, 11)
            , badness  = 10.0
            )
        , Check_Melody_Interval
            ( "0.1.2: no Devils interval"
            , interval = (6,)
            , badness  = 10.0
            )
        , Check_Melody_Interval
            ("0.1.2: No unison (Prim) allowed"
            , interval =  (0,)
            , badness  = 10.0
            , octave   = False
            )
        , Check_Melody_Interval
            ( "5 or 7"
            , interval =  (5, 7)
            , ugliness = 1.0
            , octave   = False
            )
        , Check_Melody_Interval
            ( "8 or 9"
            , interval =  (8, 9)
            , ugliness = 10.0
            , octave   = False
            )
        , Check_Melody_Interval
            ( "Octave"
            , interval =  (12,)
            , ugliness = 2.0
            , octave   = False
            )
        , Check_Melody_Jump
            ( "Jump"
            , badness = 10.0
            )
        ]
    melody_checks_cp = \
        [ Check_Melody_Interval
            ( "0.1.2: no seventh (Septime)"
            , interval = (10, 11)
            , badness  = 10.0
            )
        , Check_Melody_Interval
            ( "0.1.2: no Devils interval"
            , interval = (6,)
            , badness  = 10.0
            )
        , Check_Melody_Interval
            ("0.1.2: No consecutive unison (Prim) allowed"
            , interval    = (0,)
            , badness     = 10.0
            , octave      = False
            , only_repeat = True
            )
        , Check_Melody_Jump
            ( "Jump"
            , badness = 10.0
            )
        ]
    harmony_interval_checks = \
        [ Check_Harmony_Interval
            ( "1.2: Use no unisons except at the beginning or end"
            , interval  = (0,)
            , badness   = 10.0
            , octave    = False
            , not_first = True
            , not_last  = True
            )
        , Check_Harmony_Interval
            ( "No Sekund"
            , interval = (1, 2)
            , badness  = 10.0
            , octave   = True
            )
        , Check_Harmony_Interval
            ( "Magdalena: 5/6 verboten"
            , interval = (5, 6)
            , badness  = 10.0
            , octave   = True
            )
        , Check_Harmony_Interval
            ( "Magdalena: 10/11 verboten"
            , interval = (10, 11)
            , badness  = 10.0
            , octave   = True
            )
        # 1.6: Attempt to keep any two adjacent parts within a tenth
        # of each other, unless an exceptionally pleasing line can
        # be written by moving outside of that range.
        , Check_Harmony_Interval_Max
            ( "max. 16"
            , maximum  = 16
            , badness  = 10.0
            )
        , Check_Harmony_Interval_Max
            ( "Magdalena: intervals above octave should be avoided"
            , maximum  = 12
            , ugliness = 1.0
            )
        , Check_Harmony_Interval_Min
            ( "Contrapunctus voice must be *up*"
            , minimum  = 0
            , badness  = 10.0
            )
        , Check_Harmony_First_Interval
            ( "1.1. Begin and end on either unison, octave, fifth,"
              " unless the added part is underneath [it isn't here],"
              " in which case begin and end only on unison or octave."
            , interval = (0, 7, 12)
            , badness  = 100.
            )
        ]
    harmony_melody_checks = \
        [ Check_Melody_Jump_2
            ( "Not both voices may jump"
            , badness  = 10.0
            )
        # This might need more history, should probably only trigger if
        # the *last* was already a fifth or octave. And switching from
        # fifth to octave ore vice-versa might still be allowed, in
        # which case we would need *two* checks.
        #, Check_Harmony_Melody_Direction
        #    ( "Magdalena: Avoid parallel fifth or octaves: Ensure that"
        #      " the last direction (from where is the fifth or octave"
        #      " approached) is different."
        #    , interval = (7, 12)
        #    , dir      = 'same'
        #    , badness  = 9.0
        #    )
        # This implements the spec above
        , Check_Harmony_History
            ( "Magdalena: Avoid parallel fifth"
            , interval = (7,)
            , badness  = 9.0
            )
        , Check_Harmony_History
            ( "Magdalena: Avoid parallel octaves"
            , interval = (12,)
            , badness  = 9.0
            )

        # This only checks for two of the *same*. Not if we have several
        # sixth in a row with different CF. This might need changes to
        # the underlying check implementation.
        #, Check_Harmony_Melody_Direction
        #    ( "For sext (sixth) or terz (third) don't allow several in a row"
        #    , interval = (3, 4, 8, 9)
        #    , dir      = 'zero'
        #    , ugliness = 3
        #    )
        # This doesn't allow several (unrelated) sixth or thirds in a row
        , Check_Harmony_History
            ( "For sext (sixth) don't allow several in a row"
            , interval = (8, 9)
            , ugliness = 3
            )
        , Check_Harmony_History
            ( "For terz (third) don't allow several in a row"
            , interval = (3, 4)
            , ugliness = 3
            )
        , Check_Harmony_Melody_Direction
            ( "Generally it's better that voices move in opposite"
              " direction (or one stays the same if allowed)"
            , interval = () # All
            , dir      = 'same'
            , ugliness = 0.1
            )
        ]

    def __init__ (self, args):
        self.do_explain  = False
        self.explanation = []
        self.args        = args
        self.tunelength  = args.tune_length
        assert args.tune_length > 3
        # The first voice in the gene is the cantus firmus, the second
        # voice is the contrapunctus.
        # Length of the automatically-generated voices
        # Now that we allow up to 1/8 notes the gene for the first voice
        # is longer.
        # A bar can contain at most 14 notes:
        # - A 'heavy' position must not contain 1/8
        # - so we have at least 2*1/4 for the heavy position
        # - and the rest 1/8 makes 16/8 - 2*1/4 = 12/8
        # We have for each note in a bar:
        # - length of note (or pause, for now we do not generate a pause)
        # - the length can only be 16, 12, 8, 6, 4, 3, 2, 1
        # But we only use one bar (8/8) and we bind the second note if
        # it is the same pitch (maybe with some probability). The gene
        # coding is:
        # - log_2 of the length (left out if there is only 1 possibility)
        # - pitch for each note
        # Thats 7 pairs of genes (where the length is sometimes left out):
        # - 1-3 (8, 4, 2)/8, the heavy position has at least 1/4
        # - pitch 0-16
        # - 0-1 (2 or 1)/8 for first 1/4 light position
        # - pitch 0-16
        # - pitch 0-16 (1/8 light can only be 1/8, so no length)
        # - 1-2 (4, 2)/8, the half-heavy position has at least 1/4
        # - pitch 0-16
        # - pitch 0-16 (1/8 light can only be 1/8)
        # - 0-1 (2 or 1)/8
        # - pitch 0-16
        # - pitch 0-16 (1/8 light can only be 1/8)
        # if the previous note is longer some of the genes are not used

        self.cflength   = self.tunelength - 3
        self.cplength   = self.tunelength - 2
        init            = [(0,7)] * self.cflength
        for i in range (self.cplength):
            init.append ((1,  3)) # duration heavy
            init.append ((0,  7)) # pitch
            init.append ((0,  1)) # duration light 1/4
            init.append ((0,  7)) # pitch
            init.append ((0,  7)) # pitch light 1/8
            init.append ((1,  2)) # duration half-heavy 1/4 or 1/2
            init.append ((0,  7)) # pitch
            init.append ((0,  7)) # pitch light 1/8
            init.append ((0,  1)) # duration light 1/4
            init.append ((0,  7)) # pitch
            init.append ((0,  7)) # pitch light 1/8
        stop_on = \
            [ pga.PGA_STOP_NOCHANGE
            , pga.PGA_STOP_MAXITER
            , pga.PGA_STOP_TOOSIMILAR
            ]
        d = dict \
            ( maximize      = False
            , init          = init
            , random_seed   = self.args.random_seed
            , pop_size      = 500
            , num_replace   = 450
            , print_options = [pga.PGA_REPORT_STRING]
            , stopping_rule_types = stop_on
            )
        if self.args.output_file:
            d ['output_file'] = args.output_file
        super ().__init__ (type (2), len (init), **d)
    # end def __init__

    def evaluate (self, p, pop):
        tune       = self.phenotype (p, pop)
        badness    = 1.0
        ugliness   = 1.0
        dir        = (-1, 1)
        # Reset history
        for check in self.melody_checks_cf:
            check.reset ()
        for check in self.melody_checks_cp:
            check.reset ()
        for check in self.harmony_melody_checks:
            check.reset ()
        # harmony_interval_checks do not need reset

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

            for check in self.melody_checks_cf:
                b, u = check.check (cf_obj)
                if b:
                    badness *= b
                ugliness += u
                self.explain (check)
            bsum = usum = 0
            for cp_obj in cp.objects:
                for check in self.melody_checks_cp:
                    b, u = check.check (cp_obj)
                    bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                    usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                    self.explain (check)
                for check in self.harmony_interval_checks:
                    b, u = check.check (cf_obj, cp_obj)
                    bsum += b * len (cp_obj) ** 2 / cp_obj.bar.unit
                    usum += u * len (cp_obj) ** 2 / cp_obj.bar.unit
                    self.explain (check)
                for check in self.harmony_melody_checks:
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

    def from_gene_lines (self, iter):
        idx = 0
        c   = 0
        if self.args.best_eval:
            for n, line in enumerate (iter):
                if line.startswith ('The Best String:'):
                    c = n
                    break
        for n, line in enumerate (iter):
            ln = n + 1 + c
            if not line.startswith ('#'):
                continue
            i, l = line [1:].split (':')
            i = int (i)
            if i != idx:
                raise ValueError ("Line %s: Invalid gene-file format" % ln)
            for offs, i in enumerate (l.split (',')):
                if idx + offs + 1 > len (self):
                    raise ValueError ("Line %s: Gene too long" % ln)
                i = int (i.strip ().lstrip ('[').rstrip (']').strip ())
                self.set_allele (1, pga.PGA_NEWPOP, idx + offs, i)
            idx += offs + 1
            if idx + 1 > len (self):
                idx = 0
                yield True
        else:
            if idx > 0:
                raise ValueError ("Line %s: Gene too short" % ln)
    # end def from_gene_lines

    def from_gene (self):
        with open (self.args.gene_file, 'r') as f:
            for k in self.from_gene_lines (f):
                self.print_string (sys.stdout, 1, pga.PGA_NEWPOP)
                if self.args.verbose:
                    self.do_explain = True
                    print ('Eval: %g' % self.evaluate (1, pga.PGA_NEWPOP))
                    print ('\n'.join (self.explanation))
    # end def from_gene

    def phenotype (self, p, pop):
        cf = Voice (id = 'CantusFirmus')
        b  = Bar (8, 8)
        b.add (Tone (dorian.finalis, 8, unit = 8))
        cf.add (b)
        for i in range (self.cflength):
            a = self.get_allele (p, pop, i)
            b = Bar (8, 8)
            b.add (Tone (hypodorian [a], 8, unit = 8))
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
        b  = Bar (8, 8)
        b.add (Tone (dorian.step2, 8, unit = 8))
        cf.add (b)
        b  = Bar (8, 8)
        b.add (Tone (dorian.finalis, 8, unit = 8))
        cf.add (b)
        tune = Tune \
            ( number = 1
            , meter  = Meter (4, 4)
            , Q      = '1/4=200'
            , key    = 'DDor'
            , unit   = 8
            , score  = '(Contrapunctus) (CantusFirmus)'
            )
        tune.add (cf)
        cp  = Voice (id = 'Contrapunctus')
        off = self.cflength
        for i in range (self.cplength):
            boff = 0 # offset in bar
            v = []
            for j in range (11):
                v.append (self.get_allele (p, pop, j + off))
            off += 11
            b = Bar (8, 8)
            l = 1 << v [0]
            assert 2 <= l <= 8
            b.add (Tone (dorian [v [1]], l, unit = 8))
            boff += l
            if boff == 2:
                l = 1 << v [2]
                assert 1 <= l <= 2
                b.add (Tone (dorian [v [3]], l, unit = 8))
                boff += l
            if boff == 3:
                b.add (Tone (dorian [v [4]], 1, unit = 8))
                boff += 1
            if boff == 4:
                l = 1 << v [5]
                assert 2 <= l <= 4
                b.add (Tone (dorian [v [6]], l, unit = 8))
                boff += l
            if boff == 5:
                # Probably never reached, prev tone may not be len 1
                b.add (Tone (dorian [v [7]], 1, unit = 8))
                boff += 1
            if boff == 6:
                l = 1 << v [8]
                assert 1 <= l <= 2
                b.add (Tone (dorian [v [9]], l, unit = 8))
                boff += l
            if boff == 7:
                b.add (Tone (dorian [v [10]], 1, unit = 8))
                boff += 1
            cp.add (b)
        b  = Bar (8, 8)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the
        # subsemitonium for the contrapunctus.
        b.add (Tone (dorian.subsemitonium, 8, unit = 8))
        cp.add (b)
        b  = Bar (8, 8)
        b.add (Tone (dorian [7], 8, unit = 8))
        cp.add (b)
        tune.add (cp)
        return tune
    # end def phenotype

    def print_string (self, file, p, pop):
        tune = self.phenotype (p, pop)
        if self.args.transpose:
            tune = tune.transpose (self.args.transpose)
        print (tune, file = file)
        file.flush ()
        super ().print_string (file, p, pop)
    # end def print_string

# end class Create_Contrapunctus

def main (argv = None):
    cmd = ArgumentParser ()
    cmd.add_argument \
        ( "-b", "--best-eval"
        , help    = "Asume a search trace for -g option and output best"
        , action  = 'store_true'
        )
    cmd.add_argument \
        ( "-g", "--gene-file"
        , help    = "Read gene-file and output phenotype, no searching"
        )
    cmd.add_argument \
        ( "-R", "--random-seed"
        , help    = "Random seed initialisation for reproduceable results"
                    " default=%(default)s"
        , type    = int
        , default = 23
        )
    cmd.add_argument \
        ( "-l", "--tune-length"
        , help    = "Length of generated tune, default=%(default)s"
        , type    = int
        , default = 12
        )
    cmd.add_argument \
        ( "-O", "--output-file"
        , help    = "Output file for progress information"
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
        , action  = 'store_true'
        )
    args = cmd.parse_args (argv)
    cp = Create_Contrapunctus (args)
    if args.gene_file:
        cp.from_gene ()
    else:
        cp.run ()
# end def main

if __name__ == '__main__':
    main (sys.argv [1:])

