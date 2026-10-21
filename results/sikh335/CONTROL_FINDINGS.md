# Horse control ownership findings

The native inspection found456 pose bones and two rig-deformed meshes: the
22514-vertex horse and72000-vertex short coat. Source320 remained unchanged.
All64 invalid armature drivers have missing object targets, but they drive
`bbone_easein` or `bbone_easeout`, not the limb IK/FK switch. Their target paths
refer to existing rubber-tweak or mane-curve properties on the horse rig.
They affect deformation interpolation and require explicit repair; they do not
by themselves explain the rigid whole-body action.

The object-level Rigify drivers were removed during the historical import.
Consequently custom IK/FK and follow properties cannot be assumed operational.
The current forelegs explicitly select FK, whereas the hind ORG chains have
both FK and IK copy constraints at full influence: the later IK result wins.
The hind IK stretch remains enabled. Neck follow is fixed at0.5 and head follow
at1.0 through actual constraints, regardless of control-property intent.

This supports a targeted, explicit ownership repair rather than generic driver
restoration or another unverified angle pass. Restore only the64 proven
same-rig property targets after resolving every path. Then establish one
authoritative limb path and solve supported whole poses with fixed bone
lengths, not arbitrary control offsets or stretch. Test visible hoof endpoints
and adjacent deformation rather than only IK target positions.

The reference comparison still fails artistically. It shows compact hindquarter
loading and neck/poll flexion before the rise; source320 lacks that coordinated
shape. Its costume, face and saddle also remain below the accepted film floor.
No pose, continuous motion, clothing or Director AV approval follows from this
inspection. The ownership diagnostic is complete; integrated335 work is open.
