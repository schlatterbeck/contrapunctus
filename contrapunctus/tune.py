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

from bisect import bisect_right
from functools import cached_property
from fractions import Fraction

def sgn (i):
    if i > 0:
        return 1
    if i < 0:
        return -1
    return 0
# end def sgn

def transpose_steps_to_fifth (steps):
    """ Determine by how many fifth to transpose to reach the given
        number of halftone-steps.
        Note that a fifth has 7 halftones and the multiplicative
        inverse of 7 mod 12 is again 7:
        7 * 7 = 49 -> mod 12 -> 1
        So to divide by 7 mod 12 we can multiply by 7.
        transpose_steps_to_fifth (1)
        -5
        transpose_steps_to_fifth (-1)
        5
        transpose_steps_to_fifth (7)
        1
        transpose_steps_to_fifth (-2)
        -2
    """
    nfifth = (7 * steps) % 12
    if nfifth > 6:
        nfifth = nfifth - 12
    assert (nfifth * 7 - steps) % 12 == 0
    return nfifth
# end def transpose_steps_to_fifth

class Halftone:
    """ Model a halftone with abc notation
        We have a table of the first two octaves and extrapolate the
        rest.
    >>> h = Halftone ('_C')
    >>> h.offset
    -10
    >>> h = Halftone ('_C,')
    >>> h.offset
    -22
    >>> h = Halftone ('_C,,')
    >>> h.offset
    -34
    >>> h = Halftone ('^c')
    >>> h.offset
    4
    >>> h = Halftone ("^c'")
    >>> h.offset
    16
    >>> h = Halftone ("^c''")
    >>> h.offset
    28
    >>> Halftone ("C")
    C
    """
    sym_intervals = \
        ( ('_C', -10), ('C', -9), ('^C', -8)
        , ('_D',  -8), ('D', -7), ('^D', -6)
        , ('_E',  -6), ('E', -5), ('^E', -4)
        , ('_F',  -5), ('F', -4), ('^F', -3)
        , ('_G',  -3), ('G', -2), ('^G', -1)
        , ('_A',  -1), ('A',  0), ('^A',  1)
        , ('_B',   1), ('B',  2), ('^B',  3)
        , ('_c',   2), ('c',  3), ('^c',  4)
        , ('_d',   4), ('d',  5), ('^d',  6)
        , ('_e',   6), ('e',  7), ('^e',  8)
        , ('_f',   7), ('f',  8), ('^f',  9)
        , ('_g',   9), ('g', 10), ('^g', 11)
        , ('_a',  11), ('a', 12), ('^a', 13)
        , ('_b',  13), ('b', 14), ('^b', 15)
        )
    symbols = dict (sym_intervals)
    symlist = [x [0] for x in sym_intervals]
    # standard_pitch has halftone offset 0
    standard_pitch = 'A'

    enharmonics = \
        { '^B,' : 'C'
        , '^C'  : '_D'
        , '_C'  : 'B,'
        , '^D'  : '_E'
        , '^E'  : 'F'
        , '_F'  : 'E'
        , '^F'  : '_G'
        , '^G'  : '_A'
        , '^A'  : '_B'
        , '^B'  : 'c'
        , '_c'  : 'B'
        }
    # Add Reverse mappings
    enharmonics.update \
        ((v, k) for k, v in list (enharmonics.items ()) if v [0] in '^_')

    fifth_up = dict \
        (( ( 'C',   'G')
         , ('^C',  '^G')
         , ( 'D',   'A')
         , ('^D',  '^A')
         , ( 'E',   'B')
         , ( 'F',   'c')
         , ('^F',  '^c')
         , ('_G',  '_d')
         , ( 'G',   'd')
         , ('^G',  '^d')
         , ( 'A',   'e')
         , ('^A',  '^e')
         , ( 'B',  '^f')
         , ( 'c',   'g')
         , ('^c',  '^g')
         , ( 'd',   'a')
         , ('^d',  '^a')
         , ( 'e',   'b')
         , ( 'f',   "c'")
         , ('^f',  "^c'")
         , ('_g',  "_d'")
         , ( 'g',   "d'")
         , ('^g',  "^d'")
         , ( 'a',   "e'")
         , ('^a',  "^e'")
         , ( 'b',  "^f'")
        ))
    fifth_up_inv = dict \
        ((v, k) for k, v in fifth_up.items () if not v.startswith ('_'))
    fifth_down = dict \
        (( ( 'C',   'F,')
         , ('_D',  '_G,')
         , ( 'D',   'G,')
         , ('_E',  '_A,')
         , ( 'E',   'A,')
         , ( 'F',  '_B,')
         , ('^F',   'B,')
         , ('_G',  '_C')
         , ( 'G',   'C')
         , ('_A',  '_D')
         , ( 'A',   'D')
         , ('_B',  '_E')
         , ( 'B',   'E')
         , ( 'c',   'F')
         , ( 'd',   'G')
         , ('_d',  '_G')
         , ( 'e',   'A')
         , ('_e',  '_A')
         , ( 'f',  '_B')
         , ('^f',   'b')
         , ('_g',  '_c')
         , ( 'g',   'c')
         , ('_a',  '_d')
         , ( 'a',   'd')
         , ('_b',  '_e')
         , ( 'b',   'e')
        ))
    fifth_down_inv = dict \
        ((v, k) for k, v in fifth_down.items () if not v.startswith ('^'))

    reg = {}

    def register (self):
        self.reg [self.name] = self
    # end def register

    def __init__ (self, name):
        tr = 0
        ln = name
        while ln.endswith (','):
            ln = ln [:-1]
            tr = tr - 12
        assert not ln.endswith ("'") or tr == 0
        while ln.endswith ("'"):
            ln = ln [:-1]
            tr = tr + 12
        self.offset = self.symbols [ln] + tr
        self.name   = name
        self.register ()
    # end def __init__

    def __str__ (self):
        return self.name
    # end def __str__
    __repr__ = __str__

    @classmethod
    def get (cls, name):
        """ Implement sort-of singleton
        """
        if name in cls.reg:
            return cls.reg [name]
        return cls (name)
    # end def get

    @property
    def prefix (self):
        """ Optional prefix ^ or _
        """
        n = self.name
        if n.startswith ('^') or n.startswith ('_'):
            return n [0]
        return ''
    # end def prefix

    @property
    def stem (self):
        """ The tone without the (optional) prefix and without trailing
            comma or primes.
        >>> halftone ('a').stem
        'a'
        >>> halftone ('^a').stem
        'a'
        >>> halftone ('^A,,,,').stem
        'A'
        >>> halftone ('_a').stem
        'a'
        >>> halftone ('F').as_abc (Key.get ('G'))
        '=F'
        >>> halftone ('_F').as_abc (Key.get ('G'))
        '_F'
        """
        if self.prefix:
            return self.name [1]
        return self.name [0]
    # end def stem

    def as_abc (self, key = None):
        if key is None:
            return self.name
        ustem = self.stem.upper ()
        if ustem in key.accidentals:
            prefix = key.accidentals [ustem]
            if self.prefix == prefix:
                return self.name [1:]
            elif not self.prefix:
                return '=' + self.name
            else:
                return self.name
        else:
            return self.name
    # end def as_abc

    def enharmonic_equivalent (self):
        """ We return the enharmonic equivalent of the current Halftone.
            Note that we only do this for tones with a flat or sharp
            mark and we consider only single marks.
        >>> halftone ('^b').enharmonic_equivalent ()
        c'
        >>> halftone ('^B').enharmonic_equivalent ()
        c
        >>> halftone ('^e').enharmonic_equivalent ()
        f
        >>> halftone ('^E').enharmonic_equivalent ()
        F
        >>> halftone ('^a').enharmonic_equivalent ()
        _b
        >>> halftone ('^A').enharmonic_equivalent ()
        _B
        >>> halftone ('^d').enharmonic_equivalent ()
        _e
        >>> halftone ('^D').enharmonic_equivalent ()
        _E
        >>> halftone ('^g').enharmonic_equivalent ()
        _a
        >>> halftone ('^G').enharmonic_equivalent ()
        _A
        >>> halftone ('^C').enharmonic_equivalent ()
        _D
        >>> halftone ('^C,,').enharmonic_equivalent ()
        _D,,
        >>> halftone ('^c').enharmonic_equivalent ()
        _d
        >>> halftone ('^f').enharmonic_equivalent ()
        _g
        >>> halftone ('^F').enharmonic_equivalent ()
        _G
        >>> halftone ('_f').enharmonic_equivalent ()
        e
        >>> halftone ('_F').enharmonic_equivalent ()
        E
        >>> halftone ('_c').enharmonic_equivalent ()
        B
        >>> halftone ('_C').enharmonic_equivalent ()
        B,
        >>> halftone ('_g').enharmonic_equivalent ()
        ^f
        >>> halftone ('_G').enharmonic_equivalent ()
        ^F
        >>> halftone ('_d').enharmonic_equivalent ()
        ^c
        >>> halftone ('_D').enharmonic_equivalent ()
        ^C
        >>> halftone ('_a').enharmonic_equivalent ()
        ^g
        >>> halftone ('_A').enharmonic_equivalent ()
        ^G
        >>> halftone ('_e').enharmonic_equivalent ()
        ^d
        >>> halftone ('_E').enharmonic_equivalent ()
        ^D
        >>> halftone ('_b').enharmonic_equivalent ()
        ^a
        >>> halftone ('_B').enharmonic_equivalent ()
        ^A
        >>> halftone ('B').enharmonic_equivalent ()
        B
        """
        name = self.name
        if not name.startswith ('^') and not name.startswith ('_'):
            return self
        if name in self.enharmonics:
            return self.get (self.enharmonics [name])
        oct, off = divmod (self.offset, 12)
        while off > 2:
            off -= 12
            oct += 1
        assert -10 <= off <= 2
        tr = self.transpose_octaves (-oct)
        assert tr.name in self.enharmonics
        return tr.enharmonic_equivalent ().transpose_octaves (oct)
    # end def enharmonic_equivalent

    def transpose_fifth (self, fifth = 1, key = 'C'):
        """ Transpose by fifth (up or down).
            Positive means up, negative down.
            Note that the key is used internally for determining when we
            need the enharmonic equivalent. Also note that we don't
            output keys with more than 6 flats or 6 sharps. These are
            using the enharmonic equivalent. For input we accept keys
            with a maximum of 7 flats or sharps.
        >>> h = halftone ('C')
        >>> h.transpose_fifth (0)
        C
        >>> h.transpose_fifth ()
        G

        >>> for i in range (12):
        ...     h.transpose_fifth (i, 'C')
        C
        G
        d
        a
        e'
        b'
        ^f''
        _d'''
        _a'''
        _e''''
        _b''''
        f'''''

        >>> for i in range (12):
        ...     h.transpose_fifth (-i , 'C')
        C
        F,
        _B,,
        _E,,
        _A,,,
        _D,,,
        _G,,,,
        B,,,,,
        E,,,,,
        A,,,,,,
        D,,,,,,
        G,,,,,,,
        """
        ht   = self
        oct  = 0
        key  = Key.get (key)
        while fifth:
            if key.offset >= 6 and fifth > 0 or key.offset <= -6 and fifth < 0:
                ht = ht.enharmonic_equivalent ()
            if "," in ht.name or "'" in ht.name or ht.offset > 3:
                oc, off = divmod (ht.offset, 12)
                oct += oc
                ht = ht.transpose_octaves (-oc)
                if ht.offset > 8:
                    ht = ht.transpose_octaves (-1)
                    oct += 1
            lt  = [self.fifth_up, self.fifth_down]        [fifth < 0]
            lti = [self.fifth_down_inv, self.fifth_up_inv][fifth < 0]
            n   = lt.get (ht.name)
            if not n:
                n = lti.get (ht.name)
            assert n
            ht  = halftone (n)
            key = key.transpose (sgn (fifth))
            fifth -= sgn (fifth)
        return ht.transpose_octaves (oct)
    # end def transpose_fifth

    def transpose_octaves (self, octaves = 1):
        """ Transpose given tune by given number of octaves.
            Positive means up, negative down.
        >>> h = halftone ('^C')
        >>> h.transpose_octaves ()
        ^c
        >>> h.transpose_octaves (1).transpose_octaves (-1)
        ^C
        >>> h.transpose_octaves (-1).transpose_octaves (1)
        ^C
        >>> h.transpose_octaves (2)
        ^c'
        >>> h.transpose_octaves (-2)
        ^C,,
        >>> h.transpose_octaves (-2).transpose_octaves (2)
        ^C
        >>> h.transpose_octaves (2).transpose_octaves (-2)
        ^C
        """
        n = self.name
        if octaves > 0:
            for i in range (octaves):
                if n.endswith (","):
                    n = n [:-1]
                elif n.lower () != n:
                    n = n.lower ()
                else:
                    n = n + "'"
        elif octaves < 0:
            for i in range (abs (octaves)):
                if n.endswith ("'"):
                    n = n [:-1]
                elif n.upper () != n:
                    n = n.upper ()
                else:
                    n = n + ","
        return self.get (n)
    # end def transpose_octaves

    def transpose (self, steps, key = 'C'):
        """ Transpose by given number of halftone steps.
            Positive is up.
            We determine the number of fifth to transpose and decide how
            many octaves we must use to compensate.
            We use this complicated method of transposing by fifth to
            keep the correct enharmonic equivalence. When transposing
            up, sharps are preferred while when transposing down, flats
            are preferred.
        >>> Halftone ("C").transpose (-1)
        B,
        >>> Halftone ("c").transpose (-1)
        B
        >>> Halftone ("c").transpose (-2)
        _B
        >>> Halftone ("C,,,").transpose (-1)
        B,,,,
        >>> Halftone ("c'''").transpose (-1)
        b''
        >>> Halftone ("c").transpose (1)
        _d
        >>> Halftone ("C").transpose (6)
        ^F
        >>> Halftone ("c").transpose (-6)
        _G
        >>> Halftone ("E").transpose (2)
        ^F
        >>> Halftone ("_A").transpose (-2)
        _G
        """
        key = Key.get (key)
        nfifth = transpose_steps_to_fifth (steps)
        oct  = - (nfifth * 7 - steps) // 12
        ht   = self.transpose_octaves (oct)
        ht   = ht.transpose_fifth (nfifth, key)
        offs = key.transpose (nfifth).offset
        if offs == 6 and steps < 0:
            ht = ht.enharmonic_equivalent ()
        return ht
    # end def transpose

