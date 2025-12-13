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

# Used for default argument when None is a valid value
DEFAULT_ARG = -1

# Badness in n-th root of 2
BAD_MAX = 2
BAD_2   = 2 ** (1/2)
BAD_4   = 2 ** (1/4)
BAD_8   = 2 ** (1/8)

class Check:
    """ Super class of all checks
        This gets the description of the check.
    """
    prefix    = ''
    lookahead = 0 # how much we look into the future using next

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
        , badness       = 0
        , ugliness      = 0
        , signed        = False
        , octave        = True
        , bar_position  = None
        , note_length   = None
        , next_length   = None
        , next2_length  = None
        , prev_length   = None
        , prev2_length  = None
        , next_interval = None
        , prev_interval = None
        , badness_2     = 0
        , ugliness_2    = 0
        , msg_2         = None
        ):
        super ().__init__ (desc, badness, ugliness)
        self.interval      = set (interval)
        self.signed        = signed
        self.octave        = octave
        self.bar_position  = bar_position
        self.note_length   = note_length
        self.next_length   = next_length
        self.next2_length  = next2_length
        self.prev_length   = prev_length
        self.prev2_length  = prev2_length
        self.next_interval = next_interval
        self.prev_interval = prev_interval
        self.badness_2     = badness_2
        self.ugliness_2    = ugliness_2
        self.badness_1     = badness
        self.ugliness_1    = ugliness
        self.msg_2         = msg_2 or self.desc
        if self.badness_2 == 0 and self.ugliness_2 == 0:
            self.badness_2  = self.badness_1
            self.ugliness_2 = self.ugliness_1
        # signed and octave flags may not currently be combined
        assert not (self.signed and self.octave)
    # end def __init__

    def compute_description (self):
        bar   = self.current.bar
        voice = bar.voice.id
        self.prefix = \
            ( '%s bar: %d note: %d'
            % (voice, bar.idx + 1, self.current.idx + 1)
            )
    # end def compute_description

    def compute_interval (self, current = DEFAULT_ARG):
        if current is DEFAULT_ARG:
            current = self.current
        if current is None:
            return
        prev = current.prev_with_bind
        if not prev or not current.is_tone or not prev.is_tone:
            return
        d = current.halftone.offset - prev.halftone.offset
        if not self.signed:
            d = abs (d)
        if self.octave:
            assert d >= 0
            d %= 12
        return d
    # end def compute_interval

    def timing_check (self, current):
        """ Check if bar position, note length and next/prev note
            lengths are matching, return True if this rule applies in
            this regard
        """
        if self.bar_position and current.offset not in self.bar_position:
            return False
        if self.note_length and current.length not in self.note_length:
            return False
        if self.next_length and self.next_with_bind:
            if self.next_with_bind.length not in self.next_length:
                return False
            nn = self.next_with_bind.next_with_bind
            if self.next2_length and nn:
                if nn.length not in self.next2_length:
                    return False
        if self.prev_length and self.prev:
            if self.prev_length.length not in self.prev_length:
                return False
            pp = self.prev_with_bind.prev_with_bind
            if self.prev2_length and pp:
                if pp.length not in self.prev2_length:
                    return False
        return True
    # end def timing_check

# end class Check_Melody

class Check_Melody_Interval (Check_Melody):
    """ Check on the progression of a melody
        This compares two consecutive tones of a voice.
        We keep a history of the last tone.
    """

    def _check (self, current):
        if not self.timing_check (current):
            return
        self.current = current
        d = self.compute_interval ()
        if d is not None and d in self.interval:
            return True
        if self.next_interval:
            d = self.compute_interval (self.next_with_bind)
            if d is not None and d in self.next_interval:
                return True
        if self.prev_interval:
            d = self.compute_interval (self.prev_with_bind)
            if d is not None and d in self.prev_interval:
                return True
    # end def _check

# end class Check_Melody_Interval

class Check_Melody_History (History_Mixin, Check_Melody_Interval):
    pass

class Check_Melody_Jump (Check_Melody_History):

    def __init__ (self, desc, badness = 0, ugliness = 0, limit = 2, msg_2 = ''):
        super ().__init__ \
            (desc, (), badness, ugliness, True, False, msg_2 = msg_2)
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
        # We want to make the badness and the ugliness different
        # for jumps and directional movements after a jump, so we assign
        # self.badness and self.ugliness here depending on the condition
        if abs (d) > self.limit:
            if self.prev_match:
                self.msg = self.desc
                self.badness  = self.badness_1
                self.ugliness = self.ugliness_1
                retval = True
            self.prev_match = sgn (d)
        else: # Step not jump
            if self.prev_match and self.prev_match == sgn (d):
                self.msg = self.msg_2
                self.badness  = self.badness_2
                self.ugliness = self.ugliness_2
                retval = True
            self.prev_match = 0
        return retval
    # end def _check

    def reset (self):
        super ().reset ()
        self.msg = self.desc
    # end def reset

# end class Check_Melody_Jump

