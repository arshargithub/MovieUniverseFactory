#363 temporal ownership investigation — current evidence, not final acceptance

-31 actual phase images reveal orphaned reins at new310/322, despite correct
  contact at mapped source phase anchors.32 measures hand errors35/53cm and bit
  errors47/75cm. Camera-25deg independently supplies useful face/pole clearance.
-33 quaternion-hemisphere control flips6686 keys on29 tracks but has no benefit
  for those errors. Do not promote this control into the root cause.
-34 actual source fractional evaluation fails before any time changes. Thus
  nonlinear retiming alone was not the origin, although shared inverse-clock
  sampling remains mathematically necessary across sparse/dense consumers.
-35 bone-local matrices are smooth, no NLA/constraints/modifiers in that chain;
  actor world translation ramps by roughly half-metre then resets at integers.
-36 identifies obsolete fractional parent-support keys interleaved with newer
  replacement poses. Actual pivotY340=-.1827m, old340.9356=+.4358m,341=-.1583m.
-37 full-interval eligibility removes zero keys: individual tracks lack complete
  integer-key coverage. Failed preservation selection is retained, not waived.
-38 local bracketing removes3224 obsolete keys on62 tracks, with exactly zero
  change in190 measured integer world/head/grasp poses. Most source fractional
  contact errors drop below1mm;291.809(41mm) and346.192(262mm) remain where
  replacement-key coverage has gaps. This supports the causal explanation but
  fails the full guard; no phase render or completed result followed.
-39 is the current test: atomically bake the owned support/rider/horse/actor,
  material spear and17 rigid face/crown/beard attachments from their actual190
  original integer curve samples. Preserve outside keys, source native and190
  actual world/head/grasp poses; require source fractional8mm and new-clock
  source-pose0.2mm agreement before gesture/framing/render. Actual source integer
  worlds remain exact and fractional contact passes0.71mm. It then fails a guard
  counting retained outside keys as new allocation.
-40 retains39 source repair and all pose/contact guards, but counts positive
  incremental new keys against the same4million bound. Test pending here.

Carry forward: replacing animation requires explicit ownership of the whole
interval and removal/replacement of superseded keys, not adding another layer
of keys. Validate at newly consumed subframes before time edits, motion blur or
simulation. Integer-only render success can hide severe temporal defects.
An atomic bake with source-pose preservation is preferable to accumulating
local deletion thresholds. Preserve negative controls and actual failed source
samples, and keep the current adopted method separate from historical guesses.

The pure sparse/dense clock regression demonstrates a real noncommuting edit
counterexample; it does not prove which source defect caused this production
failure. Actual native controls above establish that causal attribution.
