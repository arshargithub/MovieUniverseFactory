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