class Check_Melody_Avoid_Notelen_Jump (Check_Melody_Interval):
    """ Eighth notes should not be reached by jumps and should be
        followed by step. (Ganter p. 90)
        We also allow a pause after or before a jump. And the check also
        doesn't match when the jump is the first or last thing in a tune.
        Note that the note length here by default is 1 (one eighth).
    """

    def __init__ \
        (self, desc, note_length = 1, badness = 0, ugliness = 0, limit = 2):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.note_length = note_length
        self.limit       = limit
    # end def __init__

    def _check (self, current):
        self.current = current

        # Check if current note fits the given length (typically 1/8)
        if current.length == self.note_length and current.is_tone:
            # Check if reached by jump
            if current.prev and current.prev.is_tone:
                prev_interval = abs \
                    (current.halftone.offset - current.prev.halftone.offset)
                if prev_interval > self.limit:
                    self.msg = self.desc
                    return True

            # Check if followed by jump
            # 1/8 never has a bind to the next note
            assert not self.current.bind
            if current.next and current.next.is_tone:
                next_interval = abs \
                    (current.next.halftone.offset - current.halftone.offset)
                if next_interval > self.limit:
                    self.msg = self.desc
                    return True
        return False
    # end def _check

# end class Check_Melody_Avoid_Notelen_Jump

class Check_Melody_Note_Length_Jump (Check_Melody_Interval):
    """ Usually no jumps between short notes (e.g. LaMotte p. 76, 122),
    """

    def __init__ (self, desc, note_length = (1, 2), badness=0, ugliness=0):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.note_length = note_length
    # end def __init__

    def _check (self, current):
        self.current = current

        # No check if this is a pause
        if not current.is_tone:
            return False
        # Check if current note is involved in a jump
        if current.prev and current.prev.is_tone:
            prev = current.prev
            interval = abs (current.halftone.offset - prev.halftone.offset)
            if interval > 2:  # It's a jump
                # Check if both note length are short
                if  (   current.length in self.note_length
                    and prev.length in self.note_length
                    ):
                    return True
        return False
    # end def _check

# end class Check_Melody_Note_Length_Jump

class Check_Melody_Note_Length_Double_Jump (Check_Melody_Interval):
    """ No double jumps between short notes
    """

    def __init__ (self, desc, note_length = (1, 2), badness=0, ugliness=0):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.note_length = note_length
        prev_jump = False
    # end def __init__

    def _check (self, current):
        self.current = current

        # No check if this is a pause
        if not current.is_tone:
            return False
        # Check if current note is involved in a jump
        if current.prev and current.prev.is_tone:
            prev = current.prev
            interval = abs (current.halftone.offset - prev.halftone.offset)
            if interval > 2:  # It's a jump
                # Check if both note length are short
                if  (   current.length in self.note_length
                    and prev.length in self.note_length
                    ):
                    if self.prev_jump:
                        return True
                    self.prev_jump = True
        self.prev_jump = False
        return False
    # end def _check

# end class Check_Melody_Note_Length_Double_Jump

class Check_Melody_laMotte_Jump (Check_Melody_Jump):
    """ Implements laMotte's rules for jumps:
        - When jumping a minor sixth or octave, there must be a contrary
          motion before and after
        - For third, fourth and fifth jumps, movement in the same
          direction is allowed
        - For upward movement, the larger interval should come first
        - For downward movement, the smaller interval should come first
        - Not yet implemented:
          You may combine third jumps with the bigger jumps
          Three jumps are allowed if first and last is a third jump and
          they are in contrary motion
        laMotte 1981, p. 69ff
    """

    def _check (self, current):
        self.current = current
        if not current.prev or not current.next:
            return False

        d = self.compute_interval ()
        if d is None:
            return False

        next_d = current.next.halftone.offset - current.halftone.offset

        # Check for sixth or octave jumps
        if abs (d) in (8, 12):
            prev_d = 0
            if current.prev.prev:
                prev = current.prev
                prev_d = prev.halftone.offset - prev.prev.halftone.offset

            # Check if there's contrary motion before and after
            if sgn (d) == sgn (prev_d) or sgn (d) == sgn (next_d):
                self.msg = "For sixth or octave jumps, " \
                           "there must be contrary motion before and after"
                return True

        # Check for third, fourth, fifth jumps in same direction
        elif abs (d) in (3, 4, 5, 7):
            # If same direction, check interval size rules
            if sgn (d) == sgn (next_d) and abs (next_d) > 2:
                # Upward: larger interval should come first:
                if d > 0 and abs (d) < abs (next_d):
                    self.msg = "For upward movement, " \
                               "the larger interval should come first"
                    return True
                # Downward: smaller interval should come first
                elif d < 0 and abs (d) > abs (next_d):
                    self.msg = "For downward movement, " \
                               "the smaller interval should come first"
                    return True
        return False
    # end def _check

# end class Check_Melody_laMotte_Jump

class Check_Melody_Jump_Magdalena (Check_Melody_Jump):
    """ If there are consecutive jumps:
        - Check how big the intervals are, generally: Not too large jumps
        - No more than 20 halftones in sum (absolute values)
          -> violations are scaled with the difference above 20
        - Big jumps are octave or sixth, no two big jumps in a row
    """
    jump_sum = 0

    def _check (self, current):
        self.current = current
        d = self.compute_interval ()
        if d is None:
            return False
        if d <= 2:
            jump_sum = 0
            return False
        jump_sum += abs (d)
        if not current.prev.prev:
            return False
        prev = current.prev
        prev_d = prev.halftone.offset - prev.prev.halftone.offset
        # No two big jumps in a row
        if abs (d) >= 8 and abs (prev_d) >= 8:
            self.ugliness = self.ugliness_1
            self.badness  = self.badness_1
            return True
        if jump_sum > 20:
            self.ugliness = self.ugliness_2 * (jump_sum - 20)
            self.badness  = self.badness_2
            return True
    # end def _check
