# Controlled head-quality comparison — outcome on continuation302

## Decision

The controlled investigation produced a useful negative export result and a narrower runtime blocker, **not a production-ready Sikh head**. Preserve the approved Sikh v03 direction and accepted Pashtun; do not put the failed512 source into the sequence as a finished actor. The1024 source-quality comparison is **NOT_RUN**, because no1024 mesh reached export.

| Control | Observed result | What it establishes |
|---|---|---|
| Same512 source, alpha enabled | Patchy/translucent facial hair; rejected | Transparency is not the rescue |
| Same512 source,300k/2K versus1M/2K | More beard relief, malformed eyes and slab-like moustache remain | Final polygon reduction is not the whole problem |
| Same1M geometry/UVs,2K versus4K | Little useful visual difference at matched480x600 review size | Larger atlas alone is not the rescue |
| Same input/seed/default samplers,1024 cascade on48GB L40S | Sampling completed; both decoders returned; CuMesh initialization for hole repair failed with CUDA OOM | The earlier24GB shape-decoder barrier moved, but complete1024 delivery remains unqualified |

See [export review](EXPORT_REVIEW.md) for the nine matched textured/clay views, actual face counts and independent native reopen. None of these controls is a benchmark of TRELLIS's best possible visual output. We have not tested alternate seeds, input preparation or sampler parameters here.

## Exact1024 evidence

- One actual worker: `i-0fdc266d5cc5b0883`, `g6e.xlarge`, US East1a, NVIDIA L40S,47,665,709,056 exposed GPU bytes. The larger-host2xlarge requests returned insufficient capacity; no second GPU ran.
- Same admitted input SHA256 `7f74def2304b885d029c8cf427f027e88f6b2ca0fbc5c5067a8674ebb7e99008`, seed298, `1024_cascade`, no sampler overrides, pinned runtime/weights and approved private payload. No new provider, public upload or rights route.
- Inference preflight PASS; pipeline loading83.784s; generation attempt243.105s. These exclude instance setup/download/build time and are not total engineering time.
- Recorded PyTorch peak33,230,480,384 bytes. This is a peak, not the live allocation at failure, and excludes CuMesh's direct CUDA allocations. CUDA-free bytes, allocator-reserved bytes and requested CuMesh allocation size were not captured; therefore cache pressure versus genuinely excessive live geometry is **not resolved**.
- Trace: `decode_latent` calls `decode_shape_slat`, then `decode_tex_slat`, then `m.fill_holes`; failure is `CuMesh.init` → direct `cudaMalloc` in `utils.h:43`. This establishes execution reached repair initialization, not that the unsaved decoded mesh looked good or was valid.
- The11,048,600-byte pre-decode safetensors file and metadata were privately uploaded before decode, independently retrieved, and hash-verified: `1676894daec0ef9006db5ecc6abf2251b4eca41882ed378c6acbc8652aadfbc6`. The final9,436,944-byte diagnostic archive was also retrieved. No decoded mesh or GLB was recovered.
- Checkpoint contains plain shape/texture features and coordinates, shape/scale metadata and provenance. Sparse caches were not saved. Reconstruction equivalence must be tested before calling it a validated replay; a hash proves file integrity, not decoder equivalence.
- Raw evidence: `.runtime/trellis301/cascade/retrieved/evidence/`; independently downloaded checkpoint: `.runtime/trellis301/cascade/checkpoint/`; exact returned inventory: [retrieved manifest](cloud-1024/retrieved-manifest.json). No secrets were passed to Blender or included in the approved payload.

## Recommended next work package: checkpoint-to-mesh recovery

**Audience-visible outcome:** an honest matched1024 versus512 head comparison, and only if it clears source admission, a coherent Sikh reveal candidate that belongs beside the accepted Pashtun. This immediate package ends at static source admission, not body/rig/cloth or actor acceptance.

**Recommended method:** preserve the already sampled1024 intent and separate neural decoding from native mesh repair/export. Do not buy a larger GPU or regenerate another random head as the first response.

