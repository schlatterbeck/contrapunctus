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
        # Can't use '[[0, 7]] * cflength' due to aliasing
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
            , key    = 'DDor' 
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

__all__ = ['Rhythm_Semibreve']