# end class Check_Melody_Jump_Magdalena

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
        , octave     = False
        , signed     = False
        , not_first  = False
        , not_last   = False
        , exceptions = None
        ):
        self.interval   = set (interval or ())
        self.octave     = octave
        self.signed     = signed
        self.not_first  = not_first
        self.not_last   = not_last
        self.lookahead  = self.lookahead # copy from class
        self.exceptions = []
        self.prev_interval = [None, None]
        # Only keep applicable exceptions
        for exc in (exceptions or []):
            if not exc.interval or not self.interval:
                self.exceptions.append (exc)
                self.lookahead = max (self.lookahead, exc.lookahead)
                continue
            if self.interval.intersection (exc.interval):
                self.lookahead = max (self.lookahead, exc.lookahead)
                self.exceptions.append (exc)
        super ().__init__ (desc, badness, ugliness)
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        if self.not_first and (cf_obj.is_first and cp_obj.is_first):
            return False
        if self.not_last and (cp_obj.is_last and cf_obj.is_last):
            return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d in self.interval:
            if self.check_exceptions (cf_obj, cp_obj):
                self.prev_interval = [cf_obj, cp_obj]
                return False
            self.prev_interval = [cf_obj, cp_obj]
            return True
        self.prev_interval = [cf_obj, cp_obj]
        return False
    # end def _check

    def check_exceptions (self, cf_obj, cp_obj):
        """ Check if any exception applies """
        for exception in self.exceptions:
            if exception.applies (self, cf_obj, cp_obj):
                return True
        return False
    # end def check_exceptions

    def compute_interval (self, cf_obj, cp_obj):
        assert cf_obj.overlaps_with_bind (cp_obj)
        self.cf_obj = cf_obj
        self.cp_obj = cp_obj
        if not cf_obj.is_tone or not cp_obj.is_tone:
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
        assert cf_obj.overlaps_with_bind (cp_obj)
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
            p_obj = p_obj.prev_with_bind
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
        , stepped_bad_ugly = False
        ):
        # We keep a copy of badness, ugliness if we want to set it
        # depending on overflow
        self.badness_default  = badness
        self.ugliness_default = ugliness
        self.stepped_bad_ugly = stepped_bad_ugly
        self.maximum          = maximum
        super ().__init__ (desc, None, badness, ugliness, False, signed = True)
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        d = self.compute_interval (cf_obj, cp_obj)
        if d is not None and d > self.maximum:
            if self.stepped_bad_ugly:
                self.badness  = self.badness_default   * (self.maximum - d)
                self.ugliness = self.ugliness_default ** (self.maximum - d)
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
        # FIXME: If the contrapunctus is the lower voice this is different
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
        assert cf_obj.overlaps_with_bind (cp_obj)
        self.cp_obj = cp_obj
        self.cf_obj = cf_obj
        # First we must establish that cp_obj and cf_obj both start at
        # the same offset, otherwise we won't have a jump on both
        if cp_obj.bar.idx != cf_obj.bar.idx:
            return False
        if cp_obj.offset != cf_obj.offset:
            return False
        # None of the two notes may be bound: If they still start on the
        # same offset we would already have seen them
        if cp_obj.is_bound or cf_obj.is_bound:
            return False
        # Now that we've established they both start at same offset we
        # can get previous tone of both
        p_cp_obj = cp_obj.prev
        p_cf_obj = cf_obj.prev
        if not p_cp_obj or not p_cf_obj:
            return False
        if not cf_obj.is_tone or not p_cf_obj.is_tone:
            return False
        if not cp_obj.is_tone or not p_cp_obj.is_tone:
            return False
        d1 = abs (cf_obj.halftone.offset - p_cf_obj.halftone.offset)
        d2 = abs (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
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
        assert cf_obj.overlaps_with_bind (cp_obj)
        p_cp_obj = cp_obj.prev_with_bind
        p_cf_obj = cf_obj.prev_with_bind
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

class Check_Harmony_Akzentparallelen (Check_Harmony_Interval):
    """ Check for Akzentparallelen (accent parallels).
        These are parallels of perfect consonant intervals (unisons, fifths,
        and octaves) that occur from a strong beat in one measure to a strong
        beat in the next measure, even when there is contrary motion on the
        weak beats in between.
        From Kontrapunkt im Selbststudium und Unterricht, Thomas Krämer, 2012
        S. 89-90.
    """

    def __init__ (self, desc, badness = 0, ugliness = 0):
        # Perfect consonant intervals: unison, fifth, octave
        # (reduced to within octave because we set octave = True)
        intervals = {0, 7}
        super ().__init__ (desc, intervals, badness, ugliness, octave = True)
        self.reset ()
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        """ Check for accent parallels between strong beats across measures """
        assert cf_obj.overlaps_with_bind (cp_obj)

        # Only check on strong beats (offset 0 in a bar)
        if cf_obj.offset != 0 or cp_obj.offset != 0:
            return False

        # Need both to be tones
        if not cf_obj.is_tone or not cp_obj.is_tone:
            return False

        # Calculate current interval using parent's method with octave reduction
        current_interval = self.compute_interval (cf_obj, cp_obj)
        if current_interval is None:
            return False

        # Only check perfect consonant intervals (0=unison, 7=fifth)
        # Note that multiple octaves reduce to unison
        if current_interval not in self.interval:
            return False

        # Check if we have a previous strong beat interval that matches
        if self.prev_strong_interval == current_interval:
            assert self.prev_strong_interval in self.interval
            # This is an Akzentparallel
            return True

        # Store current interval for next check
        self.prev_strong_interval = current_interval
        return False
    # end def _check

    def reset (self):
        """ Reset the check state """
        self.prev_strong_interval = None
    # end def reset

# end class Check_Harmony_Akzentparallelen

class Check_Harmony_Nachschlagende_Parallelen (Check_Harmony_Interval):
    """ Check for nachschlagende Parallelen (also called Klapperoktaven).
        These are parallels of perfect consonant intervals (unisons, fifths,
        and octaves) that occur when one voice moves from an unaccented beat
        to an accented beat, creating parallel motion into perfect consonances.

        Kontrapunkt im Selbststudium und Unterricht, Thomas Krämer, 2012, p. 108
    """
    lookahead = 8

    def __init__ (self, desc, badness = 0, ugliness = 0):
        # Perfect consonant intervals: unison, fifth, octave
        # (reduced to within octave because we set octave = True)
        intervals = {0, 7}
        super ().__init__ (desc, intervals, badness, ugliness, octave = True)
        self.reset ()
    # end def __init__

    def _check (self, cf_obj, cp_obj):
        """ Check for nachschlagende parallels from weak to strong beats """
        assert cf_obj.overlaps_with_bind (cp_obj)

        # Only check on weak beats
        strong_beats = {0, 8}
        if cp_obj.offset in strong_beats:
            return False

        # Need both to be tones
        if not cf_obj.is_tone or not cp_obj.is_tone:
            return False

        # Calculate current interval using parent's method with octave reduction
        current_interval = self.compute_interval (cf_obj, cp_obj)
        if current_interval is None:
            return False

        # Only check perfect consonant intervals (0=unison, 7=fifth)
        if current_interval not in self.interval:
            return False

        # Need next tone, we take the current note length and add twice
        # that length. If that note that starts there is the same
        # interval the check is positive.

        duration = cp_obj.duration
        if duration not in {4, 8}:
            return False
        next_offset = cp_obj.offset + 8
        bar = cp_obj.bar
        while (bar.duration <= next_offset):
            next_offset -= bar.duration
            bar = bar.next
            if not bar:
                return False
        next_cp = bar.by_offset (next_offset)
        next_cf = cf_obj.bar.get_by_offset (next_cp)

        if not next_cf or not next_cp:
            return False
        if not next_cf.is_tone or not next_cp.is_tone:
            return False

        # Previous interval must also be a perfect consonance
        next_interval = self.compute_interval (next_cf, next_cp)
        if next_interval is None or next_interval not in self.interval:
            return False

        # Check that we have the same type of perfect consonance
        if current_interval != next_interval:
            return False

        return True
    # end def _check

    def reset (self):
        pass
    # end def reset

# end class Check_Harmony_Nachschlagende_Parallelen

class Harmony_Exception:
    """ Base class for exceptions to harmony rules.
        An exception can override a harmony check under certain conditions.
    """
    lookahead = 0
    consonant_allowed = (0, 3, 4, 7, 8, 9)
    consonant_octave  = True

    def __init__ (self, interval):
        self.interval = set (interval)
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        """ Check if this exception applies to the given objects.
            Should be overridden by subclasses.
            The 'parent' argument is the Check_Harmony_Interval instance.
            Returns True if the exception applies
            (i.e., the rule from which it is called should be ignored).
        """
        raise NotImplementedError ('Need applies method') # pragma: no cover
    # end def applies

    def is_consonant (self, p_cf_obj, p_cp_obj):
        interval = abs (p_cf_obj.halftone.offset - p_cp_obj.halftone.offset)
        if self.consonant_octave:
            interval %= 12
        if interval in self.consonant_allowed:
            return True
        return False
    # end def is_consonant

# end class Harmony_Exception

class Exception_Harmony_Passing_Tone (Harmony_Exception):
    """ If a note is reached by step and left by step in the *same*
        direction, it can be a dissonance as long as it's on a weak
        beat. Exception: hard passing tone (half-strong).
        From: Zweistimmiger Kontrapunkt -- Ein Lehrgang in 30 Lektionen,
        Thomas Daniel, 2002, S. 112-120.
    """
    lookahead = 1

    def __init__ \
        ( self, interval
        , octave         = True
        , note_length    = (1, 2)
        , bar_position   = None
        ):
        super ().__init__ (interval)
        self.octave       = octave
        self.note_length  = note_length
        self.bar_position = bar_position
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        assert cf_obj.overlaps_with_bind (cp_obj)

        d = parent.compute_interval (cf_obj, cp_obj)
        if d is None or d not in self.interval:
            return False

        # Check note length
        if cp_obj.length not in self.note_length:
            return False

        # Check bar position if specified
        if self.bar_position is not None:
            if cp_obj.offset not in self.bar_position:
                return False

        # Check if reached by step
        p_cp_obj = cp_obj.prev_with_bind
        if not p_cp_obj or not p_cp_obj.is_tone or not cp_obj.is_tone:
            return False

        prev_interval = abs \
            (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        if prev_interval > 2 or prev_interval == 0:
            return False

        # Check if left by step
        n_cp_obj = cp_obj.next_with_bind
        if not n_cp_obj or not n_cp_obj.is_tone:
            return False

        next_interval = abs \
            (n_cp_obj.halftone.offset - cp_obj.halftone.offset)
        if next_interval > 2 or next_interval == 0:
            return False

        # Check direction
        prev_dir = sgn (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        next_dir = sgn (n_cp_obj.halftone.offset - cp_obj.halftone.offset)

        if prev_dir != next_dir:
            return False

        p_cp_obj, p_cf_obj = parent.prev_interval
        if not self.is_consonant (p_cf_obj, p_cp_obj):
            return False
        # Prev CP tone length must be >= current tone length
        if p_cp_obj.duration < cp_obj.duration:
            return False

        # If we got here, it's a valid passing tone exception
        return True
    # end def applies

# end class Exception_Harmony_Passing_Tone

class Exception_Harmony_Wechselnote (Harmony_Exception):
    """ Exception for Wechselnoten (changing tones).
        These are melodic ornaments that can create dissonances but are allowed
        when they follow specific melodic patterns:
        - step away and back to same tone, dissonance on weak beat
        - must be on weak beats and move by step
        From: Zweistimmiger Kontrapunkt -- Ein Lehrgang in 30 Lektionen,
        Thomas Daniel, 2002, S. 112-120.
    """
    lookahead = 1
    consonant_allowed = (3, 4, 7, 8, 9, 12, 15, 16, 19, 20, 21)
    consonant_octave  = False

    def __init__ \
        ( self, interval
        , octave       = True
        , note_length  = (1, 2)  # eighth and quarter notes typically
        , bar_position = None    # weak beats only
        ):
        super ().__init__ (interval)
        self.octave       = octave
        self.note_length  = note_length
        self.bar_position = bar_position
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        assert cf_obj.overlaps_with_bind (cp_obj)

        d = parent.compute_interval (cf_obj, cp_obj)
        if d is None or d not in self.interval:
            return False

        # Must be on weak beats if bar_position is specified
        if self.bar_position is not None:
            if cp_obj.offset not in self.bar_position:
                return False

        # Check note length (typically short ornamental notes)
        if cp_obj.length not in self.note_length:
            return False

        # Need previous and next tones to check melodic pattern
        p_cp_obj = cp_obj.prev_with_bind
        n_cp_obj = cp_obj.next_with_bind
        if not p_cp_obj or not n_cp_obj:
            return False
        # If anything is a pause we don't need to check further
        if not p_cp_obj.is_tone or not cp_obj.is_tone or not n_cp_obj.is_tone:
            return False

        prev_interval = cp_obj.halftone.offset - p_cp_obj.halftone.offset
        next_interval = n_cp_obj.halftone.offset - cp_obj.halftone.offset

        # Both intervals must be steps (1 or 2 semitones)
        if not abs (prev_interval) <= 2 and abs (next_interval) <= 2:
            return False
        # Wechselnote: step away and back
        # (opposite directions, return to same tone)
        if  (   sgn (prev_interval) != sgn (next_interval)
            and prev_interval != 0 and next_interval != 0
            ):
            # Check if we return to the same tone
            total_movement = abs \
                (p_cp_obj.halftone.offset - n_cp_obj.halftone.offset)
            if total_movement != 0:  # Returns to same tone
                return False
        else:
            return False

        p_cp_obj, p_cf_obj = parent.prev_interval
        if not self.is_consonant (p_cf_obj, p_cp_obj):
            return False
        return True
    # end def applies

# end class Exception_Harmony_Wechselnote

class Exception_Harmony_Cambiata (Harmony_Exception):
    """ Exception for Cambiata (Nota cambiata or Fuxsche Wechselnote).
        The Cambiata is a five-tone melodic sequence where three tones
        must be consonances and one or two can be dissonances. The first
        and fifth tones must fall on strong beats and must be consonances.
        The sequence has a fixed order.

        Descending form: first tone is higher than the last
        step down, third down, step up, step up
        Ascending form: first tone is lower than the last
        step up, third up, step down, step down

        Note that for note_length 6: Only the first tone may be 6 long.

        From Schoenberg's "Harmonielehre" p. 42
        Zweite stehende Formel: Die Cambiata
    """
    lookahead = 4

    def __init__ ( self, interval, octave = True):
        super ().__init__ (interval)
        self.octave       = octave
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        current = cp_obj
        for k in range (3):
            current = current.prev_with_bind
            if current is None:
                return False
            cfo  = cf_obj.bar.get_by_offset (current)
            if self.check_cambiata (parent, cfo, current):
                return True
        return False
    # end def applies

    def check_cambiata (self, parent, cf_obj, cp_obj):
        """ We assume that we're called with the *first* tone of the cambiata
        """
        assert cf_obj.overlaps_with_bind (cp_obj)

        # Check if it's a tone
        d = parent.compute_interval (cf_obj, cp_obj)
        if d is None:
            return False

        # For Cambiata we need to check a sequence of 5 tones
        # Get the current and next 4 tones
        tones = []
        current = cp_obj
        tones.append (current)

        # Go forward 4 tones
        for _ in range (4):
            if current.next_with_bind and current.next_with_bind.is_tone:
                current = current.next
                tones.append (current)
            else:
                break

        # We need exactly 5 tones for a complete Cambiata
        if len (tones) != 5:
            return False

        # Check note length
        if tones [0].length not in [2, 4, 6]:
            return False
        if tones [4].length == 1:
            return False
        for idx in (1, 2, 3):
            if tones [idx].length not in [2, 4]:
                return False

        # Check if first and last tones are on strong beats
        first_tone = tones [0]
        last_tone = tones [4]

        # Strong beats are typically at offset 0 and 8 in a 8/4 measure
        strong_beats = {0, 4, 8, 12}
        if first_tone.offset not in strong_beats:
            return False
        if last_tone.offset  not in strong_beats:
            return False

        # Cambiata patterns (descending and ascending forms)
        # Descending: down step, down third, up step, up step
        # Ascending: up step, up third, down step, down step
        descending_pattern = [[-1, -2], [-3, -4], [ 1,  2], [ 1,  2]]
        ascending_pattern  = [[ 1,  2], [ 3,  4], [-1, -2], [-1, -2]]

        # Check the melodic pattern fits the characteristic Cambiata shape:
        intervals = []
        for i in range (len (tones) - 1):
            interval = tones [i+1].halftone.offset - tones [i].halftone.offset
            intervals.append (interval)

        def matches_pattern (intervals, pattern):
            if len (intervals) != len (pattern):
                return False
            for i, (actual, expected) in enumerate (zip (intervals, pattern)):
                if actual not in expected:
                    return False
            return True
        # end def matches_pattern

        # Check if it matches either Cambiata pattern
        if  (   not matches_pattern (intervals, descending_pattern)
            and not matches_pattern (intervals, ascending_pattern)
            ):
            return False
        # Verify that we have the right number of consonances/dissonances
        # At most 2 dissonances allowed in the 5-tone sequence
        # The first and last must be consonances
        dissonance_count = 0
        for n, tone in enumerate (tones):
            # Find corresponding CF tone for harmony check
            cf_tone = cf_obj.bar.get_by_offset (tone)
            if cf_tone and cf_tone.is_tone and tone.is_tone:
                interval = parent.compute_interval (cf_tone, tone)
                if interval is not None and interval in self.interval:
                    dissonance_count += 1
                    # first and last must be consonances
                    if n == 0 or n == 4:
                        return False

        # Allow if we have at most 2 dissonances (and at least one)
        if 0 < dissonance_count <= 2:
            return True

        return False
    # end def check_cambiata

# end class Exception_Harmony_Cambiata

class Exception_Harmony_Suspension (Harmony_Exception):
    """ Exception for Synkopendissonanz (suspension).
        A suspension follows a three-step process:
        1. Consonant preparation (at least a half note duration)
        2. Becomes dissonant when the other voice moves on a strong beat
        3. Resolves stepwise downward to consonance on the next weak beat

        Fourth or seventh suspensions are always in the upper voice.
        Second or ninth suspensions are always in the lower voice.

        Ganter p. 53, 54, Spuller p. 12, 13
    """
    lookahead = 1

    def __init__ (self, interval, octave = True):
        super ().__init__ (interval)
        self.octave = octave
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        assert cf_obj.overlaps_with_bind (cp_obj)

        # Check if it's a dissonance that this exception handles
        d = parent.compute_interval (cf_obj, cp_obj)
        if d is None or d not in self.interval:
            return False

        # Must be on a strong beat (heavy half note position)
        # Strong beats are at offset 0 and 8 in a 4/4 measure
        strong_beats = {0, 8}

        # The current location is the maximum of both combined offsets
        cp_off = (cp_obj.bar.idx, cp_obj.offset)
        cf_off = (cf_obj.bar.idx, cf_obj.offset)
        maxoff = max (cp_off, cf_off)
        if maxoff [1] not in strong_beats:
            return False

        # Must be at least a half note (minima) duration
        if cp_obj.length < 4:  # 4 = half note in our system
            return False

        # Check voice leading rules based on interval type
        if not self._check_voice_leading_rules (parent, cf_obj, cp_obj, d):
            return False

        # Step 1: Check consonant preparation
        chk = self._check_consonant_preparation
        if not (  chk (parent, cf_obj, cp_obj, False)
               or chk (parent, cf_obj, cp_obj, True)
               ):
            return False

        # Step 2: Check that dissonance occurs when other voice moves
        # This is already established: We know we have dissonance now,
        # we know the last interval was not dissonant and we know the CP
        # has not changed. So the CF must have moved.

        # Step 3: Check stepwise downward resolution
        if not self._check_stepwise_resolution (parent, cf_obj, cp_obj):
            return False

        return True
    # end def applies

    def _check_voice_leading_rules (self, parent, cf_obj, cp_obj, interval):
        """ Check that fourth/seventh suspensions are in upper voice,
            second/ninth suspensions are in lower voice
        """
        # Get the actual interval (not reduced to octave)
        cf_offset = cf_obj.halftone.offset
        cp_offset = cp_obj.halftone.offset
        actual_interval = cp_offset - cf_offset

        # Fourth (5 semitones) or seventh (10, 11 semitones) in upper voice
        if interval in {5, 10, 11}:
            return actual_interval > 0  # CP must be above CF

        # Second (1, 2 semitones) or ninth (1, 2 reduced) in lower voice
        elif interval in {1, 2}:
            # Check if it's actually a ninth (second + octave) or second
            return actual_interval < 0  # CP must be below CF for ninth or 2nd

        return False
    # end def _check_voice_leading_rules

    def _check_consonant_preparation (self, parent, cf_obj, cp_obj, use_cf):
        """ Step 1: Check that the suspension tone was introduced consonantly
            and held for at least a half note
        """
        # Ether the CP or the CF changes and the other is kept equal
        tone = cp_obj
        if use_cf:
            tone = cf_obj
        # Check the *previous* interval: The tone must be the same
        # halftone.
        prev_tone = parent.prev_interval [(use_cf + 1) % 2]
        if not prev_tone or not prev_tone.is_tone:
            return False

        # Must be the same pitch (tied or repeated)
        if prev_tone.halftone != tone.halftone:
            return False

        # The prev_tone must either be the same as tone or bound to it
        if prev_tone is not tone and not prev_tone.bind:
            return False

        # Must be at least a half note duration for preparation
        if prev_tone.length < 4:
            return False

        # Find the corresponding CF tone for the preparation
        prev_other = parent.prev_interval [use_cf]
        if not prev_other or not prev_other.is_tone:
            return False

        # The preparation must be consonant
        if use_cf:
            prep_interval = parent.compute_interval (prev_tone, prev_other)
        else:
            prep_interval = parent.compute_interval (prev_other, prev_tone)
        if prep_interval is None:
            return False

        # Consonant intervals (unison, third, fifth, sixth, octave)
        consonant_intervals = {0, 3, 4, 7, 8, 9}
        return prep_interval in consonant_intervals
    # end def _check_consonant_preparation

    def _check_stepwise_resolution (self, parent, cf_obj, cp_obj):
        """ Step 3: Check stepwise downward resolution to consonance
            on the next weak beat
        """
        next_cp = cp_obj.next_with_bind
        if not next_cp or not next_cp.is_tone:
            return False

        # Must resolve on a weak beat (not 0 or 8)
        weak_beats = {2, 4, 6, 10, 12, 14}
        if next_cp.offset not in weak_beats:
            return False

        # Must resolve downward by step (1 or 2 semitones)
        resolution_interval = cp_obj.halftone.offset - next_cp.halftone.offset
        if resolution_interval not in {1, 2}:
            return False

        # Find corresponding CF tone for resolution
        next_cf = cf_obj.bar.get_by_offset (next_cp)
        if not next_cf or not next_cf.is_tone:
            return False

        # next cf must be the same as cf
        if next_cf != cf_obj:
            return False

        # Resolution must be consonant
        res_interval = parent.compute_interval (next_cf, next_cp)
        if res_interval is None:
            return False

        # Consonant intervals
        consonant_intervals = {0, 3, 4, 7, 8, 9}
        return res_interval in consonant_intervals
    # end def _check_stepwise_resolution

# end class Exception_Harmony_Suspension

# Define passing tone exceptions
tone_exceptions = \
    [ Exception_Harmony_Passing_Tone
        ( interval       = (1, 2, 5, 6, 10, 11)
        , octave         = True
        , note_length    = (4,)
        , bar_position   = (4, 8, 12)
        )
    , Exception_Harmony_Passing_Tone
        ( interval       = (1, 2, 5, 6, 10, 11)
        , octave         = True
        , note_length    = (2,)
        , bar_position   = (2, 4, 6, 10, 12, 14)
        )
    , Exception_Harmony_Passing_Tone
        ( interval       = (1, 2, 5, 6, 10, 11)
        , octave         = True
        , note_length    = (1,)
        , bar_position   = (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15)
        )
    , Exception_Harmony_Wechselnote
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        , note_length    = (2,)  # quarter notes
        # weak beats:
        , bar_position   = (2, 6, 10, 14)
        )
    , Exception_Harmony_Wechselnote
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        , note_length    = (1,)  # eighth notes
        # weak beats:
        , bar_position   = (1, 3, 5, 7, 9, 11, 13, 15)
        )
    , Exception_Harmony_Cambiata
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        )
    , Exception_Harmony_Suspension
        ( interval       = (1, 2, 5, 10, 11)  # dissonant intervals
        , octave         = True
        )
    ]

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
        , msg_2   = 'Same-direction movement after jump'
        )
    ]

