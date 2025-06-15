CXXFLAGS=-std=c++23 -Wall -Wextra -O2

all: sitcoms.html decades

title.basics.tsv.gz:
	curl https://datasets.imdbws.com/title.basics.tsv.gz -o $@

title.basics.tsv: title.basics.tsv.gz
	gunzip  $<

decades: decades.cc title.basics.tsv.gz
	$(CXX) $(CXXFLAGS) -o $@ $<

sitcoms.html: sitcoms $(wildcard series/*.md)
	./sitcoms

%.hh: %.hh.tt tt
	./tt $<

sitcoms: sitcoms.cc sitcoms.hh
	$(CXX) $(CXXFLAGS) -o $@ $< -llowdown -lm -fconcepts-diagnostics-depth=2

.PHONY: all
