# 3D-02 qualification report

**Decision: GREEN**

The frozen external asset set passed safe acquisition, digest verification, Blender import, normalization, material repair, texture packing, native save/reopen, targeted revision, Director review, and provider-free replay.

- Authoritative run: `asset-set-v1-20260910T034104Z-cffdd816`
- Source commit: `40f604e812cc2773ad0222e44c823eba354fd066`
- Source tree: `153726123a13547c775483183895e56821808f8d`
- Evidence tag: `3d-02-v1-green`
- Director score: **4.7/5**; no hands-on edits
- Provider calls and API cost: **0 / $0**
- Replay differences: **0**
- Baseline/revision save-reopen differences: **0 / 0**
- Packed images verified by SHA-256: **5/5**
- Motorcycle topology: **10,746 vertices / 10,477 polygons**
- Sword topology: **150 vertices / 80 polygons**
- Courtyard topology: **3,536 vertices / 2,178 polygons**

The motorcycle is normalized to 2.4 m and grounded. The sword is normalized to 1.0 m and supported by a verified imported plinth. The revision translates only `motorcycle_01` by 0.6 m on X and rotates only `sword_01` by 25 degrees on Z.

The result qualifies this frozen CC0 FBX/GLB set and the two supported structured revisions. It does not qualify arbitrary asset formats, rigging, animation retargeting, topology repair, or production-quality rendering.
