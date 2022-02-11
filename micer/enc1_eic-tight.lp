rule(R) :- body(R,_).
rule(R) :- head(R,_).
atom(|A|) :- body(_,A).
atom(A) :- head(_,A).

% Pick essential rules
ic(R) :- e(R).

% Pick subset of rules
{ ic(R) : rule(R) }.

% Guess assignment
assign(A) | assign(-A) :- atom(A).

% Check inconsistency
sat(R,A) :- head(R,A).
sat(R,-A) :- body(R,A).
incons :- ic(R), assign(-X): sat(R,A).

:- not incons.

% Saturate
assign(A) :- incons, atom(A).
assign(-A) :- incons, atom(A).

#show ic/1.