{ g(X,Y); b(X,Y); r(X,Y) } :- edge(X,Y).
:- g(X,Y), b(X,Y).
:- g(X,Y), r(X,Y).
:- r(X,Y), b(X,Y).
%not coloring 2 outgoing edges the same
:- g(X,Y), g(X,Z), Y < Z.
:- b(X,Y), b(X,Z), Y < Z.
:- r(X,Y), r(X,Z), Y < Z.