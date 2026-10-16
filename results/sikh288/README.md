# TRELLIS exporter qualification

The local replacement is implemented and passes synthetic raster, material, GLB and independent Blender checks. **The full CUDA exporter and generation pipeline are not yet qualified.** Canada Central is selected for the next test, but the account has zero GPU quota and AWS has opened a quota-increase case. No cloud worker or paid inference was started.

This work supports a better Sikh sculpt donor, not a new character foundation. Approved Sikh direction, the accepted Pashtun film and all failed character candidates remain unchanged.

## Implemented and tested

- A source-pinned patch replaces the restricted UV rasterizer in the official exporter. No automatic fallback to NVIDIA research-only code is present in the adapted path.
- Ragged candidate scheduling fixes the mixed-aspect allocation defect and splits individual oversized triangles. The bound applies to candidate count, not all GPU memory. CPU tests cover winding, shared edges, overlap ownership, empty/degenerate geometry and malformed inputs, plus an independent scalar oracle.
- Prepared-alpha admission removes BRIA construction and rejects RGB, opaque or empty masks; the public run path cannot bypass admission. Foreground cropping also corrects inclusive bounds and one-pixel handling. This deliberately changes preprocessing edge cases, not the neural models.
- The original PBR finishing code is shared by the adapted exporter and local controls, with CPU input arrays copied to prevent caller mutation. Color, metallic/roughness channels, alpha storage, GLB geometry and UVs survive roundtrip. Upstream `alphaMode=OPAQUE` is retained: transparent hair cards are not qualified.
- Blender imports the asymmetric analytic fixture with the expected four world-space vertices, two triangles, UVs, sRGB color and Non-Color material map. A fresh reopen reproduces the recorded snapshot. The rendered four-quadrant texture has the expected pixel values and orientation. This is an emission diagnostic, not PBR appearance or character review.
- The patch applies cleanly to the exact upstream source, including its missing terminal newline. Drift is rejected. Source snapshots and MIT notice are retained.

The final local suite has **26 passing tests**. Evidence: `tests.txt`, `tests.xml`, `visual-check.json`, `artifact-manifest.json`, `local-dependencies.json` and the fixed synthetic fixture under `.runtime/trellis288/fixture/`. Maximum analytic position error was approximately8.35e-8 in normalized units. The suite covers components, not CUDA execution or commercial runtime clearance.

## Failures retained

Initial tests exposed a fixture indexing error and the newline difference introduced when storing upstream source; both were corrected without replacing the original source hash. The first Blender process crashed at sandbox startup. The second imported/saved the fixture successfully but failed at an unsupported EEVEE identifier. The final CPU diagnostic and independent reopen succeeded. Logs and separate job receipts remain; no failed run is presented as a pass. These were local test/launcher failures, not evidence of TRELLIS generation quality.

## Cloud authority and blocker

Director explicitly approved **US$15 total** for synthetic qualification, including compute, temporary storage and transfer, plus isolated dependency installation and removal of temporary compute. No protagonist upload/generation, gated-weight agreement, public endpoint or paid model service is authorized.

Regional API inspection confirms `g6.2xlarge` and `g5.2xlarge` in Canada Central, but not `g6e.2xlarge`. Use the24GB L4 for synthetic export: full model weights are not loaded. The recorded Canadian L4 rate is US$1.08547/hour, excluding ancillary charges. See [rate receipt](../sikh285/aws-prices.json). Forty-eight GB was a conservative future inference choice, not a necessity established for this exporter test.

Canadian quota request: `653be7e500c34e07b1b1ed143307a83cIgbSQlyu`, eight G/VT vCPUs, **CASE_OPENED**, support case `179219438700276`. US East request `01950d95208642989a85173282bfcabaPPLDXzj2` was submitted before the region discussion and does not authorize a US launch. Quota requests themselves create no compute. No cloud instances, volumes, buckets, network or IAM resources were created. New AWS resource spend from this pass is zero; future billing is not estimated from quota approval.

## Next execution package