1. Prepare a reviewed decode-only path locally. Reconstruct the two sparse tensors with the recorded shape/scale/dtypes and prove round-trip equivalence on a small control. Load only the required decoders; do not load DINO, sampling models or rerun sampling.
2. Decode and save vertices/faces plus voxel attributes/coordinates **before** hole repair, using the same numerical settings. Capture process/GPU free memory, PyTorch allocated/reserved/peak and geometry counts at each boundary.
3. Release decoder/substructure/cache state; prefer a fresh process for repair/export so cached framework allocations cannot silently compete with native CUDA buffers. A cheap diagnostic may test explicit cache release, but do not claim that alone is a demonstrated fix.
4. Preserve the existing repair/export semantics for comparison. If a changed reconstruction or bypass is necessary, retain both raw and converted geometry and label that changed variable; never silently skip a failing validation.
5. Reuse the prepared fixed-camera/scale/light Blender comparison, inspect all nine textured/clay views and approved references. Explicitly inspect eyes/lids, moustache/beard volume, turban crown/rear and same-film coherence. Technical output is not an artistic pass; motion and connected-cloth performance stay NOT_RUN.

**Resources/authority:** local design/tests need no new subscription or provider. A further GPU recovery run is not part of this completed single-worker dispatch. Admit it separately only after offline tests, exact payload scope, residual-resource check, current price and cumulative cost reconciliation. Do not silently activate the conditional extra10USD. Current run's3.50USD hold remains conservative until billing reconciliation; actual total invoice is unknown.

**Internal exit/replan:** return a verified source comparison or a specific evidenced decode/repair/export blocker. A new OOM without boundary telemetry or recoverable raw output is not an acceptable repeat. No blind seed/step/resolution tournament, full-body generation, character-design change or production acceptance in this package.

## Carry-forward learnings

1. **Treat generation, mesh conversion and actor construction as separate products.** A failed exporter does not prove weak generation; a good static surface does not prove animation readiness. Keep distinct verdicts and recovery checkpoints.
2. **Mixed GPU allocators need explicit lifetime boundaries.** More VRAM moved the failure but did not solve the end-to-end path. Direct native allocations can fail while framework peak metrics look below device capacity. Capture the right measurements, preserve raw stage outputs and isolate processes before escalating hardware again.
3. **Controlled comparisons reduce expensive guesswork.** Holding source/geometry/UVs fixed showed that export density/atlas/opacity were not sufficient; do not repeat those knobs as cosmetic optimism.
4. **Checkpoint before destructive or expensive transitions.** The predecode checkpoint survived this failure and may avoid regeneration; the missing pre-repair decoded checkpoint is the next required boundary. Retrieval/hash verification precedes temporary deletion.
5. **Budget guards are safety, not artistic deadlines.** No time-based relaxation of the quality bar occurred. The worker failed in minutes of inference, not because its lifetime cap forced a creative compromise.
6. **Deliver usable scene footage explicitly.** The Director missed the scene300 render; direct22s Sikh and42s joined links were surfaced on302. A report or queued panel alone is not proof the user saw a clip.

## Protection and closure

Cloud teardown verification and final cost bounds are appended below after independent inventory. All previous failed sources and accepted masters remain unchanged. Current Git protection and native/media recovery coverage are separate: checkpoint300 source/text through `0f9dde1` was pushed and verified; later implementation/evidence are local until the next authorized checkpoint. Git does not protect ignored native assets/media. This temporary bucket is not a durable production backup.

Independent inventory at2026-10-18T05:28:35.608882UTC found **zero remaining instances, buckets, roles, profiles, functions, rules, security groups or volumes** belonging to this1024 test. See [teardown receipt](cloud-1024/teardown-verification.json). Only the explicitly approved temporary test resources were deleted, after verified local retrieval; accepted production files were not removed. The cloud staging copy is gone; returned diagnostics/checkpoint remain recoverable locally, not yet in a new durable off-device backup.

The conservative launch-to-verification lifetime upper is1857.609s at1.861USD/hour: **0.960281USD compute upper**, not an invoice or all-in cost. Both301workers together have1.326313USD compute upper; setup, downloads/builds and shutdown delay are included in these lifetime bounds. The original15USD cumulative admission bound remains11.50closed conservative liabilities plus the unchanged3.50current reservation. Extra10USD inactive; actual total billing unknown. No spare budget is inferred from the compute-only figure.

Cleanup removed resources successfully, then its duplicate unknown-cost settlement conflicted with the earlier pre-launch staging cleanup's unknown settlement(responseIDnull). The ledger correctly rejected replacing it with another unknown settlement tied to the instance. Preserve the original event/hash chain and3.50hold; record the worker linkage and verified resource closure separately in `cloud-1024/budget-reconciliation.json`. This is not a new charge, refund or permission to reuse a spent allowance. Future staging cleanup should not prematurely settle a never-launched reservation that may continue under exact consent.
