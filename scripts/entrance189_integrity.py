"""Read-only bounded source/cache receipts; not a visual or dynamics verdict."""
import hashlib
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_groom import read_mdd
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    folder=BASE/'entrance189-performance14'
    result=json.loads((folder/'result.json').read_text())
    if digest(folder/'scene.blend')!=result['native_sha256']:raise ValueError('Selected source changed')
    original=json.loads((BASE/'entrance188-seal19/result.json').read_text())
    current={row['object']:(folder/row['path']).resolve() for row in result['caches']}
    old={row['object']:(BASE/'entrance188-seal19'/row['path']).resolve() for row in original['caches']}
    changed=[]
    for row in result['caches']:
        path=current[row['object']]
        if not path.is_relative_to(BASE.resolve()) or digest(path)!=row['sha256']:raise ValueError('Cache changed')
        if digest(path)!=digest(old[row['object']]):changed.append(row['object'])
    if set(changed)!={'MF185_moving_shawl','MF188_flowing_mane','MF185_gait_Full Bushy Flowing Horse Tail'}:
        raise ValueError('Unexpected source motion changed')
    tailname='MF185_gait_Full Bushy Flowing Horse Tail'
    tail0=read_mdd(old[tailname]);tail=read_mdd(current[tailname]);roots=tail0[0,:,1]<6.35
    mane0=read_mdd(old['MF188_flowing_mane']);mane=read_mdd(current['MF188_flowing_mane'])
    rows=[]
    for i in range(144):
        root_error=float(abs(tail[i,roots]-tail0[i,roots]).max())
        a=np.asarray(mane0[i]).reshape(3141,12,3,3).mean(2)[:,0]
        b=np.asarray(mane[i]).reshape(6282,12,3,3).mean(2)[:,0]
        mane_error=float(abs(b-np.repeat(a,2,axis=0)).max())
        if root_error>1e-6 or mane_error>1e-5:raise ValueError('Root transfer failed')
        rows.append({'frame':217+i,'tail_root_error_native':root_error,'mane_root_center_error_native':mane_error})
    protected={
        'natural152-seal-16/natural-hair.blend':'9a204ec2e3951274aeff52aeb554de6b8bc7fa169933e27bfea7073bb62f323f',
        'body168-hip66/adult-body-fit.blend':'1ed613b16dc5b618ae601b9645f6042927e036f60f74314a31fc07e3c5e5c327',
        'wardrobe186-delivery06/riding-corrected.blend':'2dffaf976e1e2e9848f832c149c4578a4a65bbdbaefca67ba1c7e8703db8340e',
        'wardrobe185-seal02/neutral-look-master.blend':'8efd1cfee9684d2b479bc6b24e1e993d0f1a1147ad62f72c72cf82a611f313aa'}
    for name,sha in protected.items():
        if digest(BASE/name)!=sha:raise ValueError('Protected original changed')
    output=BASE/'entrance189-integrity18'
    if output.exists():raise ValueError('Preserve receipt')
    output.mkdir();(output/'handler.py').write_bytes(Path(__file__).read_bytes())
    (output/'result.json').write_text(json.dumps({'native_sha256':result['native_sha256'],
        'cache_count':len(result['caches']),'changed_caches':changed,'root_checks':rows,
        'protected_files':protected,'visual_gate':'NOT_RUN','scope':'Exact protected files, dependency hashes and groom roots; not contact or natural dynamics qualification'},indent=2)+'\n')
    print(json.dumps({'cache_count':len(result['caches']),'protected_files':len(protected),'frames':len(rows)}))


if __name__=='__main__':main()
