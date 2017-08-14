from rsclib.Rational  import Rational
from rsclib.autosuper import autosuper

def sgn (i) :
    if i > 0 :
        return 1
    if i < 0 :
        return -1
    return 0
# end def sgn

class Halftone (autosuper) :
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

    reg = {}

    def register (self) :
        self.reg [self.name] = self
    # end def register

    def __init__ (self, name) :
        tr = 0
        ln = name
        while ln.endswith (',') :
            ln = ln [:-1]
            tr = tr - 12
        assert not ln.endswith ("'") or tr == 0
        while ln.endswith ("'") :
            ln = ln [:-1]
            tr = tr + 12
        self.offset = self.symbols [ln] + tr
        self.name   = name
        self.register ()
    # end def __init__

    @classmethod
    def get (cls, name) :
        """ Implement sort-of singleton
        """
        if name in cls.reg :
            return cls.reg [name]
        return cls (name)
    # end def get

    def get_interval (self, offset) :
        """ Transpose the current Halftone by offset (in half-tones)
        >>> Halftone ("C").get_interval (-1)
        B,
        >>> Halftone ("c").get_interval (-1)
        B
        >>> Halftone ("c").get_interval (-2)
        ^A
        >>> Halftone ("C,,,").get_interval (-1)
        B,,,,
        >>> Halftone ("c'''").get_interval (-1)
        b''
        >>> Halftone ("c").get_interval (1)
        ^c
        """
        (octaves, offs) = divmod (offset, 12)
        name = self.name
        while (name.endswith (',')) :
            octaves -= 1
            name = name [:-1]
        while (name.endswith ("'")) :
            octaves += 1
            name = name [:-1]
        if self.offset + offs > 15 :
            assert name.upper () != name
            name = name.upper ()
            offs -= 12
            octaves += 1
        if self.offset + offs < -10 :
            assert name.lower () != name
            name = name.lower ()
            offs += 12
            octaves -= 1
        idx = self.symlist.index (name)
        while (self.symbols [self.symlist [idx]] != offs + self.offset) :
            idx += sgn (offs)
        symbol = self.symlist [idx]
        while (octaves) :
            if octaves > 0 :
                if symbol.lower () != symbol :
                    symbol = symbol.lower ()
                else :
                    symbol = symbol + "'"
                octaves -= 1
            if octaves < 0 :
                if symbol.upper () != symbol :
                    symbol = symbol.upper ()
                else :
                    symbol = symbol + ","
                octaves += 1
        return self.get (symbol)
    # end get_interval

    def transpose_octaves (self, octaves=1) :
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
        if octaves > 0 :
            for i in range (octaves) :
                if n.endswith (",") :
                    n = n [:-1]
                elif n.lower () != n :
                    n = n.lower ()
                else :
                    n = n + "'"
        elif octaves < 0:
            for i in range (abs (octaves)) :
                if n.endswith ("'") :
                    n = n [:-1]
                elif n.upper () != n :
                    n = n.upper ()
                else :
                    n = n + ","
        return self.get (n)
    # end def transpose_octaves

    def __str__ (self) :
        return self.name
    # end def __str__
    __repr__ = __str__

# end class Halftone

def halftone (name) :
    """ Return singleton tone """
    return Halftone.get (name)
# end def halftone

class Bar_Object (autosuper) :

    def __init__ (self, duration, unit = 8) :
        self.__super.__init__ ()
        self.duration = duration
        self.unit     = unit
    # end def __init__

    def length (self, unit = None) :
        unit = unit or self.unit
        l = Rational (self.duration, self.unit) * Rational (unit)
        return l
    # end def length

# end class Bar_Object

class Tone (Bar_Object) :

    def __init__ (self, halftone, duration, unit = 8) :
        self.halftone = halftone
        self.__super.__init__ (duration, unit)
        self.duration = duration
        self.unit     = unit
    # end def __init__

    def as_abc (self, unit = None) :
        return "%s%s" % (self.halftone.name, self.length (unit))
    # end def as_abc

# end class Tone

class Pause (Bar_Object) :

    def as_abc (self, unit = None) :
        return "z%s" % (self.length (unit))
    # end def as_abc

# end class Pause