# end class Halftone

def halftone (tone):
    """ Return singleton tone """
    if isinstance (tone, Halftone):
        return tone
    return Halftone.get (tone)
# end def halftone

class Bar_Object:
    """ Base class of all objects that go into a Bar
    """

    def __init__ (self, duration):
        super ().__init__ ()
        assert duration == int (duration)
        self.duration = int (duration)
        # offset in Bar (parent), filled when inserting into Bar
        self.offset   = None
        # Index into Bar (parent)
        self.idx      = None
        self.bar      = None
        self._prev    = None
        self._next    = None
    # end def __init__

    @classmethod
    def from_string (cls, accidentals, s):
        if s.startswith ('z'):
            return Pause.from_string (s)
        return Tone.from_string (accidentals, s)
    # end def from_string

    def __str__ (self):
        name = self.__class__.__name__
        return \
            ( '%s (bar=%s, idx=%s, offset=%s, dur=%s)'
            % (name, self.bar, self.idx, self.offset, self.duration)
            )
    # end def __str__
    __repr__ = __str__

    @property
    def abslen (self):
        try:
            unit = self.bar.voice.tune.unit
        except AttributeError:
            return None
        return len (self) / unit
    # end def abslen

    @property
    def next (self):
        if self.bar.objects [-1] is self:
            # An empty next bar may exist during testing/searching
            if self.bar.next is None or not self.bar.next.objects:
                return None
            return self.bar.next.objects [0]
        else:
            return self._next
    # end def next

    @property
    def prev (self):
        if self.offset == 0:
            # An empty prev bar may exist during testing/searching
            if self.bar.prev is None or not self.bar.prev.objects:
                return None
            return self.bar.prev.objects [-1]
        else:
            return self._prev
    # end def prev

    @property
    def is_first (self):
        if self.prev is None and self.bar.idx == 0:
            return True
        return False
    # end def is_first

    @property
    def is_last (self):
        l = len (self.bar.voice.bars)
        if self.next is None and self.bar.idx == l - 1:
            return True
        return False
    # end def is_last

    @property
    def is_pause (self):
        return isinstance (self, Pause)
    # end def is_pause

    def copy (self):
        return self.__class__ (self.duration)
    # end def copy

    def length (self):
        assert isinstance (self.duration, int)
        return self.duration
    # end def length
    __len__ = length

    def register (self, bar, offset, idx):
        assert self.offset is None
        assert self.idx    is None
        assert self.bar    is None
        self.bar    = bar
        self.offset = offset
        self.idx    = idx
    # end def register

    def transpose (self, steps, key = 'C'):
        return self.copy ()
    # end def transpose

