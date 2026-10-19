# Forehoof orientation control

The first study was interrupted after source review found that its Euler edits
could not affect quaternion-driven bones. Its images are invalid controls, not
failed artistic variants. `jointstudy-05` applies offsets around the admitted
bone-local equivalent of the rig X axis, preserving the rest of the pose.
Compare the actual hoof/leg silhouette, not the nominal rotation number.

Study05's evaluated coordinates changed, but render-time evaluation restored
the keyed pose. Its images therefore do not test the changed pose. Study06 keys
the bounded diagnostic offsets at the test frame and restores the captured
baseline quaternion before each variant. The coordinates also show that reducing
the wrist angle raises the hoof; the initial direction assumption was wrong.
