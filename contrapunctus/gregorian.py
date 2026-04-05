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

from .tune import Tone, halftone, Key, Bar, Pause

class End_Sequence:

    def __init__ (self, sequence):
        self.sequence = tuple ((self.halftone (a), b) for a, b in sequence)
        self.len = sum (k [1] for k in self.sequence)
    # end def __init__

    def __getitem__ (self, idx):
        return self.sequence [idx]
    # end def __getitem__

    def __iter__ (self):
        return iter (self.sequence)
    # end def __iter__

    def __len__ (self):
        return self.len
    # end def __len__

    def __str__ (self):
        return str (list ((str (a), b) for a, b in self.sequence))
    # end def __str__

    @classmethod
    def halftone (cls, x):
        """ Use normal halftone if x != 'z', else 'z'
        """
        if x == 'z':
            return x
        return halftone (x)
    # end def halftone

    def transpose (self, key1, key2):
        """ Transpose from key1 to key2
        """
        offset = key1.transpose_offset (key2)
        return self.__class__ \
            ((a.transpose (offset), b) for a, b in self.sequence)
    # end def transpose

    def append_end_sequence (self, voice):
        last_bar = voice.bars [-1]
        assert last_bar.unit == 8
        dur = last_bar.duration
        assert dur in (8, 16)
        last_obj = last_bar.objects [-1]
        assert not last_obj.bind
        remain   = dur - (last_obj.offset + last_obj.duration)
        assert len (self) % dur == remain % dur
        voice.end_seq_duration = len (self)
        for ht, l in self:
            if remain == 0:
                remain = dur
                voice.add (Bar (dur, 8))
                last_bar = voice.bars [-1]
            l1 = min (l, remain)
            l2 = l - l1
            if ht == 'z':
                bo = Pause (l1)
            else:
                bo = Tone (ht, l1)
                if l2:
                    bo.bind = True
            last_bar.add (bo)
            remain -= l1
            if l2:
                assert remain == 0
                remain = dur
                voice.add (Bar (dur, 8))
                last_bar = voice.bars [-1]
                if ht == 'z':
                    bo = Pause (l2)
                else:
                    bo = Tone (ht, l2)
                last_bar.add (bo)
                remain -= l2
        # Last bar must be full
        lastobj = last_bar.objects [-1]
        assert lastobj.offset + lastobj.duration == dur
    # end def append_end_sequence

# end class End_Sequence
ES = End_Sequence

class Mode_End_Sequences:

    def __init__ (self, modename, cf, cp):
        self.cp       = cp
        self.cf       = cf
        self.modename = modename
        assert len (cp) == len (cf)
        if len (cp) == 0:
            self.min_cf_len = self.max_cf_len = 0
            self.min_cp_len = self.max_cp_len = 0
        else:
            self.min_cf_len = min (len (x) for x in self.cf)
            self.max_cf_len = max (len (x) for x in self.cf)
            self.min_cp_len = min (len (x) for x in self.cp)
            self.max_cp_len = max (len (x) for x in self.cp)
    # end def __init__

    def __len__ (self):
        return len (self.cp)
    # end def __len__

    def append_end_sequence (self, voice, sq_idx = 0):
        """ Append the correct end sequence to the given voice
            We use voice.id for determining if this is cf or cp.
        """
        if voice.id == 'CantusFirmus':
            sq = self.cf [sq_idx]
        else:
            sq = self.cp [sq_idx]
        sq.append_end_sequence (voice)
    # end def append_end_sequence

    def transpose (self, other_modename):
        frm = Key.byname (self.modename)
        to  = Key.byname (other_modename)
        result = {}
        for v in 'cp', 'cf':
            voice = getattr (self, v)
            result [v] = []
            for es in voice:
                result [v].append (es.transpose (frm, to))
        return self.__class__ (other_modename, **result)
    # end def transpose

# end class Mode_End_Sequences

# These assume L:1/8, each end sequence consists of cp, cf in a separate
# dictionary -- these must match by length, the first cp entry belongs
# to the first cf entry, etc. Note that they need not have the same
# length, the rest of the framework can generate tones where undefined.

