"""Admitted data-only positive-form cache; no code or arbitrary file execution."""
import hashlib,importlib.util,json
from pathlib import Path
import numpy as np


def validate(e):
    if set(e)!={'kind','target','data'} or e['kind']!='mounted_horse_chest379' or e['target']!='horse':raise ValueError('CHEST379_FIELDS')
    b=e['data']
    if not isinstance(b,dict) or set(b)!={'path','sha256'} or not isinstance(b['path'],str) or not b['path'].startswith('.runtime/art-direction/sikh379-targets/') or '..' in Path(b['path']).parts or not b['path'].endswith('.npz') or not isinstance(b['sha256'],str) or len(b['sha256'])!=64:raise ValueError('CHEST379_DATA_BINDING')
    return e


def load(root,b):
    p=(root/b['path']).resolve()
    if not p.is_relative_to(root.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=b['sha256']:raise ValueError('CHEST379_DATA_STALE')
    with np.load(p,allow_pickle=False) as q:
        if set(q.files)!={'source','target','rest','mask','times'}:raise ValueError('CHEST379_ARRAY_KEYS')
        v={k:q[k].copy() for k in q.files}
    if v['source'].shape!=(183,22514,3) or v['target'].shape!=v['source'].shape or v['rest'].shape!=(22514,3) or v['mask'].shape!=(22514,) or not np.array_equal(v['times'],np.arange(552,735)/2):raise ValueError('CHEST379_ARRAY_SHAPE')
    if not all(np.isfinite(a).all() for a in v.values()) or np.linalg.norm(v['target']-v['source'],axis=2).max()>.45 or (v['mask']<0).any() or (v['mask']>1).any():raise ValueError('CHEST379_ARRAY_BOUND')
    if not np.array_equal(v['target'][:,v['mask']==0],v['source'][:,v['mask']==0]):raise ValueError('CHEST379_OUTSIDE_DRIFT')
    return v


def run(bpy,out,e):
    validate(e);root=Path(__file__).resolve().parents[4];q=load(root,e['data'])
    spec=importlib.util.spec_from_file_location('chest379_cache',Path(__file__).with_name('nihang_cache376.py'));base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    def target(p,rest,edges,breast,t):
        index=int(round((t-276)*2))
        if not np.array_equal(rest,q['rest']) or np.max(np.abs(p-q['source'][index]))>2e-5:raise ValueError('CHEST379_ACTUAL_SOURCE_MISMATCH')
        return q['target'][index]-p,q['mask']
    result=base.run(bpy,out,dict(kind='mounted_horse_cache376',target='horse'),target_function=target)
    result.update(method='Reference-qualified local shape-preserving ARAP target; not exact volume conservation, exact183sample data-only playback',target_binding=e['data'],artistic_pass=False)
    (out/'chest379.json').write_text(json.dumps(result,indent=2)+'\n');return result
