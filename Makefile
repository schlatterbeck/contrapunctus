# To use this Makefile, get a copy of Release Tools
# git clone git@github.com:schlatterbeck/releasetool.git
# or from sourceforge:
# git clone git://git.code.sf.net/p/sfreleasetools/code sfreleasetools
# And point the environment variable RELEASETOOL to the checkout
ifeq (,${RELEASETOOL})
    RELEASETOOL=../releasetool
endif

README=README.rst
CONTRAPUNCTUS=circle.py gregorian.py gentune.py tune.py
SRC=Makefile setup.py $(README) $(CONTRAPUNCTUS:%.py=contrapunctus/%.py)

LASTRELEASE:=$(shell $(RELEASETOOL)/lastrelease -n)

USERNAME=schlatterbeck
PROJECT=contrapunctus
PACKAGE=contrapunctus
CHANGES=changes
NOTES=notes
VERSIONPY=$(PROJECT)/Version.py
VERSIONTXT=VERSION
VERSION=$(VERSIONPY) $(VERSIONTXT)
CMD_CONTRAPUNCTUS=python3 -m contrapunctus.gentune

all: $(VERSIONPY)

%.ps: %.abc
	abcm2ps -O $@ $<

%.pdf: %.ps
	ps2pdf $<

%.mid: %.abc
	abc2midi $< -o $@

%.abc: %.log
	$(CMD_CONTRAPUNCTUS) -vv -b -g $< > $@

clean:
	rm -f MANIFEST Version.py README.html VERSION
	rm -rf ${CLEAN} *.egg-info __pycache__ $(PACKAGE)/__pycache__

include $(RELEASETOOL)/Makefile-pyrelease
