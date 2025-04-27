#!/usr/bin/python3
# Copyright (C) 2024-25
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

from textwrap import fill as text_wrap
from .tune    import sgn, Pause

class Check:
    """ Super class of all checks
        This gets the description of the check.
    """
    prefix = ''

    def __init__ (self, desc, badness, ugliness):
        self.desc     = self.msg = desc
        self.badness  = badness
        self.ugliness = ugliness
    # end def __init__

    def __str__ (self):
        """ Describes a failed check
            This interpolates the parameters of the last check into the
            desc attribute and into the suffix.
        """
        if not self.result:
            return ''
        self.compute_description ()
        suffix = '    (B: %(badness)g U: %(ugliness)g)'
        desc   = text_wrap \
            ( self.msg
            , initial_indent    = ' ' * 4
            , subsequent_indent = ' ' * 4
            )
        return (self.prefix + ':\n' + desc + '\n' + suffix) % self.__dict__
    # end def __str__
    __repr__ = __str__

    def check (self, *args, **kw):
        """ We require an _check method for the actual implementation.
            This *must* return True when the check condition matches,
            i.e., when there is a violation of the rule.
        """
        self.result = self._check (*args, **kw)
        if self.result:
            return self.badness, self.ugliness
        return 0, 0
    # end def check

    def compute_description (self):
        raise NotImplementedError ('Need compute_description method') \
            # pragma: no cover
    # end def compute_description

# end class Check

class History_Mixin:
    """ This does the same checks as its class but matches only on the
        *second* occasion when the check matches will it raise an error
        condition.
    """

    def __init__ (self, *args, **kw):
        super ().__init__ (*args, **kw)
        self.reset ()
    # end def __init__

    def _check (self, *args, **kw):
        result = super ()._check (*args, **kw)
        # It's a single tone if bound to previous one
        # We keep the history in this case
        # (Must be after super call above, otherwise self.current is not
        # yet defined and self.current doesn't exist in harmony checks)
        if isinstance (self, Check_Melody_Interval):
            prev = self.current.prev
            if prev and prev.bind:
                return False
        if self.prev_match and result:
            return True
        self.prev_match = result
        return False
    # end def _check

    def reset (self):
        if hasattr (super (), 'reset'):
            super ().reset ()
        self.prev_match = False
    # end def reset

# end class History_Mixin

class Check_Melody (Check):
    """ Common base class for melody checks
    """
    def __init__ \
        ( self, desc, interval
        , badness = 0, ugliness = 0
        , signed      = False
        , octave      = True
        ):
        super ().__init__ (desc, badness, ugliness)
        self.interval    = set (interval)
        self.signed      = signed
        self.octave      = octave
    # end def __init__

    def compute_description (self):
        bar   = self.current.bar
        voice = bar.voice.id
        self.prefix = \
            ( '%s bar: %d note: %d'
            % (voice, bar.idx + 1, self.current.idx + 1)
            )
    # end def compute_description

    def compute_interval (self):
        prev = self.current.prev
        if not getattr (self.current, 'halftone', None):
            return
        if not getattr (prev, 'halftone', None):
            return
        d = self.current.halftone.offset - prev.halftone.offset
        if not self.signed:
            d = abs (d)
        if self.octave:
            d %= 12
        return d
    # end def compute_interval

# end class Check_Melody

class Check_Melody_Interval (Check_Melody):
    """ Check on the progression of a melody
        This compares two consecutive tones of a voice.
        We keep a history of the last tone.
    """

    def _check (self, current):
        self.current = current
        prev = current.prev
        if not prev:
            return False
        d = self.compute_interval ()
        if d is not None and d in self.interval:
            # It's a single tone if bound to previous one
            prev = self.current.prev
            if prev and prev.bind:
                return False
            return True
    # end def _check

# end class Check_Melody_Interval

class Check_Melody_History (History_Mixin, Check_Melody_Interval):
    pass

