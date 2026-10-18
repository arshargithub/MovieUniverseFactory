# TRELLIS301 — local opacity control

## Result

**Opacity alone does not rescue this head.** Eight matched renders were completed from the preserved298d native scene: original opaque and image-alpha-enabled materials, each at front, both quarters and rear. Geometry, object/material bindings, camera positions, lighting and render seed were held fixed. No source asset was saved or replaced. This is a completed diagnostic, not a character-production pass.

Manual review of all four paired sheets finds that alpha affects actual rendered surfaces, not only unused atlas pixels. It thins the eyebrows and removes much of the solid moustache, exposing a patchy/translucent lip outline. The nape also becomes patchier. These changes are not a convincing natural-hair improvement. The broad beard remains a coarse, lumpy solid with irregular fragments; the turban retains noisy surface cavities. Alpha cannot create separate eye/lid anatomy or coherent beard strands from absent geometry.

Compared directly with the approved Sikh v03 illustration, neither version has its legible expressive eyes, connected natural moustache/beard flow or deliberately designed cloth folds. The rugged long-face/blue-crown direction is recognizable, but recognition is not source-quality admission. Compared with the accepted Pashtun close frame, the Sikh's chunky facial-hair masses and unresolved eyes remain visibly below the existing shared-film character quality floor. This is a qualitative reference comparison, not matched lighting between different characters or a pixel-fidelity requirement. No changes to the accepted Pashtun are justified.

## Evidence and limitations

- Native source: `.runtime/art-direction/series01-trellis298/head512-remeshed/source.blend`.
- Matched angle pairs: `.runtime/trellis301/opacity/comparison-front.jpg`, `comparison-left-quarter.jpg`, `comparison-right-quarter.jpg`, `comparison-back.jpg`.
- Individual480×600 renders, material-change receipts and render log: `.runtime/trellis301/opacity/`.
- Identity authority inspected: `.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png`.
- Accepted co-star reference inspected: `.runtime/art-direction/series01-finish248/opening-final/frame-0200.png`, bound to delivery manifest and current253 approval; the wider frame0100 was also inspected for context.
- Difference metrics are recorded for reproducibility only. Changed-pixel fractions and average differences are **not quality scores**, nor proof that beard transparency improved.
- Local Blender initially crashed in sandbox Metal startup; an approved outside-sandbox offline run then exposed a missing scripts import path. After that bounded handler correction, all eight renders completed in one worker. Neither failure altered the source. No cloud operation was attempted by this subagent.

Technical render/control: PASS. Alpha-as-artistic-rescue hypothesis: rejected. Current source visual admission: FAIL. Eyes/lids, beard motion, continuous cloth release, body integration and reveal performance: NOT_RUN. The production evidence gate must remain blocked; the diagnostic itself is complete.

## Next controlled comparison and exact blocker

Keep the preserved opaque298d version as the comparison control; do not promote the alpha variant. The next useful test remains300k/2K versus1M/2K and1M/4K exports of the same preserved unsigned reconstructed shell and original attributes. It tests lost detail at export without repeating generation. The1M2K/4K pair shares exactly the same prepared geometry and UVs. Neither higher triangles nor4K guarantees improvement.

Fresh read-only AWS preflight found no c/d residual resources and no previous/301 active GPU. The export-only payload is412,803,117bytes with SHA256 `20ddd52ac059cda6508f2caf84a1c17d69dbd675d6a83aa5fafe1681470cfb4c`; it contains preserved protagonist mesh/attribute data and admitted exporter sources, no credentials or encoder weights. Prospective admission is$10 historical conservative liability plus$4 reservation under the original$15 ceiling; invoice totals remain unknown and the conditional extra$10 remains inactive.

Root's guards call was rejected by tool auto-review **before execution**, requiring explicit Director consent for this exact sensitive payload's transfer to private bucket `mf-trellis301-export-281482331395` in us-east-1. Root has requested that consent. No alternate upload, guard creation, GPU launch or paid inference may bypass this boundary. No export-comparison result exists yet. Contingent1024 worker preparation does not activate its separate dispatch/budget authority.

Once that explicit transfer approval is recorded and root authorizes dispatch, run the prepared fixed-source exporter, retrieve/verify results, remove and independently verify temporary resources, then inspect source-quality comparisons. Proceed to one adequately sized1024 test only if the fixed-source results justify it and its separate cost/authority gate passes. Do not integrate a known-failing head merely to keep footage moving.
