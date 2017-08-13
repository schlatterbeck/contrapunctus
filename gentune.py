#!/usr/bin/python

from   __future__    import print_function
import pga
from   Tune          import Tune, Voice, Bar, Meter, Tone, halftone, sgn
from   gregorian     import dorian
from   pga           import PGA, PGA_REPORT_STRING, PGA_REPORT_ONLINE

class Create_Contrapunctus (PGA) :

    def evaluate (self, p, pop) :
        jumpcount = 0.0
        badness   = 1.0
        tune      = self.gen (p, pop)
        last      = None
        jump      = False
        uglyness  = 1.0
        for tone in tune.iter (0) :
            if not last :
                last = tone
                continue
            off_o = last.halftone.offset
            off_n = tone.halftone.offset
            diff  = abs (off_o - off_n)
            # Prim
            if diff == 0 :
                badness *= 1000.0
            # Septime
            if 10 <= diff <= 11 :
                badness *= 1000.0
            # Devils interval:
            if diff == 6 :
                badness *= 1000.0
            # Good: step 1 <= diff <= 2
            if diff > 2 :
                # Jump
                if jump :
                    # No two jumps in series
                    badness *= 1000.0
                jump = sgn (off_n - off_o)
                if diff == 5 or diff == 7 :
                    uglyness += 50
                if 8 <= diff <= 9 :
                    uglyness += 500
                if diff == 12 :
                    uglyness += 100
            else :
                # Step not jump
                # After a jump movement should not be same direction
                if jump == sgn (off_n - off_o) :
                    badness *= 1000
                jump = False
            last = tone
        return uglyness * badness
    # end def evaluate

    def gen (self, p, pop) :
        v1 = Voice (id = 'V1')
        b  = Bar (4, 4)
        b.add (Tone (dorian.finalis, 4, unit = 4))
        v1.add (b)
        for i in range (len (self)) :
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
            (number = 1, meter = Meter (4, 4), Q = '1/4=370', key='C', unit = 4)
        tune.add (v1)
        return tune
    # end def gen

    def print_string (self, file, p, pop) :
        tune = self.gen (p, pop)
        print (tune, file = file)
    # end def print_string

# end class Create_Contrapunctus

def main () :
    cp = Create_Contrapunctus \
        ( type (2), 8
        , maximize = False
        , init     = [(0,7)] * 8
        , print_options = \
            [ PGA_REPORT_STRING
            , PGA_REPORT_ONLINE
            ]
        )
    cp.run ()
# end def main

if __name__ == '__main__' :
    main ()