After Canadian quota approval, continue the already-authorized synthetic qualification without another routine Director go-ahead:

1. Recheck account identity, rate and live quota; choose and record exact AMI, subnet/security group and narrowly scoped management role. No inbound model service. Bind encrypted temporary storage, delete-on-termination and independent cloud termination watchdog before launch. Reserve the full conservative session allowance in the persistent ledger before creating billable resources; no launch script is supplied here that bypasses this gate.
2. Use one L4 worker and an isolated Linux environment. Limit the first reservation to two hours of machine uptime plus conservative ancillary allowance, within aggregate US$15. This is a spending safeguard, not a cutoff for engineering effort. Keep compilation concurrency modest. Check setup progress before any retry; never leave paid idle compute while waiting for a Director response.
3. Check out official TRELLIS.2 at `75fbf0183001ed9876c8dbb35de6b68552ee08bd`. Apply `adapter.patch` after hash verification. Do **not** run upstream `setup.sh` or install its preview/background-removal dependencies. The runtime only needs the export module, not model weights.
4. Resolve and inventory Linux dependencies with wheel/source hashes and notices. CUDA build candidates: CuMesh `12289e1062f0603f2f0d0771b02e1395d247f26f`, FlexGEMM `6dd94a859c26ee8246888502eada3dd8ad85532e`; recursively bind CuMesh cubvh/Eigen revisions and notices. Their inspected build scripts compile local extensions; FlexGEMM also writes an autotune cache in the isolated worker user's home. No unreviewed binary wheels or general fork launcher. The Mac dependency receipt is **not** a Linux lockfile or full transitive license audit.
5. Run `scripts/trellis288_cuda_probe.py --checkout /exact/patched/checkout --output /new/evidence/path` in the isolated runtime with this repository's source on its import path. It exercises the real CuMesh unwrap/BVH, FlexGEMM constant attribute-volume sampling, replacement rasterizer and PBR GLB export without model weights. It blocks named restricted imports and unexpected source. The export-only package bypasses unrelated `o_voxel` package initialization intentionally; full image-pipeline integration remains a separate gate.
6. Inspect/import the resulting GLBs in Blender, compare geometry/materials and fresh reopen, and record GPU memory plus full session time and costs. Retrieve outputs, terminate only the tagged temporary resources and verify removal. If the two-hour allocation is inadequate, preserve results and reassess within the remaining approved budget rather than running unbounded.

The CUDA probe is syntax-checked and its import guard unit-tested, **not GPU-executed**. If CUDA qualification passes, complete official DINO access and the full inference dependency/weight manifest before proposing a bounded character-generation trial. A favorable synthetic export does not establish that the learned output can become an expressive actor.

## Reproduction and scope

Local tests use the project's `.venv` launcher plus isolated dependencies in `.runtime/trellis288-deps` (about549MB). No global packages or project dependency declarations changed. The initial `pip` invocation failed because the existing environment has no pip; the installed `uv` manager completed the isolated installation.

```sh
PYTHONPATH=.runtime/trellis288-deps:src .venv/bin/python -m pytest tests/test_trellis288.py -q
PYTHONPATH=.runtime/trellis288-deps:src .venv/bin/python scripts/qualify_trellis288.py package
```

`build`, `inspect` and `reopen` are fixed structured operations for the synthetic fixture only. Successful fixture files are preserved; dispatch logs retain failed attempts. `package` regenerates current patch/test/hash evidence. No production `.blend` is opened. The upstream snapshots are review inputs, not installed packages; their restricted imports remain historical text, never executed.

Strategy and manual knowledge reconciliation are in [STRATEGY.md](STRATEGY.md). The pilot retrieves production constraints but does not cover CUDA licensing/infrastructure; its production handoff gate stays blocked by unrun asset/motion/rights obligations. Local implementation and design commits are separate. No remote push or S3 backup is claimed. Operating capture excludes initial context recovery and leaves engineering tokens/cost unknown. The next blocker is infrastructure availability, not a Director creative decision.
