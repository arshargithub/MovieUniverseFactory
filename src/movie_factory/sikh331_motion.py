"""Whole-pose control values in native frames, not a physics simulator.

Numbers are authored hypotheses. Reference phase silhouettes and support are the
qualification, not these parameter values. No old rear curve retiming.
"""
from movie_factory.sikh318_motion import flow
# frame, body pitch, pelvis forward offset, vertical offset, spine pitch,
# neck release, poll flex, fore shoulder, elbow, wrist, rider counter pitch
POSES=(
 (252,0,0,0,0, .08,.12, 0,0,0,0),
 (283,0,0,0,0, .10,.16, 0,0,0,0),
 (298,-.06,.05,-.13,-.05, .35,.50, -.04,-.10,.12,.08),
 (306,-.16,.01,-.18,-.08, .32,.52, -.12,-.32,.42,.17),
 (314,-.48,-.07,-.06,-.10, .28,.68, -.22,-1.02,2.00,.44),
 (322,-.80,-.08,-.06,-.12, .34,1.28, -.27,-1.20,2.55,.68),
 (327,-.87,-.06,-.08,-.10, .39,1.48, -.25,-1.15,2.58,.72),
 (331,-.83,-.03,-.07,-.07, .40,1.38, -.20,-1.08,2.45,.66),
 (338,-.64,.02,-.06,-.03, .43,.75, -.10,-.70,1.55,.48),
 (344,-.32,.04,-.10,.02, .40,.61, .06,-.22,.35,.24),
 (348,-.07,.05,-.07,.04, .44,.60, .06,-.06,.07,.07),
 (350,.02,.04,-.16,.08, .51,.62, -.05,-.12,.16,.04),
 (353,.04,.02,-.21,.10, .50,.59, -.10,-.18,.23,.08),
 (358,-.01,0,-.08,-.02, .27,.37, -.02,-.05,.07,.02),
 (366,0,0,0,0, .12,.19, 0,0,0,0),
 (390,0,0,0,0, .08,.12, 0,0,0,0),
 (441,0,0,0,0, .08,.12, 0,0,0,0),
)
FIELDS=('pitch','forward','drop','spine','neck','head','shoulder','elbow','wrist','rider')
def pose(frame):
    return {k:flow(frame,tuple((r[0],r[i+1]) for r in POSES)) for i,k in enumerate(FIELDS)}
