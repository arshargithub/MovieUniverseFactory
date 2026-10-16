# Sikh image to 3D options and Meshy assumptions

2026-10-16, Director exchange284. Research only. Recommendation: defer the paid Meshy purchase and test source quality separately from conversion quality. The failed283 construction does not establish that free generation is exhausted, that Meshy6Lite caused all failures, or that a subscription would deliver an actor.

## What a subscription would and would not change

Meshy's current [free-plan documentation](https://help.meshy.ai/en/articles/15696428-what-is-included-on-the-free-plan) distinguishes downloadable6Lite assets from6/7 downloads requiring payment. Its [ownership guidance](https://help.meshy.ai/en/articles/10137554-what-is-the-ownership-of-the-generated-models) gives paid users private ownership subject to valid inputs and not publishing to the community. These are entitlement/rights changes, not measured character-quality improvements. Non-Enterprise input/output training permissions remain in [terms section2.9](https://www.meshy.ai/terms-of-use); private is not a no-training promise. Do not assume upgrading converts earlier free assets into exclusive assets.

The283 recommendation bundled three untested variables: stronger generator, character-specific input and successful downstream conversion. Better face planes from a stronger model are plausible, not established. Moving from a generic bald input to an approved-character derivative may improve individuality independently of payment. Neither change fixes our own eye integration, beard design, surface projection or transform errors automatically. The proposed US$25 ceiling was a spending proposal, not a verified checkout price or authorization.

The source assets did supply useful shape information. [279](../sikh279/ASSESSMENT.md) and [283](../sikh283/ASSESSMENT.md) also record conversion failures introduced locally. Eleven completed283 controls did not establish an acceptable integrated actor. A technically working eyelid component did not establish attractive bilateral eyes or expressive whole-face performance. More grooming and painted detail did not rescue weak form. Our application of the early whole-form gate was itself inadequate.

## The required deliverable is an actor not a static mesh

| Requirement | Potential contribution of image to 3D | Remaining proof |
|---|---|---|
| Rugged individual face and authentic crown | Facial planes, major beard/turban volumes, plausible unseen surfaces | Front, both obliques, profile, rear/crown; match approved direction without literal reconstruction |
| Skin and illustrated finish | UV coordinates and surface maps; some methods estimate lighting-separated colour | No baked shadow disguising weak geometry; shared quality with accepted Pashtun |
| Eyes and facial acting | Reference shape around sockets and lids | Separate eyeballs, deformable lids, gaze, restrained recognition/respect, natural neck transition |
| Beard | Overall silhouette and clump guide | Editable rooted groom, believable moustache transition and motion; fused sculpt is not moving hair |
| Turban and removable face cover | Crown shape/fold reference | One-cloth route, fixed crown, slack end, hand/ear/beard release, controlled drape |
| Reuse | Exported mesh and maps | Revision without identity loss, save/reopen, actual shot performance and rights |

Retopology means building a controllable surface over the generated sculpt. Automatic quadrilateral remeshing does not establish eyelid/mouth deformation flow. PBR maps describe material properties, not an illustrated art direction. A body skeleton does not certify facial acting, beard roots or cloth support. A single image leaves hidden shape ambiguous; generated extra views can disagree and are not measured anatomy.

## Open models worth considering

Primary documentation checked on2026-10-16. No model below has been run or visually ranked on our input. Hardware figures are publisher requirements, not our benchmarks.

