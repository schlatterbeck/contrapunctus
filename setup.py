#!/usr/bin/python3
import sys
from setuptools import setup
try :
    from Version    import VERSION
except :
    VERSION = None

description = []
with open ('README.rst') as f :
    description = f.read ()

setup \
    ( name         = 'contrapunctus'
    , version      = VERSION
    , description  = 'Experimenting with automatic musical composition'
    , packages     = ['contrapunctus']
    , author       = "Magdalena Schlatterbeck; Ralf Schlatterbeck"
    , author_email = "rsc@runtux.com"
    , url          = "https://github.com/schlatterbeck/contrapunctus"
    , platforms    = 'Any'
    , classifiers  = \
        [ 'Development Status :: 3 - Alpha'
        , 'Intended Audience :: Education'
        , 'Intended Audience :: Science/Research'
        # FIXME: License
        , 'Operating System :: OS Independent'
        , 'Programming Language :: Python'
        , 'Topic :: Education'
        , 'Topic :: Games/Entertainment'
        , 'Topic :: Scientific/Engineering :: Artificial Intelligence'
        , 'Topic :: Multimedia'
        , 'Topic :: Multimedia :: Sound/Audio'
        , 'Topic :: Multimedia :: Sound/Audio :: MIDI'
        , 'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
        ]
    , install_requires = ['rsclib', 'pgapy']
    , python_requires  = '>=3.7'
    , entry_points     = dict
        ( console_scripts =
            ['contrapunctus=contrapunctus.gentune:main']
        )
    , long_description_content_type = 'text/x-rst'
    , long_description = ''.join (description)
    )
