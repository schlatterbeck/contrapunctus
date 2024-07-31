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

import os.path
from setuptools import setup

if os.path.exists ("VERSION"):
    with open ("VERSION", 'r', encoding="utf8") as f:
        __version__ = f.read ().strip ()
else:
    __version__ = '0+unknown'

description = []
with open ('README.rst', encoding="utf8") as f:
    description = f.read ()

license = 'GNU General Public License v2 or later (GPLv2+)'

setup \
    ( name         = 'contrapunctus'
    , version      = __version__
    , description  = 'Experimenting with automatic musical composition'
    , packages     = ['contrapunctus']
    , author       = "Magdalena Schlatterbeck; Ralf Schlatterbeck"
    , author_email = "rsc@runtux.com"
    , url          = "https://github.com/schlatterbeck/contrapunctus"
    , platforms    = 'Any'
    , license      = license
    , classifiers  = \
        [ 'Development Status :: 3 - Alpha'
        , 'Intended Audience :: Education'
        , 'Intended Audience :: Science/Research'
        , 'License :: OSI Approved :: ' + license
        , 'Operating System :: OS Independent'
        , 'Programming Language :: Python'
        , 'Programming Language :: Python :: 3'
        , 'Programming Language :: Python :: 3.7'
        , 'Programming Language :: Python :: 3.8'
        , 'Programming Language :: Python :: 3.9'
        , 'Programming Language :: Python :: 3.10'
        , 'Programming Language :: Python :: 3.11'
        , 'Programming Language :: Python :: 3.12'
        , 'Programming Language :: Python :: 3.13'
        , 'Topic :: Education'
        , 'Topic :: Games/Entertainment'
        , 'Topic :: Scientific/Engineering :: Artificial Intelligence'
        , 'Topic :: Multimedia'
        , 'Topic :: Multimedia :: Sound/Audio'
        , 'Topic :: Multimedia :: Sound/Audio :: MIDI'
        , 'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
        ]
    , install_requires = ['rsclib', 'pgapy']
    , python_requires  = '>=3.10'
    , entry_points     = dict
        ( console_scripts =
            ['contrapunctus=contrapunctus.gentune:main']
        )
    , long_description_content_type = 'text/x-rst'
    , long_description = ''.join (description)
    )