end_sequences = dict \
    ( dorian =  Mode_End_Sequences
        ( 'dorian'
        , cp =
            [ ES ([('d',  8), ('^c', 4), ('d',  8)])
            , ES ([('d',  6), ('^c', 2), ('c',  2), ('B', 2), ('d', 8)])
            , ES ([('d',  6), ('B',  2), ('^c', 4), ('d', 8)])
            , ES ([('d',  6), ('^c', 2), ('c',  4), ('d', 8)])
            , ES ([('d',  6), ('^c', 1), ('B',  1), ('c', 4), ('d', 8)])
            , ES ([('^c', 4), ('d',  8)])
            , ES ([('c',  4), ('A',  4), ('d',  8)])
            ]
        , cf =
            [ ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('E',  8), ('D',  8)])
            , ES ([('E',  8), ('D',  8)])
            ]
        )
    , phrygian = Mode_End_Sequences
        ( 'phrygian'
        , cp =
            [ ES ([('F', 8), ('E', 8)])
            , ES ([('B', 4), ('e', 8), ('d', 4), ('e', 8)])
            , ES ([('B', 4), ('e', 6), ('d', 2), ('d', 2), ('c', 2), ('e', 8)])
            , ES ([('B', 4), ('e', 6), ('c', 2), ('d', 4), ('e', 8)])
            , ES ([('B', 4), ('e', 6), ('d', 2), ('d', 4), ('e', 8)])
            , ES ([('B', 4), ('e', 6), ('d', 1), ('c', 1), ('d', 4), ('e', 8)])
            , ES ([('F', 2), ('G', 2), ('F', 4), ('E', 8)])
            , ES ([('F', 8), ('E', 8)])
            ]
        , cf =
            [ ES ([('D', 8), ('E', 8)])
            , ES ([('G', 8), ('F', 8), ('E', 8)])
            , ES ([('G', 8), ('F', 8), ('E', 8)])
            , ES ([('G', 8), ('F', 8), ('E', 8)])
            , ES ([('G', 8), ('F', 8), ('E', 8)])
            , ES ([('G', 8), ('F', 8), ('E', 8)])
            , ES ([('D', 8), ('E', 8)])
            , ES ([('D', 8), ('E', 8)])
            ]
        )
    , ionian = Mode_End_Sequences
        ( 'ionian'
        , cp =
            [ ES ([('c', 8), ('B', 4), ('c', 8)])
            , ES ([('c', 6), ('B', 2), ('B', 2), ('A', 2), ('c', 8)])
            , ES ([('c', 6), ('A', 2), ('B', 4), ('c', 8)])
            , ES ([('c', 6), ('B', 2), ('B', 4), ('c', 8)])
            , ES ([('c', 6), ('B', 1), ('A', 1), ('B', 4), ('c', 8)])
            # quintfallend:
            , ES ([('c', 8), ('c', 8)])
            , ES ([('G', 8), ('C', 8)])
            ]
        , cf =
            [ ES ([('E', 8), ('D', 8), ('C', 8)])
            , ES ([('E', 8), ('D', 8), ('C', 8)])
            , ES ([('E', 8), ('D', 8), ('C', 8)])
            , ES ([('E', 8), ('D', 8), ('C', 8)])
            , ES ([('E', 8), ('D', 8), ('C', 8)])
            # quintfallend:
            , ES ([('G', 8), ('C', 8)])
            , ES ([('C', 8), ('C', 8)])
            ]
        )
    , hypodorian = Mode_End_Sequences
        ( 'hypodorian'
        , cf =
            [ ES ([('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('F',  8), ('E',  8), ('D',  8)])
            , ES ([('E',  8), ('D',  8)])
            ]
        , cp =
            [ ES ([('C',  4), ('A,', 4), ('D',  8)])
            , ES ([('D',  8), ('^C', 4), ('D',  8)])
            , ES ([('D',  6), ('^C', 2), ('C',  2), ('B', 2), ('D', 8)])
            , ES ([('D',  6), ('B',  2), ('^C', 4), ('D', 8)])
            , ES ([('D',  6), ('^C', 2), ('C',  4), ('D', 8)])
            , ES ([('D',  6), ('^C', 1), ('B,', 1), ('C', 4), ('D', 8)])
            , ES ([('^C', 4), ('D',  8)])
            ]
        )
    , hypophrygian = Mode_End_Sequences
        ( 'hypophrygian'
        , cf =
            [ ES ([('G',  8), ('F', 8), ('E', 8)])
            , ES ([('G',  8), ('F', 8), ('E', 8)])
            , ES ([('G',  8), ('F', 8), ('E', 8)])
            , ES ([('G',  8), ('F', 8), ('E', 8)])
            , ES ([('G',  8), ('F', 8), ('E', 8)])
            , ES ([('D',  8), ('E', 8)])
            , ES ([('D',  8), ('E', 8)])
            ]
        , cp =
            [ ES ([('B,', 4), ('E', 8), ('D', 4), ('E', 8)])
            , ES ([('B,', 4), ('E', 6), ('D', 2), ('D', 2), ('C', 2), ('E', 8)])
            , ES ([('B,', 4), ('E', 6), ('C', 2), ('D', 4), ('E', 8)])
            , ES ([('B,', 4), ('E', 6), ('D', 2), ('D', 4), ('E', 8)])
            , ES ([('B,', 4), ('E', 6), ('D', 1), ('C', 1), ('D', 4), ('E', 8)])
            , ES ([('F',  2), ('G', 2), ('F', 4), ('E', 8)])
            , ES ([('F',  8), ('E', 8)])
            ]
        )
    , hypoionian = Mode_End_Sequences
        ( 'hypoionian'
        , cf =
            [ ES ([('E', 8), ('D',  8), ('C',  8)])
            , ES ([('E', 8), ('D',  8), ('C',  8)])
            , ES ([('E', 8), ('D',  8), ('C',  8)])
            , ES ([('E', 8), ('D',  8), ('C',  8)])
            , ES ([('E', 8), ('D',  8), ('C',  8)])
            ]
        , cp =
            [ ES ([('C', 8), ('B,', 4), ('C',  8)])
            , ES ([('C', 6), ('B,', 2), ('B,', 2), ('A,', 2), ('C', 8)])
            , ES ([('C', 6), ('A,', 2), ('B,', 4), ('C',  8)])
            , ES ([('C', 6), ('B,', 2), ('B,', 4), ('C',  8)])
            , ES ([('C', 6), ('B,', 1), ('A,', 1), ('B,', 4), ('C', 8)])
            ]
        )
    )
# We currently do not have end-sequences for locrian and hypolocrian
end_sequences ['locrian'] = Mode_End_Sequences ('locrian', [], [])
end_sequences ['hypolocrian'] = Mode_End_Sequences ('hypolocrian', [], [])

# mixolydian and aeolian end-sequences are re-used from dorian
# lydian end-sequence is re-used from ionian
# Same for the hypo variants
for k, lst in (('dorian', ('mixolydian', 'aeolian')), ('ionian', ('lydian',))):
    hk = 'hypo' + k
    for name in lst:
        hname = 'hypo' + name
        end_sequences [name]  = end_sequences [k].transpose (name)
        end_sequences [hname] = end_sequences [hk].transpose (hname)
# Common aliases
end_sequences ['major'] = end_sequences ['ionian']
end_sequences ['minor'] = end_sequences ['aeolian']

intermediate_sequences = dict \
    ( ionian = Mode_End_Sequences
        ( 'ionian'
        , cp =
            [ ES ([ ('E',  6), ('D',  1), ('C',  1), ('D',  4)
                  , ('E', 4), ('z', 4)
                  ])
            ]
        , cf =
            [ ES ([('A,', 8), ('B,', 8), ('C',  8)])
            ]
        )
    , hypoionian = Mode_End_Sequences
        ( 'hypoionian'
        , cf =
            [ ES ([('E',  8), ('D',  8), ('C',  8)])
            ]
        , cp =
            [ ES ([ ('C',  6), ('B,', 1), ('A,', 1), ('B,', 4)
                  , ('A,', 4), ('z', 4)
                  ])
            ]
        )
    , dorian = Mode_End_Sequences
        ( 'dorian'
        , cp =
            [ ES ([ ('E',  4), ('F',  6), ('E',  1), ('D', 1), ('E', 4)
                  , ('F', 4), ('z', 4)
                  ])
            ]
        , cf =
            [ ES ([('A,', 8), ('C',  8), ('D',  8)])
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
    >>> print (type (dorian.es))
    <class 'contrapunctus.gregorian.Mode_End_Sequences'>
    >>> print (type (mixolydian.es))
    <class 'contrapunctus.gregorian.Mode_End_Sequences'>
    >>> modes = [mixolydian, aeolian, lydian]
    >>> for g in modes:
    ...     print ("Mode: %s" % g.mode)
    ...     for voice in ('cp', 'cf'):
    ...         print ('Voice: %s' % voice)
    ...         for sq in getattr (g.es, voice):
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
    >>> modes = [hypomixolydian, hypoaeolian, hypolydian]
    >>> for g in modes:
    ...     print ("Mode: %s" % g.mode)
    ...     for voice in ('cf', 'cp'):
    ...         print ('Voice: %s' % voice)
    ...         for sq in getattr (g.es, voice):
    ...             print (str (sq))
    Mode: hypomixolydian
    Voice: cf
    [('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('_B', 8), ('A', 8), ('G', 8)]
    [('A', 8), ('G', 8)]
    Voice: cp
    [('F', 4), ('D', 4), ('G', 8)]
    [('G', 8), ('^F', 4), ('G', 8)]
    [('G', 6), ('^F', 2), ('F', 2), ('e', 2), ('G', 8)]
    [('G', 6), ('e', 2), ('^F', 4), ('G', 8)]
    [('G', 6), ('^F', 2), ('F', 4), ('G', 8)]
    [('G', 6), ('^F', 1), ('E', 1), ('F', 4), ('G', 8)]
    [('^F', 4), ('G', 8)]
    Mode: hypoaeolian
    Voice: cf
    [('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('c', 8), ('B', 8), ('A', 8)]
    [('B', 8), ('A', 8)]
    Voice: cp
    [('G', 4), ('E', 4), ('A', 8)]
    [('A', 8), ('^G', 4), ('A', 8)]
    [('A', 6), ('^G', 2), ('G', 2), ('^f', 2), ('A', 8)]
    [('A', 6), ('^f', 2), ('^G', 4), ('A', 8)]
    [('A', 6), ('^G', 2), ('G', 4), ('A', 8)]
    [('A', 6), ('^G', 1), ('^F', 1), ('G', 4), ('A', 8)]
    [('^G', 4), ('A', 8)]
    Mode: hypolydian
    Voice: cf
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    [('A', 8), ('G', 8), ('F', 8)]
    Voice: cp
    [('F', 8), ('E', 4), ('F', 8)]
    [('F', 6), ('E', 2), ('E', 2), ('D', 2), ('F', 8)]
    [('F', 6), ('D', 2), ('E', 4), ('F', 8)]
    [('F', 6), ('E', 2), ('E', 4), ('F', 8)]
    [('F', 6), ('E', 1), ('D', 1), ('E', 4), ('F', 8)]
    """

    end_sequences          = end_sequences
    intermediate_sequences = intermediate_sequences

    def __init__ (self, ambitus, key, offset = 0):
        assert len (ambitus) == 7
        self.ambitus = [halftone (x) for x in ambitus]
        self.key     = Key.get (key)
        self.offset  = offset
        self.mode    = self.key.mode
        self.omode   = 'hypo' + self.mode
        if self.offset:
            assert self.offset == -3
            self.omode = self.mode
            self.mode  = 'hypo' + self.mode
        self.es      = self.end_sequences [self.mode]
    # end def __init__

    @property
    def finalis (self):
        return self.ambitus [0]
    # end def finalis

    @property
    def other (self):
        return getattr (self.__class__, self.omode)
    # end def other

    @property
    def step2 (self):
        return self.ambitus [1]
    # end def step2

    @property
    def subsemitonium (self):
        """ Leading tone, German: Leitton
        """
        return self [7].transpose (-1)
    # end def subsemitonium

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

    def mode_end_sequences (self, parent, bar_duration):
        """ The length of the second tone depends on parent.rhythm
            The second tone has the length of rhythm.bar_duration.
            When parent has set randomize_end_sequence we return
            self.es, otherwise we compute the default es.
        """
        if getattr (self, 'mes', None):
            return self.mes
        if parent.args.randomize_end_sequence and len (self.es):
            self.mes = self.es
            return self.mes
        l = bar_duration
        e = Mode_End_Sequences \
            ( self.mode
            , cf =
                [ ES ([ (str (self.other.step2),   8)
                      , (str (self.other.finalis), l)
                      ])
                ]
            , cp =
                [ ES ([ (str (self.subsemitonium), 8)
                      , (str (self [7]),           l)
                      ])
                ]
            )
        self.mes = e
        return self.mes
    # end def mode_end_sequences

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

Gregorian.ionian       = ionian
Gregorian.hypoionian   = hypoionian
Gregorian.dorian       = dorian
Gregorian.hypodorian   = hypodorian
Gregorian.phrygian     = phrygian
Gregorian.hypophrygian = hypophrygian
Gregorian.lydian       = lydian
Gregorian.hypolydian   = hypolydian
Gregorian.aeolian      = aeolian
Gregorian.hypoaeolian  = hypoaeolian
Gregorian.locrian      = locrian
Gregorian.hypolocrian  = hypolocrian

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
