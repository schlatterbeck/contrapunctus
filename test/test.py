#!/usr/bin/python3

from contrapunctus.Tune  import Voice, Bar, Tone, Tune, Pause, halftone, Meter

v1 = Voice (id = 'T1', clef='treble-8', name='Tenore I', snm='T.I')
b1 = Bar (8, 8)
b1.add (Tone (halftone ('B'), 2))
b1.add (Tone (halftone ('c'), 2))
b1.add (Tone (halftone ('d'), 2))
b1.add (Tone (halftone ('g'), 2))
v1.add (b1)
b1 = Bar (8, 8)
b1.add (Tone (halftone ('f'), 6))
b1.add (Tone (halftone ('e'), 2))
v1.add (b1)
b1 = Bar (8, 8)
b1.add (Tone (halftone ('d'), 2))
b1.add (Tone (halftone ('c'), 2))
b1.add (Tone (halftone ('d'), 2))
b1.add (Tone (halftone ('e'), 2))
v1.add (b1)
b1 = Bar (8, 8)
b1.add (Tone (halftone ('d'), 4))
b1.add (Tone (halftone ('c'), 2))
b1.add (Pause (2))
v1.add (b1)

v2 = Voice (id = 'T2', clef='treble-8', name='Tenore II', snm='T.II')
b2 = Bar (8, 8)
b2.add (Tone (halftone ('G'), 2))
b2.add (Tone (halftone ('A'), 2))
b2.add (Tone (halftone ('B'), 2))
b2.add (Tone (halftone ('e'), 2))
v2.add (b2)
b2 = Bar (8, 8)
b2.add (Tone (halftone ('d'), 6))
b2.add (Tone (halftone ('c'), 2))
v2.add (b2)
b2 = Bar (8, 8)
b2.add (Tone (halftone ('B'), 2))
b2.add (Tone (halftone ('A'), 2))
b2.add (Tone (halftone ('B'), 2))
b2.add (Tone (halftone ('c'), 2))
v2.add (b2)
b2 = Bar (8, 8)
b2.add (Tone (halftone ('B'), 4))
b2.add (Tone (halftone ('A'), 2))
b2.add (Pause (2))
v2.add (b2)

v3 = Voice \
    ( id        = 'B1'
    , clef      = 'bass'
    , name      = 'Basso I'
    , snm       = 'B.I'
    , transpose = '-24'
    , middle    = 'd'
    )
b3 = Bar (8, 8)
b3.add (Pause (8))
v3.add (b3)
b3 = Bar (8, 8)
b3.add (Pause (2))
b3.add (Tone (halftone ('f'), 2))
b3.add (Tone (halftone ('g'), 2))
b3.add (Tone (halftone ('a'), 2))
v3.add (b3)
b3 = Bar (8, 8)
b3.add (Tone (halftone ('b'), 2))
b3.add (Pause (2))
b3.add (Pause (2))
b3.add (Tone (halftone ('e'), 2))
v3.add (b3)
b3 = Bar (8, 8)
b3.add (Tone (halftone ('f'), 4))
b3.add (Tone (halftone ('f'), 2))
b3.add (Pause (2))
v3.add (b3)

t = Tune \
    ( number = 1
    , title  = 'Zocharti Loch'
    , C      = 'Louis Lewandowski (1821-1894)'
    , meter  = Meter (4, 4)
    , Q      = '1/4=76'
    , key    = 'Gm'
    , score  = '(T1 T2) (B1)'
    )
t.add (v1)
t.add (v2)
t.add (v3)

print (t.as_abc ())

