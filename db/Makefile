CXXFLAGS+=-std=c++23 -Wall -Wextra -O3 -flto -Werror=switch

all: sitcoms.html decades.html

title.basics.tsv.gz:
	curl https://datasets.imdbws.com/title.basics.tsv.gz -o $@

title.basics.tsv: title.basics.tsv.gz
	gunzip  $<

decades: decades.cc decades.hh title.basics.tsv.gz
	$(CXX) $(CXXFLAGS) -o $@ $<

sitcoms.html: sitcoms $(wildcard series/*.md)
	./sitcoms

decades.html: decades
	./decades

%.hh: %.hh.tt tt
	./tt $<

sitcoms: sitcoms.cc sitcoms.hh
	$(CXX) $(CXXFLAGS) -o $@ $< -llowdown -lm -fconcepts-diagnostics-depth=2

.PHONY: all
