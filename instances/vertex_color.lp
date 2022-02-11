vertex(X) :- edge(X,_); edge(_,X).

g(X) :- vertex(X), not b(X), not r(X).
r(X) :- vertex(X), not b(X), not g(X).
b(X) :- vertex(X), not g(X), not r(X).

%no edge same color
:- edge(X,Y), g(X), g(X).
:- edge(X,Y), b(X), b(X).
:- edge(X,Y), r(X), r(X).