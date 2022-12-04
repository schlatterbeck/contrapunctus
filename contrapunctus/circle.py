#!/usr/bin/python3

from .tune import halftone

class Circle_Of_Fifth (object):
    fifth_up = dict \
        (( ( 'C',   'G')
         , ('^C',  '^G')
         , ( 'D',   'A')
         , ('^D',  '^A')
         , ( 'E',   'B')
         , ( 'F',   'c')
         , ('^F',  '^c')
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
         , ( 'g',   "d'")
         , ('^g',  "^d'")
         , ( 'a',   "e'")
         , ('^a',  "^e'")
         , ( 'b',  "^f'")
        ))
    fifth_down = dict \
        (( ( 'C',   'F,')
         , ('_D',  '_G,')
         , ( 'D',   'G,')
         , ('_E',  '_A,')
         , ( 'E',   'A,')
         , ( 'F',  '_H,')
         , ('_G',  '_C')
         , ( 'G',   'C')
         , ('_A',  '_D')
         , ( 'A',   'D')
         , ('_B',  '_E')
         , ( 'B',   'E')
         , ( 'c',   'F')
         , ( 'd',   'G')
         , ('_d',  '^G')
         , ( 'e',   'A')
         , ('_e',  '_A')
         , ( 'f',  '_H')
         , ('_g',  '_c')
         , ( 'g',   'c')
         , ('_a',  '_d')
         , ( 'a',   'd')
         , ('_b',  '_e')
         , ( 'b',   'e')
        ))

    @classmethod
    def transpose_quint_up (cls, h):
        """ Transpose a quint up
        >>> Circle_Of_Fifth.transpose_quint_up (halftone ('g'))
        d'
        """
        return halftone (cls.fifth_up [h.name])
    # end def transpose_quint_up

    @classmethod
    def transpose_quint_down (cls, h):
        """ Transpose a quint down
        >>> Circle_Of_Fifth.transpose_quint_down (halftone ('g'))
        c
        """
        return halftone (cls.fifth_down [h.name])
    # end def transpose_quint_down

# end class Circle_Of_Fifth
