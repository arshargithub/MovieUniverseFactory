"""Semantic chest edit boundaries from the actual inherited rig ownership.

A box mask alone cannot preserve accepted foreleg surfaces. This explicit guard
is a local actor contract, not universal anatomical or perceptual qualification.
"""
import numpy as np


def foreleg_ownership(weights,names):
    names=[str(n) for n in names]
    if not all(n in names for n in ['DEF-forearm.L','DEF-forearm.R']):raise ValueError('ANATOMY386_MISSING_FOREARM_OWNERSHIP')
    columns=[i for i,n in enumerate(names) if n.startswith(('DEF-forearm.','DEF-f_toe.','DEF-f_hoof.'))]
    w=np.asarray(weights)
    if w.ndim!=2 or w.shape[1]!=len(names) or not np.isfinite(w).all():raise ValueError('ANATOMY386_INVALID_OWNERSHIP')
    return np.clip(w[:,columns].sum(1),0,1)


def preserve_forelegs(source,target,weights,names):
    ownership=foreleg_ownership(weights,names);protected=ownership>=.35
    if not protected.any():raise ValueError('ANATOMY386_EMPTY_FORELEG_PROTECTION')
    a=np.asarray(source);b=np.asarray(target)
    if a.shape!=b.shape or a.shape[-2:]!=(len(ownership),3):raise ValueError('ANATOMY386_OWNERSHIP_SHAPE')
    if not np.array_equal(a[...,protected,:],b[...,protected,:]):raise ValueError('ANATOMY386_FROZEN_FORELEG_DRIFT')
    return dict(protected_vertices=int(protected.sum()),max_protected_delta=0.,scope='Exact inherited forearm/downstream surface preservation; not anatomical or motion approval.')