# end class Bar_Object

class Tone (Bar_Object):

    def __init__ (self, halftone, duration, bind = False):
        self.halftone = halftone
        self.bind     = bind # bind to next tone
        super ().__init__ (duration)
    # end def __init__

    @classmethod
    def from_string (cls, accidentals, s):
        assert s
        n = None
        bind = False
        if s [-1] == '-':
            bind = True
            s = s [:-1]
        for n, x in enumerate (reversed (s)):
            if not x.isdigit ():
                break
        if n:
            dur = int (s [-n:])
            ht  = s [:-n]
        else:
            dur = 1
            ht  = s
        if ht.startswith ('^') or ht.startswith ('_'):
            ht = halftone (ht)
        else:
            h0 = ht [0].upper ()
            if h0 in accidentals:
                ht = halftone (accidentals [h0] + ht)
            else:
                ht = halftone (ht)
        return cls (ht, dur, bind = bind)
    # end def from_string

    def as_abc (self):
        try:
            key = self.bar.voice.tune.key
        except AttributeError:
            key = None
        b = ['', '-'][self.bind]
        e = ' '
        # No trailing space when not last and abslen <= 1/8
        eights = Fraction (1, 8)
        if not self.is_last and self.abslen and self.abslen <= eights:
            if self.next and self.next.abslen <= eights:
                e = ''
        return "%s%s%s%s" % (self.halftone.as_abc (key), self.length (), b, e)
    # end def as_abc

    def copy (self):
        # self.halftone is a singleton
        return self.__class__ (self.halftone, self.duration, bind = self.bind)
    # end def copy

    def transpose (self, steps, key = 'C'):
        return self.__class__ \
            ( self.halftone.transpose (steps, key)
            , duration = self.duration
            , bind = self.bind
            )
    # end def transpose

