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
        prev = current.prev
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
        if self.next_length and self.next:
            if self.next.length not in self.next_length:
                return False
            if self.next2_length and self.next.next:
                if self.next.next.length not in self.next2_length:
                    return False
        if self.prev_length and self.prev:
            if self.prev.length not in self.prev_length:
                return False
            if self.prev2_length and self.prev.prev:
                if self.prev.prev.length not in self.prev2_length:
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
            d = self.compute_interval (self.next)
            if d is not None and d in self.next_interval:
                return True
        if self.prev_interval:
            d = self.compute_interval (self.prev)
            if d is not None and d in self.prev_interval:
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

class Check_Melody_Avoid_Eighth_Jump (Check_Melody_Interval):
    """ Eighth notes should not be reached by jumps and should be
        followed by step. (Ganter p. 90)
        We also allow a pause after or before a jump. And the check also
        doesn't match when the jump is the first or last thing in a tune.
        Note that the note length here by default is 1 (one eighth).
    """

    def __init__ (self, desc, note_length = (1,), badness = 0, ugliness = 0):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.note_length = note_length
    # end def __init__

    def _check (self, current):
        self.current = current

        # Check if current note fits the given length (typically 1/8)
        if current.length in self.note_length and current.is_tone:
            # Check if reached by jump
            if current.prev and current.prev.is_tone:
                prev_interval = abs \
                    (current.halftone.offset - current.prev.halftone.offset)
                if prev_interval > 2:  # More than a step
                    self.msg = "Eighth note should not be reached by a jump"
                    return True

            # Check if followed by jump
            # 1/8 never has a bind to the next note
            assert not self.bind
            if current.next and current.next.is_tone:
                next_interval = abs \
                    (current.next.halftone.offset - current.halftone.offset)
                if next_interval > 2:  # More than a step
                    self.msg = "Eighth note should be followed by a step"
                    return True
        return False
    # end def _check

# end class Check_Melody_Avoid_Eighth_Jump

class Check_Melody_Note_Length_Jump (Check_Melody_Interval):
    """ Jumps are preferred on half notes or longer (Daniel S.78)
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
            interval = abs \
                (current.halftone.offset - current.prev.halftone.offset)
            if interval > 2:  # It's a jump
                # Check if note length is shorter than preferred
                if current.length in self.note_length:
                    return True
        return False
    # end def _check

# end class Check_Melody_Note_Length_Jump

class Check_Melody_laMotte_Jump (Check_Melody_Jump):
    """ Implements laMotte's rules for jumps:
        - When jumping a minor sixth or octave, there must be a contrary
          motion before and after
        - For third, fourth and fifth jumps, movement in the same
          direction is allowed
        - For upward movement, the larger interval should come first
        - For downward movement, the smaller interval should come first
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
        if abs (d) == 8 or abs (d) == 9 or abs (d) == 12:
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
            if sgn (d) == sgn (next_d) and abs (next_d) > 1:
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
        self.exceptions = []
        # Only keep applicable exceptions
        for exc in (self.exceptions or []):
            if not exc.interval or not self.interval:
                self.exceptions.append (exc)
                continue
            if self.interval.intersection (exc.interval):
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
                return False
            return True
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
        assert cf_obj.overlaps (cp_obj)
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
        if not cf_obj.is_tone or not p_cf_obj.is_tone:
            return False
        if not cp_obj.is_tone or not p_cp_obj.is_tone:
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
        assert cf_obj.overlaps (cp_obj)

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

class Harmony_Exception:
    """ Base class for exceptions to harmony rules.
        An exception can override a harmony check under certain conditions.
    """

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

# end class Harmony_Exception