class Check_Melody_Jump (Check_Melody_History):

    def __init__ (self, desc, badness = 0, ugliness = 0, limit = 2):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.limit = limit
    # end def __init__

    def _check (self, current):
        self.current = current
        if not current.prev:
            return False
        d = self.compute_interval ()
        if d is None:
            return False
        retval = False
        # We might want to make the badness and the ugliness different
        # for jumps and directional movements after a jump
        if abs (d) > self.limit:
            if self.prev_match:
                self.msg = self.desc
                retval = True
            self.prev_match = sgn (d)
        else: # Step not jump
            if self.prev_match and self.prev_match == sgn (d):
                self.msg = 'Same-direction movement after jump'
                retval = True
            self.prev_match = 0
        return retval
    # end def _check

    def reset (self):
        super ().reset ()
        self.msg = self.desc
    # end def reset

# end class Check_Melody_Jump

class Check_Harmony (Check):

    def compute_description (self):
        b_cp = self.cp_obj.bar
        b_cf = self.cf_obj.bar
        v_cp = b_cp.voice.id
        v_cf = b_cf.voice.id
        self.prefix = \
            ('%s bar: %d note: %d %s bar: %d note: %d'
            % ( v_cp, b_cp.idx + 1, self.cp_obj.idx + 1
              , v_cf, b_cf.idx + 1, self.cf_obj.idx + 1
              )
            )
    # end def compute_description

# end class Check_Harmony

class Check_Harmony_Interval (Check_Harmony):

    def __init__ \
        ( self, desc, interval
        , badness = 0, ugliness = 0
        , octave    = False
        , signed    = False
        , not_first = False
        , not_last  = False
        ):
        self.interval  = interval
        self.octave    = octave
        self.signed    = signed
        self.not_first = not_first
        self.not_last  = not_last
        super ().__init__ (desc, badness, ugliness)
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        if self.not_first and (cf_obj.is_first and cp_obj.is_first):
            return False
        if self.not_last and (cp_obj.is_last and cf_obj.is_last):
            return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d in self.interval:
            return True
        return False
    # end def _check

    def compute_interval (self, cf_obj, cp_obj):
        assert cf_obj.overlaps (cp_obj)
        self.cf_obj = cf_obj
        self.cp_obj = cp_obj
        if not getattr (cf_obj, 'halftone', None):
            return
        if not getattr (cp_obj, 'halftone', None):
            return
        self.cft    = cf_obj.halftone.offset
        self.cpt    = cp_obj.halftone.offset
        d = self.cpt - self.cft
        if not self.signed:
            d = abs (d)
        if self.octave:
            d %= 12
        return d
    # end def compute_interval

# end class Check_Harmony_Interval

class Check_Harmony_First_Interval (Check_Harmony_Interval):
    """ Note that the interval is *inverted*: Only the elements in
        interval are allowed.
        Note that this checks the first harmony interval where we do not
        have a pause from the start (the first real harmony interval).
    """
    def _check (self, cf_obj, cp_obj):
        """ We check the first two objects *which are not a Pause*
        """
        assert cf_obj.overlaps (cp_obj)
        if cf_obj.is_pause or cp_obj.is_pause:
            return False
        cpp = self.is_first_non_pause (cp_obj)
        cfp = self.is_first_non_pause (cf_obj)
        if not cpp and not cfp:
            return False
        if cpp and not cfp:
            if not self.is_first_non_pause (cf_obj, cp_obj.bar, cp_obj.offset):
                return False
        if cfp and not cpp:
            if not self.is_first_non_pause (cp_obj, cf_obj.bar, cf_obj.offset):
                return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d not in self.interval:
            return True
        return False
    # end def _check

    def is_first_non_pause (self, obj, bar = None, offset = None):
        if obj.is_pause:
            return False
        # Check if everything *before* obj is a pause
        # If baridx and offset if given only up to that point (backwards)
        p_obj = obj
        while not p_obj.is_first:
            if bar is not None:
                assert offset is not None
                if p_obj.bar.idx < bar.idx:
                    return True
                if p_obj.bar.idx == bar.idx and p_obj.offset <= offset:
                    return True
            p_obj = p_obj.prev
            # Happens only during testing/searching when the previous
            # bar has no objects:
            if p_obj is None:
                return False
            if not p_obj.is_pause:
                return False
        return True
    # end def is_first_non_pause

# end def Check_Harmony_First_Interval

class Check_Harmony_Interval_Max (Check_Harmony_Interval):

    def __init__ \
        ( self, desc, maximum
        , badness = 0, ugliness = 0
        ):
        self.maximum = maximum
        super ().__init__ (desc, None, badness, ugliness, False, signed = True)
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d > self.maximum:
            return True
        return False
    # end def _check

