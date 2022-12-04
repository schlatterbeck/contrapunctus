#!/usr/bin/python3

import os
import pytest
import doctest
import contrapunctus
import contrapunctus.tune
import contrapunctus.circle
import contrapunctus.gentune
import contrapunctus.gregorian

from contrapunctus.tune  import Voice, Bar, Tone, Tune, Pause, halftone, Meter

tune_output = """\
X: 1
T: Zocharti Loch
M: 4/4
C: Louis Lewandowski (1821-1894)
Q: 1/4=76
%%score (T1 T2) (B1)
L: 1/8
V:T1 clef=treble-8 name="Tenore I" snm=T.I
V:T2 clef=treble-8 name="Tenore II" snm=T.II
V:B1 clef=bass name="Basso I" snm=B.I transpose=-24 middle=d
K: Gm
[V:T1] B2 c2 d2 g2 |f6 e2 |d2 c2 d2 e2 |d4 c2 z2 |
[V:T2] G2 A2 B2 e2 |d6 c2 |B2 A2 B2 c2 |B4 A2 z2 |
[V:B1] z8 |z2 f2 g2 a2 |b2 z2 z2 e2 |f4 f2 z2 |
"""

class Test_Contrapunctus:

    def test_tune (self):
        v1 = Voice (id = 'T1', clef='treble-8', name='Tenore I', snm='T.I')
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('B'), 2))
        b1.add (Tone (halftone ('c'), 2))
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('g'), 2))
        v1.add (b1)
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('f'), 6))
        b1.add (Tone (halftone ('e'), 2))
        v1.add (b1)
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('c'), 2))
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('e'), 2))
        v1.add (b1)
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('d'), 4))
        b1.add (Tone (halftone ('c'), 2))
        b1.add (Pause (2))
        v1.add (b1)

        v2 = Voice (id = 'T2', clef='treble-8', name='Tenore II', snm='T.II')
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('G'), 2))
        b2.add (Tone (halftone ('A'), 2))
        b2.add (Tone (halftone ('B'), 2))
        b2.add (Tone (halftone ('e'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('d'), 6))
        b2.add (Tone (halftone ('c'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('B'), 2))
        b2.add (Tone (halftone ('A'), 2))
        b2.add (Tone (halftone ('B'), 2))
        b2.add (Tone (halftone ('c'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('B'), 4))
        b2.add (Tone (halftone ('A'), 2))
        b2.add (Pause (2))
        v2.add (b2)

        v3 = Voice \
            ( id        = 'B1'
            , clef      = 'bass'
            , name      = 'Basso I'
            , snm       = 'B.I'
            , transpose = '-24'
            , middle    = 'd'
            )
        b3 = Bar (8, 8)
        b3.add (Pause (8))
        v3.add (b3)
        b3 = Bar (8, 8)
        b3.add (Pause (2))
        b3.add (Tone (halftone ('f'), 2))
        b3.add (Tone (halftone ('g'), 2))
        b3.add (Tone (halftone ('a'), 2))
        v3.add (b3)
        b3 = Bar (8, 8)
        b3.add (Tone (halftone ('b'), 2))
        b3.add (Pause (2))
        b3.add (Pause (2))
        b3.add (Tone (halftone ('e'), 2))
        v3.add (b3)
        b3 = Bar (8, 8)
        b3.add (Tone (halftone ('f'), 4))
        b3.add (Tone (halftone ('f'), 2))
        b3.add (Pause (2))
        v3.add (b3)

        t = Tune \
            ( number = 1
            , title  = 'Zocharti Loch'
            , C      = 'Louis Lewandowski (1821-1894)'
            , meter  = Meter (4, 4)
            , Q      = '1/4=76'
            , key    = 'Gm'
            , score  = '(T1 T2) (B1)'
            )
        t.add (v1)
        t.add (v2)
        t.add (v3)
        assert t.as_abc ().strip () == tune_output.strip ()
    # end def test_tune
# end class Test_Contrapunctus

class Test_Doctest:

    flags = doctest.NORMALIZE_WHITESPACE

    num_tests = dict \
        ( circle    =  2
        , gentune   =  0
        , gregorian = 10
        , tune      = 99
        )

    def test_doctest (self):
        fmt = '%(name)s.py passes all of %(num)s doc-tests'
        for name in self.num_tests:
            num = self.num_tests [name]
            m = getattr (contrapunctus, name)
            f, t = doctest.testmod \
                (m, verbose = False, optionflags = self.flags)
            fn = os.path.basename (m.__file__)
            format_ok  = '%(fn)s passes all of %(t)s doc-tests'
            format_nok = '%(fn)s fails %(f)s of %(t)s doc-tests'
            if f:
                msg = format_nok % locals ()
            else:
                msg = format_ok % locals ()
            assert (fmt % locals () == msg)
    # end def test_doctest
# end class Test_Doctest
