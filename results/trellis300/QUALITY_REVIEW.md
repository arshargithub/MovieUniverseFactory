# TRELLIS300 — quality ceiling and next controlled proof

## Finding

**The 512 result is not TRELLIS's demonstrated quality ceiling.** We tested one prepared image, seed 298, default samplers and a limited export configuration. The 1024 attempt failed before returning a mesh, so there is no 512-versus-1024 quality comparison. Exchange 298's rejection of the current head as a production actor remains valid; its recommendation to proceed directly to local actor conversion is superseded by this controlled-quality investigation. This is research, not authorization or execution of another GPU run.

Director-approved Sikh v03 remains art-direction authority; the accepted Pashtun supplies same-film quality context. Neither a higher polygon count nor successful inference is actor admission. Eyes/lids, beard behavior, topology, continuous turban/face-cover mechanics and actual reveal performance remain separate interfaces.

## What was actually run

- Source commit75fbf0183001ed9876c8dbb35de6b68552ee08bd; model revisionaf44b45f2e35a493886929c6d786e563ec68364d.
- Prepared RGBA input `.runtime/art-direction/series01-sikh295/head-input-v01.png`, SHA2567f74def2304b885d029c8cf427f027e88f6b2ca0fbc5c5067a8674ebb7e99008; seed298.
- Pinned pipeline configuration fetched read-only from the exact public model revision and its SHA256 independently matched the recorded weight manifest:222c359ab1ed9bc6735a640a34f95d47f8681b9bc4aaa101bfb80274676253c6. The worker supplies no sampler overrides.
- Structure:12steps, guidance7.5, rescale0.7, interval0.6–1.0, timestep rescale5. Shape:12steps, guidance7.5, rescale0.5, interval0.6–1.0, timestep rescale3. Texture:12steps, guidance1, rescale0, interval0.6–0.9, timestep rescale3.
-512 pipeline generated a source in183.897s, excluding setup/export.1024 used `1024_cascade`, not direct1024.
- Both used `low_vram=True`; export target300k triangles,2K atlas for512 and planned4K for1024. The latter export was never reached.
- Corrected export-only298d used unsigned narrow-band reconstruction, band1/project0, approximately298k final triangles and2K textures. Raw and reconstructed dense sources remain preserved. Its GLB SHA256 is9678b00014314123640e9a5437ae81f738e143d30d528a2df1f5f6e8fc11d915.

## 1024 failed on memory capacity before quality could be assessed

`build.log:187–248` in `.runtime/trellis298c/retrieved/evidence/` shows all sampling stages completed; shape decoding failed at FP32 layer normalization. The failed allocation requested 7.97 GiB; visible GPU capacity was 22.03 GiB, with 2.45 GiB free, 19.14 GiB actively allocated by PyTorch and about 209 MiB reserved but unused. This predominantly indicates live activation pressure, not allocator fragmentation. `expandable_segments` was already enabled.

The worker deletes512 outputs, latents, mesh and GLB and empties the CUDA cache before1024. Retained512 outputs are not an established cause. Separate processes improve isolation but are not a proven fix. Lower export polygon count/texture size acts downstream and cannot solve this decoder failure.

`low_vram` offloads whole stage models. The pinned shape decoder declares the flag but does not implement a tiled-decoding branch. The cascade's `max_num_tokens` is also not a hard1024 cap: its reduction loop exits at1024 regardless of count. Neither is an untried magic switch.

No1024 latent checkpoint was retrieved: `return_latent=True` returns only after decoding. Future workers should save CPU shape/texture latents, coordinates and resolution before decode, with hashes and a reconstruction recipe. This avoids repeating sampling after a decode/export failure.

## Controls worth understanding

| Control | Meaning | Proposed use / limit |
|---|---|---|
|512→1024 generation|Finer3D spatial grid, not just image resolution|May preserve smaller features; does not guarantee likeness/anatomy or separate eyes/hair|
|1024 direct vs cascade|Direct high-resolution structure versus512 scaffold refined by1024 models|Different generation path, not a proven memory fix; keep cascade first for controlled comparison|
|1536 cascade|Higher requested grid using the1024 model family|Not a secret larger model; defer until1024 benefit and capacity are proven|
|Seed|Another stochastic interpretation|Test only after export/resolution controls, with same input/settings|
|Steps|Denoising iteration count|A targeted12→24 shape-step test is a proposed experiment, not an established optimum; more steps may not improve quality|
|Guidance / rescale / interval|Strength and timing of image conditioning|Higher adherence can introduce artifacts; do not sweep everything together|
|Timestep rescale|Redistributes sampling times|Not object scale or geometry resolution; leave default absent evidence|
|Export triangles|Amount of generated geometry retained|Test300k versus higher retention on the same reconstructed source|
|Export2K→4K|Atlas sampling capacity|Cannot create absent geometry/detail; isolate from triangle count|
|Opacity handling|Whether generated opacity affects rendered surface|CurrentGLB isOPAQUE; fixed-source material control must precede any claim that alpha solves beard artifacts|