# end class Tone

class Pause (Bar_Object):

    @classmethod
    def from_string (cls, s):
        assert s.startswith ('z')
        duration = int (s [1:])
        return cls (duration)
    # end def from_string

    def as_abc (self):
        return "z%s " % (self.length ())
    # end def as_abc

# end class Pause

class Meter:
    """ Represent the meter of a tune, e.g. 4/4, 3/4 or similar
    >>> m = Meter.from_string ('C')
    >>> print (m)
    4/4
    >>> m = Meter.from_string ('C|')
    >>> print (m)
    2/2
    """

    def __init__ (self, measure, beats):
        self.measure = measure
        self.beats   = beats
    # end def __init__

    @classmethod
    def from_string (cls, s):
        if s == 'C':
            m, b = 4, 4
        elif s == 'C|':
            m, b = 2, 2
        else:
            m, b = (int (x) for x in s.split ('/'))
        return cls (m, b)
    # end def from_string

    def __str__ (self):
        return '%s/%s' % (self.measure, self.beats)
    # end def __str__
    __repr__ = __str__

    def as_abc (self):
        return "M: %s/%s" % (self.measure, self.beats)
    # end def as_abc

# end class Meter

class Key (object):
    """ Model a key, either major or minor or one of the gregorian modes
    >>> key = Key.get ('E')
    >>> key.transpose (-12)
    E
    >>> key.transpose (12)
    E
    >>> key.transpose (48)
    E
    >>> key.transpose (-1)
    A
    >>> key.transpose (-2)
    D
    >>> key.transpose (-3)
    G
    >>> key.transpose (-4)
    C
    >>> key.transpose (-5)
    F
    >>> key.transpose (-6)
    Bb
    >>> key.transpose (-7)
    Eb
    >>> key.transpose (-8)
    Ab
    >>> key.transpose (-9)
    Db
    >>> key.transpose (-10)
    Gb
    >>> key.transpose (-11)
    B
    >>> key.transpose (1)
    B
    >>> key.transpose (2)
    F#
    >>> key.transpose (3)
    Db
    >>> key.transpose (4)
    Ab
    >>> key.transpose (5)
    Eb
    >>> key.transpose (6)
    Bb
    >>> key.transpose (7)
    F
    >>> key.transpose (8)
    C
    >>> key.transpose (9)
    G
    >>> key.transpose (10)
    D
    >>> key.transpose (11)
    A
    >>> Key.get ('Cb').transpose (0)
    B
    >>> Key.get ('C#').transpose (0)
    Db
    >>> Key.get ('Gb').transpose (12)
    F#
    >>> Key.get ('Gb').transpose (-12)
    Gb
    >>> Key.get ('F#').transpose (-12)
    Gb
    >>> Key.get ('F#').transpose (12)
    F#
    >>> Key.get ('C').transpose (-2)
    Bb
    >>> Key.get ('DDor').transpose (-2)
    CDor
    """

    ionian = major = \
        ( 'Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F'
        , 'C',  'G',  'D',  'A',  'E',  'B',  'F#', 'C#'
        )
    aeolian = minor = \
        ( 'Abm', 'Ebm', 'Bbm', 'Fm',  'Cm',  'Gm',  'Dm'
        , 'Am',  'Em',  'Bm',  'F#m', 'C#m', 'G#m', 'D#m', 'A#m'
        )
    mixolydian = \
        ( 'GbMix', 'DbMix', 'AbMix', 'EbMix', 'BbMix', 'FMix',  'CMix'
        , 'GMix',  'DMix',  'AMix',  'EMix',  'BMix',  'F#Mix', 'C#Mix', 'G#Mix'
        )
    dorian = \
        ( 'DbDor', 'AbDor', 'EbDor', 'BbDor', 'FDor',  'CDor',  'GDor'
        , 'DDor',  'ADor',  'EDor',  'BDor',  'F#Dor', 'C#Dor', 'G#Dor', 'D#Dor'
        )
    phrygian = \
        ( 'EbPhr', 'BbPhr', 'FPhr',  'CPhr',  'GPhr',  'DPhr',  'APhr'
        , 'EPhr',  'BPhr',  'F#Phr', 'C#Phr', 'G#Phr', 'D#Phr', 'A#Phr', 'E#Phr'
        )
    lydian = \
        ( 'FbLyd', 'CbLyd', 'GbLyd', 'DbLyd', 'AbLyd', 'EbLyd', 'BbLyd'
        , 'FLyd',  'CLyd',  'GLyd',  'DLyd',  'ALyd',  'ELyd',  'BLyd', 'F#Lyd'
        )
    locrian = \
        ( 'BbLoc', 'FLoc',  'CLoc',  'GLoc',  'DLoc',  'ALoc',  'ELoc'
        , 'BLoc',  'F#Loc', 'C#Loc', 'G#Loc', 'D#Loc', 'A#Loc', 'E#Loc', 'B#Loc'
        )
    modes = ( 'ionian', 'major', 'aeolian', 'minor', 'mixolydian'
            , 'dorian', 'phrygian', 'lydian', 'locrian'
            )

    table = {}
    reg   = {}

    def __init__ (self, name):
        self.mode, self.offset = self.table [name]
        self.name = name
    # end def __init__

    @classmethod
    def get (cls, name):
        """ Implement sort-of singleton
        """
        if isinstance (name, cls):
            return name
        if name not in cls.reg:
            cls.reg [name] = cls (name)
        return cls.reg [name]
    # end def get

    @cached_property
    def accidentals (self):
        assert -7 <= self.offset <= 7
        alltones = 'CDEFGAB'
        tones = [halftone (x) for x in alltones]
        # transposition doesn't generate 7 flats or sharps:
        if self.offset == -7:
            tt = [halftone ('_' + x) for x in alltones]
        elif self.offset == 7:
            tt = [halftone ('^' + x) for x in alltones]
        else:
            tt = [x.transpose_fifth (self.offset) for x in tones]
        return dict ((t.stem.upper (), t.prefix) for t in tt if t.prefix)
    # end def accidentals

    def transpose (self, n_fifth):
        """ Note that on transposition we never return something with
            more than 6 flats or sharps. This can be used to transpose
            something with 7 sharps or 7 flats to something with 5 flats
            or 5 sharps, respectively. If we transpose up, we prefer
            sharps, if we transpose down we prefer flats.
            To get the enharmonic equivalent of something with 6 sharps
            or flats transpose up or down by a multiple of 12.
        """
        t = (self.offset + n_fifth) % 12
        if t > 6:
            t -= 12
        if t == 6 and n_fifth < 0:
            t = -6
        return self.get (getattr (self, self.mode) [t + 7])
    # end def transpose

    def __str__ (self):
        return self.name
    # end def __str__
    __repr__ = __str__

