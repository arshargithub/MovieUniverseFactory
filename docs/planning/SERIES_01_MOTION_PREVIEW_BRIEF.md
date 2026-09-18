# C motion preview — bounded brief

Exchange 79, 2026-09-18. Director authorized narrow Runway API implementation after plugin billing mismatch; total generation ceiling remains USD 5. Three initial five-second clips; at most one correction per treatment, no automatic retries. Forecast 15–25 net minutes including setup/tests/retrieval, provider wait unknown, under 100 MB initial media. Reassess at 20 net minutes; stop/review at 60. No Blender or full renderer qualification.

## Intention, reference and invariants

Compare continuous cinematic movement, cinematic movement with illustrated punctuation, and overt moving-comic timing. Reuse left panel of C v04 (Pashtun gallop); mechanically extract it without redesign. Input face/horse/clothing are provisional, not canon. Original Director request: “I think i need to see the alternatives. how can we generate quick moving examples?”

No human/horse motion reference has been reviewed for this pass. This is an agent-authored motion proposal from the existing still, not biomechanical validation. Same model, input, seed 303, five seconds, 720:1280, silent MP4 for all three; prompts differ only in temporal treatment. Request camera tracking backward at the rider's pace, avoiding an artificial zoom-only still. Preserve indigo/ochre painted masses and ink outlines; no photorealistic conversion, new equipment or powers.

| Phase | Intention | Head/torso | Arms/hands | Contact and support |
|---|---|---|---|---|
| 0–1 s | Continue existing gallop, no new action setup | Alert gaze along route; torso absorbs gait | Elbows flex, hands maintain reins | Rider remains seated/feet supported; horse grounded cyclically |
| 1–4 s | Purposeful advance, readable rhythmic stride | Coordinated hips/torso/head, not rigid translation | Reins move with horse head, not fixed in world | Four consistent legs; contact/suspension phases, dust follows hoof impacts |
| 4–5 s | Continue through shot, no abrupt finish pose | Sustained intent | Maintain control | No fall, teleport or sudden stop |

Cinematic variant runs continuously. Illustrated variant requests two brief, intentional key-pose accents while preserving spatial trajectory. Comic variant requests held drawn poses with short transitions, while retaining the same action/camera intent. Timing adherence is observed, not guaranteed. Do not label generic stutter as intentional limited animation.

## Constraint compatibility and review

There is no editable rig or world-space solver here; bone/transform constraints, exact joint geometry and deterministic replay are NOT_TESTED. Contact and appearance are perceptual invariants. Cloth may flow without passing through face or horse. Whole rider and horse must remain coherently connected, not separate sliding cutouts. Background motion may vary but should maintain location identity. No prompt can guarantee these constraints; inspect outputs.

Technical checks: playable H.264/MP4, 720×1280, duration 5 seconds within 0.25 s, no unwanted audio. Perceptual checks: full playback by Director, supplementary sampled frames for identity/style/deformation, temporal differentiation and camera/action adherence. Samples alone do not certify motion quality. No invented naturalness scores or full qualification GREEN. If variants converge, record inconclusive comparison; do not spend the rest of the balance polishing automatically.

## Learning delta and architecture continuity

| Prior evidence | Change | Verification / disposition |
|---|---|---|
| B/C wrong triptych geometry | Use one existing panel, vertical output | ADOPT: inspect extracted input before paid submission |
| 3D-05 reactive motion repairs | State intent, joint/contact coordination and limits first | ADOPT: this brief; no claims of inaccessible geometry checks |
| Original Capability Decision 8 and handoff decision | Preserve input/output identity, style, cost, task IDs and failure evidence | ADOPT: see source approvals in SERIES_01_ART_DIRECTION_C.md |
| Plugin Free workspace vs funded API account | Use authorized narrow API provider | ADOPT: verified API balance 1000 credits; no web upgrade |

Cost model: gen4.5 at 12 credits/s, $0.01/credit; five seconds estimated $0.60. Existing append-only ledger reserves before each physical submission. Unknown actual charges retain reservation; account deltas are corroboration, not independent per-task invoices. Signed output URLs stay in private ignored runtime storage. No provider response code executes locally. Implementation and design commits remain separate. Full API integration, hybrid handoffs, cross-shot identity and targeted revision remain unqualified.
