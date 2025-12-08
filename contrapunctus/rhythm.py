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

from .tune      import Tune, Voice, Bar, Meter, Tone

class Rhythm:
    """ The encapsulates the rhythm generation. We specify all the
        combinations of note length in a bar (as well as the bar length)
        and derive the structure of the gene concerning the rhythm part.
    """

    def __init__ (self, parent, tunelength):
        self.parent      = parent
        self.tunelength  = tunelength
    # end def __init__

    @property
    def generate_cf (self):
        # This is computed *after* we're initialized
        return not self.parent.cantus_firmus
    # end def generate_cf

    def compute_init (self):
        raise NotImplementedError ("Must be implemented in derived class")
    # end def compute_init

    def phenotype (self, p, pop, maxidx = None):
        raise NotImplementedError ("Must be implemented in derived class")
    # end def phenotype

# end class Rhythm

class Rhythm_Semibreve (Rhythm):
    """ Length of the automatically-generated voices
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

    bar_duration = 8 # in 1/8

    @property
    def cflength (self):
        if self.generate_cf:
            return self.tunelength - 3
        return 0
    # end def cflength

    @property
    def cplength (self):
        return self.tunelength - 2
    # end def cplength

    def compute_init (self):
        init            = []
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
        return init
    # end def compute_init

    def phenotype (self, p, pop, maxidx = None):
        tune = Tune \
            ( number = 1
            , meter  = Meter (4, 4)
            , Q      = '1/4=200'
            , key    = self.parent.mode [0].key
            , unit   = 8
            , score  = '(Contrapunctus) (CantusFirmus)'
            )
        if self.parent.cantus_firmus:
            cf = self.parent.cantus_firmus.copy ()
            assert self.cflength == 0
        else:
            cf = Voice (id = 'CantusFirmus', name = 'Cantus Firmus')
            b  = Bar (8, 8)
            b.add (Tone (self.parent.mode [1].finalis, 8))
            cf.add (b)
        tune.add (cf)
        for i in range (self.cflength):
            if maxidx is not None and i > maxidx:
                return tune
            a = self.parent.get_fixed_allele (p, pop, i)
            b = Bar (8, 8)
            b.add (Tone (self.parent.mode [1][a], 8))
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
        if not self.parent.cantus_firmus:
            b  = Bar (8, 8)
            b.add (Tone (self.parent.mode [1].step2, 8))
            cf.add (b)
            b  = Bar (8, 8)
            b.add (Tone (self.parent.mode [1].finalis, 8))
            cf.add (b)
        cp  = Voice (id = 'Contrapunctus', name = 'Contrapunctus')
        tune.add (cp)
        for i in range (self.cplength):
            off  = i * 11 + self.cflength
            boff = 0 # offset in bar
            v = []
            for j in range (11):
                idx = j + off
                a = self.parent.get_fixed_allele (p, pop, idx)
                v.append (a)
            b = Bar (8, 8)
            cp.add (b)
            if maxidx is not None and off + 1 > maxidx:
                return tune
            l = 1 << v [0]
            assert 2 <= l <= 8
            b.add (Tone (self.parent.mode [0][v [1]], l))
            boff += l
            if boff == 2:
                if maxidx is not None and off + 3 > maxidx:
                    return tune
                l = 1 << v [2]
                assert 1 <= l <= 2
                b.add (Tone (self.parent.mode [0][v [3]], l))
                boff += l
            if boff == 3:
                if maxidx is not None and off + 4 > maxidx:
                    return tune
                b.add (Tone (self.parent.mode [0][v [4]], 1))
                boff += 1
            if boff == 4:
                if maxidx is not None and off + 6 > maxidx:
                    return tune
                l = 1 << v [5]
                assert 2 <= l <= 4
                b.add (Tone (self.parent.mode [0][v [6]], l))
                boff += l
            if boff == 5: # pragma: no cover
                # Probably never reached, prev tone may not be len 1
                if maxidx is not None and off + 7 > maxidx:
                    return tune
                b.add (Tone (self.parent.mode [0][v [7]], 1))
                boff += 1
            if boff == 6:
                if maxidx is not None and off + 9 > maxidx:
                    return tune
                l = 1 << v [8]
                assert 1 <= l <= 2
                b.add (Tone (self.parent.mode [0][v [9]], l))
                boff += l
            if boff == 7:
                if maxidx is not None and off + 10 > maxidx:
                    return tune
                b.add (Tone (self.parent.mode [0][v [10]], 1))
                boff += 1
        b  = Bar (8, 8)
        # 0.1.1: "The final must be approached by step. If the final is
        # approached from below, then the leading tone must be raised in
        # a minor key (Dorian, Hypodorian, Aeolian, Hypoaeolian), but
        # not in Phrygian or Hypophrygian mode. Thus, in the Dorian mode
        # on D a C# is necessary at the cadence." We achieve this by
        # hard-coding the tone prior to the final to be the
        # subsemitonium for the contrapunctus.
        b.add (Tone (self.parent.mode [0].subsemitonium, 8))
        cp.add (b)
        b  = Bar (8, 8)
        b.add (Tone (self.parent.mode [0][7], 8))
        cp.add (b)
        return tune
    # end def phenotype

# end class Rhythm_Semibreve

class Rhythm_Breve (Rhythm):
    """ A bar is 16/8 long.
        For the details see the compute_init method
    """

    cf_tbl = [4, 6, 8, 12, 16]
    cp_tbl = [1, 2, 4, 6, 8, 12, 16]

    bar_duration = 16 # in 1/8

    @property
    def cflength (self):
        """ Cantus Firmus length *in bars*
        """
        if self.generate_cf:
            return self.tunelength - 3
        return 0
    # end def cflength

    @property
    def cplength (self):
        """ Contrapunctus length *in bars*
        """
        return self.tunelength - 2
    # end def cplength

    def cf_duration (self, p, pop, idx):
        a  = self.parent.get_fixed_allele (p, pop, idx)
        return self.cf_tbl [a]
    # end def cf_duration

    def cp_duration (self, p, pop, idx):
        a  = self.parent.get_fixed_allele (p, pop, idx)
        return self.cp_tbl [a]
    # end def cp_duration

    def compute_init (self):
        init            = []
        # Allow 16/8, 12/8, 8/8, 4/8
        # 12/8 at end may go into next bar!
        # Syncope from 16/8, 8/8
        # After dotted note next is always 1/3 of it
        # Syncopes are *NOT* reached by a dotted note!
        # (e.g. 12/8 followed by 4/8) in that case we ignore the length

        if self.cflength:
            # The first tone of CF is always finalis:
            # Start with finalis in length 3:16 2:12 1:8
            # offset 0
            init.append ([2, 4]) # duration 4:16 3:12 2:8, pitch is finalis
            # offset 8
            init.append ([0, 4]) # duration heavy 4:16, 3:12, 2:8, 1:6, 0:4
            init.append ([0, 7]) # pitch
            # offset 12
            init.append ([0, 2]) # duration light 1/2 2:8, 1:6, 0:4
            init.append ([0, 7]) # pitch
            # offset 14: only 1/4 allowed, only pitch
            init.append ([0, 7]) # pitch

            for i in range (self.cflength):
                # offset 0 # [0, 1]
                init.append ([0, 4]) # duration heavy 4:16, 3:12, 2:8, 1:6, 0:4
                init.append ([0, 7]) # pitch
                # offset 2 # [2]: only 1/4 allowed, only pitch
                init.append ([0, 7]) # pitch
                # offset 4 # [3, 4]
                init.append ([0, 2]) # duration light 1/2 2: 8, 1:6, 0:4
                init.append ([0, 7]) # pitch
                # offset 6 # [5]: only 1/4 allowed, only pitch
                init.append ([0, 7]) # pitch
                # offset 8 # [6, 7]
                init.append ([0, 4]) # duration heavy 4:16, 3:12, 2:8, 1:6, 0:4
                init.append ([0, 7]) # pitch
                # offset 10 # [8]: only 1/4 allowed, only pitch
                init.append ([0, 7]) # pitch
                # offset 12 # [9, 10]
                init.append ([0, 2]) # duration light 1/2 2: 8, 1:6, 0:4
                init.append ([0, 7]) # pitch
                # offset 14 [11]: only 1/4 allowed, only pitch
                init.append ([0, 7]) # pitch
            # offset 0 # [0, 1]
            init.append ([0, 2]) # duration heavy 2: 8, 1:6->4
            init.append ([0, 7]) # pitch
            # offset 2 # [2]
            init.append ([0, 7]) # duration light 4/8 pitch
            # offset 4 # [3]
            init.append ([0, 7]) # duration light 4/8 pitch
        # Allow 16/8, 12/8, 8/8, 6/8, 4/8, 2/8, 1/8
        for i in range (self.cplength):
            # offset 0 # [0, 1]
            init.append ([1,  5]) # heavy: 5:12/8 4:8/8 3:6/8 2:4/8 1:2/8
            init.append ([0,  7]) # pitch
            # offset 2 # [2, 3]
            init.append ([0,  2]) # light 1/4: 2:4/8 1:2/8 0:1/8
            init.append ([0,  7]) # pitch
            # offset 3 # [4]
            init.append ([0,  7]) # pitch light 1/8
            # offset 4 # [5, 6]
            init.append ([1,  4]) # half-heavy: 4:8/8 3:6/8 2:4/8 1:2/8
            init.append ([0,  7]) # pitch
            # offset 6 # [7, 8]
            init.append ([0,  2]) # light 1/4: 2:4/8 1:2/8 0:1/8
            init.append ([0,  7]) # pitch
            # offset 7 # [9]
            init.append ([0,  7]) # pitch light 1/8
            # offset 8 # [10, 11]
            init.append ([1,  5]) # heavy: 5:12/8 4:8/8 3:6/8 2:4/8 1:2/8
            init.append ([0,  7]) # pitch
            # offset 10 # [12, 13]
            init.append ([0,  2]) # light 1/4: 2:4/8 1:2/8 0:1/8
            init.append ([0,  7]) # pitch
            # offset 11 # [14]
            init.append ([0,  7]) # pitch light 1/8
            # offset 12 # [15, 16]
            init.append ([1,  4]) # half-heavy: 4:8/8 3:6/8 2:4/8 1:2/8
            init.append ([0,  7]) # pitch
            # offset 14 # [17, 18]
            init.append ([0,  2]) # light 1/4: 2:4/8 1:2/8 0:1/8
            init.append ([0,  7]) # pitch
            # offset 15 # [19]
            init.append ([0,  7]) # pitch light 1/8
        # offset 0 # [0, 1]
        init.append ([1,  4]) # heavy: 4:8/8 3:6/8 2:4/8 1:2/8
        init.append ([0,  7]) # pitch
        # offset 2 # [2, 3]
        init.append ([0,  2]) # light 1/4: 2:4/8 1:2/8 0:1/8
        init.append ([0,  7]) # pitch
        # offset 3 # [4]
        init.append ([0,  7]) # pitch light 1/8
        # offset 4 # [5, 6]
        init.append ([1,  2]) # half-heavy: 2:4/8 1:2/8
        init.append ([0,  7]) # pitch
        # offset 6 # [7, 8]
        init.append ([0,  1]) # light 1/4: 1:2/8 0:1/8
        init.append ([0,  7]) # pitch
        # offset 7 # [9]
        init.append ([0,  7]) # pitch light 1/8
        return init
    # end def compute_init

    def phenotype (self, p, pop, maxidx = None):
        tune = Tune \
            ( number = 1
            , meter  = Meter (8, 4)
            , Q      = '1/4=200'
            , key    = self.parent.mode [0].key
            , unit   = 8
            , score  = '(Contrapunctus) (CantusFirmus)'
            )
        if self.parent.cantus_firmus:
            cf = self.parent.cantus_firmus.copy ()
            assert self.cflength == 0
            idx = 0
        else:
            r  = None
            cf = Voice (id = 'CantusFirmus', name = 'Cantus Firmus')
            b  = Bar (16, 8)
            d  = d1 = off = self.cf_duration (p, pop, 0)
            b.add (Tone (self.parent.mode [1].finalis, d))
            cf.add (b)
            if off == 8:
                d = self.cf_duration (p, pop, 1)
                a = self.parent.get_fixed_allele (p, pop, 2)
                t, r = self.split_tone (1, a, off, d)
                b.add (t)
                off += d
            if off == 12:
                d = self.cf_duration (p, pop, 3)
                # If last tone was 12 long only 4 is allowed now
                if d1 == 12:
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, 4)
                t, r = self.split_tone (1, a, off, d)
                b.add (t)
                off += d
            if off == 14:
                # last tone was 6 long, only 2 is allowed now
                d = 2
                a = self.parent.get_fixed_allele (p, pop, 5)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if r:
                b = Bar (16, 8)
                cf.add (b)
                b.add (r)
            off %= 16
            idx = 6
        tune.add (cf)
        for i in range (self.cflength):
            if maxidx is not None and i > maxidx:
                return tune
            if off == 0:
                b = Bar (16, 8)
                cf.add (b)
                d = self.cf_duration (p, pop, idx)
                a = self.parent.get_fixed_allele (p, pop, idx + 1)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 1
            if off == 2:
                d = 2
                assert b.objects [-1].is_dotted
                assert b.objects [-1].length == 6
                a = self.parent.get_fixed_allele (p, pop, idx + 2)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 3
            if off == 4:
                d = self.cf_duration (p, pop, idx + 3)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 12
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 4)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 5
            if off == 6:
                d = 2
                assert b.objects [-1].is_dotted
                assert b.objects [-1].length == 6
                a = self.parent.get_fixed_allele (p, pop, idx + 5)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 7
            if off == 8:
                d = self.cf_duration (p, pop, idx + 6)
                a = self.parent.get_fixed_allele (p, pop, idx + 7)
                t, r = self.split_tone (1, a, off, d)
                b.add (t)
                off += d
            assert off != 9
            if off == 10:
                d = 2
                assert b.objects [-1].is_dotted
                assert b.objects [-1].length == 6
                a = self.parent.get_fixed_allele (p, pop, idx + 8)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 11
            if off == 12:
                d = self.cf_duration (p, pop, idx + 9)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 12
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 10)
                t, r = self.split_tone (1, a, off, d)
                b.add (t)
                off += d
            assert off != 13
            if off == 14:
                d = 2
                assert b.objects [-1].is_dotted
                assert b.objects [-1].length == 6
                a = self.parent.get_fixed_allele (p, pop, idx + 11)
                t, r = self.split_tone (1, a, off, d)
                b.add (t)
                off += d
            if r:
                b = Bar (16, 8)
                cf.add (b)
                b.add (r)
                assert off % 16 > 0
            assert off >= 16
            off %= 16
            idx += 12
        # CF end sequence
        if self.cflength:
            if off == 0:
                b = Bar (16, 8)
                cf.add (b)
                d = self.cf_duration (p, pop, idx)
                # Gene is 2:8, 1:6 but we need 4
                if d == 6:
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 1)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 2:
                d = 2
                assert b.objects [-1].is_dotted
                assert b.objects [-1].length == 6
                a = self.parent.get_fixed_allele (p, pop, idx + 2)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 4:
                d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 3)
                t, r = self.split_tone (1, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off == 8
            idx += 4
            b.add (Tone (self.parent.mode [1].step2, 8))
            b  = Bar (16, 8)
            cf.add (b)
            b.add (Tone (self.parent.mode [1].finalis, 16))
        cp  = Voice (id = 'Contrapunctus', name = 'Contrapunctus')
        tune.add (cp)
        off = 0
        for i in range (self.cplength):
            if off == 0:
                b = Bar (16, 8)
                cp.add (b)
                d = self.cp_duration (p, pop, idx)
                a = self.parent.get_fixed_allele (p, pop, idx + 1)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 1
            if off == 2:
                d = self.cp_duration (p, pop, idx + 2)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = 2
                a = self.parent.get_fixed_allele (p, pop, idx + 3)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 3:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 4)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 4:
                d = self.cp_duration (p, pop, idx + 5)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 12
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 6)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            assert off != 5
            if off == 6:
                d = self.cp_duration (p, pop, idx + 7)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = 2
                a = self.parent.get_fixed_allele (p, pop, idx + 8)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 7:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 9)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 8:
                d = self.cp_duration (p, pop, idx + 10)
                a = self.parent.get_fixed_allele (p, pop, idx + 11)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
            assert off != 9
            if off == 10:
                d = self.cp_duration (p, pop, idx + 12)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = 2
                a = self.parent.get_fixed_allele (p, pop, idx + 13)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 11:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 14)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off == 12:
                d = self.cp_duration (p, pop, idx + 15)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 12
                    d = 4
                a = self.parent.get_fixed_allele (p, pop, idx + 16)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
            assert off != 13
            if off == 14:
                d = self.cp_duration (p, pop, idx + 17)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = 2
                a = self.parent.get_fixed_allele (p, pop, idx + 18)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
            if off == 15:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 19)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if r:
                b = Bar (16, 8)
                cp.add (b)
                b.add (r)
            idx += 20
            assert off >= 16
            off %= 16
        if off == 0:
            b = Bar (16, 8)
            cp.add (b)
            d = self.cp_duration (p, pop, idx)
            a = self.parent.get_fixed_allele (p, pop, idx + 1)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        assert off != 1
        if off == 2:
            d = self.cp_duration (p, pop, idx + 2)
            if b.objects [-1].is_dotted:
                assert b.objects [-1].length == 6
                d = 2
            a = self.parent.get_fixed_allele (p, pop, idx + 3)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        if off == 3:
            d = 1
            a = self.parent.get_fixed_allele (p, pop, idx + 4)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        if off == 4:
            d = self.cp_duration (p, pop, idx + 5)
            a = self.parent.get_fixed_allele (p, pop, idx + 6)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        assert off != 5
        if off == 6:
            d = self.cp_duration (p, pop, idx + 7)
            if b.objects [-1].is_dotted:
                assert b.objects [-1].length == 6
                d = 2
            a = self.parent.get_fixed_allele (p, pop, idx + 8)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        if off == 7:
            d = 1
            a = self.parent.get_fixed_allele (p, pop, idx + 9)
            t, r = self.split_tone (0, a, off, d)
            assert r is None
            b.add (t)
            off += d
        # End sequence
        assert off == 8
        b.add (Tone (self.parent.mode [0].subsemitonium, 8))
        b  = Bar (16, 8)
        cp.add (b)
        b.add (Tone (self.parent.mode [0][7], 16))
        return tune
    # end def phenotype

    def split_tone (self, vidx, pitch, off, d, maxlen = 16):
        """ Return two tones if off + d exceeds maxlen, otherwise the
            second item returned is None. If we return two tones, the
            first is bound to the second.
            The vidx is the voice index (1 for cantus firmus), pitch is
            the tone pitch, off is the current bar offset, d is the tone
            length (if it exceeds the bar we split).
        """
        t1 = Tone (self.parent.mode [vidx][pitch], min (d, maxlen - off))
        t2 = None
        if off + d > maxlen:
            t2 = Tone (self.parent.mode [vidx][pitch], (off + d) % maxlen)
            t1.bind = True
        return t1, t2
    # end def split_tone

# end class Rhythm_Breve

__all__ = ['Rhythm_Semibreve', 'Rhythm_Breve']
