# Frozen camera interface — Courier reuse

A new **3–5-second continuous shot** from the existing 24-second world. Director chooses the creative request after this interface is frozen; the setup smoke frame is only a technical control, not the held-out request.

Supported direction:

- Pick any existing time interval: gallop throughout, flag/head response around13–18s, destination approach toward the ending.
- Choose a front, side, rear or elevated view, with a stationary relative position or a smooth move between two relative positions.
- Choose subject scale with camera distance and a24–70mm lens; choose forward room/aim height using a fixed target offset.
- World motion, rider performance, scenery, dust and lighting stay as recorded. Preview is640×360,24fps,16 Eevee samples; no new sound design.

Coordinates are metres relative to the original moving body reference: X is lateral, negative Y is forward along the path, Z is height above that reference. Endpoint camera offsets: X[-25,25],Y[-30,30],Z[0,20]; target offsets:X[-3,3],Y[-6,6],Z[-2,3]. Camera must remain≥3m from its aim point along the interpolated move. This geometric bound does not guarantee framing, absence of scenery occlusion or compelling composition. Endpoints interpolate with smoothstep; target offset/lens remain fixed. Actor animation is unchanged.

Input is strict structured JSON bound to the accepted scene SHA. Timeline is integer global frames, start inclusive, duration72–120 frames within0–575. Output restricted to the new reuse episode's smoke verification attempts and shot/revision/replay paths. No code, arbitrary scene paths or arbitrary output paths. Supervisor translates Director wording into these parameters and records that intervention; this is not autonomous natural-language direction.

One full shot followed by one Director-requested meaningful composition revision. No post-freeze implementation edits may be hidden; any required code repair makes the primary result reuse not demonstrated (at most one repair inside the same budget). All work counts toward60 active minutes, including setup≤20; native process sum≤30min, additional paid API≤$5 including retries and stricter campaign ceiling retained. No provider calls planned. One worker;5GiB free-space guard. No render while waiting for the creative request.
