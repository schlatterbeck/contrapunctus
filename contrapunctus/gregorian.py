#!/usr/bin/python3

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

    def __init__ (self, ambitus):
        assert len (ambitus) == 7
        self.ambitus = [halftone (x) for x in ambitus]
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
        return self [1]
    # end def step2

    def __getitem__ (self, idx):
        """ Get halftone with index idx from our tones, note that we
            synthesize tones outside the given ambitus dynamically.
        """
        if 0 <= idx < len (self.ambitus):
            return self.ambitus [idx]
        d, m = divmod (idx, 7)
        return self.ambitus [m].transpose_octaves (d)
    # end def __getitem__

# end class Gregorian

dorian = Gregorian (['D', 'E', 'F', 'G', 'A', 'B', 'c'])
