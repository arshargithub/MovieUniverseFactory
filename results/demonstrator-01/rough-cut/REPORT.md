# The Courier — 24-second development rough cut

**Development YELLOW: complete rough cut; Director playback review is pending.** This delivers the authorized four-shot film, without claiming final photorealism or a newly scored GREEN campaign. No closed 3D campaign has been reopened.

Watch [the complete film](../../../runs/demonstrator-01/cut-review/the-courier-24s.mp4) or use the [review player with exact source-frame stepping](../../../runs/demonstrator-01/cut-review/review.html). The film is 24 seconds, 576 frames at 24 fps, 960×540, with original provisional hoofbeats, wind and a signal bell.

## The sequence and motion change

The six-second opening descends from an offset aerial view into a frontal tracking hold. A seven-second lateral view shows full-pace gallop and trailing dust on the meadow track. The five-second signal shot brings the rider closer as the flag rises and the head turns. A six-second departure keeps the destination in view. All shots share one continuous 12 m/s world path; the user-requested meadow replaces the earlier mountain-road concept.

The front-leg recovery uses a monotone timing warp, reaching 1.5× phase rate at mid-swing and returning to the original timing and first derivative at support boundaries. All four dependent control families on each front leg share that clock. It does not stretch the mesh to force more extension. The prior source/player investigation and the Director's perceived apex hesitation remain distinct: timing-map tests and unique PNGs do not prove that the perceived hitch is gone. Complete playback judgment remains pending.

## Verification

| Evidence | Result |
| --- | --- |
| Full motion sampling | 4,609 eighth-frame samples through frame 576; only frames 0–575 are rendered |
| Fixed material hoof travel, limit 20 mm | 10.19 mm; passed |
| Measured floor penetration, limit 20 mm | 0.00 mm; passed |
| Maximum rein gap, limit 10 mm | 3.55 mm; passed |
| Actual path travel across validation interval | 288.00 m |
| Off-grid real path-speed corruption | Positive 9.70 mm; corrupted 295.93 mm; correctly rejected |
| Saved final scene versus validated base | Zero horse vertex difference at 17 selected times; intended head offset reaches 18° |
| Relevant offline tests | 37 passed |
| Encoded timeline | 576 frames; every presentation timestamp checked against 24 fps |
| Adjacent identical source PNGs | 0 |
| Independent saved-scene frame reproduction | Pixel-identical: True; RMS channel difference 0.000000/255 |

The historical changing-centroid contact screen remains a failure: 111.48 mm against its retained 50 mm screen. It is preserved as a diagnostic, not quietly converted into a pass. The accepted material-point contact screen and its real negative control are separate evidence. Geometry and timing checks are not biological gait certification.

The [frozen cut](FROZEN_CUT.json), [motion validation](motion-validation.json), [real negative control](contact-control.json), [final reopen check](final-reopen.json), [frame inventory](frame-inventory.json), [media audit](media-audit.json), and [replay](replay.json) retain the detailed records. Scene-build preflight and independently loaded render workers produced the replay comparison; no provider call was used for replay.

## Cost, time and storage

Additional paid API cost is **$0.513970 of the authorized $10**, including the incomplete first response, retry and reasoning. Campaign cumulative calculated cost is $3.736270; no unresolved reservations remain in the recorded snapshot. These are conservative ledger calculations, not a provider invoice. No assets, paid media or cloud rendering were purchased. The sound is deterministic original synthesis.

Native jobs consumed **81.4 process-minutes**, including failed attempts, against the four-hour native ceiling. Authorization-to-finalization elapsed is **102.3 minutes**, including overlapping rendering and supervision; it is a conservative bound rather than a claim of pure active engineering time. Do not add these quantities. Subscription tokens, exact thinking time and Director review duration are unknown. See [costs](costs.json) and [operating records](operating-summary.json).

Free storage at finalization is **8.17 GiB**. Available disk fell during the initial concurrent render, consistent with memory/swap pressure, and triggered the 5 GiB guard. Exact swap attribution was not independently measured. Both failures were preserved. The current-pass intermediate scenes were losslessly compressed with verified round-trip hashes; rendering completed with one worker. Closed campaign files were untouched. See [storage preservation](storage-preservation.json) and the [process review](PROCESS_REVIEW.md).

## Scope, durability and next review

This is one modified free horse/rider fixture with authored motion, procedural meadow scenery and a bounded dust effect. The environment remains visibly simplified, the dust treatment is approximate, and the sound is provisional. Early aerial frames also show some dust/ground shading and grain variation (for example frames 8–9); this remains a rough-cut finishing limitation. The head turn and flag are a modest narrative beat; their readability is for the Director to judge. This does not establish arbitrary asset support or final production realism.

The prior authorized source push reached GitHub at `f05f0fa`. The new cut implementation is locally committed at `dae2c5dd85e85cb18d9cc495d66430df7542ff3d`; its files match the implementation digest frozen before rendering. The final film, native scenes and images remain local. No new public native-asset upload or large archive rebuild was performed. [Reproduction instructions](REPRODUCIBILITY.md) explain native paths, compressed intermediate restoration and frame assembly.

Next: review the complete film as a sequence, then inspect the lateral shot for the front-leg apex. Record story clarity, motion credibility, visual coherence, cinematography and sound/editing, plus review duration. No scores or approval are inferred from the earlier six-second preview.
