#63 minimum intervention and face constraints

62 stopped on a250mm contact-jump guard at the fitted border. The code still
projected already-clear points whenever a radial ray hit some other body region.
That is unnecessary: preserve ANY seed with actual7mm clearance before casting.
For a colliding point, reject a remote radial hit and test its local outward-normal
exterior ray. Missing or250mm results still fail and now record actual data.

Apply shared-vertex corrections for colliding triangle centres, not vertices
alone. At most five bounded rounds, alternating face correction and point contact;
retain all original mesh/actions and final thickened fullframe checks. A sphere
regression has outside vertices but an inside face, and checks that the correction
repairs it while leaving an already-clear triangle exactly unchanged. This is
contact construction on a kinematic seed, not cloth/force simulation.

63 must produce actual all39frame evidence and clear revealing renders; no
qualification from the new unit test or fewer errors. Progress samples every8
frames are diagnostic only and cannot qualify an interrupted/failed cache.