class Exception_Harmony_Passing_Tone (Harmony_Exception):
    """ If a note is reached by step and left by step in the *same*
        direction, it can be a dissonance as long as it's on a weak
        beat. Exception: hard passing tone (half-strong).
        From: Zweistimmiger Kontrapunkt -- Ein Lehrgang in 30 Lektionen,
        Thomas Daniel, 2002, S. 112-120.
    """

    def __init__ \
        ( self, interval
        , octave         = True
        , note_length    = (2,)
        , bar_position   = None
        ):
        super ().__init__ (interval)
        self.octave       = octave
        self.note_length  = note_length
        self.bar_position = bar_position
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        assert cf_obj.overlaps (cp_obj)

        # Check if it's a dissonance that this exception handles
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
        p_cp_obj = cp_obj.prev
        if not p_cp_obj or not p_cp_obj.is_tone or not cp_obj.is_tone:
            return False

        prev_interval = abs \
            (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        if prev_interval > 2:
            return False

        # Check if left by step in same direction
        n_cp_obj = cp_obj.next
        if not n_cp_obj or not n_cp_obj.is_tone:
            return False

        next_interval = abs \
            (n_cp_obj.halftone.offset - cp_obj.halftone.offset)
        if next_interval > 2:
            return False

        # Check direction
        prev_dir = sgn (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        next_dir = sgn (n_cp_obj.halftone.offset - cp_obj.halftone.offset)

        if prev_dir != next_dir:
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
        assert cf_obj.overlaps (cp_obj)

        # Check if it's a dissonance that this exception handles
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
        p_cp_obj = cp_obj.prev
        n_cp_obj = cp_obj.next
        if not p_cp_obj or not n_cp_obj:
            return False
        # If anything is a pause we don't need to check further
        if not p_cp_obj.is_tone or not cp_obj.is_tone or not n_cp_obj.is_tone:
            return False

        prev_interval = cp_obj.halftone.offset - p_cp_obj.halftone.offset
        next_interval = n_cp_obj.halftone.offset - cp_obj.halftone.offset

        # Both intervals must be steps (1 or 2 semitones)
        if abs (prev_interval) <= 2 and abs (next_interval) <= 2:
            # Wechselnote: step away and back
            # (opposite directions, return to same or nearby tone)
            if  (   sgn (prev_interval) != sgn (next_interval)
                and prev_interval != 0 and next_interval != 0
                ):
                # Check if we return to the same tone or close to it
                total_movement = abs \
                    (p_cp_obj.halftone.offset - n_cp_obj.halftone.offset)
                if total_movement <= 2:  # Returns to same or nearby tone
                    return True

        return False
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

    def __init__ ( self, interval, octave = True):
        super ().__init__ (interval)
        self.octave       = octave
    # end def __init__

    def applies (self, parent, cf_obj, cp_obj):
        current = cp_obj
        for k in range (3):
            current = current.prev
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
        assert cf_obj.overlaps (cp_obj)

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
            if current.next and current.next.is_tone:
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

# Define passing tone exceptions
passing_tone_exceptions = \
    [ Exception_Harmony_Passing_Tone
        ( interval       = (1, 2, 5, 6, 10, 11)
        , octave         = True
        , note_length    = (4,)
        , bar_position   = (4, 12)
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
        , bar_position   = (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15)
        )
    , Exception_Harmony_Wechselnote
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        , note_length    = (4,)  # half notes
        # half-weak beats
        , bar_position   = (4, 12)
        )
    , Exception_Harmony_Wechselnote
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        , note_length    = (2,)  # quarter notes
        # weak beats:
        , bar_position   = (2, 4, 6, 10, 12, 14)
        )
    , Exception_Harmony_Wechselnote
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
        , octave         = True
        , note_length    = (1,)  # eighth notes
        # weak beats:
        , bar_position   = (1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15)
        )
    , Exception_Harmony_Cambiata
        ( interval       = (1, 2, 5, 6, 10, 11)  # dissonances
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
        , signed  = True
        , octave  = False
        , interval = (9, -8)
        , badness  = 1.5
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
    , Check_Melody_laMotte_Jump
        ( "Jump according to laMotte rules"
        , badness = 1.5
        )
    , Check_Melody_Avoid_Eighth_Jump
        ( "Eighth should not be reached by jumps and should be followed by step"
        , badness      = 1.5
        )
    , Check_Melody_Note_Length_Jump
        ( "Jumps are preferred on half notes or longer"
        , note_length  = (1, 2)
        , badness      = 1.1
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
        , interval   = (0,)
        , badness    = 10.0
        , octave     = False
        , not_first  = True
        , not_last   = True
        , exceptions = passing_tone_exceptions
        )
    , Check_Harmony_Interval
        ( "No Sekund"
        , interval = (1, 2)
        , badness  = 10.0
        , octave   = True
        , exceptions = passing_tone_exceptions
        )
    , Check_Harmony_Interval \
        ( "Magdalena: 5/6 verboten"
        , interval = (5, 6)
        , badness  = 10.0
        , octave   = True
        , exceptions = passing_tone_exceptions
        )
    , Check_Harmony_Interval \
        ( "Magdalena: 10/11 verboten"
        , interval = (10, 11)
        , badness  = 10.0
        , octave   = True
        , exceptions = passing_tone_exceptions
        )
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
        ( "Magdalena: Ensure that the last direction"
          " (from where is the fifth or octave approached) is different."
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
    , Check_Harmony_Akzentparallelen
        ( "2.1.9: Avoid Akzentparallelen"
          " (accent parallels of perfect consonances)"
        , badness = 5.0
        )
    ]

checks = dict \
    ( default = (old_melody_checks_cf, old_melody_checks_cp, old_harmony_checks)
    , special = ( magi_melody_checks_cf, magi_melody_checks_cp
                , magi_harmony_checks
                )
    )

__all__ = ['checks']
