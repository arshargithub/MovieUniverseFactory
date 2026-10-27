#188: repair a discriminated optimizer failure

187 did not actually deform: every step returned in one iteration withJacobian1
and cut errors growing to.4996m. It failed the attachment gate, and no target or
native candidate was produced. This is not evidence of an anatomically
impossible goal: its invalid-line-search branch returned1e30 with zero gradient,
which allowedL-BFGS to report termination while remaining at the start.

188 replaces that invalid branch with the smooth quadratic continuation of the
neo-Hookean log energy belowJ=.1, using the analytic cofactor derivative rather
than an inverse atJ=0. Actual inverted and nearcollapsed finite-difference tests
and a nontrivial soft-pin solve now test the previously missing behavior.
The finalJ(.02,5], <=.06m attachment and convergence guards remain unchanged.
Intermediate trial states may be inverted; no such state is an output/PASS.

Same cage, continuous actualsource cuttracking, fixedaccepted primaryaction,
raw neutral goal and static339only scope. No new artistic hypothesis inferred
from this repair. Actual asset numerical proof first, then separately admitted
native339 multi-view review; no fullmotion/cache/production qualification.
Original same-task max226 and no new resources/authority.
