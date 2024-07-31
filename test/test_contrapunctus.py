# Copyright (C) 2017-2022 Dr. Ralf Schlatterbeck Open Source Consulting.
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

#!/usr/bin/python3

import os
import pytest
import doctest
import contrapunctus
import contrapunctus.tune
import contrapunctus.circle
import contrapunctus.gentune
import contrapunctus.gregorian
from pga.testsupport import PGA_Test_Instrumentation
from contrapunctus.tune import Voice, Bar, Tone, Tune, Pause, halftone, Meter
from contrapunctus.gentune import main as gentune_main
from contrapunctus.checks import *

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

class Test_Contrapunctus (PGA_Test_Instrumentation):

    def test_tune (self):
        if pytest.mpi_rank != 0:
            return
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

    def test_prev (self):
        v1 = Voice (id = 'V1')
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('a'), 1))
        b1.add (Tone (halftone ('b'), 1))
        b1.add (Tone (halftone ('c'), 1))
        b1.add (Tone (halftone ('d'), 1))
        b1.add (Tone (halftone ('e'), 1))
        b1.add (Tone (halftone ('f'), 1))
        b1.add (Tone (halftone ('g'), 1))
        b1.add (Pause (1))
        v1.add (b1)
        t = b1.objects [-1]
        assert isinstance (t, Pause)
        tones = []
        while t:
            t = t.prev
            if t:
                tones.append (t.as_abc ())
        assert ' '.join (tones) == 'g1 f1 e1 d1 c1 b1 a1'
    # end def test_prev

    def test_check_harmony_interval_max (self):
        check = Check_Harmony_Interval_Max \
            ('must be up', maximum = 12, badness = 1)
        t_cf  = Tone (halftone ('E'), 8)
        t_cp  = Tone (halftone ('e'), 8)
        t_cp2 = Tone (halftone ('f'), 8)
        # This is the normal order of parameters for checks, cf first
        b, u = check.check (t_cf, t_cp)
        assert b == 0
        b, u = check.check (t_cf, t_cp2)
        assert b == 1
    # end def test_check_harmony_interval_max

    def test_check_harmony_interval_min (self):
        check = Check_Harmony_Interval_Min \
            ('must be up', minimum = 0, badness = 1)
        t_cp = Tone (halftone ('e'), 8)
        t_cf = Tone (halftone ('f'), 8)
        # This is the normal order of parameters for checks, cf first
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 0
        b, u = check.check (t_cp, t_cp)
        assert b == 0
    # end def test_check_harmony_interval_min

    def test_check_harmony_interval_octave (self):
        check = Check_Harmony_Interval \
            ( 'Sekund'
            , interval = (1, 2)
            , badness  = 1
            , octave   = True
            )
        t_cp = Tone (halftone ('e'), 8)
        t_cf = Tone (halftone ('f'), 8)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        t_cp = Tone (halftone ('c'), 8)
        t_cf = Tone (halftone ('d'), 8)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        t_cp = Tone (halftone ('C'), 8)
        t_cf = Tone (halftone ('d'), 8)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        t_cp = Tone (halftone ('c'), 8)
        t_cf = Tone (halftone ('e'), 8)
        b, u = check.check (t_cf, t_cp)
        assert b == 0
        b, u = check.check (t_cp, t_cf)
        assert b == 0
    # end def test_check_harmony_interval_octave

    def test_check_harmony_interval_sign (self):
        check = Check_Harmony_Interval \
            ( 'Sekund'
            , interval = (1, 2)
            , badness  = 1
            , octave   = False
            , signed   = True
            )
        t_cf = Tone (halftone ('e'), 8)
        t_cp = Tone (halftone ('f'), 8)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 0
    # end def test_check_harmony_interval_sign

    def test_check_harmony_interval_first_last (self):
        check = Check_Harmony_Interval \
            ( 'first-last'
            , interval  = (1, 2)
            , badness   = 1
            , not_first = True
            , not_last  = True
            )
        b_cf  = Bar (8, 8)
        b_cp  = Bar (8, 8)
        t_cf  = Tone (halftone ('e'), 8)
        b_cf.add (t_cf)
        t_cp1 = Tone (halftone ('f'), 4)
        t_cp2 = Tone (halftone ('f'), 4)
        b_cp.add (t_cp1)
        b_cp.add (t_cp2)
        b, u = check.check (t_cf, t_cp1)
        assert b == 0
        b, u = check.check (t_cf, t_cp2)
        assert b == 0
    # end def test_check_harmony_interval_first_last

    def test_check_harmony_melody_direction_same (self):
        check = Check_Harmony_Melody_Direction \
            ( 'Opposite direction'
            , interval = () # All
            , dir      = 'same'
            , ugliness = 0.1
            )
        t_cf  = Tone (halftone ('D'), 8)
        t_cp1 = Tone (halftone ('B'), 4)
        t_cp2 = Tone (halftone ('B'), 4)
        b_cf = Bar (8, 8)
        b_cp = Bar (8, 8)
        b_cf.add (t_cf)
        b_cp.add (t_cp1)
        b_cp.add (t_cp2)
        b, u = check.check (t_cf, t_cp1)
        assert u == 0
        b, u = check.check (t_cf, t_cp2)
        assert u == 0
    # end def test_check_harmony_melody_direction_same

    def test_check_harmony_melody_direction_zero (self):
        check = Check_Harmony_Melody_Direction \
            ( 'No sixth or third in a row'
            , interval = (3, 4, 8, 9)
            , dir      = 'zero'
            , ugliness = 3
            )
        # Although D-^A (8) and D-B (9) are both sixth they don't trigger
        # if 8 follows 9.
        t_cf  = Tone (halftone ('D'), 8)
        t_cp1 = Tone (halftone ('^A'), 2)
        t_cp2 = Tone (halftone ('^A'), 2)
        t_cp3 = Tone (halftone ('B'), 2)
        t_cp4 = Tone (halftone ('B'), 2)
        b_cf = Bar (8, 8)
        b_cp = Bar (8, 8)
        b_cf.add (t_cf)
        b_cp.add (t_cp1)
        b_cp.add (t_cp2)
        b_cp.add (t_cp3)
        b_cp.add (t_cp4)
        b, u = check.check (t_cf, t_cp1)
        assert u == 0
        b, u = check.check (t_cf, t_cp2)
        assert u == 3
        # Should this trigger, too??
        b, u = check.check (t_cf, t_cp3)
        assert u == 0
        b, u = check.check (t_cf, t_cp4)
        assert u == 3
    # end def test_check_harmony_melody_direction_zero

    def test_check_melody_interval (self):
        check = Check_Melody_Interval \
            ( 'Devils interval'
            , interval = (6,)
            , badness  = 10
            )
        bar = Bar (8, 8)
        t1  = Tone (halftone ('C'), 1)
        bar.add (t1)
        t2  = Tone (halftone ('^F'), 1)
        bar.add (t2)
        t3  = Tone (halftone ('C'), 1)
        bar.add (t3)
        t4  = Tone (halftone ('^f'), 1)
        bar.add (t4)
        b, u = check.check (t1)
        assert b == 0
        b, u = check.check (t2)
        assert b == 10
        b, u = check.check (t3)
        assert b == 10
        b, u = check.check (t4)
        assert b == 10
    # end def test_check_melody_interval

#    def test_gentune (self):
#        gentune_main (self.out_options)
#        self.compare ()
#    # end def test_gentune

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
