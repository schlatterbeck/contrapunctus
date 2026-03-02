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

from .tune import Tone, halftone, Key

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
# We currently do not have end-sequences for locrian and hypolocrian
end_sequences ['locrian'] = dict (cp = [], cf = [])
end_sequences ['hypolocrian'] = end_sequences ['locrian']

# mixolydian and aeolian end-sequences are re-used from dorian
# lydian end-sequence is re-used from ionian
# Same for the hypo variants
for k, lst in (('dorian', ('mixolydian', 'aeolian')), ('ionian', ('lydian',))):
    for name in lst:
        frm = Key.get (getattr (Key, k)[7])
        offset = frm.transpose_offset (Key.get (getattr (Key, name)[7]))
        end_sequences [name]          = dict (cp = [], cf = [])
        end_sequences ['hypo' + name] = dict (cp = [], cf = [])
        for voice in ('cp', 'cf'):
            for sq in end_sequences [k][voice]:
                end_sequences [name][voice].append ([])
                t_sq = end_sequences [name][voice][-1]
                for ht, l in sq:
                    t_ht = halftone (ht).transpose (offset)
                    t_sq.append ((str (t_ht), l))
            for sq in end_sequences ['hypo' + k][voice]:
                end_sequences ['hypo' + name][voice].append ([])
                t_sq = end_sequences ['hypo' + name][voice][-1]
                for ht, l in sq:
                    t_ht = halftone (ht).transpose (offset)
                    t_sq.append ((str (t_ht), l))
# Common aliases
end_sequences ['major'] = end_sequences ['ionian']
end_sequences ['minor'] = end_sequences ['aeolian']

intermediate_sequences = dict \
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
    >>> for g in mixolydian, aeolian, lydian:
    ...     print ("Mode: %s" % g.mode)
    ...     for voice in ('cp', 'cf'):
    ...         print ('Voice: %s' % voice)
    ...         for sq in g.es [voice]:
    ...             print (str (sq))
    Mode: mixolydian
    Voice: cp
    [('g', 8), ('^f', 4), ('g', 8)]
    [('g', 6), ('^f', 2), ('f', 2), ('e', 2), ('g', 8)]
    [('g', 6), ('e', 2), ('^f', 4), ('g', 8)]
    [('g', 6), ('^f', 2), ('f', 4), ('g', 8)]
    [('g', 6), ('^f', 1), ('e', 1), ('f', 4), ('g', 8)]
    [('^f', 4), ('g', 8)]
    [('f', 4), ('d', 4), ('g', 8)]
    Voice: cf
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('A', 8), ('G', 8)]
    [('A', 8), ('G', 8)]
    Mode: aeolian
    Voice: cp
    [('a', 8), ('^g', 4), ('a', 8)]
    [('a', 6), ('^g', 2), ('g', 2), ('^f', 2), ('a', 8)]
    [('a', 6), ('^f', 2), ('^g', 4), ('a', 8)]
    [('a', 6), ('^g', 2), ('g', 4), ('a', 8)]
    [('a', 6), ('^g', 1), ('^f', 1), ('g', 4), ('a', 8)]
    [('^g', 4), ('a', 8)]
    [('g', 4), ('e', 4), ('a', 8)]
    Voice: cf
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('B', 8), ('A', 8)]
    [('B', 8), ('A', 8)]
    Mode: lydian
    Voice: cp
    [('f', 8), ('e', 4), ('f', 8)]
    [('f', 6), ('e', 2), ('e', 2), ('d', 2), ('f', 8)]
    [('f', 6), ('d', 2), ('e', 4), ('f', 8)]
    [('f', 6), ('e', 2), ('e', 4), ('f', 8)]
    [('f', 6), ('e', 1), ('d', 1), ('e', 4), ('f', 8)]
    [('f', 8), ('f', 8)]
    [('c', 8), ('F', 8)]
    Voice: cf
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('c', 8), ('F', 8)]
    [('F', 8), ('F', 8)]
    """

    end_sequences          = end_sequences
    intermediate_sequences = intermediate_sequences

    def __init__ (self, ambitus, key, offset = 0):
        assert len (ambitus) == 7
        self.ambitus = [halftone (x) for x in ambitus]
        self.key     = Key.get (key)
        self.offset  = offset
        self.mode    = self.key.mode
        self.es      = self.end_sequences [self.mode]
        assert len (self.es ['cp']) == len (self.es ['cf'])
        self.eslen   = len (self.es ['cp'])
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

    def transpose (self, key, halftone):
        """ Transpose a halftone to another key
        """
        offset = self.key.transpose_offset (key)
        return halftone.transpose (offset)
    # end def transpose

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
