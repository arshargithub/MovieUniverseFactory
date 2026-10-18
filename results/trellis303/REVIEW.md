# TRELLIS303 — checkpoint recovery prepared; AWS capacity blocked

## Outcome

The recovery implementation and exact private payload are ready, but **no GPU
instance was created**. AWS returned `InsufficientInstanceCapacity` for both
g6e.xlarge and g6e.2xlarge in us-east-1a/b/c/d. Therefore decoder recovery,
repair/export and the matched1024 Blender comparison are **NOT_RUN**. This is
neither evidence against the recovery method nor a new model-quality result.
Do not reuse the old512 render as if it came from this test.

## Completed

-Bound and inspected the301 checkpoint:38,362 unique coordinates, matching
shape/texture locations, finite32-channel float32 features and unchanged SHA.
-Implemented decoder-only loading of the two exact pinned weights; no input
image, DINO encoder or sampling. Shape is saved immediately, full voxel source
before repair, then a separate process performs original repair/export.
-Added live allocated/reserved/free VRAM telemetry, private incremental checkpoint
uploads, a small GPU sparse-cache reconstruction control and fail-closed stages.
The GPU control is staged, not passed; local structural/control tests passed65.
-Prepared the matched9-view textured/clay Blender comparison and independent
reopen using the unchanged301 normalization, camera, light and opacity control.
-Fresh AWS account/rate/quota/AMI/hardware checks passed. Exact18,333,527-byte
payload approved, uploaded privately; expiry guard invoked successfully. Eight
capacity failures exhausted the two same-GPU host configurations that fit this
reservation with the specified contingency. No larger/different GPU, new region,
public service or additional paid inference was substituted.

## Budget and protection

Director explicitly approved3.50USD reservation under the conditional extra10;
retain the prior15USD liability conservatively, aggregate held ceiling18.50USD.
No GPU ran. Temporary staging costs and prior actual AWS billing remain unknown;
the reservation is not a statement that3.50USD was spent or refunded.

Cleanup and independent resource inventory are recorded in `cleanup.json` and
`teardown-verification.json`; closure requires every remaining-resource list to
be empty. Local latent checkpoint, frozen runtime payload and all failure evidence
remain on the SSD. The temporary S3 bucket is not a production backup. Scoped
implementation/design commits are local only; no new remote push or media backup.

## Learning and application

1. Preserve expensive stage outputs before native repair/export, not only before
neural decode.303's boundaries implement301's lesson; their GPU behavior is unrun.
2. Separate model, conversion, capacity and artistic failures. This pass is a
capacity block. Eight unavailable placements are not eight generated candidates.
3. Compare actual provider hardware properties, not nominal marketing GB. The
larger-host preflight initially rejected an incorrect48GiB expectation; exact
matching to the admitted45,776MiB L40S fixed the guard before any launch.
4. Keep reservation and observed cost separate. Do not reset a failed staging
episode's unknown ledger or silently assume its whole reserve is available again.
5. Before retry, recheck authentication, capacity, price, cleanup and the aggregate
ledger. Reuse this exact reviewed checkpoint/runtime; do not spend on resampling.

## Next concrete work package

**Recommended action:** retry this frozen checkpoint-recovery package when AWS
48GB capacity is available, after renewed resource/ledger admission. The desired
Director-visible result is one compact matched512/1024 comparison with a clear
static-source admission/rejection, not another infrastructure milestone.

Included: decode-only recovery, raw source capture, original repair/export,
matched front/oblique/profile/rear and clay review, technical reopen, teardown.
Excluded: new sampling, actor acceptance, body/rig/cloth integration, scene polish,
changes to accepted Sikhv03 or Pashtun, and automatic extra paid retries.

Exit: recovered viewable evidence with separated design/ensemble/technical/
performance verdicts, or a concrete failed stage with preserved evidence and a
method recommendation. Actual animated actor readiness remains blocked regardless
of static technical success. No Director taste decision is required by the
capacity failure; the integrated comparison remains unfinished.
