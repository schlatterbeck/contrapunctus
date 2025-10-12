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
from fractions import Fraction
from textwrap import dedent
from pga.testsupport import PGA_Test_Instrumentation
from contrapunctus.tune import Voice, Bar, Tone, Tune, Pause, halftone, Meter
from contrapunctus.tune import Key
from contrapunctus.gentune import main as gentune_main
from contrapunctus import checks

tune_output = """
X: 1
T: Zocharti Loch
M: 4/4
C: Louis Lewandowski (1821-1894)
Q: 1/4=76
%%score (T1 T2) (B1)
L: 1/8
V:T1 clef=treble-8 name="Tenore I" snm=T.I
V:T2 clef=treble-8 name="Tenore II" snm=T.II
V:B1 clef=bass name="Basso I" snm=B.I transpose=-24
K: Gm
""".strip ()

tune_voices = """
[V:T1] B2 c2 d2 g2 |f6 e2 |d2 c2 d2 e2 |d4 c2 z2 |
[V:T2] G2 A2 B2 e2 |d6 c2 |B2 A2 B2 c2 |B4 A2 z2 |
[V:B1] z8 |z2 f2 g2 a2 |b2 z2 z2 e2 |f4 f2 z2 |
""".strip ()
transposed_voices = """
[V:T1] A2 B2 c2 f2 |e6 d2 |c2 B2 c2 d2 |c4 B2 z2 |
[V:T2] F2 G2 A2 d2 |c6 B2 |A2 G2 A2 B2 |A4 G2 z2 |
[V:B1] z8 |z2 e2 f2 g2 |a2 z2 z2 d2 |e4 e2 z2 |
""".strip ()

tune_transposed  = tune_output.replace ('K: Gm', 'K: F#m')
tune_output     += '\n' + tune_voices
tune_transposed += '\n' + transposed_voices

# Explicit decorator for long-running tests, but all tests in
# Test_Contrapunctus_Slow are automagically skipped if longrun is not set
# @pytest.mark.slow