| Route | Published capability and license | Practical assessment |
|---|---|---|
| [Microsoft TRELLIS.2](https://github.com/microsoft/TRELLIS.2), [weights](https://huggingface.co/microsoft/TRELLIS.2-4B) | Image-conditioned geometry and PBR materials; model/code MIT, dependencies have separate terms. Model card acknowledges holes and no alignment to particular aesthetics. | First hosted-demo candidate. Official local route needs Linux, NVIDIA and at least24GB VRAM; not a supported native installation on this Mac. |
| [VAST TripoSG](https://github.com/VAST-AI-Research/TripoSG), [weights](https://huggingface.co/VAST-AI/TripoSG) | Shape generation, MIT core/weights; documented CUDA GPU requirement at least8GB. | Useful second geometry candidate, conditional on preprocessing rights. No verified Mac runtime. Generic HF code-widget MPS comments are not evidence that this complete pipeline works on Mac. |
| [Stable Fast 3D](https://github.com/Stability-AI/stable-fast-3d) | Single-image textured mesh, UVs and illumination disentanglement; experimental MPS and CPU routes documented. [Community license](https://github.com/Stability-AI/stable-fast-3d/blob/main/LICENSE.md) allows limited commercial use subject to terms, registration and revenue threshold. | Best documented local-Mac fallback among these, not a promised quality winner. Authors advise CPU below32GB unified memory; launcher also warns baking needs CUDA/MPS. End-to-end export and memory need proof, not just model loading. |
| [Tencent Hunyuan3D2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) and [2mini](https://huggingface.co/tencent/Hunyuan3D-2mini) | Separate shape/paint stages;2.1 lists10GB VRAM shape and29GB combined, mini uses a smaller0.6B shape generator. Custom community licenses. | Technically relevant but not recommended as a production dependency while territorial/output restrictions remain unresolved. |
| [TripoSR](https://github.com/VAST-AI-Research/TripoSR) | Lightweight single-image reconstruction; code/weights MIT, default approximately6GB VRAM. | Useful low-complexity baseline, not evidence of better hero-face detail. CPU/dependency/export viability on this Mac is untested. Do not prioritize it merely because it is easier to install. |

Live read-only hardware check: Apple M4,17,179,869,184 bytes RAM (16GiB); external project volume reports789GiB available. Unified memory also serves the OS/apps and is not equivalent to dedicated CUDA VRAM. A downloaded model fitting on the SSD does not imply it fits/runs in memory. No verified local runtimes or timings are claimed.

A [community Hunyuan2.1 Mac port](https://github.com/VladimirTalyzin/hunyuan3d-2.1-mac-rocm) reports shape and low-resolution paint on an M4 Pro24GB. This is the port author's evidence on different hardware, not ours and not upstream certification. It makes Mac feasibility worth investigating, not guaranteed on16GB. No safety limits will be disabled to force it to run.

## Rights and hosted execution caveats

The current [Hunyuan2.1 license](https://huggingface.co/tencent/Hunyuan3D-2.1/blob/main/LICENSE), section5(c), explicitly includes Outputs in restrictions outside its Territory, excluding EU, UK and South Korea. The [2mini license](https://huggingface.co/tencent/Hunyuan3D-2mini/blob/main/LICENSE) has the same issue. This is material to our European audience and future app distribution, not a blanket claim that every Hunyuan-derived film is legally prohibited. Obtain clarification or avoid adopting it; Canadian execution alone does not resolve the clause.

An MIT core does not clear the whole application. TripoSG's example downloads [BRIA RMBG1.4](https://huggingface.co/briaai/RMBG-1.4); its free weights are noncommercial. TRELLIS.2's [official demo code](https://huggingface.co/spaces/microsoft/TRELLIS.2/raw/main/app.py) can send opaque input to BRIA's hosted background remover but skips that branch when genuine transparency is supplied. Pre-mask through an already-cleared process and verify the path; do not relabel a noncommercial preparation stage as production-cleared. Hosted service terms may differ from weight licenses and need their own check. This research does not make a final legal clearance determination.

Official hosted demos exist for [TRELLIS.2](https://huggingface.co/spaces/microsoft/TRELLIS.2), [TripoSG](https://huggingface.co/spaces/VAST-AI/TripoSG) and [Stable Fast 3D](https://huggingface.co/spaces/stabilityai/stable-fast-3d). Public page/code existence is not a successful live generation or a guaranteed current quota. [HF ZeroGPU](https://huggingface.co/docs/hub/spaces-zerogpu) supports free use with queues/quotas. That is remote execution, not local processing; no hosting subscription or paid GPU rental should be assumed necessary merely to try an existing free demo. Inputs leave the Mac and the actual host's retention, visibility and additional service calls must be checked before upload. No private/public retention promises are inferred from an MIT model license.

## Proposed next proof

Outcome: identify whether a generator supplies a useful individualized sculpt AND whether we can preserve its useful form while adding the required actor controls. Do not start another full-head beautification campaign or a generalized inference platform.

1. Preserve and compare the existing raw280 source against the283 converted head under matched views. Identify inherited form defects versus conversion damage. Reuse existing controls where sufficient; a new causal visual comparison is still pending.
2. Preflight TRELLIS.2's official free demo first: actual availability, download, dependency terms and upload handling. TripoSG is a second candidate only if its preprocessing path is cleared; Stable Fast3D is the alternative and local fallback. Do not install all five or assume free hosted service is private. New model installation, external input approval and any charges remain separate boundaries.
3. Use the same transparent head input/settings record for cross-generator shape comparison. Existing generic input can isolate reconstruction behavior without uploading the protagonist. A character-specific derivative is a separate input variable, kept consistent across candidates and evaluated against v03 as directional authority. Testing only generic anatomy cannot prove Sikh identity. Keep raw exports immutable; do not compare one model's raw output with another's locally polished derivative. Meshy6/7 preview could be an additional control if current account entitlement allows it without purchase, but cannot establish native geometry quality without download.
4. Inspect clay and textured outputs at matched cameras before native eye/groom rebuilding. Reject a good front with damaged profile/crown, painted-on anatomy or fused beard treated as ready hair. Avoid winner claims from unequal inputs. Stop poorly performing candidates before finish; no arbitrary elapsed-time cutoff or compulsory retry count.
5. On one viable donor, prove an integrated eye/lid, small expression and neck turn while preserving source shape. Compare neutral before/after and all intermediate states. If conversion damages the good donor, fix conversion rather than buying a different generator. Prove broad beard masses and actual moving roots before density. Whole-head design and same-film checks precede cloth release/body integration.

Final method selection must consider usable shape, conversion burden, rights, runtime and memory, not marketing sample quality alone. Authoring time, waits, external spend and accepted output are separate metrics; current research engineering tokens and exact active duration are unknown. New provider generation spend and native render jobs this exchange: zero. Free software is not free engineering effort.

The immediate recommendation is a zero-dollar hosted source/conversion comparison, subject to preflight and explicit execution/input authority, not a Meshy subscription. Local-only alternative: a scoped Stable Fast3D compatibility proof after installation approval; fail closed on memory/export problems rather than starting a CUDA-porting project. Paid Meshy becomes a bounded fallback only if evidence identifies a source-quality limitation it might address. No next route is guaranteed to work.

## Learning application and handoff

Fresh planning packet: `.runtime/knowledge-pilot213/sikh284-packet.json`. It routes anatomy, representation, performance, contact, garment, rights and shared quality obligations. Read and reconcile283 assessment,271 rejection contract, Sikh baseline, current strategy, production-strategy decision, Pashtun retrospective and Efficient Quality guidance. New model hardware/license facts are manually reconciled here; the bounded graph does not know these providers automatically. Original corpus pins remain unchanged.

Known failure controls stay failed. No new image inspection, native mutation, source conversion, upload, installation, paid call, push or S3 backup is claimed. Research completion is not a visual admission: the evidence gate must retain NOT_RUN/FAIL for actor checks. The proposed next pass must satisfy the same v03/C/Pashtun quality floor, with the turban and face cover still one cloth. Sikh only; Gurkha remains queued. These findings replace the current purchase recommendation, not historical evidence or Director creative choices.
