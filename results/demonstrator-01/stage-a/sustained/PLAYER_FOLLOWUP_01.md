# Frame-label reliability follow-up

Director reports that displayed frames21 and22 are visibly identical, with slight foreleg movement at23. This observation is retained. Source-frame hashes and separately decoded MP4 frames21/22 differ; that does not prove what the browser displayed under those labels.

Code inspection finds the original slider updates its label immediately, without awaiting seek completion, and requests exact boundary timestamps n/24. These are presentation ambiguities. Browser reproduction of the reported pair has not been established; do not assert the precise cause is proven. The earlier source-only rebuttal was insufficient.

A separate [frame-exact inspection page](../../../../runs/demonstrator-01/sustained-preview/review-frame-exact.html) now uses numbered PNGs for stepping, waits for both images to decode before confirming the frame label, and uses presented-video metadata where supported during playback. It starts at frame21. The old player, MP4s, animation and sealed manifest remain unchanged. All288 referenced images exist and JavaScript syntax was checked; interactive browser behaviour has not been independently verified.
