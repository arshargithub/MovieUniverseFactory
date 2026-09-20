# Costume refinement 03: proportions and finishing

2026-09-20. Authorized continuation of costume refinement 02. Director specifically finds the neck a little too long. Accepted face/jaw remain locked; no change to canon, planning exchange count (119), animation scope or source assets. No paid calls, purchases, uploads or remote pushes.

Read both approved B illustrations and candidate 28. The exposed neck and low shoulder line contribute to the elongated impression. Correct the body/neck junction, not facial scale or jaw shape. Start with a neck-only candidate 29 so the effect is independently visible, then combine bounded hair, fold and leather finishing in candidate 30. Reserve 31 only for a diagnosed correction. Preserve older evidence. Estimated 25–45 recorded minutes, 150 MB new evidence; reassess at 20 minutes and before exceeding three candidates. Lifecycle activity: `costume-refinement-3` in the existing open FaceBuilder episode.

Implementation intent: add a gentle, monotonic upward shift below the protected face plane, reaching 0.17 model units at the lower neck/shoulders. This is a proportion adjustment rather than a uniform scaled head. Keep collar/skin/garment/straps coordinated. Reduce schematic collarbone color bands, vary hair lock ends without concealing the jaw, break the cowl's parallel horizontal rings with diagonal/asymmetric fold flow, and tension/smooth leather over support. Maintain modest coverage and the indigo/brown vocabulary. No new accessory.

Acceptance evidence: direct original/reference and 28/29/selected front and three-quarter inspection; side shoulder view; exact protected facial surface/UV and original head invariants; focused unit tests; packed native scene and fresh reopen; fixed-region emission comparison with residuals reported, not relabeled as pixel-exact. Director review remains pending. This pass does not qualify rigging, dynamics or a finished rear/full-body asset.

## Candidate decisions

29: retain modest proportion correction after front/three-quarter inspection. 30: softer hair tips and tensioned leather are useful, but asymmetric cowl changes expose an unwanted skin gap at the shoulder; reject that cowl change. 31 restores 29's coverage-preserving cowl while retaining the lower diagonal scarf variation, hair and leather treatment. It also reduces the projected illustration lighting in the editable neck material by mixing 45% reference-sampled neutral skin; this is not recovered albedo and never touches the original facial branch. No new sourcing, paid calls or extra variants planned.

High-resolution 31 reveals far-side hair tips projecting beneath the chin in both three-quarter views. A single extra, diagnosed repair (32) moves the lower physical locks back behind the neck, rather than hiding them by camera or editing the face. This is a narrow extension beyond the initial three-candidate plan; preserve 31 as regression evidence. Neck/costume geometry and material remain identical to 31. Side/rear inspection also confirms the rear veil/cowl junction remains unfinished and is not within a claimed all-angle completion.

## Selected result and checks

**32: YELLOW static review candidate**, not a finished costume or new Director acceptance. Inspected all final 955×1647 portraits plus side/rear diagnostics. The neck is modestly shorter, the clavicle shading is less graphic, physical hair ends are feathered and swept back instead of showing beneath the chin, and front leather is less wavy. Restored upper-cowl coverage is retained. Face/jaw geometry is unchanged. Fold refinement is limited to the lower diagonal shawl; do not describe the rejected asymmetric cowl as delivered.

Proportion evidence: the authored clavicle-center landmark at pre-lift z=-1.88 moves from z=-1.69728443 in 28 to -1.52728443 in 32, an additional +0.17 model-unit lift. The transformation fades to exactly zero at z=-0.86 and above and is monotonic; coordinated skin/clothes/straps move together. This is a measured model-space change, not a claim of anatomically calibrated centimeters or an exact percentage derived from the two stylized portraits.

Paths are relative to `.runtime/art-direction/series01-facebuilder-trial-01/`:

- `upperbody-package-32/character-upperbody.blend`, SHA-256 `62b0ea560cd50e4a4e9fa0b61d26667c65fc960808188fd396d57208efe84a63`.
- `upperbody-build-32/upperbody.blend`, SHA-256 `72690b37797875d5841ceb174301433711abeed52bc2310c4218c3e1c9d354e3`.
- `upperbody-portraits-32/{front,left,right}.png`: final front and ±45° views, not true profiles; matched camera-relative lighting.
- `upperbody-shoulders-32/{side,rear}.png`: final diagnostic views, not rear-design approval.
- `upperbody-verify_package-32/result.json`: fresh native reopen passes; seven file images embedded, original hidden FBHead mesh/material/shape values unchanged, protected visible surface/UV digest remains `fd256f12c5d2b7ae09496eab6da8615576a06bfa1abf60253031848d74c21f77`.
- `upperbody-facecheck-32/comparison.json`: fixed-region emission comparison, front/left/right MAE `0.00437694 / 0.00555057 / 0.00515115`, maxima `21 / 25 / 38`, pixels over 2 `53 / 136 / 97`. These match 31's numerical comparison; hair correction introduces no measured change there. Small boundary color residuals remain, as in 28; no pixel-exact color claim or altered region/gate.

**98 focused tests passed** in the final combined suite, including source/operation guards, face-boundary preservation, monotonic shortening and outward-only tension relaxation. Implementation commits `29f0ac0` and `9361a27`; result records retain handler hashes. All dispatched jobs completed with no unreconciled starts. Visual rejection of 30's cowl and 31's hair tips is distinct from successful native execution.

Remaining: simplified collarbone/neck material, regular upper-cowl folds, some shoulder leather edge irregularity, rear veil/cowl gaps and lower-body joining. The rear hood has a provisional layered curtain silhouette. These are explicit limitations, not a finished all-angle asset. No rig, animation, hair/cloth dynamics, final illustrated-C lighting or horse integration has been qualified. Do not continue face/jaw sculpting to solve them.

Attribution is unchanged from refinement 02: adapted hood from lam_m_zack's **Hijab**, CC BY 4.0; visible other garment/hair/harness geometry locally authored, with approved project illustrations as references. Hidden historical donor objects remain in this internal working scene; not a cleaned redistribution bundle.

Resource record: four candidates (29–32), including one diagnosed repair beyond the three-candidate forecast. Retained candidate evidence totals **155,601,055 bytes / 53 files**, excluding job inputs, logs and operating export: approximately 5.6 MB over the 150 MB forecast. All failures retained; no deletions, paid provider calls, purchases, uploads or remote pushes. Recorded activity starts 14:59:18 UTC; exact end/wait boundaries are in `costume-refinement-03-operating/`. Initial inspection before capture is not included. Engineering tokens/model effort/cost allocation and exact historical experiment net time remain UNKNOWN. Native evidence lives on the SSD; Git commits are not an off-machine asset backup.

This block concludes the requested modest proportion correction and bounded finishing pass. The wider FaceBuilder episode stays open, with Director review pending. Implementation and documentation commits remain separate. Planning exchange counter remains 119.
