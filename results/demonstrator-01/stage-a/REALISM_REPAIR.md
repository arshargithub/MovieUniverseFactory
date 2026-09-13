# Head, tail and gallop-coordination repair

Status: complete intermediate development candidate; Director review pending. [New comparison page](../../../runs/demonstrator-01/realism-motion/review.html). Stage A remains open. No full-film production, replacement asset or paid media generation has started.

## Director direction and changes

The Director described the previous tail as wiry/mop-like, the head as too big, and an uncertain mismatch between stride/body movement and travel. Overall the motion was considered fairly decent and natural. Scores and review duration were not supplied; this is not retrospective acceptance of the previous failed contact screen. [Recorded feedback](realism-director-feedback.json).

The repaired candidate multiplies the existing head-control scale by 0.67, with face/helmet attachments following its existing hierarchy. It retains the source tail groom with 12 interpolated children instead of one, reduced clumping/roughness, and fine tapered strands. Old unstable dynamics stay disabled. These are appearance adaptations; no physical tail simulation claim.

The last-frame black region was actual scene occlusion: camera rays toward horse, body, head and saddle hit `Icosphere.001` immediately outside the camera. The diagnostic rock was moved away from the camera path. Both views now test four actor-center rays on every frame before rendering. This checks those rays, not every screen pixel; complete playback still matters.

Dense source sampling at 1/32-frame intervals revealed the actual near-floor stance windows. A joint minimax fit across all four hooves selects 6.47 m/s, versus 3.454 m/s previously. The existing gallop cadence is retained; source vertical motion is preserved. All world-space rider, tack and rein travel is compensated together, avoiding a horse that accelerates away from its rider. A separate existing-IK layer uses these dense intervals, rather than the earlier coarse windows. Maximum correction is 0.2272 m, below the retained 0.30 m cap.

## What this does and does not establish

The pre-render 1/16-frame screen over two cycles measures 0.005344 m stance travel, 0.001699 m floor penetration and 0.003529 m rein endpoint error, against 0.05 m, 0.02 m and 0.01 m limits respectively. The previous 0.220464 m result remains preserved. No threshold was relaxed. The new fit is tested between its 1/8-frame animation keys. Repeated source geometry is still the sole estimator; these numbers do not independently establish physical contact, skin quality, hand enclosure or stirrup fit.

The smaller head and fuller tail must be judged in playback. This fixture fit does **not** yet establish the ultimate full-pace extended gallop: 6.47 m/s at 2.4 cycles/s yields only 2.70 m per cycle. Relevant measurements of event horses report approximately 12.09 m/s and 6.04 m strides; racing Thoroughbreds show a different, faster envelope. These are reference context, not universal gates for this courier. [Event-horse study](https://pubmed.ncbi.nlm.nih.gov/8470461/), [Thoroughbred study](https://pubmed.ncbi.nlm.nih.gov/33098592/).

A realistic extended stride needs a coordinated change in footfall timing, limb reach and body travel on the existing rig. Accelerating video or hiding the feet under dust would not establish it. The [motion brief](../../../feasibility/demonstrator-01/REALISM_REPAIR.md) retains the full-pace goal and the Director's visible trailing dust/dirt-cloud direction. Dust remains unrendered until the base motion and production gate support it.

## Validation, process and boundaries

The fixed repository handlers read only the hash-admitted existing scene, with embedded scripts disabled and a credential-free Blender environment. They cannot accept runtime code. 21 focused unit tests passed; the added tests reject altered modes, nonempty profiles, injected code fields and output escape. Native source measurements, six pose probes and contact screens preceded full rendering. Original assets and historical scenes are unchanged.

Automatic approval initially rejected the full render as exceeding the compute budget. The ledger established that the prior repair ended at 16:41 UTC and the new Director-requested pass started at 18:08 UTC. This pass had used 92.93 native seconds; the proposed 580-second hard timeout capped exposure at 672.93 seconds, below its 900-second ceiling. Review accepted that evidence and dispatch proceeded. No bypass or duplicate render was used. [Budget proof](realism-budget-proof.json).

No paid API request was made in this pass. The existing campaign total remains $2.156012501 with no outstanding reservations; this is a local calculated estimate, not invoice reconciliation. Subscription token usage remains unknown. All native jobs have completed; measured totals follow.

The captured source lives in [realism-source](realism-source/binding.json); its later fixed reopen verifier is identified separately. Failed prior candidates remain unchanged. The repaired tail is denser and less tangled, but final groom/shading quality remains a visual judgment, especially at diagnostic resolution.

## Completed playback and save/reopen result

Both lateral and three-quarter MP4s contain exactly 60 frames at 24 fps, 2.5 seconds. [Comparison](../../../runs/demonstrator-01/realism-motion/review.html) · [lateral video](../../../runs/demonstrator-01/realism-motion/lateral.mp4) · [contact video](../../../runs/demonstrator-01/realism-motion/threequarter.mp4). The last contact frame was visually inspected and the black obstruction is absent. Player JavaScript passes syntax validation; no automated browser playback claim is made.

The exact saved scene was reopened with scripts disabled, then sampled through all frames 0–59 at **0.05-frame intervals**, off both the source sampling and bake grids. Maximum stance travel: **0.005901 m**; penetration: **0.001699 m**; rein-endpoint gap: **0.003527 m**. Screen result: **True**. Actor mesh bounds are finite at all integer frames. Persisted head scale and tail density match the intended changes. This verifies saved-state screens, not physical hair, skin/contact surfaces or artistic acceptance. [Reopen evidence](../../../runs/demonstrator-01/realism-reopen/reopen.json).

Recorded activity: **20.1 minutes** including overlapping native work; native process time: **11.88 minutes** against 15; final two-view rendering: **7.72 minutes**. **$0 new paid API cost**. No render was discarded in this pass. The six-pose probe and one complete two-view candidate are retained, as are all previous failed results. [Summary](realism-summary.json).

The next motion-design problem is extended stride at full pace on the existing rig, with supporting limb reach, footfalls, suspension and rider absorption. The final visible dust/dirt trail remains part of the film target, with contact-driven emission and measured render cost. Neither it nor full production is silently declared complete by the successful intermediate contact screen.

[Checksummed inventory](realism-manifest.json): 175 artifacts retained in place, with no duplicate archive.
