#!/usr/bin/python

from   __future__ import print_function

import pga
from   Tune      import Tune, Voice, Bar, Meter, Tone, halftone, sgn
from   gregorian import dorian
from   pga       import PGA, PGA_REPORT_STRING, PGA_REPORT_ONLINE
from   pga       import PGA_STOP_NOCHANGE, PGA_STOP_MAXITER, PGA_STOP_TOOSIMILAR
from   argparse  import ArgumentParser
from   rsclib.iter_recipes import zip

class Create_Contrapunctus (PGA) :

    def __init__ (self, args) :
        self.args = args
        assert args.tune_length > 3
        self.tunelength = args.tune_length
        # Length of the automatically-generated voices
        self.v1length   = self.tunelength - 3
        self.v2length   = self.tunelength - 2
        stop_on = [PGA_STOP_NOCHANGE, PGA_STOP_MAXITER, PGA_STOP_TOOSIMILAR]
        PGA.__init__ \
            ( self, type (2), self.v1length + self.v2length
            , maximize      = False
            , init          = [(0,7)] * self.v1length + [(0,16)] * self.v2length
            , random_seed   = self.args.random_seed
            , pop_size      = 500
            , num_replace   = 250
            , print_options = [PGA_REPORT_STRING, PGA_REPORT_ONLINE]
            , stopping_rule_types = stop_on
            )
    # end def __init__

    def evaluate (self, p, pop) :
        jumpcount  = 0.0
        badness    = 1.0
        tune       = self.gen (p, pop)
        last       = ()
        jump       = [False, False]
        uglyness   = 1.0
        prim_seen  = False
        quint_seen = False
        okt_seen   = False
        dir        = (-1, 1)
        for tone in zip (tune.iter (0), tune.iter (1)) :
            dist = tone [1].halftone.offset - tone [0].halftone.offset
            if not last :
                last = tone
                if dist != 0 and dist != 7 and dist != 12 :
                    badness *= 100.
                continue
            off_o = tuple (last [n].halftone.offset for n in range (2))
            off_n = tuple (tone [n].halftone.offset for n in range (2))
            diff  = tuple (abs (off_o [n] - off_n [n]) for n in range (2))
            # Prim
            if diff [0] == 0 :
                badness *= 10.0
            if diff [1] == 0 :
                if prim_seen :
                    badness *= 10.0
                prim_seen = True
            # Septime
            for i in range (2) :
                if 10 <= diff [i] <= 11 :
                    badness *= 10.0
            # Devils interval:
            for i in range (2) :
                if diff [i] == 6 :
                    badness *= 10.0
            if diff [0] > 2 :
                # Jump
                if jump [0] :
                    # No two jumps in series
                    badness *= 10.0
                jump [0] = sgn (off_n [0] - off_o [0])
                if diff [0] == 5 or diff [0] == 7 :
                    uglyness += 1
                if 8 <= diff [0] <= 9 :
                    uglyness += 10
                if diff [0] == 12 :
                    uglyness += 2
            else :
                # Step not jump
                # After a jump movement should not be same direction
                if jump [0] == sgn (off_n [0] - off_o [0]) :
                    badness *= 10.0
                jump [0] = False
            if diff [1] > 2 :
                # Jump
                if jump [1] == sgn (off_n [1] - off_o [1]) :
                    # No two jumps in same direction
                    badness *= 10.0
                jump [1] = sgn (off_n [1] - off_o [1])
            else :
                jump [1] = False
            # Not both voices may jump
            if jump [0] and jump [1] :
                badness *= 10.0
            # Prime or Sekund between tones
            if 0 <= dist <= 2 :
                badness *= 10.0
            if 5 <= dist <= 6 :
                badness *= 10.0
            if 10 <= dist <= 11 :
                badness *= 10.0
            # Don't get carried away :-)
            if dist > 14 :
                badness *= 10.0
            # Upper voice must be *up*
            if dist < 0 :
                badness *= 10.0
            if dist == 7 or dist == 12 :
                if dir [0] == dir [1] :
                    badness *= 9.0
            # For sext (sixth) or terz (third) don't allow several in a row
            if 3 <= dist <= 4 or 8 <= dist <= 9 :
                if dir [0] == dir [1] == 0 :
                    uglyness += 3
            dir  = tuple (sgn (off_n [n] - off_o [n]) for n in range (2))
            last = tone
        return uglyness * badness
    # end def evaluate

    def gen (self, p, pop) :
        v1 = Voice (id = 'V1')
        b  = Bar (4, 4)
        b.add (Tone (dorian.finalis, 4, unit = 4))
        v1.add (b)
        for i in range (self.v1length) :
            a = self.get_allele (p, pop, i)
            b = Bar (4, 4)
            b.add (Tone (dorian [a], 4, unit = 4))
            v1.add (b)
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
            , key    = 'C'
            , unit   = 4
            , score  = '(V2) (V1)'
            )
        tune.add (v1)
        v2 = Voice (id = 'V2')
        for i in range (self.v2length) :
            a = self.get_allele (p, pop, i + self.v1length)
            b = Bar (4, 4)
            b.add (Tone (dorian [a], 4, unit = 4))
            v2.add (b)
        b  = Bar (4, 4)
        # FIXME: Don't hard-code subsemitonium
        b.add (Tone (halftone ('^c'), 4, unit = 4))
        v2.add (b)
        b  = Bar (4, 4)
        b.add (Tone (dorian [7], 4, unit = 4))
        v2.add (b)
        tune.add (v2)
        return tune
    # end def gen

    def print_string (self, file, p, pop) :
        tune = self.gen (p, pop)
        print (tune, file = file)
    # end def print_string

# end class Create_Contrapunctus

def main () :
    cmd = ArgumentParser ()
    cmd.add_argument \
        ( "-r", "--random-seed"
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
    args = cmd.parse_args ()
    cp = Create_Contrapunctus (args)
    cp.run ()
# end def main

if __name__ == '__main__' :
    main ()

