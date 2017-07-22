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
    """
    symbols = dict \
        (( ('_C', -10), ('C', -9), ('^C', -8)
        ,  ('_D',  -8), ('D', -7), ('^D', -6)
        ,  ('_E',  -6), ('E', -5), ('^E', -4)
        ,  ('_F',  -5), ('F', -4), ('^F', -3)
        ,  ('_G',  -3), ('G', -2), ('^G', -1)
        ,  ('_A',  -1), ('A',  0), ('^A',  1)
        ,  ('_B',   1), ('B',  2), ('^B',  3)
        ,  ('_c',   2), ('c',  3), ('^c',  4)
        ,  ('_d',   4), ('d',  5), ('^d',  6)
        ,  ('_e',   6), ('e',  7), ('^e',  8)
        ,  ('_f',   7), ('f',  8), ('^f',  9)
        ,  ('_g',   9), ('g', 10), ('^g', 11)
        ,  ('_a',  11), ('a', 12), ('^a', 13)
        ,  ('_b',  13), ('b', 14), ('^b', 15)
        ))
    # standard_pitch has halftone offset 0
    standard_pitch = 'A'

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
    # end def __init__

# end class Halftone
