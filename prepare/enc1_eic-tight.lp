rule(R) :- body(R,_).
rule(R) :- head(R,_).
atom(|A|) :- body(_,A).
%atom(-A) :- body(_,A), A<0.
atom(A) :- head(_,A).

% Pick essential rules
ic(R) :- e(R).
%:- e(R), not ic(R).

% Pick subset of rules
{ ic(R) : rule(R) }.

% Guess assignment
assign(A) | assign(-A) :- atom(A).

% Check inconsistency
sat(R,A) :- head(R,A).
sat(R,-A) :- body(R,A).
incons :- ic(R), assign(-X): sat(R,A).

% Check support for every atom
incons :- assign(X), X > 0, bodyusat(R) : ic(R), head(R,X).
bodyusat(R) :- assign(-X), body(R,X).

:- not incons.

% Saturate
assign(A) :- incons, atom(A).
assign(-A) :- incons, atom(A).

#show ic/1.