# end class Check_Harmony_Interval_Max

class Check_Harmony_Interval_Min (Check_Harmony_Interval):

    def __init__ \
        ( self, desc, minimum
        , badness = 0, ugliness = 0
        ):
        self.minimum = minimum
        super ().__init__ (desc, None, badness, ugliness, False, signed = True)
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d < self.minimum:
            return True
        return False
    # end def _check

# end class Check_Harmony_Interval_Min

class Check_Melody_Jump_2 (Check_Harmony):

    def __init__ (self, desc, limit = 2, badness = 0, ugliness = 0):
        super ().__init__ (desc, badness, ugliness)
        self.limit = limit
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        assert cf_obj.overlaps (cp_obj)
        self.cp_obj = cp_obj
        self.cf_obj = cf_obj
        p_cp_obj    = cp_obj.prev
        if not p_cp_obj:
            return False
        p_cf_obj = cf_obj.bar.get_by_offset (p_cp_obj)
        # This would only happen if the CF bar is empty
        if not p_cf_obj:
            return False # pragma: no cover
        if not getattr (cf_obj, 'halftone', None):
            return False
        if not getattr (p_cf_obj, 'halftone', None):
            return False
        if not getattr (cp_obj, 'halftone', None):
            return False
        if not getattr (p_cp_obj, 'halftone', None):
            return False
        d1 = cf_obj.halftone.offset - p_cf_obj.halftone.offset
        d2 = cp_obj.halftone.offset - p_cp_obj.halftone.offset
        if d1 > self.limit and d2 > self.limit:
            return True
        return False
    # end def _check

# end class Check_Melody_Jump_2

class Check_Harmony_History (History_Mixin, Check_Harmony_Interval):
    pass

