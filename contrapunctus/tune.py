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

from __future__ import division
from rsclib.Rational  import Rational
from rsclib.autosuper import autosuper

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

class Halftone (autosuper):
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

    @classmethod
    def get (cls, name):
        """ Implement sort-of singleton
        """
        if name in cls.reg:
            return cls.reg [name]
        return cls (name)
    # end def get

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

    def __str__ (self):
        return self.name
    # end def __str__
    __repr__ = __str__

# end class Halftone

def halftone (name):
    """ Return singleton tone """
    return Halftone.get (name)
# end def halftone

class Bar_Object (autosuper):
    """ Base class of all objects that go into a Bar
    """

    def __init__ (self, duration, unit = 8):
        self.__super.__init__ ()
        self.duration = duration
        # offset in Bar (parent), filled when inserting into Bar
        self.offset   = None
        # Index into Bar (parent)
        self.idx      = None
        self.bar      = None
        self.unit     = unit
        self._prev    = None
        self._next    = None
    # end def __init__

    @property
    def prev (self):
        if self.offset == 0:
            if self.bar.prev is None:
                return None
            return self.bar.prev.objects [-1]
        else:
            return self._prev
    # end def prev


    def length (self, unit = None):
        unit = unit or self.unit
        l = Rational (self.duration, self.unit) * Rational (unit)
        assert int (l) == l
        return int (l)
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

# end class Bar_Object

class Tone (Bar_Object):

    def __init__ (self, halftone, duration, unit = 8):
        self.halftone = halftone
        self.__super.__init__ (duration, unit)
    # end def __init__

    def as_abc (self, unit = None):
        return "%s%s" % (self.halftone.name, self.length (unit))
    # end def as_abc

    def transpose (self, steps, key = 'C'):
        return self.__class__ \
            ( self.halftone.transpose (steps, key)
            , duration = self.duration
            , unit     = self.unit
            )
    # end def transpose

# end class Tone

class Pause (Bar_Object):

    def as_abc (self, unit = None):
        return "z%s" % (self.length (unit))
    # end def as_abc

    def transpose (self, steps, key = 'C'):
        return self
    # end def transpose

# end class Pause

class Meter (autosuper):
    """ Represent the meter of a tune, e.g. 4/4, 3/4 or similar
    """

    def __init__ (self, measure, beats):
        self.measure = measure
        self.beats   = beats
    # end def __init__

    @property
    def duration (self):
        return len (self)
    # end def duration

    def as_abc (self):
        return "M: %s/%s" % (self.measure, self.beats)
    # end def as_abc

    def length (self):
        return Rational (self.measure, self.beats)
    # end def length

    def __str__ (self):
        return '%s/%s' % (self.measure, self.beats)
    # end def __str__

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
        if name in cls.reg:
            return cls.reg [name]
        return cls (name)
    # end def get

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

class Bar (autosuper):

    def __init__ (self, duration, unit = 8, *bar_object):
        assert isinstance (duration, int)
        self.duration = duration
        self.dur_sum  = 0
        self.objects  = []
        self.unit     = unit
        self.prev     = None
        self.next     = None
        self.voice    = None
        for b in bar_object:
            self.add (b)
    # end def __init__

    def add (self, bar_object):
        if self.dur_sum + bar_object.length () > self.duration:
            raise ValueError \
                ( "Overfull bar: %s + %s > %s"
                % (self.dur_sum, bar_object.duration, self.duration)
                )
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
        r.append ('|')
        return ' '.join (r)
    # end def as_abc

    def transpose (self, steps, key = 'C'):
        b = self.__class__ (self.duration, self.unit)
        for o in self.objects:
            b.add (o.transpose (steps, key))
        return b
    # end def transpose

# end class Bar

class Voice (autosuper):
    """ A single voice of a complex tune
    """
    def __init__ (self, id = None, *bars, **properties):
        self.bars = []
        self.id   = id
        for b in bars:
            self.add (b)
        self.properties = properties
    # end def __init__

    def __getattr__ (self, prop):
        try:
            v = self.properties [prop]
        except KeyError as err:
            raise AttributeError (err)
    # end def __getattr__

    def add (self, bar):
        assert bar.next is None
        assert bar.prev is None
        if self.bars:
            assert self.bars [-1].next is None
            self.bars [-1].next = bar
            bar.prev = self.bars [-1]
        self.bars.append (bar)
        bar.voice = self
    # end def add

    def as_abc (self):
        r = []
        if id:
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
        return 'V:%s %s' % (self.id, ' '.join (prp))
    # end def as_abc_header

    def transpose (self, steps, key = 'C'):
        v = self.__class__ (self.id, **self.properties)
        for b in self.bars:
            v.add (b.transpose (steps, key))
        return v
    # end def transpose

# end class Voice

class Tune (autosuper):

    def __init__ \
        ( self, meter, key
        , title  = None
        , number = 1
        , unit   = None
        , *voices, **kw
        ):
        self.voices = []
        self.meter  = meter
        self.key    = Key.get (key)
        self.title  = title
        self.number = number
        self.kw     = kw
        self.unit   = unit or Rational (8)
        for v in voices:
            self.add (v)
    # end def __init__

    def add (self, voice):
        self.voices.append (voice)
    # end def add

    def as_abc (self):
        r = []
        r.append ('X: %s' % self.number)
        if self.title:
            r.append ('T: %s' % self.title)
        r.append (self.meter.as_abc ())
        for k in self.kw:
            if len (k) == 1:
                r.append ('%s: %s' % (k, self.kw [k]))
            else:
                r.append ('%%%%%s %s' % (k, self.kw [k]))
        r.append ("L: %s" % (Rational (1) // self.unit))
        for v in self.voices:
            h = v.as_abc_header ()
            if h:
                r.append (h)
        r.append ("K: %s" % self.key)
        for v in self.voices:
            r.append (v.as_abc ())
        return '\n'.join (r)
    # end def as_abc

    @classmethod
    def from_file (cls, fn):
        """ Unfinished """
        version   = None
        in_header = True
        kw        = {}
        with open (fn, 'r') as f:
            for n, line in enumerate (f):
                if n == 0 and line.startswith ('%abc'):
                    version = line [4:].strip ()
                if in_header:
                    if line [1] == ':':
                        k = line [0]
                        if k not in kw:
                            kw [k] = []
                        kw [k].append (line [2:].strip ())
    # end def from_file

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

    def __str__ (self):
        return self.as_abc ()
    # end def __str__
    __repr__ = __str__

# end class Tune
