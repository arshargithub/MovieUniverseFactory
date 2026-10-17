# US attempt294: infrastructure works; exporter qualification blocked

Director authorized US region within the existing cumulative15USD ceiling. Live quota8, AWS-owned Ubuntu22.04/PyTorch2.7 AMI and US East L4 g6.2xlarge rate0.9776USD/hour verified. One worker launched in us-east-1a: `i-0b18e97f594363325`. It reached **PyTorch2.7.0+cu128 / CUDA12.8 / NVIDIA L4**, then exited with code1 before compiling CuMesh/FlexGEMM or running the exporter.

## Cause and correction

The fixed bootstrap incorrectly assumed that `venv --system-site-packages`, invoked from AWS's `/opt/pytorch` environment, would expose that parent environment's installed Torch to the child. It exposes the underlying Python system package paths, not automatically the parent venv's packages. The parent successfully queried the L4; the child raised `ModuleNotFoundError: torch`. This is our environment construction defect, not an unavailable GPU, failed TRELLIS inference or evidence that the exporter is infeasible.

`scripts/trellis294_runtime.py` explicitly validates matching parent/child Python versions, exact environment prefixes and contained package directories, then adds a literal parent-package directory to the child's `.pth`. No executable startup code is copied. `trellis294_worker.py` applies that correction and checks CUDA in the child **before** downloads/extension builds. Local regression creates real nested environments, proves a parent-only module is initially invisible, applies the correction and proves import succeeds.37 tests pass. The first local reproduction needed symlink-based Python because this Mac's bundled runtime uses a relative dylib path; corrected fixture then passed. This is local environment proof, **not Linux/CUDA validation of the repair**. The deployed293 worker/payload is preserved unchanged; corrected worker is not yet dispatched.

## Scope and evidence

- PASS: US capacity, real L4 visibility in AWS's runtime, private scoped upload, tested independent watchdog, failure-triggered evidence upload/shutdown.
- FAIL: isolated worker environment admission, now locally corrected but remote retest pending.
- NOT_RUN: CUDA extension compilation, full patched exporter, GPU synthetic GLBs, Blender import/reopen of those outputs, inference, weights/full-runtime rights, protagonist generation/quality/rigging.
- The independent Blender checker is prepared in `scripts/trellis294_inspect.py`; it has no runtime pass because there are no GPU GLBs yet.
- Logs and pinned payload/retrieval manifests are retained. No production images, scenes, credentials or weights were uploaded. Accepted292 staging and Pashtun masters unchanged.

## Budget and recovery

The old Canadian10USD reservation remains untouched and is **not money spent**. New US ledger reserves5USD; aggregate15USD is enforced before dispatch. Both actual invoices remain unknown. Do not erase ledger history, label a rate estimate as billed cost, or silently open a new15USD budget. One successful US launch consumes the one-worker allocation even though the bootstrap failed. A further paid launch requires reconciling conservative remaining liability and a documented retry allocation inside15USD; no automatic second launch was made.

`teardown-verification.json` is authoritative once present: independently inventory instances, volumes, exact temporary bucket/roles/profile/Lambda/event rule/security group; require no remaining live resources. Recover outputs before deleting temporary bucket contents. Compute estimate is a conservative launch-to-confirmed-cleanup time bound, not actual billed duration or total cost. Temporary cloud evidence can be recovered from the retained local archive/manifest; no existing production backup touched. Local commits are not remote backup; no remote push this pass.

## Next move / carried learning

Recommend a corrected synthetic retry in the same US region **after** the current reservations are reconciled into a safe remaining allocation. No higher budget or protagonist generation is requested by this technical conclusion. Fail fast in the exact execution interpreter before downloading dependencies; a parent-runtime success must not be treated as child-runtime success. Preserve the decisive reproduction test for future workers. Quota, hardware allocation, runtime admission, exporter correctness and character quality are separate gates.

The production-context knowledge gate remains deliberately blocked for unrun production/visual/rights obligations. Do not weaken or refresh source pins to convert this infrastructure attempt into actor acceptance. Engineering token usage and exact initial preparation time are unknown; operating capture and job records state their limits. Next planning checkpoint300.