class Check_Harmony_Melody_Direction (Check_Harmony_Interval):

    def __init__ \
        ( self, desc, interval
        , badness = 0, ugliness = 0
        , octave      = False
        , dir         = 'same'
        , only_repeat = False
        ):
        super ().__init__ \
            (desc, interval, badness, ugliness, octave, signed = True)
        self.dir         = dir
        self.only_repeat = only_repeat
        self.reset ()
        assert self.dir in ['same', 'zero', 'different']
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        """ We need to take the prev object which is nearer to the
            current time (i.e. the *latest* prev object), otherwise we
            do not correctly determine a movement.
        """
        assert cf_obj.overlaps (cp_obj)
        p_cp_obj = cp_obj.prev
        p_cf_obj = cf_obj.prev
        if not p_cp_obj and not p_cf_obj:
            return False
        if not p_cp_obj:
            p_cp_obj = cp_obj.bar.get_by_offset (p_cf_obj)
        elif not p_cf_obj:
            p_cf_obj = cf_obj.bar.get_by_offset (p_cp_obj)
        else:
            cp_tuple = (p_cp_obj.bar.idx, p_cp_obj.offset)
            cf_tuple = (p_cf_obj.bar.idx, p_cf_obj.offset)
            if cp_tuple < cf_tuple:
                p_cp_obj = cp_obj.bar.get_by_offset (p_cf_obj)
            else:
                assert cf_tuple <= cp_tuple
                p_cf_obj = cf_obj.bar.get_by_offset (p_cp_obj)
        # This indicates an empty previous bar and should only happen in tests
        if not p_cp_obj or not p_cf_obj:
            return False
        if not getattr (p_cf_obj, 'halftone', None):
            return False
        if not getattr (p_cp_obj, 'halftone', None):
            return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d is None:
            return False
        self.dir_cf = sgn (cf_obj.halftone.offset - p_cf_obj.halftone.offset)
        self.dir_cp = sgn (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        # An empty interval matches everything
        if  (   (not self.interval or d in self.interval)
            and self.direction_check ()
            ):
            if not self.only_repeat or self.prev_match:
                self.prev_match = True
                return True
        return False
    # end def _check

    def direction_check (self):
        if self.dir == 'same':
            # Sign must be positive or negative not 0 (no direction)
            return self.dir_cf and self.dir_cf == self.dir_cp
        elif self.dir == 'different':
            # currently unused
            return self.dir_cf == self.dir_cp
        elif self.dir == 'zero':
            return self.dir_cf == self.dir_cp == 0
        else:
            assert 0 # pragma: no cover
    # end def direction_check

    def reset (self):
        self.prev_match = False
    # end def reset

# end class Check_Harmony_Melody_Direction

# 0.1.2: "Permitted melodic intervals are the perfect fourth, fifth,
# and octave, as well as the major and minor second, major and minor
# third, and ascending minor sixth. The ascending minor sixth must
# be immediately followed by motion downwards." This means we allow
# the following halftone intervals: 1, 2, 3, 4, 5, 7, 8, 9, 12 and
# forbid the following: 0, 6, 10, 11
# We currently allow sixth in both directions
# We allow unison in the second voice but not several in a series.
old_melody_checks_cf = \
    [ Check_Melody_Interval
        ( "0.1.2: no seventh (Septime)"
        , interval = (10, 11)
        , badness  = 10.0
        )
    , Check_Melody_Interval
        ( "0.1.2: no Devils interval"
        , interval = (6,)
        , badness  = 10.0
        )
    , Check_Melody_Interval
        ("0.1.2: No unison (Prim) allowed"
        , interval =  (0,)
        , badness  = 10.0
        , octave   = False
        )
    , Check_Melody_Interval
        ( "5 or 7"
        , interval =  (5, 7)
        , ugliness = 1.0
        , octave   = False
        )
    , Check_Melody_Interval
        ( "8 or 9"
        , interval =  (8, 9)
        , ugliness = 10.0
        , octave   = False
        )
    , Check_Melody_Interval
        ( "Octave"
        , interval =  (12,)
        , ugliness = 2.0
        , octave   = False
        )
    , Check_Melody_Jump
        ( "Jump"
        , badness = 10.0
        )
    ]
magi_melody_checks_cf = old_melody_checks_cf

old_melody_checks_cp = \
    [ Check_Melody_Interval
        ( "0.1.2: no seventh (Septime)"
        , interval = (10, 11)
        , badness  = 10.0
        )
    , Check_Melody_Interval
        ( "0.1.2: no Devils interval"
        , interval = (6,)
        , badness  = 10.0
        )
    , Check_Melody_History
        ("0.1.2: No consecutive unison (Prim) allowed"
        , interval    = (0,)
        , badness     = 10.0
        , octave      = False
        )
    , Check_Melody_Jump
        ( "Jump"
        , badness = 10.0
        )
    ]
magi_melody_checks_cp = \
    [ Check_Melody_Interval
        ( "no big sixth, no downwards little sixth"
        , signed = True
        , interval = (9, -8)
        , badness = 1.5
        )
    , Check_Melody_Interval
        ( "0.1.2: no Devils interval"
        , interval = (6,)
        , badness  = 1.7
        )
    , Check_Melody_History
        ("0.1.2: No consecutive unison (Prim) allowed"
        , interval    = (0,)
        , badness     = 1.1
        , octave      = False
        )
    , Check_Melody_Interval
        ( "0.1.2: no seventh (Septime)"
        , interval = (10, 11)
        , badness  = 1.5
        )
#Wenn du eine kleine Sext oder Oktave springst, muss davor und danach eine 
#Gegenbewegung stattfinden. Aber auch Terz- Quart- und Quintsprünge in die 
#Gegenbewegung sind erlaubt.laMotte1981, S. 69ff.
#Bei Terz, Quint und Quart-Sprüngen, darf dieselbe Bewegungsrichtung stehen. 
#Dabei soll bei Bewegung aufwärts das größere Intervall beginnen, bei 
#Abwärtsbewegung das kleinere.
    , Check_Melody_laMotte_Jump 
        ( badness = 1.5
        )
#Achteln dürfen nicht durch Sprünge erreicht werden. Und nach einem Achtel muss
#auch ein Schritt stehen. (Ganter S.90)
    , Check_Melody_Avoid_Eighth_Jump
        ( note_length  = (1,)
        , badness      = 1.5
        )
    , Check_Melody_Quarter_Jump
        ( "Für Sprünge werden Halbe und größere Noten bevorzugt (Daniel S.78)"
        , note_length  = (2,)
        , badness      = 1.1
        )
    , Check_Melody_Interval     
        ( "Wenn zwei Vierteln auf leichter Taktzeit stehen und danach und"
          " davor längere Notenwerte sind, fallen sie schrittweise nach"
          " unten. (Daniel S.118)
        , note_length   = (2,)
        , next_length   = (2,)
        , next2_length  = (4, 6, 8, 12, 16)
        , interval      = -1
        , bar_position  = (5, 13)
        , next_interval = -1
        , badness       = 1.4
        )
    ]
old_harmony_checks = \
    [ Check_Harmony_Interval
        ( "1.2: Use no unisons except at the beginning or end"
        , interval  = (0,)
        , badness   = 10.0
        , octave    = False
        , not_first = True
        , not_last  = True
        )
    , Check_Harmony_Interval
        ( "No Sekund"
        , interval = (1, 2)
        , badness  = 10.0
        , octave   = True
        )
    , Check_Harmony_Interval
        ( "Magdalena: 5/6 verboten"
        , interval = (5, 6)
        , badness  = 10.0
        , octave   = True
        )
    , Check_Harmony_Interval
        ( "Magdalena: 10/11 verboten"
        , interval = (10, 11)
        , badness  = 10.0
        , octave   = True
        )
    # 1.6: Attempt to keep any two adjacent parts within a tenth
    # of each other, unless an exceptionally pleasing line can
    # be written by moving outside of that range.
    , Check_Harmony_Interval_Max
        ( "max. 16"
        , maximum  = 16
        , badness  = 10.0
        )
    , Check_Harmony_Interval_Max
        ( "Magdalena: intervals above octave should be avoided"
        , maximum  = 12
        , ugliness = 1.0
        )
    , Check_Harmony_Interval_Min
        ( "Contrapunctus voice must be *up*"
        , minimum  = 0
        , badness  = 10.0
        )
    , Check_Harmony_First_Interval
        ( "1.1. Begin and end on either unison, octave, fifth,"
          " unless the added part is underneath [it isn't here],"
          " in which case begin and end only on unison or octave."
        , interval = (0, 7, 12)
        , badness  = 100.
        )
    , Check_Melody_Jump_2
        ( "Not both voices may jump"
        , badness  = 10.0
        )
    # This might need more history, should probably only trigger if
    # the *last* was already a fifth or octave. And switching from
    # fifth to octave ore vice-versa might still be allowed, in
    # which case we would need *two* checks.
    #, Check_Harmony_Melody_Direction
    #    ( "Magdalena: Avoid parallel fifth or octaves: Ensure that"
    #      " the last direction (from where is the fifth or octave"
    #      " approached) is different."
    #    , interval = (7, 12)
    #    , dir      = 'same'
    #    , badness  = 9.0
    #    )
    # This implements the spec above
    , Check_Harmony_History
        ( "Magdalena: Avoid parallel fifth"
        , interval = (7,)
        , badness  = 9.0
        )
    , Check_Harmony_History
        ( "Magdalena: Avoid parallel octaves"
        , interval = (12,)
        , badness  = 9.0
        )

    # This only checks for two of the *same*. Not if we have several
    # sixth in a row with different CF. This might need changes to
    # the underlying check implementation.
    #, Check_Harmony_Melody_Direction
    #    ( "For sext (sixth) or terz (third) don't allow several in a row"
    #    , interval = (3, 4, 8, 9)
    #    , dir      = 'zero'
    #    , ugliness = 3
    #    )
    # This doesn't allow several (unrelated) sixth or thirds in a row
    , Check_Harmony_History
        ( "For sext (sixth) don't allow several in a row"
        , interval = (8, 9)
        , ugliness = 3
        )
    , Check_Harmony_History
        ( "For terz (third) don't allow several in a row"
        , interval = (3, 4)
        , ugliness = 3
        )
    , Check_Harmony_Melody_Direction
        ( "Generally it's better that voices move in opposite"
          " direction (or one stays the same if allowed)"
        , interval = () # All
        , dir      = 'same'
        , ugliness = 0.1
        )
    ]

magi_harmony_checks = \
    [ Check_Harmony_Interval
        ( "1.2: Use no unisons except at the beginning or end"
        , interval  = (0,)
        , badness   = 10.0
        , octave    = False
        , not_first = True
        , not_last  = True
        )
    , Check_Harmony_Interval
        ( "No Sekund"
        , interval = (1, 2)
        , badness  = 10.0
        , octave   = True
        )
    , Check_Harmony_Interval
        ( "Magdalena: 5/6 verboten"
        , interval = (5, 6)
        , badness  = 10.0
        , octave   = True
        )
    , Check_Harmony_Interval
        ( "Magdalena: 10/11 verboten"
        , interval = (10, 11)
        , badness  = 10.0
        , octave   = True
        )
    # 1.6: Attempt to keep any two adjacent parts within a tenth
    # of each other, unless an exceptionally pleasing line can
    # be written by moving outside of that range.
    , Check_Harmony_Interval_Max
        ( "Distance between voices should not exceed Duodezime"
        , maximum  = 19
        , badness  = 10.0
        )
    , Check_Harmony_First_Interval
        ( "1.1. Begin and end on either unison, octave, fifth,"
          " unless the added part is underneath [it isn't here],"
          " in which case begin and end only on unison or octave."
        , interval = (0, 7, 12, -12)
        , badness  = 100
        )
    , Check_Melody_Jump_2
        ( "Both voices may not jump"
        , badness  = 10.0
        )
    , Check_Harmony_Melody_Direction
        ( "Magdalena: Ensure that"
          " the last direction (from where is the fifth or octave"
          " approached) is different."
        , interval = (0, 7, 12)
        , dir      = 'same'
        , badness  = 9.0
        )
    , Check_Harmony_History
        ( "Magdalena: Avoid parallel unison, octaves, fifths"
        , interval = (0, 7, 12)
        , badness  = 9.0
        )

    # This only checks for two of the *same*. Not if we have several
    # sixth in a row with different CF. This might need changes to
    # the underlying check implementation.
    #, Check_Harmony_Melody_Direction
    #    ( "For sext (sixth) or terz (third) don't allow several in a row"
    #    , interval = (3, 4, 8, 9)
    #    , dir      = 'zero'
    #    , ugliness = 3
    #    )
    # This doesn't allow several (unrelated) sixth or thirds in a row
    , Check_Harmony_History
        ( "For sext (sixth) don't allow several in a row"
        , interval = (8, 9)
        , ugliness = 1.1
        )
    , Check_Harmony_History
        ( "For terz (third) don't allow several in a row"
        , interval = (3, 4)
        , ugliness = 1.1
        )
    , Check_Harmony_Melody_Direction
        ( "Generally it's better that voices move in opposite"
          " direction (or one stays the same if allowed)"
        , interval = () # All
        , dir      = 'same'
        , ugliness = 0.1
        )
    , Check_Passing_Tone
        ( "Wenn eine Note schrittweise erreicht wird und schrittweise"
          " IN DIESELBE Richtung wieder verlassen wird, darf sie eine"
          " Dissonanz sein, solange sie auf leichte Zeit steht."
          " Ausnahme= harter Durchgang (halbschwer).
          "HALBE:"
        , interval       = (2, 3, 6, 10, 11)
        , octave         = True
        , jump           = False
        , direction      = 'same'
        , next_direction = 'same'
        , note_length    = (4,)
        , bar_position   = (5, 13)
        )
    , Check_Passing_Tone
        ( "Wenn eine Note schrittweise erreicht wird und schrittweise"
          " IN DIESELBE Richtung wieder verlassen wird, darf sie eine"
          " Dissonanz sein, solange sie auf leichte Zeit steht."
          " Ausnahme= harter Durchgang (halbschwer).
          "VIERTEL:"
        , interval       = (2, 3, 6, 10, 11)
        , octave         = True
        , jump           = False
        , direction      = 'same'
        , next_direction = 'same'
        , note_length    = (2,)
        , bar_position   = (3, 5, 7, 11, 13, 15)
        )
    , Check_Passing_Tone
        ( "Wenn eine Note schrittweise erreicht wird und schrittweise"
          " IN DIESELBE Richtung wieder verlassen wird, darf sie eine"
          " Dissonanz sein, solange sie auf leichte Zeit steht."
          " Ausnahme= harter Durchgang (halbschwer).
          "ACHTELN:"
        , interval       = (2, 3, 6, 10, 11)
        , octave         = True
        , jump           = False
        , direction      = 'same'
        , next_direction = 'same'
        , note_length    = (1,)
        , FIXME
        )
    ]

checks = dict \
    ( default = (old_melody_checks_cf, old_melody_checks_cp, old_harmony_checks)
    , special = (magi_melody_checks_cf, magi_melody_checks_cp, magi_harmony_checks)
    )

__all__ = ['checks']
