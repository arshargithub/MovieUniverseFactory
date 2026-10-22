# 351 matched bare control diagnosis

Actual55 controls: rest front/back, native90-degree lowerarm bend front/back,
custom327 front/back. Located under `.runtime/factory-native/sikh351-c55-anatomy_*`.
Rest and native bend retain a rounded outer elbow. Custom327 has a sharp rear
elbow slit, flattened upper-arm wedge and abrupt shoulder junction. Both sides
must be inspected; this is not a completed anatomical or appearance pass.

Inventory: body relative to rig is identity; all inspected joint frame
determinants are1, so gross object scaling is not supported as cause. Body uses
linear skinning. Rest split bones are mildly non-collinear; inherited custom
solve straightens each subchain and derives rotations independently by shortest
swing. That does not preserve the anatomical elbow bend plane. Exact joint
endpoints alone cannot establish a correct skin deformation.

Cycle56 discriminating candidate transports the rest elbow plane to the posed
bend plane and preserves the split-chain curvature, original shoulder origins,
wrist and every finger matrix. No mesh smoothing, body shape, weights or material
change. Inspect283/327/350 from both sides before clothing. If this does not
remove the sharp crease without shoulder/wrist regression, reject; do not call
numerical contact or render success anatomical approval.

Cycles53 and54 were planning-dependency and Blender-startup failures respectively;
55 produced controls. All remain charged to the existing shared limit57.
