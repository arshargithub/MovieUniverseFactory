# Director-supplied free Hijab donor — audit and static fit

2026-09-19. Implementation continuation; planning exchange count unchanged. Director supplied `/Users/adisharma/Downloads/hijab.glb` after selecting the first shortlisted free candidate. No purchase, subscription, provider call or upload.

## Disposition

**Usable adaptation donor; YELLOW static candidate, not accepted costume/hair.** Unlike the earlier closed scan, this mesh contains removable mannequin geometry and a relatively lightweight garment with actual layered folds. Two fitting candidates were generated. `hijab-fit02` is preferred for further work: narrower hood and lower front wrap keep more neck and jaw visible. All three rendered views inspected. Do not substitute this checkpoint for the approved portrait silhouette: the horizontal neck-wrap design still differs from its broad diagonal shoulder folds; small gaps/slivers, incomplete shoulder volume and exposed hem require repair. The original painted scalp is retained, but no replacement side/back hair or animation has been qualified.

The approved bilateral-04 face remains unchanged and authoritative. Do not reopen face sculpting to compensate for clothing/lighting. These are neutral static fit previews, not the final illustrated-C material treatment. Camera views are front and ±45° three-quarter views, **not full profiles**, with symmetric camera-relative softboxes. Lighting differs from prior artistic previews and does not establish a face material change.

## Source and attribution

“Hijab” by **lam_m_zack**, [creator/source listing](https://sketchfab.com/3d-models/hijab-ee50e01adc864ccc880caed9b5eb3bcb), [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/). This exact author/title/source/license is embedded in the supplied GLB's `asset.extras`, not inferred solely from a search snippet. Keep attribution and indicate changes with any distributed derivative.

Preserved original: `.runtime/assets/series01-dressing-source/lam-m-zack-hijab/hijab.glb`.
SHA-256: `c209b25a85a8dad1def97880ee400af23d38ded876e578968004bee59203700a`.

One mesh/material, embedded PNG, no external URI or declared extensions. GLB reports 24,511 position entries and 41,994 indices (13,998 triangles before Blender/weld processing). After seam welding: 2,893 vertices, 5,499 faces and 299 boundary edges; counts refer to different pipeline stages, not interchangeable topology measurements. Connected components: **2,481 garment vertices and 412 mannequin vertices**. Original and transformed previews establish their identities; mannequin removed as a whole connected component, not by cutting a hole through the cloth.

Changes by MovieUniverseFactory: import/seam weld, mannequin removal, garment fit/deformation, thin solidify modifier, replacement plain indigo material. Original texture preserved in source; no generated texture or image editing. Face source SHA remains `c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322` and geometry/UV/shape-coordinate digest `f6a1e3970a74bb325e72a1c0b23c603a34673c225d9b3553b2c8a4a80ea658b6`.

## Evidence and verification

Paths relative to `.runtime/art-direction/series01-facebuilder-trial-01/`:

- `hijab-audit/`: isolated original garment/mannequin, four renders, native file and metadata.
- `hijab-fit01/`: first fit; hood too bulky and wrap too high. Preserved, not selected.
- `hijab-fit02/`: preferred working candidate, `donor.blend`, `front.png`, `left.png`, `right.png`, source/native hashes and structural result.
- `hijab-verify02/result.json`: fresh-process reopen verified native checksum, head geometry/UV/shape coordinates, shape values and material node/link/default-input signature against the original approved source. Not a claim of exhaustive visual or physical collision qualification.

Trusted handler: `src/movie_factory/adapters/blender/hijab_donor.py`; admits only fixed audit/fit01/fit02/verify02 structured stages and hash-pinned files. Rejects arbitrary paths/code, external GLB URIs, unexpected extensions and overwrites. 23 scoped tests passed across donor, prior dressing and matched-light handlers. Factory startup, autoexec disabled, explicit credential-free environment. This is trusted-handler execution, not an OS-isolation qualification.

First sandboxed Blender attempt crashed at startup; retained crash evidence in `.runtime/hijab-worker/temp/blender.crash.txt` and failed ledger job. Approved retry outside sandbox succeeded. Separate ledger jobs retain audit, two fits and reopen verification. Blender-reported rendering jobs were approximately 10, 9 and 10 seconds, excluding total engineering/testing/review effort; exact tokens unknown.

No final costume approval, head rig, cloth animation, full-body outfit or galloping integration. No remote push. Native assets remain ignored by Git: local code/documentation commits are **not** their off-machine backup.

## Next work

Keep this donor available; no reason to buy anything. Retain the approved face. Before spending effort on fine cloth texture, correct gaps and shoulder-led drape toward the portrait, then fit side hair to the resulting coverage. Do not reintroduce the previously rejected straight card fringe. If the donor's wrap topology cannot support the reference silhouette efficiently, reuse its useful hood/folds with a purpose-made shoulder panel rather than forcing the entire costume to inherit its design. That is an implementation recommendation, not Director approval of a new costume.
