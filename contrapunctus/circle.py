#!/usr/bin/python3
# Copyright (C) 2017-2024
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