class Test_Contrapunctus:

    abcheader = \
        ( "X: 1\nM: 4/4\nQ: 1/4=200\n"
          "%%score (Contrapunctus) (CantusFirmus)\n"
          'L: 1/8\nV:CantusFirmus name="Cantus Firmus"\n'
          'V:Contrapunctus name=Contrapunctus\nK: DDor\n'
        )

    def build_tune (self):
        v1 = Voice (id = 'T1', clef='treble-8', name='Tenore I', snm='T.I')
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('_B'), 2))
        b1.add (Tone (halftone ('c'), 2))
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('g'), 2))
        v1.add (b1)
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('f'), 6))
        b1.add (Tone (halftone ('_e'), 2))
        v1.add (b1)
        b1 = Bar (8, 8)
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('c'), 2))
        b1.add (Tone (halftone ('d'), 2))
        b1.add (Tone (halftone ('_e'), 2))
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
        b2.add (Tone (halftone ('_B'), 2))
        b2.add (Tone (halftone ('_e'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('d'), 6))
        b2.add (Tone (halftone ('c'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('_B'), 2))
        b2.add (Tone (halftone ('A'), 2))
        b2.add (Tone (halftone ('_B'), 2))
        b2.add (Tone (halftone ('c'), 2))
        v2.add (b2)
        b2 = Bar (8, 8)
        b2.add (Tone (halftone ('_B'), 4))
        b2.add (Tone (halftone ('A'), 2))
        b2.add (Pause (2))
        v2.add (b2)

        v3 = Voice \
            ( id        = 'B1'
            , clef      = 'bass'
            , name      = 'Basso I'
            , snm       = 'B.I'
            , transpose = '-24'
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
        b3.add (Tone (halftone ('_b'), 2))
        b3.add (Pause (2))
        b3.add (Pause (2))
        b3.add (Tone (halftone ('_e'), 2))
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
        return t
    # end def build_tune

    def build_min_tune (self):
        t = Tune \
            ( title  = 'Test tune'
            , meter  = Meter (4, 4)
            , key    = 'C'
            , unit   = Fraction (8)
            )
        v = Voice \
            ( id        = 'CantusFirmus'
            , name      = 'Cantus Firmus'
            )
        t.add (v)
        v = Voice \
            ( id        = 'Contrapunctus'
            , name      = 'Contrapunctus'
            )
        t.add (v)
        return t
    # end def build_min_tune

    def test_tune (self):
        tune = self.build_tune ()
        assert tune.as_abc ().strip () == tune_output
    # end def test_tune

    def test_transpose_tune (self):
        tune = self.build_tune ()
        # Transpose by a half tone down
        tune = tune.transpose (-1)
        assert tune.as_abc ().strip () == tune_transposed
    # end def test_transpose_tune

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
        assert ''.join (tones) == 'g1 f1 e1 d1 c1 b1 a1 '
    # end def test_prev

    def test_check_harmony_interval_max (self):
        check = checks.Check_Harmony_Interval_Max \
            ('must be up', maximum = 12, badness = 1)
        b = Bar (8)
        t_cf  = Tone (halftone ('E'), 8)
        b.add (t_cf)
        b = Bar (8)
        t_cp  = Tone (halftone ('e'), 4)
        b.add (t_cp)
        t_cp2 = Tone (halftone ('f'), 4)
        b.add (t_cp2)
        # This is the normal order of parameters for checks, cf first
        b, u = check.check (t_cf, t_cp)
        assert b == 0
        b, u = check.check (t_cf, t_cp2)
        assert b == 1
    # end def test_check_harmony_interval_max

    def test_check_harmony_interval_min (self):
        check = checks.Check_Harmony_Interval_Min \
            ('must be up', minimum = 0, badness = 1)
        b = Bar (8)
        t_cp = Tone (halftone ('e'), 8)
        b.add (t_cp)
        b = Bar (8)
        t_cf = Tone (halftone ('f'), 8)
        b.add (t_cf)
        # This is the normal order of parameters for checks, cf first
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 0
        b, u = check.check (t_cp, t_cp)
        assert b == 0
    # end def test_check_harmony_interval_min

    def test_check_harmony_interval_octave (self):
        check = checks.Check_Harmony_Interval \
            ( 'Sekund'
            , interval = (1, 2)
            , badness  = 1
            , octave   = True
            )
        b = Bar (8)
        t_cp = Tone (halftone ('e'), 8)
        b.add (t_cp)
        b = Bar (8)
        t_cf = Tone (halftone ('f'), 8)
        b.add (t_cf)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        b = Bar (8)
        t_cp = Tone (halftone ('c'), 8)
        b.add (t_cp)
        b = Bar (8)
        t_cf = Tone (halftone ('d'), 8)
        b.add (t_cf)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        b = Bar (8)
        t_cp = Tone (halftone ('C'), 8)
        b.add (t_cp)
        b = Bar (8)
        t_cf = Tone (halftone ('d'), 8)
        b.add (t_cf)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 1

        b = Bar (8)
        t_cp = Tone (halftone ('c'), 8)
        b.add (t_cp)
        b = Bar (8)
        t_cf = Tone (halftone ('e'), 8)
        b.add (t_cf)
        b, u = check.check (t_cf, t_cp)
        assert b == 0
        b, u = check.check (t_cp, t_cf)
        assert b == 0
    # end def test_check_harmony_interval_octave

    def test_check_harmony_interval_sign (self):
        check = checks.Check_Harmony_Interval \
            ( 'Sekund'
            , interval = (1, 2)
            , badness  = 1
            , octave   = False
            , signed   = True
            )
        b = Bar (8)
        t_cf = Tone (halftone ('e'), 8)
        b.add (t_cf)
        b = Bar (8)
        t_cp = Tone (halftone ('f'), 8)
        b.add (t_cp)
        b, u = check.check (t_cf, t_cp)
        assert b == 1
        b, u = check.check (t_cp, t_cf)
        assert b == 0
    # end def test_check_harmony_interval_sign

    def test_check_harmony_interval_first_last (self):
        check = checks.Check_Harmony_Interval \
            ( 'first-last'
            , interval  = (1, 2)
            , badness   = 1
            , not_first = True
            , not_last  = True
            )
        v_cf  = Voice ()
        v_cp  = Voice ()
        bcf0  = Bar (8, 8)
        v_cf.add (bcf0)
        b_cf  = Bar (8, 8)
        v_cf.add (b_cf)
        bcp0  = Bar (8, 8)
        v_cp.add (bcp0)
        b_cp  = Bar (8, 8)
        v_cp.add (b_cp)
        t_cf  = Tone (halftone ('e'), 8)
        b_cf.add (t_cf)
        t_cp1 = Tone (halftone ('f'), 4)
        t_cp2 = Tone (halftone ('f'), 4)
        b_cp.add (t_cp1)
        b_cp.add (t_cp2)
        bcfe  = Bar (8, 8)
        v_cf.add (bcfe)
        bcpe  = Bar (8, 8)
        v_cp.add (bcpe)
        b, u = check.check (t_cf, t_cp1)
        assert b == 1
        b, u = check.check (t_cf, t_cp2)
        assert b == 1
        bcf0.add (Tone (halftone ('e'), 8))
        bcp0.add (Tone (halftone ('f'), 4))
        bcp0.add (Tone (halftone ('f'), 4))
        b, u = check.check (bcf0.objects [0], bcp0.objects [0])
        assert b == 0
        b, u = check.check (bcf0.objects [0], bcp0.objects [1])
        assert b == 1
        bcfe.add (Tone (halftone ('e'), 8))
        bcpe.add (Tone (halftone ('f'), 4))
        bcpe.add (Tone (halftone ('f'), 4))
        b, u = check.check (bcfe.objects [0], bcpe.objects [0])
        assert b == 1
        b, u = check.check (bcfe.objects [0], bcpe.objects [1])
        assert b == 0
    # end def test_check_harmony_interval_first_last

    def test_check_harmony_history (self):
        check = checks.Check_Harmony_History \
            ( 'Parallel fifth'
            , interval    = (7,) # fifth
            , badness     = 9
            )
        b_cf1 = Bar (8, 8)
        b_cf1.add (Tone (halftone ('C'), 8))
        b_cf2 = Bar (8, 8)
        b_cf2.add (Tone (halftone ('D'), 8))
        b_cf3 = Bar (8, 8)
        b_cf3.add (Tone (halftone ('F'), 8))
        b_cp1 = Bar (8, 8)
        b_cp1.add (Tone (halftone ('G'), 8))
        b_cp2 = Bar (8, 8)
        b_cp2.add (Tone (halftone ('A'), 8))
        b_cp3 = Bar (8, 8)
        b_cp3.add (Tone (halftone ('B'), 8))
        b_cp = Bar (8, 8)
        b, u = check.check (b_cf1.objects [0], b_cp1.objects [0])
        assert b == 0
        b, u = check.check (b_cf2.objects [0], b_cp2.objects [0])
        assert b == 9
        b, u = check.check (b_cf3.objects [0], b_cp3.objects [0])
        assert b == 0
    # end def test_check_harmony_history

    def test_check_harmony_history_sixth (self):
        check = checks.Check_Harmony_History \
            ( "For sext (sixth) don't allow several in a row"
            , interval    = (8, 9)
            , ugliness    = 3
            )
        tune = self.build_min_tune ()
        cf = tune.voices [0]
        cp = tune.voices [1]
        b_cf1 = Bar (8, 8)
        cf.add (b_cf1)
        b_cf1.add (Tone (halftone ('F'), 8))
        b_cf2 = Bar (8, 8)
        cf.add (b_cf2)
        b_cf2.add (Tone (halftone ('F'), 4))
        b_cf2.add (Tone (halftone ('E'), 2))
        b_cf2.add (Tone (halftone ('D'), 2))
        b_cf3 = Bar (8, 8)
        cf.add (b_cf3)
        b_cf3.add (Tone (halftone ('E'), 8))
        b_cf4 = Bar (8, 8)
        cf.add (b_cf4)
        b_cf4.add (Tone (halftone ('D'), 8))

        b_cp1 = Bar (8, 8)
        cp.add (b_cp1)
        b_cp1.add (Tone (halftone ('c'), 8))
        b_cp2 = Bar (8, 8)
        cp.add (b_cp2)
        b_cp2.add (Tone (halftone ('d'), 2))
        b_cp2.add (Tone (halftone ('d'), 2))
        b_cp2.add (Tone (halftone ('B'), 4))
        b_cp3 = Bar (8, 8)
        cp.add (b_cp3)
        b_cp3.add (Tone (halftone ('^c'), 8))
        b_cp4 = Bar (8, 8)
        cp.add (b_cp4)
        b_cp4.add (Tone (halftone ('d'), 8))

        b, u = check.check (b_cf1.objects [0], b_cp1.objects [0])
        assert u == 0
        b, u = check.check (b_cf2.objects [0], b_cp2.objects [0])
        d = b_cp2.objects [0].halftone.diff (b_cf2.objects [0].halftone)
        assert d == 9
        assert u == 0
        b, u = check.check (b_cf2.objects [0], b_cp2.objects [1])
        d = b_cp2.objects [1].halftone.diff (b_cf2.objects [0].halftone)
        assert d == 9
        assert u == 3
        b, u = check.check (b_cf2.objects [1], b_cp2.objects [2])
        d = b_cp2.objects [2].halftone.diff (b_cf2.objects [1].halftone)
        assert d == 7
        assert u == 0
        b, u = check.check (b_cf2.objects [2], b_cp2.objects [2])
        d = b_cp2.objects [2].halftone.diff (b_cf2.objects [2].halftone)
        assert d == 9
        assert u == 0
        b, u = check.check (b_cf3.objects [0], b_cp3.objects [0])
        d = b_cp3.objects [0].halftone.diff (b_cf3.objects [0].halftone)
        assert d == 9
        assert u == 3
        b, u = check.check (b_cf4.objects [0], b_cp4.objects [0])
        d = b_cp4.objects [0].halftone.diff (b_cf4.objects [0].halftone)
        assert d == 12
        assert u == 0
        # Check the same using voices_iter
        uu = []
        for cfo, cpo in tune.voices_iter ():
            b, u = check.check (cfo, cpo)
            uu.append (u)
        assert uu == [0, 0, 3, 0, 0, 3, 0]
    # end def test_check_harmony_history_sixth

    def test_check_harmony_melody_direction_same (self):
        check = checks.Check_Harmony_Melody_Direction \
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
        check = checks.Check_Harmony_Melody_Direction \
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
        check = checks.Check_Melody_Interval \
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

    def test_check_melody_interval_unison (self):
        check = checks.Check_Melody_Interval \
            ( '0.1.2: No unison (Prim) allowed'
            , interval = (0,)
            , badness  = 10
            , octave   = False
            )
        tune = self.build_min_tune ()
        cf = tune.voices [0]
        cp = tune.voices [1]
        bar = Bar (8, 8)
        cf.add (bar)
        t1  = Tone (halftone ('D'), 8, bind = True)
        bar.add (t1)
        bar = Bar (8, 8)
        cf.add (bar)
        t2  = Tone (halftone ('D'), 4)
        bar.add (t2)
        t3  = Tone (halftone ('D'), 4)
        bar.add (t3)

        b, u = check.check (t1)
        assert b == 0
        b, u = check.check (t2)
        assert b == 0 # Not a violation due to binding
        b, u = check.check (t3)
        assert b == 10
    # end def test_check_melody_interval_unison

    def test_get_by_offset (self):
        v1 = Voice (id = 'V1')
        b  = Bar (8, 8)
        b.add (Tone (halftone ('B'), 2))
        b.add (Tone (halftone ('c'), 2))
        b.add (Tone (halftone ('d'), 2))
        b.add (Tone (halftone ('g'), 2))
        v1.add (b)
        b = Bar (8, 8)
        b.add (Tone (halftone ('f'), 6))
        b.add (Tone (halftone ('e'), 2))
        v1.add (b)
        v2 = Voice (id = 'V2')
        b  = Bar (8, 8)
        b.add (Tone (halftone ('B'), 4))
        b.add (Tone (halftone ('g'), 4))
        v2.add (b)
        b = Bar (8, 8)
        b.add (Tone (halftone ('f'), 2))
        b.add (Tone (halftone ('e'), 6))
        v2.add (b)

        b2 = v2.bars [0]
        offsets = [0, 0, 4, 4, 0, 2]
        idxs    = [0, 0, 1, 1, 0, 1]
        i = 0
        for b in v1.bars:
            for t in b.objects:
                other = b2.get_by_offset (t)
                assert other.bar.idx == b.idx
                assert other.offset <= t.offset
                assert other.offset == offsets [i]
                assert other.idx    == idxs [i]
                i += 1
    # end def test_get_by_offset

    def test_reset_upcall (self):
        check = checks.Check_Melody_Jump ('Jump', badness = 10)
        assert check.msg == 'Jump'
        assert check.prev_match is False
    # end def test_reset_upcall

    def test_logparse (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-b', '-g' 'test/example.log'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        txt  = cp.as_complete_tune ()
        with open ('test/example.abc') as f:
            abc = f.read ()
        assert txt.strip () == abc.strip ()
        # roundtrip test, note the missing -b ('best') option
        args = cmd.parse_args (['-v', '-v', '-g' 'test/example.abc'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        txt = cp.as_complete_tune ()
        assert txt.strip () == abc.strip ()
    # end def test_logparse

    def test_logparse_with_cf (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        log  = 'test/search_de_cf_haenschen.data'
        abc  = 'test/search_de_cf_haenschen.abc'
        args = cmd.parse_args (['-v', '-v', '-b', '-g', log])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        txt  = cp.as_complete_tune ()
        with open (abc) as f:
            abc_content = f.read ()
        assert txt.strip () == abc_content.strip ()
        # roundtrip test, note the missing -b ('best') option
        args = cmd.parse_args (['-v', '-v', '-g', abc])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        txt = cp.as_complete_tune ()
        assert txt.strip () == abc_content.strip ()
    # end def test_logparse_with_cf

    def test_gene_decode_8_44 (self):
        header = self.abcheader + '[V:CantusFirmus] D8 |F8 |E8 |D8 |\n'
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-l', '4'])
        cpl  = 11
        fake = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        fake.set_allele (1, 1, 0, 5) # CF

        # First bar CP is hardcoded
        # Second bar CP
        fake.set_allele (1, 1, 1 + 0, 3) # Len 1<<3 = 8 first tone CP
        fake.set_allele (1, 1, 1 + 1, 3) # CP pitch (G)
        # Rest is don't care
        for k in range (3, cpl):
            fake.set_allele (1, 1, k, 42)
        # Third bar CP
        fake.set_allele (1, 1, 1 + cpl + 0,  2) # Len 1<<2 = 4 first tone CP
        fake.set_allele (1, 1, 1 + cpl + 1,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 + cpl + 2, 42) # Don't care len first light
        fake.set_allele (1, 1, 1 + cpl + 3, 42) # Don't care pitch first light
        fake.set_allele (1, 1, 1 + cpl + 4, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 + cpl + 5,  2) # Len 1<<2 = 4 2nd tone CP
        fake.set_allele (1, 1, 1 + cpl + 6,  5) # CP pitch (B)
        # Rest is don't care
        for k in range (3, cpl):
            fake.set_allele (1, 1, k, 42)
        t = fake.as_tune ()
        result = header + '[V:Contrapunctus] G8 |A4 B4 |^c8 |d8 |'
        assert t == result
    # end def test_gene_decode_8_44

    def test_gene_decode_422_4211 (self):
        header = self.abcheader + '[V:CantusFirmus] D8 |F8 |E8 |D8 |\n'
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-l', '4'])
        cpl  = 11
        fake = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        fake.set_allele (1, 1, 0, 5) # CF

        # First bar CP is hardcoded
        # Second bar CP
        fake.set_allele (1, 1, 1 +  0,  2) # Len 1<<2 = 4 first tone CP
        fake.set_allele (1, 1, 1 +  1,  3) # CP pitch (G)
        fake.set_allele (1, 1, 1 +  2, 42) # Don't care len first light
        fake.set_allele (1, 1, 1 +  3, 42) # Don't care pitch first light
        fake.set_allele (1, 1, 1 +  4, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 +  5,  1) # Len 1<<1 = 2 2nd tone CP
        fake.set_allele (1, 1, 1 +  6,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 +  7, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 +  8,  1) # Len 1<<1 = 2 3rd tone CP
        fake.set_allele (1, 1, 1 +  9,  2) # CP pitch (F)
        fake.set_allele (1, 1, 1 + 10, 42) # Don't care pitch 1/8
        # Third bar CP
        fake.set_allele (1, 1, 1 + cpl +  0,  2) # Len 1<<2 = 4 first tone CP
        fake.set_allele (1, 1, 1 + cpl +  1,  3) # CP pitch (G)
        fake.set_allele (1, 1, 1 + cpl +  2, 42) # Don't care len first light
        fake.set_allele (1, 1, 1 + cpl +  3, 42) # Don't care pitch first light
        fake.set_allele (1, 1, 1 + cpl +  4, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 + cpl +  5,  1) # Len 1<<1 = 2 2nd tone CP
        fake.set_allele (1, 1, 1 + cpl +  6,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 + cpl +  7, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 + cpl +  8,  0) # Len 1<<0 = 1 3rd tone CP
        fake.set_allele (1, 1, 1 + cpl +  9,  2) # CP pitch (F)
        fake.set_allele (1, 1, 1 + cpl + 10,  3) # CP pitch (G)
        t = fake.as_tune ()
        result = header + '[V:Contrapunctus] G4 A2 F2 |G4 A2 F1G1 |^c8 |d8 |'
        assert t == result
    # end def test_gene_decode_422_4211

    def test_gene_decode_22211_211211 (self):
        header = self.abcheader + '[V:CantusFirmus] D8 |F8 |E8 |D8 |\n'
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-l', '4'])
        cpl  = 11
        fake = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        fake.set_allele (1, 1, 0, 5) # CF

        # First bar CP is hardcoded
        # Second bar CP
        fake.set_allele (1, 1, 1 +  0,  1) # Len 1<<2 = 2 first tone CP
        fake.set_allele (1, 1, 1 +  1,  3) # CP pitch (G)
        fake.set_allele (1, 1, 1 +  2,  1) # Len 1<<2 = 2 2nd tone CP
        fake.set_allele (1, 1, 1 +  3,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 +  4, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 +  5,  1) # Len 1<<1 = 2 3rd tone CP
        fake.set_allele (1, 1, 1 +  6,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 +  7, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 +  8,  0) # Len 1<<0 = 1 3rd tone CP
        fake.set_allele (1, 1, 1 +  9,  2) # CP pitch (F)
        fake.set_allele (1, 1, 1 + 10,  2) # CP pitch (F)
        # Third bar CP
        fake.set_allele (1, 1, 1 + cpl +  0,  1) # Len 1<<1 = 2 first tone CP
        fake.set_allele (1, 1, 1 + cpl +  1,  3) # CP pitch (G)
        fake.set_allele (1, 1, 1 + cpl +  2,  0) # Len 1<<0 = 1 2nd tone CP
        fake.set_allele (1, 1, 1 + cpl +  3,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 + cpl +  4,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 + cpl +  5,  1) # Len 1<<1 = 2 2nd tone CP
        fake.set_allele (1, 1, 1 + cpl +  6,  3) # CP pitch (G)
        fake.set_allele (1, 1, 1 + cpl +  7, 42) # Don't care pitch 1/8
        fake.set_allele (1, 1, 1 + cpl +  8,  0) # Len 1<<0 = 1 3rd tone CP
        fake.set_allele (1, 1, 1 + cpl +  9,  4) # CP pitch (A)
        fake.set_allele (1, 1, 1 + cpl + 10,  4) # CP pitch (A)
        t = fake.as_tune ()
        result = header + '[V:Contrapunctus] G2 A2 A2 F1F1 |' \
                          'G2 A1A1 G2 A1A1 |^c8 |d8 |'
        assert t == result
    # end def test_gene_decode_22211_211211

    def test_empty_prev_bar (self):
        """ Some of the searches have an empty bar *before* a valid one.
            This tests that nothing breaks.
        """
        check = checks.Check_Harmony_Melody_Direction \
            ( 'better same direction'
            , interval = () # All
            , dir      = 'same'
            , ugliness = 0.1
            )
        v1 = Voice (id = 'V1')
        b  = Bar (8, 8)
        v1.add (b)
        b = Bar (8, 8)
        b.add (Tone (halftone ('f'), 8))
        v1.add (b)
        assert b.objects [0].prev is None
        v2 = Voice (id = 'V2')
        b  = Bar (8, 8)
        b.add (Tone (halftone ('f'), 8))
        v2.add (b)
        b = Bar (8, 8)
        b.add (Tone (halftone ('f'), 8))
        v2.add (b)
        b, u = check.check (v1.bars [-1].objects [0], v2.bars [-1].objects [0])
        assert u == 0
    # end def test_empty_prev_bar

    def test_copy_bar (self):
        v = Voice (id = 'V1')
        b = Bar (8, 8)
        b.add (Tone (halftone ('f'), 4))
        b.add (Tone (halftone ('g'), 4))
        v.add (b)
        b2 = b.copy ()
        assert b2.voice is None
        assert b2.idx   is None
        assert len (b.objects) == len (b2.objects)
        v = Voice (id = 'V1')
        v.add (b2)
        assert str (b) == str (b2)
        for o1, o2 in zip (b.objects, b2.objects):
            assert id (o1) != id (o2)
            # This works because voices are named identically:
            assert str (o1) == str (o2)
    # end def test_copy_bar

    def test_check_harmony_first_interval (self):
        check = checks.Check_Harmony_First_Interval \
            ( 'unison, octave, fifth'
            , interval = (0, 7, 12)
            , badness  = 100
            )
        tune = self.build_min_tune ()
        v1  = tune.voices [0]
        b11 = Bar (8, 8)
        b11.add (Tone (halftone ('C'), 8))
        v1.add (b11)
        b12 = Bar (8, 8)
        b12.add (Tone (halftone ('f'), 4))
        b12.add (Tone (halftone ('g'), 4))
        v1.add (b12)
        v2 = tune.voices [1]
        b21 = Bar (8, 8)
        b21.add (Tone (halftone ('C'), 8))
        v2.add (b21)
        b22 = Bar (8, 8)
        b22.add (Tone (halftone ('g'), 4))
        b22.add (Tone (halftone ('f'), 4))
        v2.add (b22)
        b, u = check.check (b12.objects [0], b22.objects [0])
        assert b == 0
        b, u = check.check (b12.objects [1], b22.objects [1])
        assert b == 0

        # Same test but with pause in first bar
        tune = self.build_min_tune ()
        v1  = tune.voices [0]
        b11 = Bar (8, 8)
        b11.add (Pause (8))
        v1.add (b11)
        b12 = Bar (8, 8)
        b12.add (Tone (halftone ('f'), 4))
        b12.add (Tone (halftone ('g'), 4))
        v1.add (b12)
        v2 = tune.voices [1]
        b21 = Bar (8, 8)
        b21.add (Pause (8))
        v2.add (b21)
        b22 = Bar (8, 8)
        b22.add (Tone (halftone ('g'), 4))
        b22.add (Tone (halftone ('f'), 4))
        v2.add (b22)
        b, u = check.check (b12.objects [0], b22.objects [0])
        assert b == 100
        b, u = check.check (b12.objects [1], b22.objects [1])
        assert b == 0

        # Same test but also with pause in second bar
        tune = self.build_min_tune ()
        v1  = tune.voices [0]
        b11 = Bar (8, 8)
        b11.add (Pause (8))
        v1.add (b11)
        b12 = Bar (8, 8)
        b12.add (Pause (4))
        b12.add (Tone (halftone ('g'), 4))
        v1.add (b12)
        v2 = tune.voices [1]
        b21 = Bar (8, 8)
        b21.add (Pause (8))
        v2.add (b21)
        b22 = Bar (8, 8)
        b22.add (Tone (halftone ('g'), 4))
        b22.add (Tone (halftone ('f'), 4))
        v2.add (b22)
        b, u = check.check (b12.objects [0], b22.objects [0])
        assert b == 0
        b, u = check.check (b12.objects [1], b22.objects [1])
        assert b == 100
    # end def test_check_harmony_first_interval

    def test_check_harmony_first_interval_complex (self):
        check = checks.Check_Harmony_First_Interval \
            ( 'unison, octave, fifth'
            , interval = (0, 7, 12)
            , badness  = 100
            )
        tune  = self.build_min_tune ()
        v_cf  = tune.voices [0]
        v_cp  = tune.voices [1]

        bcf0  = Bar (8, 8)
        v_cf.add (bcf0)
        p_cf0 = Pause (8)
        bcf0.add (p_cf0)
        bcf1  = Bar (8, 8)
        v_cf.add (bcf1)
        t_cf11 = Tone (halftone ('D'), 8)
        bcf1.add (t_cf11)
        bcf2  = Bar (8, 8)
        v_cf.add (bcf2)
        t_cf21 = Tone (halftone ('D'), 4)
        t_cf22 = Tone (halftone ('F'), 4)
        bcf2.add (t_cf21)
        bcf2.add (t_cf22)

        bcp0  = Bar (8, 8)
        v_cp.add (bcp0)
        t_cp01 = Tone (halftone ('c'), 8)
        bcp0.add (t_cp01)
        bcp1  = Bar (8, 8)
        v_cp.add (bcp1)
        t_cp11 = Tone (halftone ('B'), 8)
        bcp1.add (t_cp11)
        bcp2  = Bar (8, 8)
        v_cp.add (bcp2)
        t_cp21 = Tone (halftone ('B'), 2)
        t_cp22 = Tone (halftone ('A'), 2)
        t_cp23 = Tone (halftone ('A'), 4)
        bcp2.add (t_cp21)
        bcp2.add (t_cp22)
        bcp2.add (t_cp23)

        b, u = check.check (p_cf0, t_cp01)
        assert b == 0
        b, u = check.check (t_cf11, t_cp11)
        assert b == 100
        b, u = check.check (t_cf21, t_cp21)
        assert b == 0
        b, u = check.check (t_cf21, t_cp22)
        assert b == 0
        b, u = check.check (t_cf22, t_cp23)
        assert b == 0
    # end def test_check_harmony_first_interval_complex

    def test_check_harmony_first_interval_cp3 (self):
        check = checks.Check_Harmony_First_Interval \
            ( 'unison, octave, fifth'
            , interval = (0, 7, 12)
            , badness  = 100
            )
        tune  = self.build_min_tune ()
        v_cf  = tune.voices [0]
        v_cp  = tune.voices [1]
        v_cf.add (Bar (8, 8))
        v_cf.bars [0].add (Tone (halftone ('D'), 8))
        v_cp.add (Bar (8, 8))
        v_cp.bars [0].add (Tone (halftone ('A'), 2))
        v_cp.bars [0].add (Tone (halftone ('B'), 2))
        v_cp.bars [0].add (Tone (halftone ('b'), 4))
        b_cf = v_cf.bars [0]
        b_cp = v_cp.bars [0]
        b, u = check.check (b_cf.objects [0], b_cp.objects [0])
        assert b == 0
        b, u = check.check (b_cf.objects [0], b_cp.objects [1])
        assert b == 0
        b, u = check.check (b_cf.objects [0], b_cp.objects [2])
        assert b == 0
    # end def test_check_harmony_first_interval_cp3

    def test_dorian_hypodorian (self):
        dorian = ['D', 'E', 'F', 'G', 'A', 'B', 'c']
        for k, d in enumerate (dorian):
            assert str (contrapunctus.gregorian.dorian [k]) == d
        assert str (contrapunctus.gregorian.dorian.finalis)       == 'D'
        assert str (contrapunctus.gregorian.dorian.step2)         == 'E'
        assert str (contrapunctus.gregorian.dorian.subsemitonium) == '^c'
        hypodorian = ['A,', 'B,', 'C', 'D', 'E', 'F', 'G']
        for k, d in enumerate (hypodorian):
            assert str (contrapunctus.gregorian.hypodorian [k]) == d
        assert str (contrapunctus.gregorian.hypodorian.finalis)       == 'D'
        assert str (contrapunctus.gregorian.hypodorian.step2)         == 'E'
        # Check if this is correct, subsemitonium is not currently used
        # for hypodorian:
        assert str (contrapunctus.gregorian.hypodorian.subsemitonium) == '^G'
    # end def test_dorian_hypodorian

    def test_phrygian_hypophrygian (self):
        phrygian = ['E', 'F', 'G', 'A', 'B', 'c', 'd']
        for k, d in enumerate (phrygian):
            assert str (contrapunctus.gregorian.phrygian [k]) == d
        assert str (contrapunctus.gregorian.phrygian.finalis)       == 'E'
        assert str (contrapunctus.gregorian.phrygian.step2)         == 'F'
        assert str (contrapunctus.gregorian.phrygian.subsemitonium) == '^d'
        hypophrygian = ['B,', 'C', 'D', 'E', 'F', 'G', 'A']
        for k, d in enumerate (hypophrygian):
            assert str (contrapunctus.gregorian.hypophrygian [k]) == d
        assert str (contrapunctus.gregorian.hypophrygian.finalis)       == 'E'
        assert str (contrapunctus.gregorian.hypophrygian.step2)         == 'F'
        # Check if this is correct, subsemitonium is not currently used
        # for hypophrygian:
        assert str (contrapunctus.gregorian.hypophrygian.subsemitonium) == '^A'
    # end def test_phrygian_hypophrygian

    def test_lydian_hypolydian (self):
        lydian = ['F', 'G', 'A', 'B', 'c', 'd', 'e']
        for k, d in enumerate (lydian):
            assert str (contrapunctus.gregorian.lydian [k]) == d
        assert str (contrapunctus.gregorian.lydian.finalis)       == 'F'
        assert str (contrapunctus.gregorian.lydian.step2)         == 'G'
        # Really e for subsemitonium???
        assert str (contrapunctus.gregorian.lydian.subsemitonium) == 'e'
        hypolydian = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        for k, d in enumerate (hypolydian):
            assert str (contrapunctus.gregorian.hypolydian [k]) == d
        assert str (contrapunctus.gregorian.hypolydian.finalis)       == 'F'
        assert str (contrapunctus.gregorian.hypolydian.step2)         == 'G'
        # Check if this is correct, subsemitonium is not currently used
        # for hypolydian:
        # Really B for subsemitonium???
        assert str (contrapunctus.gregorian.hypolydian.subsemitonium) == 'B'
    # end def test_lydian_hypolydian

    def test_mixolydian_hypomixolydian (self):
        mixolydian = ['G', 'A', 'B', 'c', 'd', 'e', 'f']
        for k, d in enumerate (mixolydian):
            assert str (contrapunctus.gregorian.mixolydian [k]) == d
        assert str (contrapunctus.gregorian.mixolydian.finalis)       == 'G'
        assert str (contrapunctus.gregorian.mixolydian.step2)         == 'A'
        assert str (contrapunctus.gregorian.mixolydian.subsemitonium) == '^f'
        hypomixolydian = ['D', 'E', 'F', 'G', 'A', 'B', 'c']
        for k, d in enumerate (hypomixolydian):
            assert str (contrapunctus.gregorian.hypomixolydian [k]) == d
        assert str (contrapunctus.gregorian.hypomixolydian.finalis)       == 'G'
        assert str (contrapunctus.gregorian.hypomixolydian.step2)         == 'A'
        # Check if this is correct, subsemitonium is not currently used
        # for hypomixolydian:
        subs = contrapunctus.gregorian.hypomixolydian.subsemitonium
        assert str (subs) == '^c'
    # end def test_mixolydian_hypolydian

    def test_halftone_register (self):
        e1 = halftone ('e')
        e2 = halftone ('e')
        e3 = halftone (e2)
        assert id (e1) == id (e2)
        assert id (e2) == id (e3)
    # end def test_halftone_register

    def test_key_register (self):
        k1 = Key.get ('C')
        k2 = Key.get ('C')
        k3 = Key.get (k2)
        assert id (k1) == id (k2)
        assert id (k2) == id (k3)
    # end def test_key_register

    def test_key_transposition (self):
        k1 = Key.get ('C')
        assert not k1.accidentals
        for fifth in range (-6, 7):
            k = k1.transpose (fifth)
            assert k.offset == fifth
            assert len (k.accidentals) == abs (fifth)
            if fifth < 0:
                assert ''.join (k.accidentals.values ()) == '_' * -fifth
            else:
                assert ''.join (k.accidentals.values ()) == '^' * fifth
        # -7 and 7 are not generated by transpose:
        k = Key.get ('Cb')
        assert k.offset == -7
        assert len (k.accidentals) == 7
        assert ''.join (k.accidentals.values ()) == '_' * 7
        k = Key.get ('C#')
        assert k.offset == 7
        assert len (k.accidentals) == 7
        assert ''.join (k.accidentals.values ()) == '^' * 7
    # end def test_key_transposition

    def test_parse_tune (self):
        tune = Tune.from_iterator (tune_output.split ('\n'))
        assert tune.number == '1'
        assert tune.title  == 'Zocharti Loch'
        assert tune.C      == 'Louis Lewandowski (1821-1894)'
        assert tune.Q      == '1/4=76'
        assert tune.score  == '(T1 T2) (B1)'
        assert str (tune.meter) == '4/4'
        assert str (tune.key)   == 'Gm'
        voice_data = \
            ( dict (clef = 'treble-8', name = 'Tenore I',  snm = 'T.I')
            , dict (clef = 'treble-8', name = 'Tenore II', snm = 'T.II')
            , dict (clef = 'bass',     name = 'Basso I')
            )
        for voice, vd in zip (tune.voices, voice_data):
            for k in vd:
                assert vd [k] == getattr (voice , k)
        # Cannot get this via getattr because we have a transpose method:
        assert voice.properties ['transpose'] == '-24'
        bars = \
            ( ( 'B2 c2 d2 g2 ', 'f6 e2 ', 'd2 c2 d2 e2 ', 'd4 c2 z2 ')
            , ( 'G2 A2 B2 e2 ', 'd6 c2 ', 'B2 A2 B2 c2 ', 'B4 A2 z2 ')
            , ( 'z8 ', 'z2 f2 g2 a2 ', 'b2 z2 z2 e2 ', 'f4 f2 z2 ')
            )
        for voice, b in zip (tune.voices, bars):
            assert len (voice.bars) == len (b)
            for bar, bstr in zip (voice.bars, b):
                bs = ''.join (obj.as_abc () for obj in bar.objects)
                assert bs == bstr
        # Finally test that it roundtrips:
        assert tune.as_abc ().strip () == tune_output
    # end def test_parse_tune

    def test_parse_tune_from_file (self):
        tune = Tune.from_file ('test/example.abc')
        with open ('test/example.abc') as f:
            tunestr = f.read ().strip ()
        assert tune.as_abc ().strip () == tunestr
    # end def test_parse_tune_from_file

    def test_parse_all_genes_from_abc_file (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cnt  = 0
        with open ('test/example.abc') as f:
            for k in cp.from_gene_lines (f):
                cnt += 1
        assert cnt == 1
    # end def test_parse_all_genes_from_abc_file

    def test_parse_gene_with_args (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-g' 'test/example.log'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        with open ('test/df.abc') as f:
            next (cp.from_gene_lines (f))
            f.seek (0)
            abc = f.read ().strip ()
        txt = cp.as_complete_tune ().strip ()
        assert txt
        assert abc
        assert txt == abc
    # end def test_parse_gene_with_args

    def test_guess_tune_length (self):
        """ Read a gene file without arguments that has a tune length
            longer than the default.
            This file also is from the early stages of a run having a
            bad evaluation which should add to test coverage.
        """
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-g' 'test/bad.log'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        abc  = cp.as_complete_tune ()
        assert len (abc.split ('\n')) > 100
    # end def test_guess_tune_length

    def test_guess_tune_length_with_cf (self):
        """ Read a gene file without arguments that has a tune length
            longer than the default. In addition the tune has a cantus
            firmus.
        """
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-g' 'test/bad_w_cf.abc'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cp.from_gene ()
        abc  = cp.as_complete_tune ()
        assert len (abc.split ('\n')) > 100
    # end def test_guess_tune_length_with_cf

    def test_invalid_cf (self):
        """ Specify a CF file for searching, the test should reveal that
            the CF file is invalid (not Contrapunctus can be found)
        """
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-c' 'test/invalid-cf.abc'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        res  = cp.verify_cantus_firmus ()
        assert not res
    # end def test_invalid_cf

    def test_cf_no_voice (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-c' 'test/nocf.abc'])
        with pytest.raises (ValueError):
            cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
    # end def test_cf_no_voice

    def test_parse_abc_with_no_voicename (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        with open ('test/df-no-name.abc') as f:
            tune = Tune.from_iterator (f)
    # end def test_parse_abc_with_no_voicename

    def test_multi_parse_gene (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cnt  = 0
        with open ('test/example.log') as f:
            for k in cp.from_gene_lines (f):
                cnt += 1
        assert cnt == 4
    # end def test_multi_parse_gene

    def test_parse_gene_with_empty_line (self):
        """ Empty line between tune and rest
        """
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        cnt  = 0
        with open ('test/spaced.log') as f:
            for k in cp.from_gene_lines (f):
                cnt += 1
        assert cnt == 1
    # end def test_parse_gene_with_empty_line

    def test_gene_roundtrip_with_cf_abc (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        fn = 'test/depth_first_with_cantus.data'
        with open (fn) as f:
            next (cp.from_gene_lines (f))
            f.seek (0)
            abc = f.read ().strip ()
        txt = cp.as_complete_tune ().strip ()
        assert txt == abc
    # end def test_gene_roundtrip_with_cf_abc

    def test_overlap (self):
        b1  = Bar (8, 8)
        b1.idx = 0
        p11 = Pause (4)
        p12 = Pause (4)
        b1.add (p11)
        b1.add (p12)
        b2  = Bar (8, 8)
        b2.idx = 0
        p21 = Pause (2)
        p22 = Pause (4)
        p23 = Pause (2)
        b2.add (p21)
        b2.add (p22)
        b2.add (p23)
        assert p11.overlaps (p21)
        assert p11.overlaps (p22)
        assert not p11.overlaps (p23)
        assert not p12.overlaps (p21)
        assert p12.overlaps (p22)
        assert p12.overlaps (p23)
        assert p21.overlaps (p11)
        assert not p21.overlaps (p12)
        assert p22.overlaps (p11)
        assert p22.overlaps (p12)
        assert not p23.overlaps (p11)
        assert p23.overlaps (p12)
    # end def test_overlap

    def test_akzentparallele_prim (self):
        check = checks.Check_Harmony_Akzentparallelen \
            ( "Test Akzentparallele prim"
            , badness  = 10.0
            )
        abc = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=treble
             [V:1] B4 d4 | c8 |
             [V:2] B8    | c8 |
             """
            ).strip ().split ('\n')
        tune   = Tune.from_iterator (abc)
        expect = (0, 0, 10)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp)
    # end def test_akzentparallele_prim

    def test_akzentparallele_quint (self):
        check = checks.Check_Harmony_Akzentparallelen \
            ( "Test Akzentparallele quint"
            , badness  = 10.0
            )
        abc = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=treble
             [V:1] G4 c4 | A4 f4 |
             [V:2] C8    | D8    |
             """
            ).strip ().split ('\n')
        tune   = Tune.from_iterator (abc)
        expect = (0, 0, 10)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp)
    # end def test_akzentparallele_quint

    def test_akzentparallele_octave (self):
        check = checks.Check_Harmony_Akzentparallelen \
            ( "Test Akzentparallele quint"
            , badness  = 10.0
            )
        abc = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=treble
             [V:1] e4 b4 | g4 e4 |
             [V:2] E8    | G8    |
             """
            ).strip ().split ('\n')
        tune   = Tune.from_iterator (abc)
        expect = (0, 0, 10)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp)
    # end def test_akzentparallele_octave

    @pytest.mark.xfail
    def test_klapperoktave (self):
        check = checks.Check_Harmony_Akzentparallelen \
            ( "Test Akzentparallele quint"
            , badness  = 10.0
            )
        abc = dedent \
            ("""
             X:1
             %%score 1 2
             Q: 1/4=280
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=bass
             [V:1] z2 D2- | D2 C2 | D2 d2 | c2 e2- |$ e2 d2 | c2 B2- |
                   B2 A2- | A2 E2 | D4 |
             [V:2] D4 | C4 | B,4 | E4 |$ D4 | E4 | D4 | C4 | D4 |
             """
            ).strip ().split ('\n')
        tune   = Tune.from_iterator (abc)
        expect = (0, 0, 0)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            import pdb; pdb.set_trace ()
            print (cfo, cpo)
            b, u = check.check (cfo, cpo)
            assert (b == exp)
    # end def test_klapperoktave

    def generic_exception_harmony_passing_tone (self, abc, expect):
        """ Test the Exception_Harmony_Passing_Tone class
            This tests passing tones that are reached by step and left
            by step in the same direction.
        """
        # Without exception, this should trigger (assuming it's a dissonance)
        check = checks.Check_Harmony_Interval \
            ( "Test dissonance"
            , interval = (1, 2, 5, 6, 10, 11)
            , octave   = True
            , badness  = 10.0
            )
        # Create a test check for now without the passing tone exception
        passing_tone_exception = checks.Exception_Harmony_Passing_Tone \
            ( interval       = (1, 2, 5, 6, 10, 11)  # Common dissonances
            , octave         = True
            , note_length    = (2,)    # quarter notes
            , bar_position   = (2, 4, 6, 10, 12, 14)
            )

        tune = Tune.from_iterator (abc)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp)

        # Now with exception
        check.exceptions.append (passing_tone_exception)
        for cfo, cpo in tune.voices_iter ():
            b, u = check.check (cfo, cpo)
            assert (b == 0), "cfo: %s  cpo: %s" % (cfo, cpo)
    # end def generic_exception_harmony_passing_tone

    def test_exception_harmony_passing_tone (self):
        abc_notation = dedent \
            ("""
             X: 1
             M: 4/4
             L: 1/8
             K: C
             %%score (Upper) (Lower)
             V:Lower clef=bass
             V:Upper
             [V:Lower] C8 |
             [V:Upper] E2 F2 G2 A2 |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0, 0)
        self.generic_exception_harmony_passing_tone (abc_notation, expect)
    # end def test_exception_harmony_passing_tone

    def test_exception_harmony_passing_tone_2 (self):
        abc_notation = dedent \
            ("""
             X: 1
             M: 4/4
             L: 1/8
             K: C
             %%score (Upper) (Lower)
             V:Lower clef=bass
             V:Upper
             [V:Lower] A,8 |
             [V:Upper] A2 G2 F2 E2 |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0, 0)
        self.generic_exception_harmony_passing_tone (abc_notation, expect)
    # end def test_exception_harmony_passing_tone_2

    def test_exception_harmony_passing_tone_hd (self):
        abc_notation = dedent \
            ("""
             X: 1
             M: 4/4
             L: 1/8
             K: C
             %%score (Contrapunctus) (CantusFirmus)
             V:CantusFirmus clef=bass
             V:Contrapunctus
             [V:CantusFirmus] D8 |
             [V:Contrapunctus] F4 G2 A2 |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0)
        self.generic_exception_harmony_passing_tone (abc_notation, expect)
    # end def test_exception_harmony_passing_tone_hd

    def test_exception_harmony_passing_tone_PT (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=treble
             [V:1] B2 c2 d2 e2 |
             [V:2] G8 |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0, 0)
        self.generic_exception_harmony_passing_tone (abc_notation, expect)
    # end def test_exception_harmony_passing_tone_PT

    def test_exception_harmony_passing_tone_PT_acc (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:Bb
             V:2 clef=treble
             V:1 clef=treble
             [V:1] B6 c2 | d6 e2 | f8 |
             [V:2] G8    | B8    | A8 |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0, 10, 0)
        self.generic_exception_harmony_passing_tone (abc_notation, expect)
    # end def test_exception_harmony_passing_tone_PT_acc

    def generic_exception_harmony_wechselnote (self, abc, expect):
        """ Test the Exception_Harmony_Wechselnote class
        """
        # Without exception, this should trigger (assuming it's a dissonance)
        check = checks.Check_Harmony_Interval \
            ( "Test dissonance"
            , interval = (1, 2, 5, 6, 10, 11)
            , octave   = True
            , badness  = 10.0
            )
        # Create a test check for now without the passing tone exception
        wechselnote_exception = checks.Exception_Harmony_Wechselnote \
            ( interval       = (1, 2, 5, 6, 10, 11)  # Common dissonances
            , octave         = True
            , note_length    = (2,)    # quarter notes
            , bar_position   = (2, 4, 6, 10, 12, 14)
            )

        tune = Tune.from_iterator (abc)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp)

        # Now with exception
        check.exceptions.append (wechselnote_exception)
        for cfo, cpo in tune.voices_iter ():
            b, u = check.check (cfo, cpo)
            assert (b == 0), "cfo: %s  cpo: %s" % (cfo, cpo)
    # end def generic_exception_harmony_wechselnote

    def test_exception_harmony_wechselnote_WN (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=treble
             V:1 clef=treble
             [V:1] B2 A2 B4 |
             [V:2] G8       |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0)
        self.generic_exception_harmony_wechselnote (abc_notation, expect)
    # end def test_exception_harmony_wechselnote_WN

    def test_exception_harmony_wechselnote_WN_acc (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:D
             V:2 clef=treble
             V:1 clef=treble
             [V:1] D6 E2 | F2 E2 F4 |
             [V:2] B8    | A8       |
             """
            ).strip ().split ('\n')
        expect = (0, 0, 0, 10, 0)
        self.generic_exception_harmony_wechselnote (abc_notation, expect)
    # end def test_exception_harmony_wechselnote_WN_acc

    def generic_exception_cambiata (self, abc, expect):
        """ Test the Exception_Harmony_Wechselnote class
        """
        # Without exception, this should trigger (assuming it's a dissonance)
        check = checks.Check_Harmony_Interval \
            ( "Test dissonance"
            , interval = (1, 2, 5, 6, 10, 11)
            , octave   = True
            , badness  = 10.0
            )
        # Create a test check for now without the passing tone exception
        cambiata_exception = checks.Exception_Harmony_Cambiata \
            ( interval       = (1, 2, 5, 6, 10, 11)  # Common dissonances
            , octave         = True
            )

        tune = Tune.from_iterator (abc)
        for exp, (cfo, cpo) in zip (expect, tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == exp), str (n)

        # Now with exception
        check.exceptions.append (cambiata_exception)
        for n, (cfo, cpo) in enumerate (tune.voices_iter ()):
            b, u = check.check (cfo, cpo)
            assert (b == 0), "cfo [%s]: %s  cpo: %s" % (n, cfo, cpo)
    # end def generic_exception_cambiata

    def test_exception_cambiata_1 (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=bass
             V:1 clef=treble
             [V:1] c6 B2 | G2 A2 B4 |
             [V:2] C8    | B,8      |
             """
            ).strip ().split ('\n')
        expect = (0, 10, 0, 10, 0)
        self.generic_exception_cambiata (abc_notation, expect)
    # end def test_exception_cambiata_1

    def test_exception_cambiata_2 (self):
        abc_notation = dedent \
            ("""
             X:1
             %%score 1 2
             L:1/8
             M:4/4
             K:C
             V:2 clef=bass
             V:1 clef=treble
             [V:1] D,4 E,4 | A,4 G,4 | E,4 F,4 | G,8 |
             [V:2] B,8     | C8-     | C8      | B,8 |
             """
            ).strip ().split ('\n')
        expect = (0, 0, 0, 10, 0, 0, 0)
        self.generic_exception_cambiata (abc_notation, expect)
    # end def test_exception_cambiata_2

# end class Test_Contrapunctus

class Base_Skip_Nonzero (PGA_Test_Instrumentation):
    @pytest.fixture (autouse = True)
    def skip_if_rank_nonzero (self, request):
        if pytest.mpi_rank != 0:
            pytest.skip ('Skipping because mpi_rank=%s' % pytest.mpi_rank)
    # end def skip_if_rank_nonzero
# end class Base_Skip_Nonzero

# These can fail if all process perform I/O to same file
# Looks like pytest.mpi_rank is only available *inside* the test method
class Test_Contrapunctus_IO (Base_Skip_Nonzero):

    def test_depth_first (self):
        args = self.out_options + ['-v', '-v', '--df']
        gentune_main (args)
        self.compare ()
    # end def test_depth_first

    def test_depth_first_with_cantus (self):
        args = self.out_options + ['-v', '-v', '--df', '-c', 'test/de-1.abc']
        gentune_main (args)
        self.compare ()
    # end def test_depth_first_with_cantus

    def test_gene_roundtrip (self):
        args = self.out_options + ['-v', '-v', '-g', self.data_name]
        gentune_main (args)
        self.compare ()
    # end def test_gene_roundtrip

    def test_ga_invalid_cf (self):
        args = self.out_options + ['-c', 'test/invalid-cf.abc']
        gentune_main (args)
        self.compare ()
    # end def test_ga_invalid_cf

    def test_df_invalid_cf (self):
        args = self.out_options + ['-c', 'test/invalid-cf.abc', '--df']
        gentune_main (args)
        self.compare ()
    # end def test_df_invalid_cf

    def test_transpose (self):
        args = self.out_options + '-t -5 test/h2.abc'.split ()
        contrapunctus.gentune.transpose_tune (args)
        self.compare ()
    # end def test_transpose

# end class Test_Contrapunctus_IO

@pytest.mark.slow
class Test_Contrapunctus_IO_Slow (Base_Skip_Nonzero):

    def test_search_df_cf_zacconi (self):
        """ Test depth first search with modified tune from Zacconi in
            german wikipedia page on Kontrapunkt.
            Seems like there is a problem *in the middle* of the tune
            where we have several melody unisons in the CF.
        """
        args = '--df -c test/zacconi.abc --explain-cp-cf'.split ()
        args = self.out_options + args
        gentune_main (args)
        self.compare ()
    # end def test_search_df_cf_zacconi

# end class Test_Contrapunctus_IO_Slow

@pytest.mark.slow
class Test_Contrapunctus_Slow (PGA_Test_Instrumentation):

    def test_search_ga (self):
        args = self.out_options
        gentune_main (args)
        self.compare ()
    # end def test_search_ga

    def test_search_ga_cf (self):
        args = self.out_options + ['-c', 'test/de-1.abc']
        gentune_main (args)
        self.compare ()
    # end def test_search_ga_cf

    def test_search_de (self):
        args = self.out_options + ['-R', '9', '--use-de']
        gentune_main (args)
        self.compare ()
    # end def test_search_de

    def test_search_de_cf (self):
        args = self.out_options + ['--use-de', '-c', 'test/de-1.abc']
        gentune_main (args)
        self.compare ()
    # end def test_search_de_cf

    def test_search_de_cf_haenschen (self):
        """ Test with modified Haenschen Klein
        """
        args = '--use-de -c test/h2t.abc --no-cf-feasibility --no-check-cf'
        args = self.out_options + args.split ()
        gentune_main (args)
        self.compare ()
    # end def test_search_de_cf_haenschen

    def test_search_de_cf_zacconi (self):
        """ Test DE search with modified tune from Zacconi in german
            wikipedia page on Kontrapunkt
        """
        args = '--use-de -c test/zacconi.abc --no-cf-feasibility --no-check-cf'
        args = self.out_options + args.split ()
        gentune_main (args)
        self.compare ()
    # end def test_search_de_cf_zacconi

# end class Test_Contrapunctus_Slow

class Test_Doctest:

    flags = doctest.NORMALIZE_WHITESPACE

    num_tests = dict \
        ( circle    =  2
        , gentune   =  9
        , gregorian = 10
        , tune      = 110
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
