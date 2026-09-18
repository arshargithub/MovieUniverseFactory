# C motion previews — first pass

## Director review and closure — exchange 80

**Creative comparison FAILED; bounded first pass closed YELLOW with findings.** Three technically delivered clips, zero Director-accepted outputs. Technical integration success must not hide the failed creative objective. Earlier pending-review observations below are historical.

- Clip 1 does not feel right and fails the intended face/character impression. Director loves the original partial face: young adult woman rather than girl, composed, determined and self-assured rather than angry, naturally regal without visible makeup. Preserve those qualities, not merely costume/palette.
- Clips 2 and 3 are described by the Director as essentially two frames with progressive zoom, not meaningful articulated animation. Clip 2's face is strongly rejected. Clip 3 scarcely adds to the starting image. This describes perceived motion, not a measured claim that the encoded files contain only two unique frames.
- C remains preferred. No motion grammar is selected or rejected as an artistic concept by these failed realizations. Sampled-frame inspection before handoff was insufficient to qualify temporal quality; full decode is not full playback quality review.
- Prompt audit: clip 2 requested two quarter-second pose holds; clip 3 requested six key poses held roughly half a second with short transitions. Those requests may have encouraged near-static results, but this is an unisolated hypothesis, not a proven cause. The test confounded face completion, gait, camera, illustration preservation and precise timing. Comparison assembly did not retime or manufacture the holds/zoom.
- Model was **gen4.5**, not Turbo. [Runway's model documentation](https://docs.dev.runwayml.com/guides/models/) identifies Gen-4.5 as a flagship model; it does not establish a universal identity-preservation ranking. [Official prompting guidance](https://help.runwayml.com/hc/en-us/articles/48324313115155-Image-to-Video-Prompting-Guide) recommends simple motion-focused prompts and iterative refinement. A stronger-model claim alone cannot resolve these failures.

Recommended next step, not execution authorization: anchor the original face and expression, keep its existing angle for the first motion test (approve any required unseen-face reference separately), then seek one continuous gallop with actual coordinated body motion and restrained camera movement. Only after identity/action pass, test intentionally designed timing/key poses; simple frame dropping is not a substitute for authored limited animation. Do not run another three-way batch or broad model bake-off automatically. If the simplified baseline fails, reassess reference/control or realization route before more prompt variants.

Cost remains $1.80 observed aggregate debit; no new calls this review. Remaining observed API credit $8.20, authorized preview headroom $3.20, neither is an instruction to spend. Failed evidence stays preserved. No production, targeted-edit, multi-shot identity or Blender qualification claimed. Engineering tokens and exact all-in elapsed time remain unknown; review resumption was captured late and prior setup coverage was incomplete. Operating report: `.runtime/art-direction/series01-motion-v01/operating/REPORT.md`. This record is the compact closure/handoff; any authorized continuation opens a linked episode.

## Original delivery record

2026-09-18, exchange 79. **Three technical outputs ready; Director review pending.** No motion-language selection, A5 completion or generative-route qualification claimed. No retries or additional variants used.

## Watch

[Synchronized comparison](../../.runtime/art-direction/series01-motion-v01/comparison.mp4): left cinematic, center illustrated accents, right moving comic. Labels are requested treatments, not certified adherence. Comparison only scales, labels and aligns raw clips; no retiming, frame dropping, interpolation or audio added.

- [1 — Cinematic](../../.runtime/art-direction/series01-motion-v01/cinematic-1.mp4)
- [2 — Illustrated accents](../../.runtime/art-direction/series01-motion-v01/illustrated-1.mp4)
- [3 — Moving comic](../../.runtime/art-direction/series01-motion-v01/comic-1.mp4)

All three are H.264, 720×1280, 24 fps, 5.041667 seconds, with no audio stream. Full decode/contact-sheet extraction succeeded. Source is the mechanically extracted left panel of C v04 (546×940); no generative redraw of input. Input SHA-256: `04df3f2adbf08ee5e60916fc8f42ed42e5703b1bc5ef3c89dcb95c9f60595d32`.

## Initial observations, not Director scores

One-second samples preserve a broadly inked/painted world and show changing horse/rider poses. They also show appearance drift: facial simplification, changing cape/head covering, evolving background details, and changes in scale/framing. The illustrated-accent clip visibly changes the head covering toward a hood. Exact likeness and wardrobe preservation are not established.

Sampled frames do not prove natural gait, rider contact throughout, exact quarter-second holds, six designed poses or a convincingly distinct animation cadence. Full playback review is needed to judge those. If these feel too similar, treat it as limited prompt control, not proof that the three proposed motion languages are equivalent. No automatic polishing or expensive rerolling before Director feedback.

## Cost, latency and evidence

- Model/settings: gen4.5, seed 303, duration request 5s, 720:1280, standard MP4. Frozen exact prompts: `config/series01-motion/{cinematic,illustrated,comic}.txt`.
- Three physical paid submissions, zero retries. Each reserved $0.60 in existing persistent BudgetLedger; campaign ceiling $5.
- API account snapshots: 1000 credits before, 820 after; observed debit 180 credits ($1.80 at $0.01/credit), matching pricebook estimate. Daily model generation count increased from zero to three, other model counts unchanged. Remaining API balance $8.20; remaining authorized ceiling $3.20, not permission for automatic further calls.
- Per-task invoice amounts remain unavailable/null; the ledger conservatively retains $1.80 in reservations. Account debit corroborates aggregate cost, not an independently itemized invoice.
- Submitted 18:05:56–18:05:58 UTC; first observed successful at 18:08:01, 18:09:04 and 18:11:33 respectively. These are polling upper bounds including queueing, not exact provider compute time. Tier allows one concurrent generation, and later tasks visibly waited in THROTTLED state.
- Raw videos total 17,542,298 bytes; input, comparison and sampled evidence are additional. Engineering tokens/cost unknown. Timing captured prospectively under SERIES01-MOTION-PREVIEW / first; earlier context/setup gaps disclosed, so do not infer exact all-in time from video generation latency.
- Task records, signed output URLs, budget ledger, balance snapshots and media are private/local under `.runtime/art-direction/series01-motion-v01/`; not included in Git backup.

| Treatment | Task ID | Output SHA-256 |
|---|---|---|
| Cinematic | e3f41ba0-794b-4d18-996a-fe9184eb4d04 | eed245d87e5dabd06a1a8e73506834818c3855072a51f7c678b7388c3cf8337c |
| Illustrated | 4b4c88a3-3f62-4d05-a0b0-e34b22e7a883 | 610656e6ff38464d5f5edd54612b1e0ff913fae22e5934fa780bf86288433dc7 |
| Comic | bcc04f11-62c1-4ca6-9e62-c1fd4d05fcae | 982e9329e935dad1937178f12fc773479b6b0ff2ab99b7fec27dc60d0d80b0cb |

## Architecture learning

Demonstrated a narrow funded API path independent of the web plugin: private key loading, bounded reservation, async submission, persisted IDs, restart-safe polling and local asset retrieval. Mocked security/budget tests and full unit suite pass (235 tests). Implementation commits `17c9703` (submitted-source adapter/prompts) and `3321d51` (retrieval extension) are separate from design records.

Preservation is already an important risk, not just a future integration concern. Existing original decisions remain ADOPT: choose realization per shot and check creative invariants across representation handoffs. This test does not prove targeted editing, multi-shot identity, hybrid 3D controls, deterministic replay, final production economics or accepted animation quality. No Blender qualification reopened.

Next: Director compares motion feel and reports whether differences are meaningful. Then select a preferred direction or identify failed differentiation; do not launch another campaign automatically. See [motion brief](SERIES_01_MOTION_PREVIEW_BRIEF.md) and [adapter notes](../engineering-intelligence/RUNWAY_PREVIEW_ADAPTER.md).
