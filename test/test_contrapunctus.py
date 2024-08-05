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

    abcheader = \
        ( "X: 1\nM: 4/4\nQ: 1/4=200\n"
          "%%score (Contrapunctus) (CantusFirmus)\n"
          "L: 1/8\nV:CantusFirmus \nV:Contrapunctus \nK: DDor\n"
        )
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
        check = Check_Harmony_History \
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
        check = Check_Melody_Jump ('Jump', badness = 10)
        assert check.msg == 'Jump'
        assert check.prev_match is False
    # end def test_reset_upcall

    def test_logparse (self):
        cmd  = contrapunctus.gentune.contrapunctus_cmd ()
        args = cmd.parse_args (['-v', '-v', '-b', '-g' 'test/example.log'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        txt  = cp.from_gene ()
        with open ('test/example.abc') as f:
            abc = f.read ()
        assert txt.strip () == abc.strip ()
        # roundtrip test, note the missing -b ('best') option
        args = cmd.parse_args (['-v', '-v', '-g' 'test/example.abc'])
        cp   = contrapunctus.gentune.Contrapunctus_Depth_First (cmd, args)
        txt  = cp.from_gene ()
        assert txt.strip () == abc.strip ()
    # end def test_logparse

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
        t = fake.as_tune (1, 1)
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
        t = fake.as_tune (1, 1)
        result = header + '[V:Contrapunctus] G4 A2 F2 |G4 A2 F1 G1 |^c8 |d8 |'
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
        t = fake.as_tune (1, 1)
        result = header + '[V:Contrapunctus] G2 A2 A2 F1 F1 |' \
                          'G2 A1 A1 G2 A1 A1 |^c8 |d8 |'
        assert t == result
    # end def test_gene_decode_22211_211211

    def test_empty_prev_bar (self):
        """ Some of the searches have an empty bar *before* a valid one.
            This tests that nothing breaks.
        """
        check = Check_Harmony_Melody_Direction \
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
        check = Check_Harmony_First_Interval \
            ( 'unison, octave, fifth'
            , interval = (0, 7, 12)
            , badness  = 100
            )
        v1  = Voice (id = 'CF')
        b11 = Bar (8, 8)
        v1.add (b11)
        b12 = Bar (8, 8)
        b12.add (Tone (halftone ('f'), 4))
        b12.add (Tone (halftone ('g'), 4))
        v1.add (b12)
        v2 = Voice (id = 'CP')
        b21 = Bar (8, 8)
        v2.add (b21)
        b22 = Bar (8, 8)
        b22.add (Tone (halftone ('g'), 4))
        b22.add (Tone (halftone ('f'), 4))
        v2.add (b22)
        b, u = check.check (b12.objects [0], b22.objects [0])
        assert b == 0
        b11.add (Tone (halftone ('g'), 8))
        b21.add (Tone (halftone ('f'), 8))
        b, u = check.check (b12.objects [0], b22.objects [0])
        assert b == 0
        b, u = check.check (b11.objects [0], b21.objects [0])
        assert b == 100
    # end def test_check_harmony_first_interval

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