class Meter (autosuper) :
    """ Represent the meter of a tune, e.g. 4/4, 3/4 or similar
    """

    def __init__ (self, measure, beats) :
        self.measure = measure
        self.beats   = beats
    # end def __init__

    @property
    def duration (self) :
        return len (self)
    # end def duration

    def as_abc (self) :
        return "M: %s/%s" % (self.measure, self.beats)
    # end def as_abc

    def length (self) :
        return Rational (self.measure, self.beats)
    # end def length

    def __str__ (self) :
        return '%s/%s' % (self.measure, self.beats)
    # end def __str__

# end class Meter

class Bar (autosuper) :

    def __init__ (self, duration, unit = 8, *bar_object) :
        self.duration = Rational (duration)
        self.dur_sum  = Rational (0)
        self.objects  = []
        for b in bar_object :
            self.add (b)
    # end def __init__

    def add (self, bar_object) :
        if self.dur_sum + bar_object.length () > self.duration :
            raise ValueError \
                ( "Overfull bar: %s + %s > %s"
                % (self.dur_sum, bar_object.duration, self.duration)
                )
        self.objects.append (bar_object)
    # end def add

    def as_abc (self) :
        r = []
        for bo in self.objects :
            r.append (bo.as_abc ())
        r.append ('|')
        return ' '.join (r)
    # end def as_abc

# end class Bar

class Voice (autosuper) :
    """ A single voice of a complex tune
    """
    def __init__ (self, id = None, *bars, **properties) :
        self.bars = []
        self.id   = id
        for b in bars :
            self.add (b)
        self.properties = properties
    # end def __init__

    def add (self, bar) :
        self.bars.append (bar)
    # end def add

    def as_abc (self) :
        r = []
        if id :
            r.append ("[V:%s] " % self.id)
        for bar in self.bars :
            r.append (bar.as_abc ())
        return ''.join (r)
    # end def as_abc

    def as_abc_header (self) :
        if not self.id :
            return ''
        def tq (p) :
            if ' ' in p :
                return '"%s"' % p
            return p
        prp = ('%s=%s' % (k, tq (self.properties [k])) for k in self.properties)
        return 'V:%s %s' % (self.id, ' '.join (prp))
    # end def as_abc_header

# end class Voice

class Tune (autosuper) :

    def __init__ \
        ( self, meter, key
        , title  = None
        , number = 1
        , unit   = None
        , *voices, **kw
        ) :
        self.voices = []
        self.meter  = meter
        self.key    = key
        self.title  = title
        self.number = number
        self.kw     = kw
        self.unit   = unit or Rational (8)
        for v in voices :
            self.add (v)
    # end def __init__

    def add (self, voice) :
        self.voices.append (voice)
    # end def add

    def as_abc (self) :
        r = []
        r.append ('X: %s' % self.number)
        if self.title :
            r.append ('T: %s' % self.title)
        r.append (self.meter.as_abc ())
        for k in self.kw :
            if len (k) == 1 :
                r.append ('%s: %s' % (k, self.kw [k]))
            else :
                r.append ('%%%%%s %s' % (k, self.kw [k]))
        r.append ("M: %s" % self.meter)
        r.append ("L: %s" % (Rational (1) // self.unit))
        for v in self.voices :
            h = v.as_abc_header ()
            if h :
                r.append (h)
        r.append ("K: %s" % self.key)
        for v in self.voices :
            r.append (v.as_abc ())
        return '\n'.join (r)
    # end def as_abc

    @classmethod
    def from_file (cls, fn) :
        """ Unfinished """
        version   = None
        in_header = True
        kw        = {}
        with open (fn, 'r') as f :
            for n, line in enumerate (f) :
                if n == 0 and line.startswith ('%abc') :
                    version = line [4:].strip ()
                if in_header :
                    if line [1] == ':' :
                        k = line [0]
                        if k not in kw :
                            kw [k] = []
                        kw [k].append (line [2:].strip ())
    # end def from_file

    def iter (self, voice_idx) :
        for bar in self.voices [voice_idx].bars :
            for bo in bar.objects :
                yield bo
    # end def iter

    def __str__ (self) :
        return self.as_abc ()
    # end def __str__
    __repr__ = __str__

# end class Tune
