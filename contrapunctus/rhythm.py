#!/usr/bin/python3
# Copyright (C) 2017-2026
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

from math   import ceil, log
from bisect import bisect_left
from .tune  import Tune, Voice, Bar, Meter, Tone

class Rhythm:
    """ The encapsulates the rhythm generation. We specify all the
        combinations of note length in a bar (as well as the bar length)
        and derive the structure of the gene concerning the rhythm part.
    """

    def __init__ (self, parent, tunelength):
        self.parent      = parent
        self.tunelength  = tunelength
        dur = self.bar_duration
        method           = self.parent.mode [0].mode_end_sequences
        self.es          = method (self.parent, dur)
        self.cf_min_esl  = int (ceil (self.es.min_cf_len / dur))
        self.cf_max_esl  = int (ceil (self.es.max_cf_len / dur))
        # remaining part after removing length of fractional part of min len
        self.cf_frac_l   = (self.cf_max_esl * dur - self.es.min_cf_len) % dur
        self.cp_min_esl  = int (ceil (self.es.min_cp_len / dur))
        self.cp_max_esl  = int (ceil (self.es.max_cp_len / dur))
        # remaining part after removing length of fractional part of min len
        self.cp_frac_l   = (self.cp_max_esl * dur - self.es.min_cp_len) % dur
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
    unit         = 8

    @property
    def cflength (self):
        if self.generate_cf:
            return self.tunelength - (1 + self.cf_max_esl)
        return 0
    # end def cflength

    @property
    def cplength (self):
        return self.tunelength - self.cp_max_esl
    # end def cplength

    def compute_init (self):
        init            = []
        self.cp_offset  = 0
        if self.cflength:
            self.cp_offset = self.cflength + (self.cf_max_esl - self.cf_min_esl)
            for i in range (self.cp_offset):
                init.append ([0, 7])
            if self.cflength and self.cf_frac_l:
                init.append ([0, 7])
                self.cp_offset += 1
        for i in range (self.cplength + (self.cp_max_esl - self.cp_min_esl)):
            init.append ([1,  3]) # duration heavy
            init.append ([0,  7]) # pitch
            init.append ([0,  1]) # duration light 1/4
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8
            init.append ([1,  2]) # duration half-heavy 1/4 or 1/2
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8 - never used?!
            init.append ([0,  1]) # duration light 1/4
            init.append ([0,  7]) # pitch
            init.append ([0,  7]) # pitch light 1/8
        if self.cp_frac_l:
            frac_ll = int (log (self.cp_frac_l) / log (2))
            assert frac_ll >= 1
            init.append ([1,  frac_ll]) # duration heavy
            init.append ([0,  7]) # pitch
            if self.cp_frac_l > 2:
                frac_ll = int (log (self.cp_frac_l - 2) / log (2))
                init.append ([0,  max (frac_ll, 1)]) # duration light 1/4
                init.append ([0,  7]) # pitch
            if self.cp_frac_l > 3:
                init.append ([0,  7]) # pitch light 1/8
            if self.cp_frac_l > 4:
                frac_ll = int (log (self.cp_frac_l - 4) / log (2))
                assert frac_ll >= 1
                init.append ([1,  max (frac_ll, 2)]) # half-heavy 1/4 or 1/2
                init.append ([0,  7]) # pitch
            if self.cp_frac_l > 5:
                init.append ([0,  7]) # pitch light 1/8
            if self.cp_frac_l > 6:
                frac_ll = int (log (self.cp_frac_l - 6) / log (2))
                init.append ([0,  max (frac_ll, 1)]) # duration light 1/4
                init.append ([0,  7]) # pitch
            assert self.cp_frac_l <= 7
        esqlen = len (self.es)
        if esqlen > 1:
            init.append ([0, esqlen - 1])
        return init
    # end def compute_init

    def phenotype (self, p, pop, maxidx = None):
        sq_idx = 0
        if len (self.es) > 1:
            l = len (self.parent.init)
            sq_idx = self.parent.get_fixed_allele (p, pop, l - 1)
        cf_esl = len (self.es.cf [sq_idx])
        cp_esl = len (self.es.cp [sq_idx])
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
        bd  = self.bar_duration
        cfl = (self.cf_max_esl * bd - cf_esl) // bd
        idx = 0
        for i in range (self.cflength + cfl):
            idx = i
            if maxidx is not None and i > maxidx:
                return tune
            a = self.parent.get_fixed_allele (p, pop, i)
            b = Bar (8, 8)
            b.add (Tone (self.parent.mode [1][a], 8))
            cf.add (b)
        idx += 1
        if self.cflength and (bd - cf_esl) % bd:
            if maxidx is not None and idx > maxidx:
                return tune
            a = self.parent.get_fixed_allele (p, pop, idx)
            b = Bar (8, 8)
            b.add (Tone (self.parent.mode [1][a], (bd - cf_esl) % bd))
            cf.add (b)
        # Append end sequence if we don't have fixed CF
        if not self.parent.cantus_firmus:
            self.es.append_end_sequence (cf, sq_idx)
        cp  = Voice (id = 'Contrapunctus', name = 'Contrapunctus')
        tune.add (cp)
        cpl = (self.cp_max_esl * bd - cp_esl) // bd
        for i in range (self.cplength + cpl):
            off  = i * 11 + self.cp_offset
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
        # Last non-full Bar
        cp_esl = (bd - cp_esl) % bd
        if cp_esl:
            i += 1
            off  = i * 11 + self.cp_offset
            boff = 0 # offset in bar
            b = Bar (8, 8)
            cp.add (b)
            if maxidx is not None and off + 1 > maxidx:
                return tune
            v = self.parent.get_fixed_allele (p, pop, off)
            l = min (1 << v, cp_esl - boff)
            assert 2 <= l <= 8
            v = self.parent.get_fixed_allele (p, pop, off + 1)
            b.add (Tone (self.parent.mode [0][v], l))
            boff += l
            if boff < cp_esl and boff == 2:
                if maxidx is not None and off + 3 > maxidx:
                    return tune
                v = self.parent.get_fixed_allele (p, pop, off + 2)
                l = min (1 << v, cp_esl - boff)
                assert 1 <= l <= 2
                v = self.parent.get_fixed_allele (p, pop, off + 3)
                b.add (Tone (self.parent.mode [0][v], l))
                boff += l
            if boff < cp_esl and boff == 3:
                if maxidx is not None and off + 4 > maxidx:
                    return tune
                v = self.parent.get_fixed_allele (p, pop, off + 4)
                b.add (Tone (self.parent.mode [0][v], 1))
                boff += 1
            if boff < cp_esl and boff == 4:
                if maxidx is not None and off + 6 > maxidx:
                    return tune
                v = self.parent.get_fixed_allele (p, pop, off + 5)
                l = min (1 << v, cp_esl - boff)
                assert 2 <= l <= 4
                v = self.parent.get_fixed_allele (p, pop, off + 6)
                b.add (Tone (self.parent.mode [0][v], l))
                boff += l
            assert boff != 5
            if boff < cp_esl and boff == 6:
                if maxidx is not None and off + 9 > maxidx:
                    return tune
                v = self.parent.get_fixed_allele (p, pop, off + 8)
                l = min (1 << v, cp_esl - boff)
                assert 1 <= l <= 2
                v = self.parent.get_fixed_allele (p, pop, off + 9)
                b.add (Tone (self.parent.mode [0][v], l))
                boff += l
            assert cp_esl == boff
        # Append end sequence
        self.es.append_end_sequence (cp, sq_idx)
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
    unit         =  8

    @classmethod
    def cf_idx (cls, maxlen):
        """ Reverse lookup from cf_tbl
        >>> b = Rhythm_Breve
        >>> for k in range (4,17):
        ...     print ('%d: %d' % (k, b.cf_idx (k)))
        4: 0
        5: 0
        6: 1
        7: 1
        8: 2
        9: 2
        10: 2
        11: 2
        12: 3
        13: 3
        14: 3
        15: 3
        16: 4
        """
        assert maxlen >= 4
        idx = bisect_left (cls.cf_tbl, maxlen)
        assert 0 <= idx <= len (cls.cf_tbl) - 1
        if cls.cf_tbl [idx] > maxlen:
            return idx - 1
        return idx
    # end def cf_idx

    @classmethod
    def cp_idx (cls, maxlen):
        """ Reverse lookup from cp_tbl
        >>> b = Rhythm_Breve
        >>> for k in range (1,17):
        ...     print ('%d: %d' % (k, b.cp_idx (k)))
        1: 0
        2: 1
        3: 1
        4: 2
        5: 2
        6: 3
        7: 3
        8: 4
        9: 4
        10: 4
        11: 4
        12: 5
        13: 5
        14: 5
        15: 5
        16: 6
        """
        assert maxlen >= 1
        idx = bisect_left (cls.cp_tbl, maxlen)
        assert 0 <= idx <= len (cls.cp_tbl) - 1
        if cls.cp_tbl [idx] > maxlen:
            return idx - 1
        return idx
    # end def cp_idx

    @property
    def cflength (self):
        """ Cantus Firmus length *in bars*
        """
        if self.generate_cf:
            return self.tunelength - (1 + self.cf_max_esl)
        return 0
    # end def cflength

    @property
    def cplength (self):
        """ Contrapunctus length *in bars*
        """
        return self.tunelength - self.cp_max_esl
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
        init           = []
        self.cp_offset = 0
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
            self.cp_offset = 6


            esl_len = self.cf_max_esl - self.cf_min_esl
            for i in range (self.cflength + esl_len):
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
                self.cp_offset += 12
            assert self.cf_frac_l < 16
            if self.cf_frac_l:
                # offset 0 # [0, 1]
                m = self.cf_idx (self.cf_frac_l)
                init.append ([0, m]) # duration heavy 2: 8, 1:6->4
                self.cp_offset += 1
                init.append ([0, 7]) # pitch
                self.cp_offset += 1
                # offset 2 # [2]
                if self.cf_frac_l > 2:
                    init.append ([0, 7]) # duration light 4/8 pitch
                    self.cp_offset += 1
                # offset 4 # [3, 4]
                if self.cf_frac_l > 4:
                    m = self.cf_idx (min (self.cf_frac_l, 8))
                    init.append ([0, m]) # duration light 1/2
                    self.cp_offset += 1
                    init.append ([0, 7]) # duration light 4/8 pitch
                    self.cp_offset += 1
                # offset 6 # [5]: only 1/4 allowed, only pitch
                if self.cf_frac_l > 6:
                    init.append ([0, 7]) # pitch
                    self.cp_offset += 1
                # offset 8 # [6, 7]
                if self.cf_frac_l > 8:
                    m = self.cf_idx (min (self.cf_frac_l, 16))
                    init.append ([0, m]) # duration heavy
                    self.cp_offset += 1
                    init.append ([0, 7]) # pitch
                    self.cp_offset += 1
                # offset 10 # [8]: only 1/4 allowed, only pitch
                if self.cf_frac_l > 10:
                    init.append ([0, 7]) # pitch
                    self.cp_offset += 1
                # offset 12 # [9, 10]
                if self.cf_frac_l > 12:
                    m = self.cf_idx (min (self.cf_frac_l, 8))
                    init.append ([0, m]) # duration light
                    self.cp_offset += 1
                    init.append ([0, 7]) # pitch
                    self.cp_offset += 1
                assert self.cf_frac_l <= 14
        # Allow 16/8, 12/8, 8/8, 6/8, 4/8, 2/8, 1/8
        esl_len = self.cp_max_esl - self.cp_min_esl
        for i in range (self.cplength + esl_len):
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
        assert self.cp_frac_l < 16
        if self.cp_frac_l:
            # offset 0 # [0, 1]
            m = self.cp_idx (self.cp_frac_l)
            assert m <= 5
            init.append ([1,  m]) # heavy: 5:12/8 4:8/8 3:6/8 2:4/8 1:2/8
            init.append ([0,  7]) # pitch
            # offset 2 # [2, 3]
            if self.cp_frac_l > 2:
                m = self.cp_idx (min (self.cp_frac_l, 4))
                init.append ([0,  m]) # light 1/4: 2:4/8 1:2/8 0:1/8
                init.append ([0,  7]) # pitch
            # offset 3 # [4]
            if self.cp_frac_l > 3:
                init.append ([0,  7]) # pitch light 1/8
            # offset 4 # [5, 6]
            if self.cp_frac_l > 4:
                m = self.cp_idx (min (self.cp_frac_l, 8))
                init.append ([1,  m]) # half-heavy: 4:8/8 3:6/8 2:4/8 1:2/8
                init.append ([0,  7]) # pitch
            # offset 6 # [7, 8]
            if self.cp_frac_l > 6:
                m = self.cp_idx (min (self.cp_frac_l, 4))
                init.append ([0,  m]) # light 1/4: 2:4/8 1:2/8 0:1/8
                init.append ([0,  7]) # pitch
            # offset 7 # [9]
            if self.cp_frac_l > 7:
                init.append ([0,  7]) # pitch light 1/8
            # offset 8 # [10, 11]
            if self.cp_frac_l > 8:
                m = self.cp_idx (min (self.cp_frac_l, 12))
                init.append ([1,  m]) # heavy
                init.append ([0,  7]) # pitch
            # offset 10 # [12, 13]
            if self.cp_frac_l > 10:
                m = self.cp_idx (min (self.cp_frac_l, 4))
                init.append ([0,  m]) # light 1/4: 2:4/8 1:2/8 0:1/8
                init.append ([0,  7]) # pitch
            # offset 11 # [14]
            if self.cp_frac_l > 11:
                init.append ([0,  7]) # pitch light 1/8
            # offset 12 # [15, 16]
            if self.cp_frac_l > 12:
                m = self.cp_idx (min (self.cp_frac_l, 8))
                init.append ([1,  m]) # half-heavy: 4:8/8 3:6/8 2:4/8 1:2/8
                init.append ([0,  7]) # pitch
            # offset 14 # [17, 18]
            if self.cp_frac_l > 14:
                m = self.cp_idx (min (self.cp_frac_l, 4))
                init.append ([0,  m]) # light 1/4: 2:4/8 1:2/8 0:1/8
                init.append ([0,  7]) # pitch
            assert self.cp_frac_l <= 15
        esqlen = len (self.es)
        if esqlen > 1:
            init.append ([0, esqlen - 1])
        return init
    # end def compute_init

    def phenotype (self, p, pop, maxidx = None):
        sq_idx = 0
        if len (self.es) > 1:
            l = len (self.parent.init)
            sq_idx = self.parent.get_fixed_allele (p, pop, l - 1)
        cf_esl = len (self.es.cf [sq_idx])
        cp_esl = len (self.es.cp [sq_idx])
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
        bd  = self.bar_duration
        cfl = self.cf_max_esl - ceil (cf_esl / bd)
        if self.cflength:
            for i in range (self.cflength + cfl):
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
            cf_rv = (bd - cf_esl) % bd
            if off > cf_rv:
                lastobj = cf.bars [-1].objects [-1]
                assert lastobj.duration >= off - cf_rv
                lastobj.duration -= off - cf_rv
                if lastobj.duration == 0:
                    del cf.bars [-1].objects [-1]
                    if len (cf.bars [-1].objects) == 0:
                        del cf.bars [-1]
                        cf.bars [-1].objects [-1].bind = False
                off = cf_rv
            if cf_rv:
                if off < cf_rv and off == 0:
                    b = Bar (16, 8)
                    cf.add (b)
                    d = min (self.cf_duration (p, pop, idx), cf_rv - off)
                    a = self.parent.get_fixed_allele (p, pop, idx + 1)
                    t, r = self.split_tone (1, a, off, d)
                    assert r is None
                    b.add (t)
                    off += d
                if off < cf_rv and off == 2:
                    d = min (2, cf_rv - off)
                    assert b.objects [-1].is_dotted
                    assert b.objects [-1].length == 6
                    a = self.parent.get_fixed_allele (p, pop, idx + 2)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                if off < cf_rv and off == 4:
                    d = min (self.cf_duration (p, pop, idx + 3), cf_rv - off)
                    a = self.parent.get_fixed_allele (p, pop, idx + 4)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                if off < cf_rv and off == 6:
                    d = min (2, cf_rv - off)
                    assert b.objects [-1].is_dotted
                    assert b.objects [-1].length == 6
                    a = self.parent.get_fixed_allele (p, pop, idx + 5)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                if off < cf_rv and off == 8:
                    d = min (self.cf_duration (p, pop, idx + 6), cf_rv - off)
                    a = self.parent.get_fixed_allele (p, pop, idx + 7)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                if off < cf_rv and off == 10:
                    d = min (2, cf_rv - off)
                    assert b.objects [-1].is_dotted
                    assert b.objects [-1].length == 6
                    a = self.parent.get_fixed_allele (p, pop, idx + 8)
                    t, r = self.split_tone (1, a, off, d)
                    assert r is None
                    b.add (t)
                    off += d
                if off < cf_rv and off == 12:
                    d = min (self.cf_duration (p, pop, idx + 9), cf_rv - off)
                    if b.objects [-1].is_dotted:
                        assert b.objects [-1].length == 12
                        d = min (4, cf_rv - off)
                    a = self.parent.get_fixed_allele (p, pop, idx + 10)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                if off < cf_rv and off == 14:
                    d = min (2, cf_rv - off)
                    assert b.objects [-1].is_dotted
                    assert b.objects [-1].length == 6
                    a = self.parent.get_fixed_allele (p, pop, idx + 11)
                    t, r = self.split_tone (1, a, off, d)
                    b.add (t)
                    off += d
                idx += off
            assert off == cf_rv
            self.es.append_end_sequence (cf, sq_idx)
        cp  = Voice (id = 'Contrapunctus', name = 'Contrapunctus')
        tune.add (cp)
        off = 0
        cpl = self.cp_max_esl - ceil (cp_esl / bd)
        idx = self.cp_offset
        for i in range (self.cplength + cpl):
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
        # CP end sequence *rest*
        cp_rv = (bd - cp_esl) % bd
        assert cp_rv < 16
        if off > cp_rv:
            lastobj = cp.bars [-1].objects [-1]
            assert lastobj.duration >= off - cp_rv
            lastobj.duration -= off - cp_rv
            if lastobj.duration == 0:
                del cp.bars [-1].objects [-1]
                if len (cp.bars [-1].objects) == 0:
                    del cp.bars [-1]
                    cp.bars [-1].objects [-1].bind = False
            off = cp_rv
        if cp_rv:
            if off < cp_rv and off == 0:
                b = Bar (16, 8)
                cp.add (b)
                d = min (self.cp_duration (p, pop, idx), cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 1)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 2:
                d = min (self.cp_duration (p, pop, idx + 2), cp_rv - off)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = min (2, cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 3)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 3:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 4)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 4:
                d = min (self.cp_duration (p, pop, idx + 5), cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 6)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 6:
                d = min (self.cp_duration (p, pop, idx + 7), cp_rv - off)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = min (2, cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 8)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 7:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 9)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 8:
                d = min (self.cp_duration (p, pop, idx + 10), cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 11)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
            if off < cp_rv and off == 10:
                d = min (self.cp_duration (p, pop, idx + 12), cp_rv - off)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = min (2, cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 13)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 11:
                d = 1
                a = self.parent.get_fixed_allele (p, pop, idx + 14)
                t, r = self.split_tone (0, a, off, d)
                assert r is None
                b.add (t)
                off += d
            if off < cp_rv and off == 12:
                d = min (self.cp_duration (p, pop, idx + 15), cp_rv - off)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 12
                    d = min (4, cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 16)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
            if off < cp_rv and off == 14:
                d = min (self.cp_duration (p, pop, idx + 17), cp_rv - off)
                if b.objects [-1].is_dotted:
                    assert b.objects [-1].length == 6
                    d = min (2, cp_rv - off)
                a = self.parent.get_fixed_allele (p, pop, idx + 18)
                t, r = self.split_tone (0, a, off, d)
                b.add (t)
                off += d
        assert off == cp_rv
        self.es.append_end_sequence (cp, sq_idx)
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
