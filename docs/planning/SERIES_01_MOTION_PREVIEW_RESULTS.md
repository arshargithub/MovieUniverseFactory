# C motion previews — first pass

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
