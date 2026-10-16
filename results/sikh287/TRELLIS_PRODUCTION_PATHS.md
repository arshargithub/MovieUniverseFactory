# TRELLIS production alternatives for the Sikh character

2026-10-16. TRELLIS-first investigation requested by Director287. **Recommend a minimal, headless TRELLIS.2 pipeline based on Microsoft's implementation, with prepared RGBA inputs and a permissively licensed texture-baking replacement.** Concrete replacement code exists; the noncommercial dependencies are not inseparable from the generation model. This is a substantiated engineering route, not yet a qualified installation or a cleared production asset. No generation, installation, paid call, cloud deployment, character upload or vendor contact occurred.

The earlier blanket parking of TRELLIS was too broad. Keep generation blocked by 286's viability gate, but investigate the specific removable dependencies before abandoning the model family. Do not replace this task with a broad model tournament.

## Outcome and strategy

The production need is an individualized Sikh sculpt donor that can become a convincing actor beside the accepted Pashtun. The approved Sikh v03 supplies direction, not a literal pixel target. A textured statue alone does not meet the need. Preserve the approved portrait, Pashtun masters, authentic turban and continuous face-cover requirement; preserve failures 271/283 as negative controls.

The intended path is prepared image → TRELLIS shape/material generation → portable mesh/material export → Blender source admission → localized conversion proof → integrated actor. This investigation establishes concrete licensing and implementation options before a quality trial. The next engineering proof must use synthetic exporter fixtures and a locked dependency inventory before any protagonist generation. No speculative new renderer, model training, or complete Factory service is needed.

## What the actual dependency chain establishes

| Component | Role and observed terms | Production treatment |
| --- | --- | --- |
| TRELLIS.2 code and 4B weights | MIT core/model release | Pin code and weights; retain notices. This does not relicense dependencies or guarantee output exclusivity. |
| TRELLIS-image-large sparse decoder | Referenced by the v2 pipeline configuration; model card identifies MIT | Include this additional weight source in the inventory, not just the v2 repository. |
| DINOv3 ViT-L/16 | Required image encoder; Meta's custom DINOv3 license | Retain the required encoder and comply with its terms; do not silently swap in DINOv2. |
| BRIA RMBG-2.0 | Default background-removal weights; noncommercial without a commercial agreement | Exclude. Use an already prepared image with a real alpha mask; disable model construction/download as well as inference. |
| nvdiffrast v0.4.0 | Standard UV rasterization for textured GLB export; noncommercial research/evaluation restriction | Exclude and replace the UV-to-surface mapping step. Merely disabling preview is insufficient. |
| nvdiffrec renderutils | Preview/PBR rendering dependency with the same inspected noncommercial restriction | Exclude original preview path. Review exported assets in Blender. |
| CuMesh, FlexGEMM, cubvh, xatlas, utils3d | Inspected top-level licenses are MIT; nested Eigen introduces its own file-level terms | Retain only needed components and notices. These receipts are not a complete resolved package inventory. |

