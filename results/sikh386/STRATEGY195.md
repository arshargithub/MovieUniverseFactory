#195: geometric falloff, semantic protection

194restdepth target passes regional/foreleg guards, but the actual restsurface
check finds100badtriangles. Atadjacentrootpoints the raw .05..35 boneweightmask
jumps from.03to.57over~2cm, causing3..7cm displacementdifferences. The bodygraph
confirms these are actualskin, not merely alpha cards. Reject194before nativeuse.

Ownership is a hardsemantic protection set, not a continuoussculpting weight.
Retain allforearm/downstream>=.35 points exact. Calculate geodesic surface
distance to thatfrozen set usingactualskin edge lengths, with a C1smoothfalloff
across.35m. Multiply the same22%depthsectiongoal by thisgeometricfalloff, not
noisyboneweights. Restrict to the original9990point connectedskin; disconnected
hair/eye/cards are frozeninproducer andclosednativeconsumer. No gain change,
per-vertex clamp or smoothingofactualbodycoordinates.

Actualsource193geometry/ownership and physical/localspatialreferences unchanged.
195buildsinertresttarget; resttriangle/region/semanticchecks first.196willapply
onoriginalLIVErig andrender283front/sidebefore333/339. Actualvisiblebib/flattening
or newseam stillfails evenifgeometricchecks pass. IfneutralApassesbutposedrootB
fails, preserveAandnarrowtoappearancebinding, notprimarymotion.

Sameoriginaltask195/226 andshared50grant; no newresources/authority.
