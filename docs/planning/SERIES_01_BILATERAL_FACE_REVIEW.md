# Bilateral face review and right-cheek correction

2026-09-19. Director says the shown left-angle face looks perfect, but the previously shown right remains wrong. Explicit instruction: compare both sides first, protect the liked side, then present left/front/right together. These refer to existing render suffixes (camera at -30/0/+30 degrees), not clinical anatomical left/right or true 90-degree profiles.

## Result

Current review candidate: `.runtime/art-direction/series01-facebuilder-trial-01/bilateral-02/head-bilateral.blend`. Identity approval remains provisional; no assumption of Director approval of the corrected right side or unfinished garment. Current authority is the liked left appearance plus approved portrait pair B. Do not present a single favorable side as completion evidence.

`bilateral-01/` diagnoses textured versus neutral-clay front and both angles under equal mirrored lights; original review lights are restored for final comparison. Clay shows modest geometric asymmetry but not the same strong discrepancy in cheek/jaw shading. The right side's texture has smoother, less distinct cheek-to-jaw transition. This supports material-first correction; it does not prove that every perceived side difference is exclusively texture.

`bilateral-02/` transfers only localized lower/outer-cheek color from the liked left side onto the flagged right through mirrored surface/UV correspondence with a smooth mask. Central face, upper face, original source images, all geometry and existing shape-key values are retained. Mask is zero on the left half. This is material detail transfer, **not** whole-face symmetry or altered bone anatomy. Portrait-derived baked shadows are also transferred, so this is not lighting-independent reconstructed skin.

Protected geometry/primary UV/shape-key/transform digest before and after: `f6a1e3970a74bb325e72a1c0b23c603a34673c225d9b3553b2c8a4a80ea658b6`. Source reconstructed blend SHA-256 remains `c61e0ea06ba7973e416fc2d3cbc78f929d2f491e06286f70292246a2cd1a59fc`. This digest includes the prior provisional cheek key; it must not be confused with original v02 geometry. Mirrored nearest-surface distances in 717 fully weighted sample vertices: mean .0038453, max .0084375 model units; descriptive correspondence metric, not an anatomical symmetry threshold.

Inspected `review-left.png`, `review-front.png`, `review-right.png` together. Right cheek/jaw material definition is improved without new global face slimming. Left-side shader input is unchanged; indirect illumination means pixel identity is not asserted. Garment holes/overlaps and rough shoulder folds persist and were intentionally not hidden or labeled fixed. No downloaded hair mesh is present in these renders; visible scalp hair remains projected texture.

Evidence includes `before-*`, `balanced-before-*`, `clay-*`, `balanced-after-*`, `review-*`, and `result.json`. Final review uses the same prior key/fill setup and framing at all three camera positions; the balanced comparison set uses equal mirrored lights for side diagnosis. No 90-degree profile/all-angle or animation qualification. Added UV/attribute/material nodes are not yet baked into the earlier portable head package.

45 scoped tests pass; native diagnostic and repair both succeeded. Source files preserved, no paid calls, local code/documentation commits only. Planning counter unchanged for this implementation continuation. Next creative review must retain the left/front/right set; no further changes to the liked side without a specific reason and approval.
