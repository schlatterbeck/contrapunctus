#!/usr/bin/python3
# Copyright (C) 2024
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
from .tune    import sgn

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
        raise NotImplementedError ('Need compute_description method')
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
        , only_repeat = False
        ):
        super ().__init__ (desc, badness, ugliness)
        self.interval    = set (interval)
        self.signed      = signed
        self.octave      = octave
        self.only_repeat = only_repeat
        self.reset ()
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
        d = self.current.halftone.offset - prev.halftone.offset
        if not self.signed:
            d = abs (d)
        if self.octave:
            d %= 12
        return d
    # end def compute_interval

    def reset (self):
        self.current    = None
        self.prev_match = False
    # end def reset

# end class Check_Melody

class Check_Melody_Interval (Check_Melody):
    """ Check on the progression of a melody
        This compares two consecutive tones of a voice.
        We keep a history of the last tone.
    """

    def _check (self, current):
        prev = current.prev
        if not prev:
            return False
        self.current = current
        d = self.compute_interval ()
        if d in self.interval:
            rv = True
            if self.only_repeat and not self.prev_match:
                rv = False
            self.prev_match = True
            return rv
        self.prev_match = False
        return False
    # end def _check

# end class Check_Melody_Interval

class Check_Melody_Jump (Check_Melody):

    def __init__ (self, desc, badness = 0, ugliness = 0, limit = 2):
        super ().__init__ (desc, (), badness, ugliness, True, False)
        self.limit = limit
    # end def __init__

    def _check (self, current):
        self.current = current
        if not current.prev:
            return False
        d = self.compute_interval ()
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
        if self.not_first and not cf_obj.prev and not cp_obj.prev:
            return False
        if self.not_last  and not cf_obj.next and not cp_obj.next:
            return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d in self.interval:
            return True
        return False
    # end def _check

    def compute_interval (self, cf_obj, cp_obj):
        self.cf_obj = cf_obj
        self.cp_obj = cp_obj
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
    """
    def _check (self, cf_obj, cp_obj):
        # Only check for the very first object
        # Not sure if this holds for *all* cp_objects in the first bar,
        # if this should be the case we need to use cf_obj below.
        if cp_obj.prev:
            return False
        d = self.compute_interval (cf_obj, cp_obj)
        if d not in self.interval:
            return True
        return False
    # end def _check

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
        if d > self.maximum:
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
        if d < self.minimum:
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
        if not self.p_cf_obj:
            self.p_cf_obj = self.cf_obj = cf_obj
            self.p_cp_obj = self.cp_obj = cp_obj
            return False
        self.cf_obj = cf_obj
        self.cp_obj = cp_obj
        d1 = cf_obj.halftone.offset - self.p_cf_obj.halftone.offset
        d2 = cp_obj.halftone.offset - self.p_cp_obj.halftone.offset
        self.p_cf_obj = cf_obj
        self.p_cp_obj = cp_obj
        if d1 > self.limit and d2 > self.limit:
            return True
        return False
    # end def _check

    def reset (self):
        self.p_cf_obj = None
        self.p_cp_obj = None
    # end def reset

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
        p_cp_obj = cp_obj.prev
        if not p_cp_obj:
            return False
        self.cf_obj = cf_obj
        self.cp_obj = cp_obj
        d = self.compute_interval (cf_obj, cp_obj)
        # An empty interval matches everything
        if  (   (not self.interval or d in self.interval)
            and self.direction_check ()
            ):
            if not self.only_repeat or self.prev_match:
                self.prev_match = True
                return True
        return False
    # end def _check

    def compute_interval (self, cf_obj, cp_obj):
        p_cp_obj = cp_obj.prev
        p_cf_obj = cf_obj.bar.get_by_offset (p_cp_obj)
        self.dir_cf = sgn (cf_obj.halftone.offset - p_cf_obj.halftone.offset)
        self.dir_cp = sgn (cp_obj.halftone.offset - p_cp_obj.halftone.offset)
        return super ().compute_interval (cf_obj, cp_obj)
    # end def compute_interval

    def direction_check (self):
        if self.dir == 'same':
            # Sign must be positive or negative not 0 (no direction)
            return self.dir_cf and self.dir_cf == self.dir_cp
        elif self.dir == 'different':
            return self.dir_cf == self.dir_cp
        elif self.dir == 'zero':
            return self.dir_cf == self.dir_cp == 0
        else:
            assert 0
    # end def direction_check

    def reset (self):
        self.prev_match = False
    # end def reset

# end class Check_Harmony_Melody_Direction

__all__ = [ 'Check_Melody_Interval', 'Check_Melody_Jump'
          , 'Check_Harmony_Interval', 'Check_Harmony_First_Interval'
          , 'Check_Harmony_Interval_Max', 'Check_Harmony_Interval_Min'
          , 'Check_Melody_Jump_2', 'Check_Harmony_Melody_Direction'
          , 'Check_Harmony_History'
          ]
