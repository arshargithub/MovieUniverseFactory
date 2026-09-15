# Five-second camera-only successor

User authorized the camera move and deferred all production changes. This requires a disclosed extension beyond the frozen two-endpoint interface: at most six validated timed camera offsets, joined with smoothstep segments, including explicit repeated-offset holds. One repair/extension is used; no actor/world changes. Original reuse result stays not demonstrated; current category is code-assisted.

Use existing global frames144–263 at24fps (five seconds). Relative camera starts centered12m behind and20m above the moving body reference; this is higher than the previous15m aerial offset. Travel to the horse's right side (negative worldX as the horse travels negativeY), then settle ahead and slightly to its right:

| Normalized time | Camera offsetXYZ metres | Intent |
|---|---|---|
|0|0,12,20|Centered elevated rear|
|.35|-10,0,2.2|Parallel side view reached|
|.52|-10,0,2.2|Hold side view|
|.84|-3,-10,1.8|Offset frontal tracking reached|
|1|-3,-10,1.8|Hold frontal tracking|

Lens32mm, original moving-body aim reference,640×360/16-sample Eevee. Five seconds makes this a brisk camera move; no invented slow motion or gait changes. Existing12m/s travel, horse/rider, dust, vegetation, lighting and audio design are protected. Silent preview avoids unrelated sound work; full movie sound remains unchanged.

Numerical validation enforces exact keys, finite bounded coordinates,2–6 strictly ordered knots spanning0–1, consistent endpoints and exact minimum3m camera-to-target distance on every interpolated segment.26 relevant offline checks pass, including hold behavior, near-knot continuity and invalid/code-bearing requests. Worker still hashes the baseline and checks noncamera identity/mesh/animation fingerprints before/after and on saved-scene reopen. Fingerprint limitations remain documented.

Initial render order covers start, first side view, end of side hold and final view before filling remaining frames; all source frames are reused in the final120-frame sequence. Inspect these camera extremes while production runs and stop on obvious framing failures. No additional smoke-only native job. One worker, compressed new scene,5GiB reserve. Measured forecast around25min native for this clip; cumulative90min ceiling includes prior654.71seconds and leaves room for one later Director revision/replay. Engineering60min and API$5 ceilings unchanged; no API calls planned.
