all: 23.pdf 23.mid

%.ps: %.abc
	abcm2ps -O $@ $<

%.pdf: %.ps
	ps2pdf $<

%.mid: %.abc
	abc2midi $< -o $@
