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

from   __future__ import print_function

import sys
import pga
from   .tune      import Tune, Voice, Bar, Meter, Tone, halftone, sgn
from   .gregorian import dorian
from   argparse   import ArgumentParser

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

    def __init__ (self, args):
        self.args = args
        assert args.tune_length > 3
        self.tunelength = args.tune_length
        # Length of the automatically-generated voices
        self.v1length   = self.tunelength - 3
        self.v2length   = self.tunelength - 2
        stop_on = \
            [ pga.PGA_STOP_NOCHANGE
            , pga.PGA_STOP_MAXITER
            , pga.PGA_STOP_TOOSIMILAR
            ]
        d = dict \
            ( maximize      = False
            , init          = [(0,7)] * self.v1length + [(0,16)] * self.v2length
            , random_seed   = self.args.random_seed
            , pop_size      = 500
            , num_replace   = 450
            , print_options = [pga.PGA_REPORT_STRING]
            , stopping_rule_types = stop_on
            )
        if self.args.output_file:
            d ['output_file'] = args.output_file
        super ().__init__ (type (2), self.v1length + self.v2length, **d)
    # end def __init__

    def evaluate (self, p, pop):
        jumpcount  = 0.0
        badness    = 1.0
        tune       = self.phenotype (p, pop)
        jump       = [False, False]
        uglyness   = 1.0
        prim_seen  = False
        par_fifth  = False
        par_oct    = False
        quint_seen = False
        okt_seen   = False
        dir        = (-1, 1)

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
        # For now each bar object only contains a single Tone object.
        for cp, cf in zip (tune.iter (0), tune.iter (1)):
            # For now a bar only contains one single note, the 0th
            # object in bar
            cf_tone = cf.objects [0].halftone.offset
            cp_tone = cp.objects [0].halftone.offset
            prev_cf = cf.prev
            prev_cp = cp.prev
            # dist is the distance between cp and cf
            dist = cf_tone - cp_tone
            # First note
            if not prev_cf:
                # 1.1. Begin and end on either unison, octave, fifth,
                # unless the added part is underneath [it isn't here],
                # in which case begin and end only on unison or octave.
                if dist != 0 and dist != 7 and dist != 12:
                    badness *= 100.
                continue
            p_cp_tone = prev_cp.objects [0].halftone.offset
            p_cf_tone = prev_cf.objects [0].halftone.offset

            off_o = (p_cp_tone, p_cf_tone)
            off_n = (cp_tone,   cf_tone)
            diff  = tuple (abs (off_o [n] - off_n [n]) for n in range (2))
            # 0.1.2: "Permitted melodic intervals are the perfect fourth,
            # fifth, and octave, as well as the major and minor second,
            # major and minor third, and ascending minor sixth. The
            # ascending minor sixth must be immediately followed by
            # motion downwards." This means we allow the following
            # halftone intervals: 1, 2, 3, 4, 5, 7, 8, 9, 12 and forbid
            # the following: 0, 6, 10, 11
            # We currently allow sixth in both directions
            # We allow unison in the second voice but not several in a
            # series.

            # 0.1.2: No unison (Prim) allowed
            if diff [0] == 0:
                badness *= 10.0
            if diff [1] == 0:
                if prim_seen:
                    badness *= 10.0
                prim_seen = True
            # 0.1.2: no seventh (Septime)
            for i in range (2):
                if 10 <= diff [i] % 12 <= 11:
                    badness *= 10.0
            # 0.1.2: no Devils interval:
            for i in range (2):
                if diff [i] % 12 == 6:
                    badness *= 10.0
            # First voice (Cantus Firmus):
            if diff [0] > 2:
                # Jump
                if jump [0]:
                    # No two jumps in series
                    badness *= 10.0
                jump [0] = sgn (off_n [0] - off_o [0])
                if diff [0] == 5 or diff [0] == 7:
                    uglyness += 1
                if 8 <= diff [0] <= 9:
                    uglyness += 10
                if diff [0] == 12:
                    uglyness += 2
            else:
                # Step not jump
                # After a jump movement should not be same direction
                if jump [0] == sgn (off_n [0] - off_o [0]):
                    badness *= 10.0
                jump [0] = False
            if diff [1] > 2:
                # Jump
                if jump [1] == sgn (off_n [1] - off_o [1]):
                    # No two jumps in same direction
                    badness *= 10.0
                jump [1] = sgn (off_n [1] - off_o [1])
            else:
                jump [1] = False
            # Not both voices may jump
            if jump [0] and jump [1]:
                badness *= 10.0
            # Prime or Sekund between tones
            # 1.2: Use no unisons except at the beginning or end.
            if dist == 0:
                badness *= 10.0
            if 1 <= dist % 12 <= 2:
                badness *= 10.0
            # 1.4: Avoid moving in parallel fourths (In practice
            # Palestrina and others frequently allowed themselves such
            # progressions, especially if they do not involve the lowest
            # of the parts)
            # Magdalena: 5/6 verboten
            if 5 <= dist % 12 <= 6:
                badness *= 10.0
            # Magdalena: 10/11 verboten
            if 10 <= dist <= 11:
                badness *= 10.0
            # Don't get carried away :-)
            # 0.2.5: "The interval of a tenth should not be exceeded
            # between two adjacent parts unless by necessity." We limit
            # this to a ninth.
            # 1.6: Attempt to keep any two adjacent parts within a tenth
            # of each other, unless an exceptionally pleasing line can
            # be written by moving outside of that range.
            if dist > 16:
                badness *= 10.0
            # Magdalena: intervals above octave should be avoided
            if dist > 12:
                uglyness += 1
            # Upper voice must be *up*
            if dist < 0:
                badness *= 10.0
            dir  = tuple (sgn (off_n [n] - off_o [n]) for n in range (2))
            # Magdalena: Avoid parallel fifth or octaves: Ensure that
            # the last direction (from where is the fifth or octave
            # approached) is different.
            if dist == 7 or dist == 12:
                if dir [0] == dir [1]:
                    badness *= 9.0
            # For sext (sixth) or terz (third) don't allow several in a row
            if 3 <= dist <= 4 or 8 <= dist <= 9:
                if dir [0] == dir [1] == 0:
                    uglyness += 3
            # Generally it's better that voices move in opposite
            # direction (or one stays the same if allowed)
            if dir [0] == dir [1]:
                uglyness += 0.1
        return uglyness * badness
    # end def evaluate

    def from_gene (self):
        idx = 0
        with open (self.args.gene_file, 'r') as f:
            c = 0
            if self.args.best_eval:
                for n, line in enumerate (f):
                    if line.startswith ('The Best String:'):
                        c = n
                        break
            for n, line in enumerate (f):
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
                    break
            else:
                raise ValueError ("Line %s: Gene too short" % ln)
        self.print_string (sys.stdout, 1, pga.PGA_NEWPOP)
        if self.args.verbose:
            print (self.evaluate (1, pga.PGA_NEWPOP))
    # end def from_gene

    def phenotype (self, p, pop):
        v1 = Voice (id = 'V1')
        b  = Bar (4, 4)
        b.add (Tone (dorian.finalis, 4, unit = 4))
        v1.add (b)
        for i in range (self.v1length):
            a = self.get_allele (p, pop, i)
            b = Bar (4, 4)
            b.add (Tone (dorian [a], 4, unit = 4))
            v1.add (b)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the step2 for
        # the first voice.
        # 1.1: "The counterpoint must begin and end on a perfect
        # consonance" is also achived by hard-coding the last tone.
        b  = Bar (4, 4)
        b.add (Tone (dorian.step2, 4, unit = 4))
        v1.add (b)
        b  = Bar (4, 4)
        b.add (Tone (dorian.finalis, 4, unit = 4))
        v1.add (b)
        tune = Tune \
            ( number = 1
            , meter  = Meter (4, 4)
            , Q      = '1/4=370'
            , key    = 'DDor'
            , unit   = 4
            , score  = '(V2) (V1)'
            )
        tune.add (v1)
        v2 = Voice (id = 'V2')
        for i in range (self.v2length):
            a = self.get_allele (p, pop, i + self.v1length)
            b = Bar (4, 4)
            b.add (Tone (dorian [a], 4, unit = 4))
            v2.add (b)
        b  = Bar (4, 4)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the
        # subsemitonium for the second voice.
        b.add (Tone (dorian.subsemitonium, 4, unit = 4))
        v2.add (b)
        b  = Bar (4, 4)
        b.add (Tone (dorian [7], 4, unit = 4))
        v2.add (b)
        tune.add (v2)
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
        , type    = int
        , default = 23
        )
    cmd.add_argument \
        ( "-l", "--tune-length"
        , help    = "Length of generated tune"
        , type    = int
        , default = 11
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

