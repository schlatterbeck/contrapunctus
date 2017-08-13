from rsclib import Rational

def sgn (i) :
    if i > 0 :
        return 1
    if i < 0 :
        return -1
    return 0
# end def sgn

class Halftone (object) :
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
        import pdb ; pdb.set_trace ()
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

    def __str__ (self) :
        return self.name
    # end def __str__
    __repr__ = __str__

# end class Halftone

def halftone (name) :
    """ Return singleton tone """
    return Halftone.get (name)
# end def halftone

class Bar_Object (object) :

    def __init__ (self, duration, unit = 8) :
        self.__super.__init__ ()
        self.duration = duration
        self.unit     = unit
    # end def __init__

    def length (self, unit) :
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
        return "Z%s" % (self.length (unit))
    # end def as_abc

# end class Pause
