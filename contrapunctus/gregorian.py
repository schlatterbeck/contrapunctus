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

from .tune import halftone

class Gregorian (object):
    """
    >>> d = dorian
    >>> d [0]
    D
    >>> d.finalis
    D
    >>> d.step2
    E
    >>> d [12]
    b
    >>> d [13]
    c'
    >>> d [15]
    e'
    >>> d [22]
    e''
    >>> d [-1]
    C
    >>> d.subsemitonium
    ^c
    """

    def __init__ (self, ambitus, key, offset = 0):
        assert len (ambitus) == 7
        self.ambitus = [halftone (x) for x in ambitus]
        self.key     = key
        self.offset  = offset
    # end def __init__

    @property
    def subsemitonium (self):
        """ Leading tone, German: Leitton
        """
        return self [7].transpose (-1)
    # end def subsemitonium

    @property
    def finalis (self):
        return self.ambitus [0]
    # end def finalis

    @property
    def step2 (self):
        return self.ambitus [1]
    # end def step2

    def __getitem__ (self, idx):
        """ Get halftone with index idx from our tones, note that we
            synthesize tones outside the given ambitus dynamically.
        """
        index = idx + self.offset
        if 0 <= index < len (self.ambitus):
            return self.ambitus [index]
        d, m = divmod (index, 7)
        return self.ambitus [m].transpose_octaves (d)
    # end def __getitem__

# end class Gregorian

ionian         = Gregorian (['C', 'D', 'E', 'F', 'G', 'A', 'B'], key = 'C')
hypoionian     = Gregorian (ionian.ambitus, ionian.key, offset = -3)
dorian         = Gregorian (['D', 'E', 'F', 'G', 'A', 'B', 'c'], key = 'DDor')
hypodorian     = Gregorian (dorian.ambitus, dorian.key, offset = -3)
phrygian       = Gregorian (['E', 'F', 'G', 'A', 'B', 'c', 'd'], key = 'EPhr')
hypophrygian   = Gregorian (phrygian.ambitus, phrygian.key, offset = -3)
lydian         = Gregorian (['F', 'G', 'A', 'B', 'c', 'd', 'e'], key = 'FLyd')
hypolydian     = Gregorian (lydian.ambitus, lydian.key, offset = -3)
mixolydian     = Gregorian (['G', 'A', 'B', 'c', 'd', 'e', 'f'], key = 'GMix')
hypomixolydian = Gregorian (mixolydian.ambitus, mixolydian.key, offset = -3)
aeolian        = Gregorian (['A', 'B', 'c', 'd', 'e', 'f', 'g'], key = 'Am')
hypoaeolian    = Gregorian (aeolian.ambitus, aeolian.key, offset = -3)
locrian        = Gregorian (['B', 'c', 'd', 'e', 'f', 'g', 'a'], key = 'BLoc')
hypolocrian    = Gregorian (locrian.ambitus, locrian.key, offset = -3)


gregorian_modes = dict \
    ( ionian     = (ionian,     hypoionian)
    , dorian     = (dorian,     hypodorian)
    , phrygian   = (phrygian,   hypophrygian)
    , lydian     = (lydian,     hypolydian)
    , mixolydian = (mixolydian, hypomixolydian)
    , aeolian    = (aeolian,    hypoaeolian)
    , locrian    = (locrian,    hypolocrian)
    )

__all__ = [ 'dorian', 'hypodorian', 'phrygian', 'hypophrygian', 'lydian'
          , 'hypolydian', 'mixolydian', 'hypomixolydian', 'gregorian_modes'
          , 'ionian', 'hypoionian', 'aeolian', 'hypoaeolian'
          , 'locrian', 'hypolocrian'
          ]
