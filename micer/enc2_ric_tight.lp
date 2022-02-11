% IC atoms
icatm(|A|) :- atom(A), body(R,A) : ic(R).
icatm(A) :- atom(A), head(R,A) : ic(R).

% Guess assignment for IC without R
assign(A,R) | assign(-A,R) :- icatm(A), ic(R).

% Check consistency for IC without R
:- ic(R), ic(R2), R != R2,
   assign(-A,R) : sat(R2,A).