Evidence: [official setup](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/setup.sh), [model configuration](https://huggingface.co/microsoft/TRELLIS.2-4B/blob/main/pipeline.json), [v1 decoder model card](https://huggingface.co/microsoft/TRELLIS-image-large), [standard exporter](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/o-voxel/o_voxel/postprocess.py), [NVIDIA rasterizer license](https://github.com/NVlabs/nvdiffrast/blob/v0.4.0/LICENSE.txt), [renderutils license](https://github.com/JeffreyXiang/nvdiffrec/blob/renderutils/LICENSE.txt), [BRIA terms](https://huggingface.co/briaai/RMBG-2.0).

DINOv3 is **not a noncommercial-only license**. Its royalty-free grant allows use and modification, subject to conditions including redistribution, research acknowledgement, lawful use, trade controls and restrictions on reverse engineering. My reading is that ordinary commercial fictional filmmaking is not prohibited by the inspected terms; that is not a legal opinion or an exclusivity guarantee. Its trade-control/end-use restrictions must not be confused with a blanket ban on depicting fictional warriors. Obtain official gated access, preserve the agreement and do not use a public mirror to bypass acceptance. No model-access agreement was accepted in this pass. [Exact DINOv3 terms](https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m/blob/main/LICENSE.md).

The class named `BiRefNet` does not make the default weights MIT: the configuration selects **BRIA's** model. Also, the upstream loader constructs that model before inspecting an image's alpha channel. Therefore supplying a transparent PNG alone does not eliminate the restricted dependency. [Loader](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/pipelines/trellis2_image_to_3d.py).

NVIDIA CUDA hardware/runtime is not synonymous with the research-only nvdiffrast/nvdiffrec licenses. Removing those two libraries does not require abandoning NVIDIA GPUs. The eventual build still needs ordinary runtime/package-license compliance.

## Alternative 1 Recommended minimal TRELLIS.2 adapter

Keep Microsoft's inference implementation and original checkpoints. Change only preprocessing admission, optional imports and texture export. The concrete reference is [andrakis/TRELLIS.2-stableprojectorz](https://github.com/andrakis/TRELLIS.2-stableprojectorz), inspected at `1481f4995870460b6442be50b6265307b6d6d07f`.

Its [MIT-labelled pure-PyTorch UV rasterizer](https://github.com/andrakis/TRELLIS.2-stableprojectorz/blob/1481f4995870460b6442be50b6265307b6d6d07f/o-voxel/o_voxel/uvraster.py) computes which triangle covers each texture pixel and the corresponding position on the generated surface. The [exporter](https://github.com/andrakis/TRELLIS.2-stableprojectorz/blob/1481f4995870460b6442be50b6265307b6d6d07f/o-voxel/o_voxel/postprocess.py) then samples TRELLIS's generated material attributes and builds the GLB. This is existing code, not an unspecified promise to invent an exporter. It does not replace the learned shape/material generators. Bake accuracy, seams and throughput still require qualification.

The [loader changes](https://github.com/andrakis/TRELLIS.2-stableprojectorz/blob/1481f4995870460b6442be50b6265307b6d6d07f/trellis2/pipelines/trellis2_image_to_3d.py) guard BRIA model loading and reject opaque input when background removal is disabled. Its `TRELLIS_UV_RASTERIZER=torch` path avoids importing nvdiffrast; the default `auto` can use it if installed. A production derivative must fail closed: explicit allowed implementation, prohibited packages absent, no fallback to restricted code. The repository's preview entry points remain unsuitable.

**Do not adopt this Windows-oriented fork wholesale.** Its API also contains debug mesh-cache reuse and Windows/memory patches unrelated to our requirement. Its multi-image endpoint currently selects the first input image; it is not proof of multi-view reconstruction. Port the small reviewed changes onto the pinned official Linux implementation. Do not use its unreviewed binary wheels, generic launcher or debug cache as the production interface. [API implementation](https://github.com/andrakis/TRELLIS.2-stableprojectorz/blob/1481f4995870460b6442be50b6265307b6d6d07f/api_spz/routes/generation.py).

### Concrete issue found before execution

The rasterizer sorts triangle bounding boxes by area, chooses a chunk using `count × largest area`, then allocates a common grid using `count × maximum width × maximum height`. Those are not equivalent. A 1000×1 box and a 1×1000 box each have area 1000, but their common rectangular allocation has one million positions per triangle. Sorting by area does not bound both dimensions. This is a source-derived counterexample to its memory-bound claim, **not an observed crash or a measured runtime**.

With 1000 such boxes, the estimated count is one million candidates but the common-grid allocation is one billion, exceeding the default 24-million budget. Fix the allocation bound or tile the work before adoption; test mixed-aspect and oversized boxes explicitly. The author's reported rasterization agreement is useful context, not our validation. Test coverage, shared edges, winding, degenerates, empty input, UV orientation, seams, texture-channel conventions and actual peak memory. No need to run restricted NVIDIA code as the correctness oracle: analytic triangles/checkerboards and independent Blender inspection can supply permitted controls.

**Disposition:** strongest route to qualify. The essential replacement exists, rights can be separated by construction, and inference changes can remain small. Still blocked for generation until a reviewed adapter, resolved package/model manifest, license/access checks and synthetic export checks are complete. No implementation was created here.

## Alternative 2 Independent TRELLIS.2 runtime

[Wimacs/trellis2.c](https://github.com/Wimacs/trellis2.c) provides a concrete C/C++ implementation, inspected at `51b364e3a4dbc1ea076b186bcf86665f507bfde4`. It documents Linux CUDA/Vulkan builds and a command-line image-to-GLB path. Its [build](https://github.com/Wimacs/trellis2.c/blob/51b364e3a4dbc1ea076b186bcf86665f507bfde4/CMakeLists.txt) and [export source](https://github.com/Wimacs/trellis2.c/blob/51b364e3a4dbc1ea076b186bcf86665f507bfde4/src/tasks/image_to_3d/export/gltf.c) implement Vulkan texture baking rather than importing nvdiffrast. The shader/source path is real; no binary was run.

The original code is MIT. Its [third-party inventory](https://github.com/Wimacs/trellis2.c/blob/51b364e3a4dbc1ea076b186bcf86665f507bfde4/THIRD_PARTY_NOTICES.md) separates dependency/model terms, including DINOv3 and Eigen. Restrict the scope to TRELLIS image-to-3D, prepared RGBA and required weights; optional segmentation, rigging and other models are not cleared by the main repository license. Its downloader defaults to a DINO mirror; use official authorized weights instead. [Downloader](https://github.com/Wimacs/trellis2.c/blob/51b364e3a4dbc1ea076b186bcf86665f507bfde4/tools/download_weights.py).

**Tradeoff:** avoids maintaining the Python UV replacement, but introduces a much larger independently implemented inference/runtime surface. Need correctness and output-quality comparison, build reproducibility, full transitive notice review and CUDA-plus-Vulkan driver compatibility. No evidence here establishes faster execution, lower memory or equivalent character quality on our AWS hardware. Vulkan support is not proof that our 16 GiB Mac is viable.

**Disposition:** concrete second route, not our first deployment recommendation. Keep it as the exporter/runtime alternative if the minimal adapter cannot be qualified without expanding into a major graphics-engine project.

## Alternative 3 TRELLIS geometry with Blender surfacing

TRELLIS.2's decoded representation exposes vertices/faces independently of the final textured exporter. A headless derivative can export a geometry donor and complete surface work in Blender. This avoids the UV-baker replacement but forfeits the immediate benefit of TRELLIS's generated material maps; reconstructing the illustrated skin/cloth appearance becomes our work. [Mesh representation](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/trellis2/representations/mesh/base.py).

Do not call this an unchanged default invocation. Importing `o_voxel` currently imports `postprocess`, which imports nvdiffrast. Isolate the geometry-only imports/loader and exclude restricted dependencies, just as in alternative 1. [Package imports](https://github.com/microsoft/TRELLIS.2/blob/75fbf0183001ed9876c8dbb35de6b68552ee08bd/o-voxel/o_voxel/__init__.py).

**Disposition:** credible reduced-scope fallback for a sculpt/turban donor, not the preferred whole textured-character workflow. It is only economically preferable if the form is valuable enough to offset extra surfacing. No measured conversion savings yet. It must not silently lower the accepted surface-quality floor.

## Hosted TRELLIS and older TRELLIS

[fal's TRELLIS.2 endpoint](https://fal.ai/models/fal-ai/trellis-2) advertises commercial use, GLB export and $0.25/$0.30/$0.35 per 512/1024/1536 request. Those are service prices, not a license to self-host the service's dependencies. Its terms retain third-party conditions and disclaim output/noninfringement guarantees. The public listing does not explain how this endpoint handles the specific NVIDIA/BRIA restrictions. That absence is not evidence of wrongdoing; it is an unresolved question under our strict gate. [Service terms](https://fal.ai/legal/terms-of-service).

Before choosing it for our unreleased character, obtain endpoint-specific confirmation of commercial output/reuse, dependency permissions or replacements, retention/deletion, confidentiality/training treatment and remaining attribution obligations. Do not infer no-training from the privacy policy. No inquiry, upload, account creation or paid request was made. Hosted service remains conditional, not the way to evade the self-hosting audit.

The TRELLIS 1 [trellis-refactored](https://github.com/kg-git-dev/trellis-refactored) project replaces rendering/texturing components, but identifies itself as archived research with stopped development and documented dependency issues. It is an implementation reference, not a production-cleared TRELLIS.2 replacement. Do not assume v2 checkpoints can be dropped into it.

## AWS operating path and cost

Use private, on-demand Linux GPU sessions, not an always-running endpoint. The [same-day AWS rate evidence](../sikh285/aws-prices.json) and [deployment assessment](../sikh285/AWS_HOSTING.md) remain applicable: US East g6.2xlarge L4/24GB is $0.97760/hour; g6e.2xlarge L40S/48GB is $2.24208/hour. Prefer 48 GB for the first authorized qualification to avoid making aggressive memory optimization part of the initial proof; then evaluate 24 GB if worthwhile. Documented requirements do not establish fit or speed on either instance.

Twenty billed hours would cost $19.55 or $44.84 in compute, before storage/network/tax; this is arithmetic, not a forecast. Count startup, compilation/loading, failed jobs and idle time. No defensible cost-per-usable-actor number exists until we measure generation AND Blender conversion. Engineering effort may dominate rental cost. Do not build a recurring service merely because inference is inexpensive.

Preserve the existing planned immutable-job interface and private result receipts. Keep model caches on encrypted storage, source/weight hashes fixed and inference offline after approved provisioning. Use narrowly scoped IAM, no public model port, explicit job reservations and an independent shutdown watchdog. Account quota/capacity, network design and an actual spend ceiling remain preflight decisions; none was changed. S3 output storage is not a substitute for our separately verified production backup.

## What TRELLIS would and would not solve

The proposed gain is better character-specific primary form and potentially richer transferable surface detail. It does not guarantee separate eyeballs, eyelids, clean deformation topology, a deformable beard, a physically continuous turban end, a rig, or an authentic reverse-side design. Do not infer those from static GLB fidelity.

After infrastructure viability, use the accepted Sikh direction for a targeted head donor, not an expensive all-in-one actor gamble. First inspect raw geometry under revealing front/oblique/profile/rear views against v03 and the accepted Pashtun. Then demonstrate one working eye/eyelid and an adjacent beard/skin interface without destroying the useful source form. Keep the turban donor separate where beneficial, but preserve the one-cloth design and expose actual uncovering as the next integration test. Generated fused hair is form/reference material, not automatically a motion-ready groom.

Evaluate source quality, conversion loss, same-film coherence and required performance separately. Repeated failure in conversion must not trigger endless regeneration without identifying whether the source or conversion representation is responsible. Do not repeat 283's decorative polishing of a weak whole head.

## Next deliverable and admission gates

Recommend a **reviewed TRELLIS.2 production adapter package**, not another model-shopping report or a protagonist beauty test. It would include the minimal source patch, exact model/package/notice manifest, synthetic exporter fixtures, restricted-import/download assertions, a reproducible Linux build recipe and a scoped AWS execution/budget proposal. This is new implementation/install/cloud authority beyond this read-only investigation; not executed here.

1. **Rights and provenance:** official model access, exact revisions and notices, no BRIA or prohibited rasterizer in the runtime image, all required resolved dependencies inventoried. No dependency with unresolved required rights can be waved through by a good render. Pinning source receipts alone is not this closure.
2. **Exporter and admission contracts:** analytic geometry/UV fixtures cover the memory-bound issue, orientation, seams, material channels and malformed/opaque inputs. Check absence of restricted imports and weight-download paths. Fail closed on missing masks or unsupported configuration. These are component tests, not an early character-generation trial.
3. **Environment proof:** after explicit install/compute approval, reproduce the pinned build, verify synthetic GLB import in Blender and measure working memory. Verify account capacity and shutdown/budget controls before generation. Do not treat passing code review as a functioning CUDA build.
4. **Only then the representative asset trial:** a small agreed head/turban input scope, no public gallery, measured source and conversion gates, preserved failed evidence. The test asks whether an established production-compatible path produces useful quality—not whether we can excuse a known commercial restriction afterward.

Reassess if the minimal adapter changes the learned inference path substantially, requires a new general renderer, cannot exclude restricted dependencies, or fails the synthetic checks. Alternative 2 is the next TRELLIS route to investigate/qualify, not an automatic parallel build. No arbitrary elapsed-time cutoff; nevertheless an unbounded infrastructure project would violate Efficient Quality and forward momentum.

## Evidence and knowledge reconciliation

[Source manifest](source-manifest.json) records 33 fetched public-file hashes and pinned revisions. Text inspection, not execution, supports the findings. It is not a complete software bill of materials, a security audit, or a guarantee of contributor provenance. Exact transitive package versions are not yet resolved; gated weights were not downloaded; runtime and visual quality remain NOT_RUN.

Fresh knowledge packet: `.runtime/knowledge-pilot213/sikh287-packet.json`, digest `d7133782acc14afbf4c8e2d92fbe8e2eb30fde9773f8cef2a917f33a44559502`. Reconciled strategy 184, approved Sikh direction, rejection 271, failed 283, AWS 285 and production-gate 286. Licensing/cloud/runtime analysis remains manual coverage outside the finite pilot. No source pins refreshed to bypass staleness; no new graph-coverage claim. Production review obligations remain NOT_RUN and the evidence gate must remain blocked for character handoff.

Planning exchange 287; next checkpoint 290. Research and recommendation complete; no native or release acceptance advances. Local design commit only, no push or S3 backup.
