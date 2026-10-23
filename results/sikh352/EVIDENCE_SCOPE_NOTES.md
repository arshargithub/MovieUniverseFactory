#352 evidence scope corrections

The60/61 technical-save review reused a sentence saying “all190frames solved.”
Those garment jobs did not rerun the arm solver: they inherited59's190-frame
arm solve and changed only garment geometry/support. Their actual new evidence
is `cloth352.json`, save/reopen, hashes and protected-owner checks. The sentence
must not be interpreted as a new motion or collision validation. Original review
records remain immutable; this note narrows their meaning explicitly.

59 PASS records are **sampled bare anatomy/hand-contact checks only**. They do
not close the full supporting-appearance `form` requirement, qualify full-speed
motion, or establish acceptance of face/turban/tack/crowd. The generic shared
requirement names are too coarse to express this distinction alone; observations,
current retained form gates and this explicit scope must govern continuation.
60 immediately retained the full form failure before garment admission. Future
workflow work should consider separate subproof and deliverable requirement IDs;
this pass does not broaden scope to implement that controller change.

The precise288 wrist extremum was inspected in60's bare-side control. Other60
bare-side frames were rendered but not separately claimed reviewed.60 contact
was intentionally not rendered after the front/reverse clothing failures.
