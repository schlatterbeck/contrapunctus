# To use this Makefile, get a copy of Release Tools
# git clone git@github.com:schlatterbeck/releasetool.git
# or from sourceforge:
# git clone git://git.code.sf.net/p/sfreleasetools/code sfreleasetools
# And point the environment variable RELEASETOOLS to the checkout
ifeq (,${RELEASETOOLS})
    RELEASETOOLS=../releasetools
endif

README=README.rst
SRC=Makefile setup.py $(README) contrapunctus/*.py
LASTRELEASE:=$(shell $(RELEASETOOLS)/lastrelease -n)

USERNAME=schlatterbeck
PROJECT=contrapunctus
PACKAGE=contrapunctus
CHANGES=changes
NOTES=notes
VERSIONPY=$(PROJECT)/Version.py

all: $(VERSIONPY)

%.ps: %.abc
	abcm2ps -O $@ $<

%.pdf: %.ps
	ps2pdf $<

%.mid: %.abc
	abc2midi $< -o $@

clean:
	rm -f MANIFEST Version.py README.html
	rm -rf ${CLEAN} *.egg-info __pycache__

include $(RELEASETOOLS)/Makefile-pyrelease
