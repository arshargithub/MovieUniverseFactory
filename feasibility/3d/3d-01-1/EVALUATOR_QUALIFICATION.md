# 3D-01.1 evaluator qualification

**Status: QUALIFIED**

The frozen reviewer is `gpt-5.4-2026-03-05` with low reasoning, low image detail, and prompt `3d011-blind-review-v3`. It passed all five accepted cases, rejected all seven negative cases, identified a critical defect in all seven negative cases, produced valid structured output for all 12 cases, and had a 0.28 mean absolute difference from the Director scores.

The balanced set contains the 30 accepted images, an earlier failed-framing pair, and six deliberately altered pairs covering a missing object, wrong color, camera drift, lighting drift, intersection, and degraded composition. Case order was blind to the reviewer.

The cheaper mini candidate was not selected because it detected only 5/7 negative cases. All earlier attempts and costs remain preserved in `results/` and the persistent ledger.

This qualifies the reviewer only for the frozen six-image 3D-01.1 rubric. It does not establish general visual judgment.
