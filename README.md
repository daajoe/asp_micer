# asp_micer

Create facts for MUS input encoding using chain of
- gringo --output=smodels
- lp2normal / lp2atomic / lp2lp
- lp_parse.py
(see folder micer).

- clingo see: https://anaconda.org/potassco/clingo
- lp2normal see: https://research.ics.aalto.fi/software/asp/lp2normal/


Essentials can be specified manually (as given in the encoding e(RULEID))
or marking essential rules lp_parse by generating ddd(...) atoms.


For input programs, see folder instances,
graphs were obtained from https://github.com/daajoe/transit_graphs.
