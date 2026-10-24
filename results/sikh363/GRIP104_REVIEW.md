#104 method revision after actual103 rejection

103 still visibly reads as a claw, despite zero wrist drift/length error and a
tiny thumb endpoint error. Reject. Actual joint flexion remains too open; move
thumb target to the curled middle index rather than proximal segment. Proposed
second variant uses1.45/1.60/.90 radians, actual origins/lengths, opposed thumb.
This may still self-intersect or misread; actual hand crops veto the method.

The pose is constant in wrist space: solve once at283, preserve those local
transforms in existing150 curves, then verify190 actual wrist poses. Rebase the
existing rein endpoint through fixed70percent hand-side weighting, bulk-updating
existing keyed points rather than repeatedly inserting100,000 channel keys.
Source/posture preservation remains numeric evidence, never a visible fist pass.

Horse corrective hypothesis is falsified: all three values0, no drivers and
zero evaluated change from muting at283/327. Retain that report; remove duplicate
no-op rendered comparisons from this revision. Inspect actual chest rest versus
posed source coordinates/weights and correctly framed side before touching it.
Do not inherit the first wrong side-crop PASS text. Sol only, no new authority.