# end class Key

for m in Key.modes:
    for n, name in enumerate (getattr (Key, m)):
        Key.table [name] = (m, n - 7)

class Bar:

    def __init__ (self, duration, unit = 8, end = ''):
        assert int (duration) == duration
        self.duration = int (duration)
        self.dur_sum  = 0
        self.objects  = []
        self.unit     = unit
        self.voice    = None
        self.idx      = None
        self.end      = end
    # end def __init__

    @classmethod
    def from_string (cls, key, unit, s):
        end = ''
        if s.endswith ('|\n'):
            end = '|\n'
            s = s [:-2]
        if s.endswith ('\n'):
            end = '\n'
            s = s [:-1]
        bar = cls (unit, unit, end)
        for t in s.strip ().split ():
            while t:
                tone = []
                if t [0] in '^_=':
                    tone.append (t [0])
                    t = t [1:]
                if t [0].lower () in 'cdefgabcz':
                    tone.append (t [0])
                    t = t [1:]
                while t and t [0] in ",'":
                    tone.append (t [0])
                    t = t [1:]
                while t and t [0].isdigit ():
                    tone.append (t [0])
                    t = t [1:]
                if t and t [0] == '-':
                    tone.append (t [0])
                    t = t [1:]
                tone = ''.join (tone)
                assert tone
                bo = Bar_Object.from_string (key.accidentals, tone)
                if bo is None:
                    raise ValueError ('Invalid Bar object: "%s"' % tone)
                bar.add (bo)
        return bar
    # end def from_string

    def __str__ (self):
        return ('Bar (voice=%s, idx=%s)' % (self.voice, self.idx))
    # end def __str__
    __repr__ = __str__

    @property
    def prev (self):
        if not self.idx:
            return None
        return self.voice.bars [self.idx - 1]
    # end def prev

    @property
    def next (self):
        if not self.idx:
            return None
        if len (self.voice.bars) <= self.idx + 1:
            return None
        return self.voice.bars [self.idx + 1]
    # end def next

    def add (self, bar_object):
        if self.dur_sum + bar_object.length () > self.duration:
            raise ValueError \
                ( "Overfull bar: %s + %s > %s"
                % (self.dur_sum, bar_object.duration, self.duration)
                ) # pragma: no cover
        bar_object.register (self, self.dur_sum, len (self.objects))
        if self.objects:
            prev = self.objects [-1]
            bar_object._prev = prev
            prev._next = bar_object
        self.dur_sum += bar_object.length ()
        self.objects.append (bar_object)
    # end def add

    def as_abc (self):
        r = []
        for bo in self.objects:
            r.append (bo.as_abc ())
        e = self.end
        if not self.next:
            e = e.rstrip ('\n')
        r.append ('|%s' % e)
        return ''.join (r)
    # end def as_abc

    def change_unit (self, unit, dry_run = False):
        """ Change unit of this bar
            Of course this needs to be done in the Tune, too.
        """
        # The following never happens if called via Tune, it also checks this
        if self.unit == unit:
            return # pragma: no cover
        factor  = Fraction (unit) / self.unit
        newunit = factor * self.unit
        newdur  = factor * self.duration
        if newunit != int (newunit) or newdur != int (newdur):
            raise ValueError \
                ( 'Cannot set unit, duration to %s, %s for %s'
                % (newunit, newdur, self)
                ) # pragma: no cover
        newunit = int (newunit)
        newdur  = int (newdur)
        for bo in self.objects:
            newlen = factor * len (bo)
            if newlen < 1:
                raise ValueError \
                    ('Cannot set length to %s for %s' % (newlen, bo)) \
                        # pragma: no cover
            if not dry_run:
                bo.duration = newlen
        if not dry_run:
            self.unit     = newunit
            self.duration = newdur
    # end def change_unit

    def copy (self):
        other = self.__class__ (self.duration, self.unit, self.end)
        for obj in self.objects:
            other.add (obj.copy ())
        return other
    # end def copy

    def get_by_offset (self, bar_object):
        """ Get a bar object matching another bar_object
            The intended use is for locating the bar_object which occurs
            at the same time as the bar_object in another voice.
            This may return None if the previous bar is empty (can occur
            during searching/testing).
        """
        bar = self
        if bar_object.bar.idx != self.idx:
            bar = self.voice.bars [bar_object.bar.idx]
        offset = bar_object.offset
        if not len (bar.objects):
            return None
        pos = bisect_right (bar.objects, offset, key = lambda x: x.offset) - 1
        assert pos >= 0
        return bar.objects [pos]
    # end def get_by_offset

    def transpose (self, steps, key = 'C'):
        b = self.__class__ (self.duration, self.unit, self.end)
        for o in self.objects:
            b.add (o.transpose (steps, key))
        return b
    # end def transpose