magi_melody_checks_cf = \
    [ Check_Melody_Interval
        ( "No seventh (Septime)"
        , interval = (10, 11)
        , badness  = BAD_MAX
        )
    , Check_Melody_Interval
        ( "No Devils interval"
        , interval = (6,)
        , badness  = BAD_MAX
        )
    , Check_Melody_Interval
        ("No unison (Prim) allowed"
        , interval =  (0,)
        , badness  = BAD_4
        , octave   = False
        )
    , Check_Melody_Interval
        ( "Small Sixth down, large sixth"
        , interval =  (-8, -9, 9)
        , badness  = BAD_2
        , signed   = True
        , octave   = False
        )
    , Check_Melody_laMotte_Jump
        ( "Jump according to laMotte rules"
        , badness      = BAD_MAX
        )
    , Check_Melody_Avoid_Notelen_Jump
        ( "Fourth should not be reached or left by large jumps"
        , limit        = 7
        , badness      = BAD_MAX
        , note_length  = 2
        )
    ]
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
        , msg_2   = 'Same-direction movement after jump'
        )
    ]

magi_melody_checks_cp = \
    [ Check_Melody_Interval
        ( "Small Sixth down, large sixth"
        , interval =  (-8, -9, 9)
        , badness  = BAD_2
        , signed   = True
        , octave   = False
        )
    , Check_Melody_Interval
        ( "No Devils interval"
        , interval = (6,)
        , badness  = BAD_MAX
        )
    , Check_Melody_Interval
        ("No unison (Prim) allowed"
        , interval =  (0,)
        , badness  = BAD_4
        , octave   = False
        )
    , Check_Melody_Interval
        ( "No seventh (Septime)"
        , interval = (10, 11)
        , badness  = BAD_MAX
        )
    , Check_Melody_laMotte_Jump
        ( "Jump according to laMotte rules"
        , badness      = BAD_MAX
        )
    , Check_Melody_Avoid_Notelen_Jump
        ( "Eighth should not be reached by jumps and should be followed by step"
        , badness      = BAD_MAX
        )
    , Check_Melody_Avoid_Notelen_Jump
        ( "Fourth should not be reached or left by large jumps"
        , limit        = 7
        , badness      = BAD_MAX
        , note_length  = 2
        )
    , Check_Melody_Note_Length_Jump
        ( "Don't jump between short notes"
        , note_length  = (1, 2)
        , badness      = BAD_8
        )
    , Check_Melody_Note_Length_Double_Jump
        ( "No double jumps between short notes"
        , note_length  = (1, 2)
        , badness      = BAD_MAX
        )
    , Check_Melody_Interval
        ( "Wenn zwei Vierteln auf leichter Taktzeit stehen und danach und"
          " davor längere Notenwerte sind, fallen sie schrittweise nach"
          " unten. (Daniel S.118)"
        , signed        = True
        , octave        = False
        , note_length   = (2,)
        , next_length   = (2,)
        , next2_length  = (4, 6, 8, 12, 16)
        , prev_length   = (4, 6, 8, 12, 16)
        , interval      = (-1, -2)
        , bar_position  = (5, 13)
        , next_interval = (-1, -2)
        , ugliness      = 5
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
        ( "Use no unisons except at the beginning or end"
        , interval   = (0,)
        , badness    = BAD_4
        , octave     = False
        , not_first  = True
        , not_last   = True
        , exceptions = tone_exceptions
        )
    , Check_Harmony_Interval
        ( "No Sekund"
        , interval = (1, 2)
        , badness  = BAD_MAX
        , octave   = True
        , exceptions = tone_exceptions
        )
    , Check_Harmony_Interval \
        ( "Magdalena: 5/6 verboten"
        , interval = (5, 6)
        , badness  = BAD_MAX
        , octave   = True
        , exceptions = tone_exceptions
        )
    , Check_Harmony_Interval \
        ( "Magdalena: 10/11 verboten"
        , interval = (10, 11)
        , badness  = BAD_MAX
        , octave   = True
        , exceptions = tone_exceptions
        )
    , Check_Harmony_Interval_Max
        ( "Distance between voices should not exceed Duodezime"
        , maximum  = 19
        , badness  = BAD_8
        , stepped_bad_ugly = True
        )
    , Check_Harmony_Interval_Min
        ( "Contrapunctus voice must be *up*"
        , minimum  = 0
        , badness  = BAD_MAX
        )
    , Check_Harmony_First_Interval
        ( "1.1. Begin and end on either unison, octave, fifth,"
          " unless the added part is underneath [it isn't here],"
          " in which case begin and end only on unison or octave."
        , interval = (0, 7, 12, -12)
        , badness  = BAD_MAX ** 2
        # FIXME: With Hypo the '7' is not allowed at all
        # So we need something like is_hypo here and instantiate two
        # different variants
        )
    , Check_Melody_Jump_2
        ( "Both voices may not jump"
        , badness  = BAD_MAX
        )
    , Check_Harmony_Melody_Direction
        ( "Magdalena: Ensure that the last direction"
          " (from where is the fifth or octave approached) is different."
        , interval = (0, 7, 12)
        , dir      = 'same'
        , badness  = BAD_2
        )
    , Check_Harmony_History
        ( "Magdalena: Avoid parallel unison, octaves, fifths"
        , interval = (0, 7, 12)
        , badness  = BAD_MAX
        )
    , Check_Harmony_History
        ( "For sext (sixth) don't allow several in a row"
        , interval = (8, 9)
        , ugliness = 1
        )
    , Check_Harmony_History
        ( "For terz (third) don't allow several in a row"
        , interval = (3, 4)
        , ugliness = 1
        )
    , Check_Harmony_History
        ( "For large third don't allow two or more (devil's interval)"
        , interval = (4,)
        , badness  = BAD_4
        )
    , Check_Harmony_Melody_Direction
        ( "Generally it's better that voices move in opposite"
          " direction (or one stays the same if allowed)"
        , interval = () # All
        , dir      = 'same'
        , ugliness = 0.1
        )
    , Check_Harmony_Akzentparallelen
        ( "Avoid Akzentparallelen"
          " (accent parallels of perfect consonances)"
        , badness = BAD_2
        )
    , Check_Harmony_Nachschlagende_Parallelen
        ( "Avoid nachschlagende Parallelen (Klapperoktaven)"
          " - parallels from weak to strong beats"
        , badness = BAD_2
        )
    ]

checks = dict \
    ( default = (old_melody_checks_cf, old_melody_checks_cp, old_harmony_checks)
    , special = ( magi_melody_checks_cf, magi_melody_checks_cp
                , magi_harmony_checks
                )
    )

__all__ = ['checks']
