#!/usr/bin/python

from Tune import halftone

class Gregorian (object) :

    def __init__ (self, ambitus) :
        assert len (ambitus) > 7
        self.ambitus = [halftone (x) for x in ambitus]
    # end def __init__

    @property
    def subsemitonium (self) :
        """ Leading tone, German: Leitton
        """
        FIXME
    # end def subsemitonium

    @property
    def finalis (self) :
        return self.ambitus [0]
    # end def finalis

# end class Gregorian

dorian = Gregorian (['D', 'E', 'F', 'G', 'A', 'B', 'C', 'd'])