# end class Bar

class Voice:
    """ A single voice of a complex tune
    """
    def __init__ (self, id = None, *bars, **properties):
        self.bars = []
        self.id   = id
        self.tune = None
        for b in bars:
            self.add (b)
        self.properties = properties
    # end def __init__

    def __getattr__ (self, prop):
        try:
            v = self.properties [prop]
        except KeyError as err: # pragma: no cover
            raise AttributeError (err)
        return v
    # end def __getattr__

    def __str__ (self):
        return 'Voice ("%s")' % self.id
    # end def __str__
    __repr__ = __str__

    def add (self, bar):
        assert bar.idx  is None
        bar.idx = len (self.bars)
        self.bars.append (bar)
        bar.voice = self
    # end def add

    def as_abc (self):
        r = []
        if self.id:
            r.append ("[V:%s] " % self.id)
        for bar in self.bars:
            r.append (bar.as_abc ())
        return ''.join (r)
    # end def as_abc

    def as_abc_header (self):
        if not self.id:
            return ''
        def tq (p):
            if ' ' in p:
                return '"%s"' % p
            return p
        prp = ('%s=%s' % (k, tq (self.properties [k])) for k in self.properties)
        prp = ' '.join (prp)
        if prp:
            prp = ' ' + prp
        return 'V:%s%s' % (self.id, prp)
    # end def as_abc_header

    def bars_from_string (self, key, unit, s):
        """ Parse (and append) bars from string.
            Can be called multiple times to append multiple lines.
        """
        bars = s.split ('|')
        for n, b in enumerate (bars):
            r = ''
            if n + 1 == len (bars):
                r = '\n'
            if n + 2 == len (bars) and bars [n + 1] == '':
                r = '|\n'
            self.add (Bar.from_string (key, unit, b + r))
            if r:
                break
    # end def bars_from_string

    def copy (self):
        bars = []
        for bar in self.bars:
            bars.append (bar.copy ())
        return self.__class__ (self.id, *bars, **self.properties)
    # end def copy

    def replace (self, idx, bar):
        """ Replace bar at position idx
        """
        assert bar.idx is None
        # raise IndexError if idx is wrong:
        oldbar = self.bars [idx]
        idx = oldbar.idx
        assert self.bars [idx] is oldbar
        bar.idx = idx
        self.bars [idx] = bar
        bar.voice = self
    # end def replace

    def transpose (self, steps, key = 'C'):
        v = self.__class__ (self.id, **self.properties)
        for b in self.bars:
            v.add (b.transpose (steps, key))
        return v
    # end def transpose

