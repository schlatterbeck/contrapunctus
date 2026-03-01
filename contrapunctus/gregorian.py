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

from .tune import Tone, halftone

# These assume L:1/8, each end sequence consists of cp, cf in a separate
# dictionary -- these must match by length, the first cp entry belongs
# to the first cf entry, etc. Note that they need not have the same
# length, the rest of the framework can generate tones where undefined.

end_sequences = dict \
    ( dorian =  dict
        ( cp =
            [ [('d',  8), ('^c', 4), ('d',  8)]
            , [('d',  6), ('^c', 2), ('c',  2), ('B', 2), ('d', 8)]
            , [('d',  6), ('B',  2), ('^c', 4), ('d', 8)]
            , [('d',  6), ('^c', 2), ('c',  4), ('d', 8)]
            , [('d',  6), ('^c', 1), ('B',  1), ('c', 4), ('d', 8)]
            , [('^c', 4), ('d',  8)]
            , [('c',  4), ('A',  4), ('d',  8)]
            ]
        , cf =
            [ [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('E',  8), ('D',  8)]
            , [('E',  8), ('D',  8)]
            ]
        )

    , phrygian = dict
        ( cp =
            [ [('F',  8), ('E',  8)]
            , [('B',  4), ('e',  8), ('d',  4), ('e', 8)]
            , [('B',  4), ('e',  6), ('d',  2), ('d', 2), ('c', 2), ('e', 8)]
            , [('B',  4), ('e',  6), ('c',  2), ('d', 4), ('e', 8)]
            , [('B',  4), ('e',  6), ('d',  2), ('d', 4), ('e', 8)]
            , [('B',  4), ('e',  6), ('d',  1), ('c', 1), ('d', 4), ('e', 8)]
            , [('F',  2), ('G',  2), ('F',  4), ('E', 8)]
            , [('F',  8), ('E',  8)]
            ]
        , cf =
            [ [('D',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('D',  8), ('E',  8)]
            , [('D',  8), ('E',  8)]
            ]
        )
    , ionian = dict
        ( cp =
            [ [('c',  8), ('B',  4), ('c',  8)]
            , [('c',  6), ('B',  2), ('B',  2), ('A', 2), ('c', 8)]
            , [('c',  6), ('A',  2), ('B',  4), ('c', 8)]
            , [('c',  6), ('B',  2), ('B',  4), ('c', 8)]
            , [('c',  6), ('B',  1), ('A',  1), ('B', 4), ('c', 8)]
            # quintfallend:
            , [('c',  8), ('c',  8)]
            , [('G',  8), ('C',  8)]
            ]
        , cf =
            [ [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            # quintfallend:
            , [('G',  8), ('C',  8)]
            , [('C',  8), ('C',  8)]
            ]
        )
    , hypodorian = dict
        ( cp =
            [ [('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('F',  8), ('E',  8), ('D',  8)]
            , [('E',  8), ('D',  8)]
            ]
        , cf =
            [ [('C',  4), ('A,', 4), ('D',  8)]
            , [('D',  8), ('^C', 4), ('D',  8)]
            , [('D',  6), ('^C', 2), ('C',  2), ('B', 2), ('D', 8)]
            , [('D',  6), ('B',  2), ('^C', 4), ('D', 8)]
            , [('D',  6), ('^C', 2), ('C',  4), ('D', 8)]
            , [('D',  6), ('^C', 1), ('B,', 1), ('C', 4), ('D', 8)]
            , [('^C', 4), ('D',  8)]
            ]
        )
    , hypophrygian = dict
        ( cp =
            [ [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('G',  8), ('F',  8), ('E',  8)]
            , [('D',  8), ('E',  8)]
            , [('D',  8), ('E',  8)]
            ]
        , cf =
            [ [('B,', 4), ('E',  8), ('D',  4), ('E', 8)]
            , [('B,', 4), ('E',  6), ('D',  2), ('D', 2), ('C', 2), ('E', 8)]
            , [('B,', 4), ('E',  6), ('C',  2), ('D', 4), ('E', 8)]
            , [('B,', 4), ('E',  6), ('D',  2), ('D', 4), ('E', 8)]
            , [('B,', 4), ('E',  6), ('D',  1), ('C', 1), ('D', 4), ('E', 8)]
            , [('F',  2), ('G',  2), ('F',  4), ('E', 8)]
            , [('F',  8), ('E',  8)]
            ]
        )
    , hypoionian = dict
        ( cp =
            [ [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            , [('E',  8), ('D',  8), ('C',  8)]
            ]
        , cf =
            [ [('C',  8), ('B,', 4), ('C',  8)]
            , [('C',  6), ('B,', 2), ('B,', 2), ('A,', 2), ('C', 8)]
            , [('C',  6), ('A,', 2), ('B,', 4), ('C',  8)]
            , [('C',  6), ('B,', 2), ('B,', 4), ('C',  8)]
            , [('C',  6), ('B,', 1), ('A,', 1), ('B,', 4), ('C', 8)]
            ]
        )
    )
# These are re-used from dorian FIXME: transpose
end_sequences ['mixolydian']     = end_sequences ['dorian']
end_sequences ['hypomixolydian'] = end_sequences ['hypodorian']
end_sequences ['aeolian']        = end_sequences ['dorian']
end_sequences ['hypoaeolian']    = end_sequences ['hypodorian']
# And these are re-used from ionian FIXME: transpose
end_sequences ['lydian']         = end_sequences ['ionian']
end_sequences ['hypolydian']     = end_sequences ['hypoionian']
# We currently do not have end-sequences for locrian and hypolocrian
end_sequences ['locrian'] = dict (cp = [], cf = [])
end_sequences ['hypolocrian'] = end_sequences ['locrian']

intermediate_sequence = dict \
    ( ionian = dict
        ( cp =
            [ [('E',  6), ('D',  1), ('C',  1), ('D',  4), ('E',  4), ('z', 4)]
            ]
        , cf =
            [ [('A,', 8), ('B,', 8), ('C',  8)]
            ]
        )
    , hypoionian = dict
        ( cp = 
            [ [('E',  8), ('D',  8), ('C',  8)]
            ]
        , cf =
            [ [('C',  6), ('B,', 1), ('A,', 1), ('B,', 4), ('A,', 4), ('z', 4)]
            ]
        )
    , dorian = dict
        ( cp =
            [ [('E',  4), ('F',  6), ('E',  1), ('D', 1), ('E', 4), ('F', 4)
              , ('z', 4)
              ]
            ]
        , cf =
            [ [('A,', 8), ('C',  8), ('D',  8)]
            ]
        )
    )

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
