# Real solver warmup failure and stability correction

111 actual CLOTH pins hold within0.5um, but at251 (still stationary-pole warmup)
maximum edge stretch1.721 exceeds the unchanged1.7 guard. No native/cache/render
candidate produced. Preserve that actual failure; do not raise the guard.
Increase solver quality12->20, tension/compression45->80 and shear25->50,
mass0.12->0.20 and air damping3->4; moderate wind10->3. This tests stable woven
fabric under the same three material pins/collider/geometry, not a rigid flag.
If it still fails, capture actual deformed/rest edges and goals for diagnosis
before further settings changes. Source40 remains a capability input only;
final41 action still requires a fresh solve. Chest branch is unchanged/independent.