The inspected official release offers the TRELLIS.2-4B family with resolution-specific shape/texture components, not a menu of successively larger released models. Pinned app export defaults are500k/2K, with controls up to1M/4K; the README example uses1M/4K. Our300k/2K is not the highest-retention configuration. Keep UI defaults, example settings and actual executed settings distinct.

The2K base-colour atlas contains alpha (2.539% of all pixels below128), but that includes atlas background. It is not proof that missing beard detail can be recovered by simply enabling transparency. Connecting alpha is a diagnostic control, not an accepted artistic change.

## Recommended bounded sequence — proposed, not dispatched

1. **Fixed-source export/material comparison.** Same corrected298d source, cameras and light: current300k/2K; opacity-only control; then higher retained geometry at2K and4K atlas at fixed geometry. Reuse preserved `remeshed-source.safetensors` with original attributes/coordinates; do not unsigned-remesh the already reconstructed shell again. Compare face, beard boundary and crown in texture and clay. No new model inference. GPU export, if needed by the adapter, still requires a budgeted worker; do not describe it as automatically free.
2. **One controlled1024 cascade**, if source detail is still the limiting factor. Same approved input/seed/default samplers. Save latents before decoding. A48GB-class GPU is the straightforward capacity candidate, not a guarantee; verify available instance, pricing, capacity and conservative all-in cost before launch. This is preferable to repeating the same known22GiB failure.
3. If limited to24GB, investigate row-chunked FP32 LayerNorm with numerical-equivalence tests and a peak-memory proof. Normalization is across channels, so chunking independent rows could reduce this allocation without intentionally changing arithmetic. It may only move the OOM downstream; this is code engineering, not a qualified configuration setting. Do not silently downgrade precision or claim tiling solves the full decoder.
4. Only then test one alternative seed or one shape-step change, selected by the remaining defect. Check prepared alpha/input framing before changing it. Preserve each result and vary one cause at a time.
5. If a materially better static source passes the same-film/source gate, prove independent eyes/lids and beard/cloth behavior in the actual reveal before full-body conversion. If no material improvement, retain evidence and reassess representation rather than repeatedly spending on resolution.

## Budget and authority

No GPU, paid provider call, new installation, asset upload or model generation occurred in this research pass. Prior cloud-c/d temporary resources were independently verified absent. Existing conservative aggregate liabilities/reservations totalUS$14 underUS$15; that is **not an invoice or measured spend**. Conditional extraUS$10 remains inactive. Reconcile actual liabilities and obtain a defensible prospective bound before any new dispatch; do not treat apparent hourly GPU cost alone as the total, or silently consume the conditional allowance.

## Carry-forward learning

- Keep source quality, export preservation and animation usefulness separate. A successful default sample is not a model-ceiling experiment.
- Save latent-stage checkpoints, not only final decoded meshes. Run failure recovery at the earliest preserved stage.
- Memory diagnosis must identify the failing allocation/stage. Texture/export knobs do not fix decoder activation pressure.
- Use controlled quality comparisons before choosing expensive artistic repair or another generation sweep. Increased resolution remains a hypothesis until inspected against the actual close-reveal need.
- Report executed settings and provenance, not the model UI's defaults inferred after the fact.

## Primary sources and local evidence

- [Official release and example](https://github.com/microsoft/TRELLIS.2), inspected2026-10-17.
- [Exact model configuration revision](https://huggingface.co/microsoft/TRELLIS.2-4B/blob/af44b45f2e35a493886929c6d786e563ec68364d/pipeline.json), hash-matched to execution manifest.
- Pinned `.runtime/trellis298-source/app.py:528–554`; pipeline `trellis2/pipelines/trellis2_image_to_3d.py:328–339,382–388,520–593`; `trellis2/modules/norm.py:6–11`; `trellis2/models/sc_vaes/sparse_unet_vae.py:238–256,421`.
- `scripts/trellis298_worker.py:144–169`; `.runtime/trellis298c/retrieved/evidence/{build.log,weight-manifest.json}`; `.runtime/trellis298d/retrieved/evidence/{receipt.json,candidate.glb}`; `results/trellis298/ASSESSMENT.md` retains historical failed controls and technical outcomes.
