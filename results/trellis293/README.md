# Canadian quota verified; GPU test blocked by live capacity

Continuation of293 after Director completes AWS login. Effective Canada Central On-Demand G/VT quota is8vCPUs. Request CASE_CLOSED alone was not treated as approval. Account281482331395 confirmed; no alternate account/region used.

## Work completed

- Reviewed and packaged the exact synthetic adapter/probe and pinned CuMesh/FlexGEMM/cubvh/Eigen source trees,2045 files/about3.6MB. No protagonist images, weights, production media, credentials or Git history uploaded.
- Prepared a single-worker bootstrap, isolated build environment and fixed synthetic probe. The original288 local tests plus five new shutdown-guard tests pass:31 total. **The worker bootstrap and CUDA extensions have NOT executed on AWS.**
- Reserved10USD inside the existing15USD ceiling before resource creation. Created a private encrypted temporary S3 bucket with public access blocked, narrowly scoped worker/guard roles, no-inbound security group and five-minute independent cloud watchdog. Invoked the watchdog successfully with zero workers; this tests invocation/selection, not a real termination. Local tests exercise expiration, hard lifetime and missing-expiry behavior.
- Live rates: g6.2xlarge L4/24GB1.08547USD/hour; fallback g5.2xlarge A10G/24GB1.34573USD/hour. Same8vCPU and two-hour maximum allocation. No larger instance, Spot reservation or US launch attempted.

## What failed

AWS rejected g6.2xlarge in Canada Central1a,1b,1d and g5.2xlarge in1a,1b with `InsufficientInstanceCapacity`. The service's suggestions of another zone were not reliable evidence of availability: each suggested alternative also failed. Every attempt was preceded by a no-existing-worker check; no GPU instance or EBS volume was created. This is a capacity shortage at the attempted times, not a quota denial, exporter failure or evidence about TRELLIS model quality.

## Protection and cost

Removed the private temporary bucket and its synthetic input, instance profile, both roles/policies, Lambda watchdog, event rule/target and no-inbound security group. The local source archives and manifests remain recoverable. Independent inventory verification is in `teardown-verification.json`; no production backup resources were changed. No instance created means0GPU compute charge. Small S3/API/Lambda support charges may apply; actual billing is not yet known. The ledger conservatively retains the10USD reservation pending reconciliation: **reserved is not spent**. Do not report a fabricated zero total or launch another paid session by clearing the ledger. Review actual/bounded ancillary liability and existing policy before the next attempt; cumulative ceiling remains15USD.

## Next move

Recommended: retry the same Canadian package when capacity returns, reconciling the prior support-charge reservation first. A US-region attempt is a Director-owned location choice, not an automatic fallback. No unattended retry/monitor is scheduled. On a successful future worker: verify CUDA/toolchain and prohibited-import checks, inspect actual GLBs in Blender and reopen them, retain resolved package hashes/notices, then terminate and verify teardown. Full inference/model access and protagonist-generation authority remain separate. Current CUDA/export gate is NOT_RUN, not qualified. Main Sikh actor/uncover remains the production dependency; no reason to reopen the accepted292 staging.

## Carry-forward learning

Quota is a permission ceiling, not a capacity guarantee. Check effective quota rather than support-case status; use idempotent single-worker requests, inspect for partial creation before a capacity retry, and bound alternate GPU choices by memory/function/rate rather than instance branding. Establish the independent shutdown guard before compute, but tear support resources down when capacity blocks the job. Preserve fixed source packages so a later capacity retry does not become a fresh dependency investigation. Our finite production knowledge pilot does not cover cloud capacity or runtime licensing automatically; this operational review remains a manual, source-bound supplement. A successful guard/test suite must never be promoted into a successful GPU exporter or an expressive character.

Engineering token usage and exact full-turn active time are unknown; operating capture begins after initial preflight. No source/model generation cost-per-actor can be inferred from this failed provisioning attempt. Local commits are not remote durability; no remote Git push or production-media S3 backup in this continuation.