def main_skin(edges,count):
    """Connected skin component; disconnected hair/eye/card geometry stays frozen."""
    parent=np.arange(count);size=np.ones(count,dtype=np.int32)
    def find(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=int(parent[i])
        return i
    for a,b in np.asarray(edges):
        a=find(int(a));b=find(int(b))
        if a==b:continue
        if size[a]<size[b]:a,b=b,a
        parent[b]=a;size[a]+=size[b]
    labels=np.array([find(i) for i in range(count)]);return labels==np.bincount(labels).argmax()


def pectoral_domains(rest,weights,names):
    """Original scope: distal legs fixed, coupled proximal skin may be reshaped.

    Rigify's forearm group includes upper tissue. The1.0m rest-height is a
    conservative local buffer for THIS actor, not an anatomical measurement.
    """
    names=[str(n) for n in names];r=np.asarray(rest);w=np.asarray(weights)
    if not all(n in names for n in ['DEF-forearm.L','DEF-forearm.R','DEF-forefoot.L','DEF-forefoot.R']):raise ValueError('ANATOMY386_PECTORAL_RIG_REQUIRED')
    # A bilateral chest blend is not dominant ownership of either foreleg.
    side=[w[:,[i for i,n in enumerate(names) if n.startswith('DEF-forearm.'+suffix)]].sum(1) for suffix in ['L','R']]
    arm=np.maximum(side[0],side[1])
    distal=w[:,[i for i,n in enumerate(names) if n.startswith(('DEF-forefoot.','DEF-f_toe.','DEF-f_hoof.'))]].sum(1)
    frozen=((arm>=.05)&(r[:,2]<=1.0))|(distal>=.05)
    proximal=(arm>=.35)&~frozen
    if not frozen.any():raise ValueError('ANATOMY386_EMPTY_DISTAL_DOMAIN')
    return frozen,proximal


def preserve_pectoral_interfaces(source,target,rest,weights,names,*,max_proximal=.06):
    if max_proximal not in {.06,.15}:raise ValueError('ANATOMY386_PROXIMAL_POLICY')
    frozen,proximal=pectoral_domains(rest,weights,names);a=np.asarray(source);b=np.asarray(target)
    if a.shape!=b.shape or a.shape[-2:]!=(len(rest),3):raise ValueError('ANATOMY386_OWNERSHIP_SHAPE')
    if not np.array_equal(a[...,frozen,:],b[...,frozen,:]):raise ValueError('ANATOMY386_DISTAL_LEG_DRIFT')
    delta=np.linalg.norm(b[...,proximal,:]-a[...,proximal,:],axis=-1);maximum=float(delta.max()) if delta.size else 0.
    if maximum>max_proximal:raise ValueError('ANATOMY386_PROXIMAL_SKIN_LIMIT')
    return dict(policy='pectoral_coupled_skin',protected_vertices=int(frozen.sum()),max_protected_delta=0.,proximal_vertices=int(proximal.sum()),proximal_max_delta=maximum,proximal_limit=max_proximal,scope='Distal lower-leg surfaces exact; bounded necessary proximal skin reshaping only. Original skeletal action must remain unchanged. Not motion/anatomy approval.')


def evaluated_preservation(before,after,outside,rig_before,rig_after):
    a=np.asarray(before);b=np.asarray(after);r0=np.asarray(rig_before);r1=np.asarray(rig_after)
    if a.shape!=b.shape or r0.shape!=r1.shape or a.ndim!=3:raise ValueError('ANATOMY386_POSE_PROOF_SHAPE')
    outside_error=float(abs(a[:,outside]-b[:,outside]).max()) if np.any(outside) else 0.
    rig_error=float(abs(r0-r1).max())
    if outside_error>2e-5 or rig_error>1e-7:raise ValueError('ANATOMY386_EVALUATED_PRESERVATION')
    return dict(poses=[283,333,339],outside_surface_max_error=outside_error,skeleton_and_world_max_error=rig_error,scope='Actualselectedpose preservation, not fullspeed/appearanceapproval.')


def preserve_owner387(source,target,rest,weights,names,edges):
    """Declared coupled shoulder/proximal-forearm unit, not a legacy waiver.

    Only the new387 target vocabulary uses this policy. The old entire-forearm
    and1.0m pectoral guards stay unchanged for all existing callers.
    """
    r=np.asarray(rest);w=np.asarray(weights);a=np.asarray(source);b=np.asarray(target)
    if r.ndim!=2 or r.shape[1]!=3 or a.shape!=b.shape or a.shape[-2:]!=r.shape or w.shape!=(len(r),len(names)):raise ValueError('OWNER387_SHAPE')
    if not all(np.isfinite(x).all() for x in (r,w,a,b)):raise ValueError('OWNER387_NONFINITE')
    required=['DEF-forefoot.L','DEF-forefoot.R','DEF-f_hoof.L','DEF-f_hoof.R']
    if not all(n in names for n in required):raise ValueError('OWNER387_RIG')
    foot=w[:,[i for i,n in enumerate(names) if n.startswith(('DEF-forefoot.','DEF-f_toe.','DEF-f_hoof.'))]].sum(1)
    allowed=main_skin(edges,len(r))&(r[:,2]>.72)&(r[:,2]<1.88)&(r[:,1]>-1.4)&(r[:,1]<-.23)&(foot<.05)
    if not allowed.any() or not (~allowed).any():raise ValueError('OWNER387_EMPTY_DOMAIN')
    if not np.array_equal(a[...,~allowed,:],b[...,~allowed,:]):raise ValueError('OWNER387_DISTAL_OR_OUTSIDE_DRIFT')
    maximum=float(np.linalg.norm(b-a,axis=-1).max())
    if maximum>.2:raise ValueError('OWNER387_SURFACE_LIMIT')
    return dict(policy='coupled_shoulder_upperarm_proximalforearm387',protected_vertices=int((~allowed).sum()),max_protected_delta=0.,max_changed_delta=maximum,scope='Distal cannon/carpus/hoof ownership and all outside skin exact; only necessary proximal skin may change. Original joint paths/actions independently checked. No anatomy/motion approval.')
