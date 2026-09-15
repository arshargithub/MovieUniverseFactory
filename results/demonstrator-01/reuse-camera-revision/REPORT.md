# Continuous camera revision — Director review pending

[Watch the revised five-second preview](../../../runs/demonstrator-01/reuse-camera-continuous-review/review.html) · [Previous preview](../../../runs/demonstrator-01/reuse-camera-review/review.html)

The Director found the earlier move too segmented: fast descent, stationary side hold and fast final sweep. The new curve takes longer to descend, moves closer while turning through the side view, and carries velocity into the final sweep. Endpoints, five-second duration and actor/world motion are preserved. The existing horse/rider/dust/scenery have not been repaired or embellished.

This is **code-assisted reuse**, with a second disclosed camera-code intervention under the explicit feedback request. It does not satisfy the original parameter-only/one-repair contract. Old requests, freezes, failures and preview remain preserved. To replay the previous runtime, use its source commit60fc086; its old source fingerprints are historical rather than assertions about the current checkout. See [feedback](feedback.json), [plan](PLAN.md), [request](request.json) and [current freeze](FREEZE.json).

28 focused tests passed, including shared nonzero interior velocity, dense bounded path sampling and conservative curve clearance. Normal native execution checked source SHA and protected noncamera fingerprints before/after and after saved-scene reopen. All120 source frames and encoded timestamps verified at24fps/5seconds; no black frames. The prior selected independent replay belongs to the previous preview and is not claimed for this revision. No repeated broad suite or additional native replay was needed for this camera adjustment.

Revision native time:11.98min. Cumulative reuse native time including every retained attempt:37.96/90min. Paid API:$0. Free disk:4.68GiB. Historical exact active/token totals and current review duration remain unknown. Director acceptance is pending; no score invented.

AWS work this turn was limited to the [S3 setup requirements](../../../docs/planning/S3_ARCHIVE_SETUP.md) and reading CLI version. No cloud resource, transfer, charge or local deletion. The next production brief remains deferred.