# end class Voice

class Tune:

    def __init__ \
        ( self, meter, key
        , title    = None
        , number   = 1
        , unit     = None
        , comment  = None
        , nlines   = None # Set when parsed from file/iterator
        , lastline = None # Last line seen during parsing (ugly hack)
        , **kw
        ):
        self.voices  = []
        self.meter   = meter
        self.key     = Key.get (key)
        self.title   = title
        self.number  = number
        self.kw      = kw
        self._unit   = unit or Fraction (8)
        self.comment = comment or []
    # end def __init__

    @classmethod
    def from_iterator (self, itr, stop_at_err = False):
        """ The iterator will usually be a file
        """
        kw = {}
        voices = {}
        barlen = None
        for lineno, line in enumerate (itr):
            line = line.strip ()
            if not line:
                if stop_at_err:
                    tune = Tune (**kw)
                    tune.nlines   = lineno + 1
                    # Ugly hack to allow the calling line parser to
                    # parse the line we didn't need
                    tune.lastline = line
                    for v in voices:
                        tune.add (voices [v])
                    return tune
                continue
            if line.startswith ('%%'):
                k, v = (line.lstrip ('%').split (None, 1))
                kw [k] = v
            elif line.startswith ('%'):
                if 'comment' not in kw:
                    kw ['comment'] = []
                kw ['comment'].append (line [1:])
            elif line.startswith ('[') or ':' not in line:
                if 'unit' not in kw:
                    if 'meter' in kw:
                        kw ['unit'] = kw ['meter'].beats
                    else:
                        raise ValueError ('No unit note length') \
                            # pragma: no cover
                unit = kw ['unit']
                if line.startswith ('['):
                    vinfo, rest = line.split (None, 1)
                else:
                    vinfo = None
                    rest  = line
                if not rest.endswith ('|'):
                    raise NotImplementedError \
                        ('Incomplete bar in "%s" % line') # pragma: no cover
                # Strip bar for later split
                rest = rest [:-1]
                # We support either the voice format with a declaration
                # of voices (using info field V) and then each line
                # prefixed with a voice in angular brackets, or a
                # *single* voice without a prior declaration.
                if vinfo:
                    if not vinfo.endswith (']'):
                        raise ValueError \
                            ('Invalid voice format: "%s"' % vinfo) \
                            # pragma: no cover
                    vinfo = vinfo [1:-1]
                    a, b = vinfo.split (':', 1)
                    if a != 'V':
                        raise NotImplementedError \
                            ('Unknown voice format "%s in "%s"' % (a, line)) \
                            # pragma: no cover
                    if b not in voices: # pragma: no cover
                        print ('Warning: Undeclared voice "%s"' % b)
                        voices [b] = Voice (b)
                else:
                    b = None
                    if not voices:
                        voices [None] = Voice ()
                    else:
                        assert len (voices) == 1 and list (voices) [0] is None
                voice = voices [b]
                key   = kw.get ('key')
                if not key:
                    raise ValueError ('No key (K) definition') #pragma: no cover
                voice.bars_from_string (key, unit, rest)
            else:
                k, v = line.split (':', 1)
                v = v.lstrip ()
                if k == 'K':
                    kw ['key'] = Key.get (v)
                elif k == 'L':
                    if 'unit' in kw:
                        raise ValueError \
                            ('Duplicate unit note length: %s' % line) \
                            # pragma: no cover
                    n, d = (int (x) for x in v.split ('/', 1))
                    unit = Fraction (1) / Fraction (n, d)
                    if int (unit) != unit:
                        raise NotImplementedError \
                            ('Non integral unit') # pragma: no cover
                    kw ['unit'] = unit
                elif k == 'M':
                    kw ['meter'] = Meter.from_string (v)
                elif k == 'T':
                    kw ['title'] = v
                elif k == 'V':
                    vkw  = {}
                    try:
                        id, rest = v.split (None, 1)
                    except ValueError:
                        id   = v
                        rest = ''
                    while rest:
                        k, rest = rest.split ('=', 1)
                        if rest.startswith ('"'):
                            vv, rest = rest [1:].split ('"', 1)
                            vkw [k] = vv
                            rest = rest.lstrip ()
                        else:
                            try:
                                vv, rest = rest.split (None, 1)
                            except ValueError:
                                vv = rest
                                rest = ''
                            vkw [k] = vv
                    voices [id] = Voice (id, **vkw)
                elif k == 'X':
                    kw ['number'] = v
                else:
                    if len (k) != 1:
                        err = None
                        for st in ['#', 'Contra', 'Cantus']:
                            if k.startswith (st):
                                err = True
                                break
                        if stop_at_err and err:
                            tune = Tune (**kw)
                            tune.nlines   = lineno + 1
                            tune.lastline = line
                            for v in voices:
                                tune.add (voices [v])
                            return tune
                        raise NotImplementedError \
                            ('Unknown field "%s"' % k) # pragma: no cover
                    if k in kw:
                        if not isinstance (kw [k], list):
                            kw [k] = [kw [k]]
                        kw [k].append (v)
                    else:
                        kw [k] = v
        tune = Tune (**kw)
        tune.nlines = lineno + 1
        for v in voices:
            tune.add (voices [v])
        return tune
    # end def from_iterator

    @classmethod
    def from_file (cls, fn):
        with open (fn, 'r') as f:
            return cls.from_iterator (f)
    # end def from_file

    @property
    def unit (self):
        return self._unit
    # end def unit

    @unit.setter
    def unit (self, unit):
        if unit == self.unit:
            return
        if unit != int (unit):
            raise ValueError ('Invalid unit: %s' % unit) # pragma: no cover
        # Do it twice, first with dry_run, first run will raise an
        # exception if impossible. This ensures that if the change is
        # impossible the tune is left consistent.
        for v in self.voices:
            for b in v.bars:
                b.change_unit (unit, dry_run = True)
        for v in self.voices:
            for b in v.bars:
                b.change_unit (unit)
    # end def unit

    def __str__ (self):
        return self.as_abc ()
    # end def __str__
    __repr__ = __str__

    def __getattr__ (self, k):
        try:
            return self.kw [k]
        except KeyError as err: # pragma: no cover
            raise AttributeError (err)
    # end def __getattr__

    def add (self, voice):
        self.voices.append (voice)
        assert voice.tune is None
        voice.tune = self
    # end def add

    def as_abc (self):
        r = []
        r.append ('X: %s' % self.number)
        if self.title:
            r.append ('T: %s' % self.title)
        r.append (self.meter.as_abc ())
        for k in self.kw:
            l = self.kw [k]
            if not isinstance (l, list):
                l = [l]
            if len (k) == 1:
                for v in l:
                    r.append ('%s: %s' % (k, v))
            else:
                for v in l:
                    r.append ('%%%%%s %s' % (k, v))
        r.append ("L: %s" % (Fraction (1) / self.unit))
        for v in self.voices:
            h = v.as_abc_header ()
            if h:
                r.append (h)
        r.append ("K: %s" % self.key)
        for v in self.voices:
            r.append (v.as_abc ())
        for c in self.comment:
            r.append ('%' + c)
        return '\n'.join (r)
    # end def as_abc

    def iter (self, voice_idx):
        for bar in self.voices [voice_idx].bars:
            yield bar
    # end def iter

    def transpose (self, steps):
        fifth = transpose_steps_to_fifth (steps)
        k = self.key.transpose (fifth)
        t = self.__class__ \
            (self.meter, k, self.title, self.number, self.unit, **self.kw)
        for v in self.voices:
            t.add (v.transpose (steps, self.key))
        return t
    # end def transpose

# end class Tune
