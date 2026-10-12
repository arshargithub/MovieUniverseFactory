"""Assemble source-bound camera-cut repair; preserve original failed frame."""
import json,os,sys
from pathlib import Path
import numpy as np
from PIL import Image
from finish237_edit import digest
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-finish237'
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
def main():
    if sys.argv[1:]:raise ValueError('Closed frame-reuse operation')
    src=OUT/'route04-full';fixed=BASE/'finish237-route05';out=OUT/'route05-full'
    old=json.loads((src/'result.json').read_text());meta=json.loads((fixed/'result.json').read_text())
    if out.exists() or not old['complete']:raise ValueError('Incomplete source or existing output')
    if [r['index'] for r in old['frames']]!=list(range(198,504)):raise ValueError('Chronology incomplete')
    if digest(BASE/'finish237-route04/scene.blend')!=old['source_sha256']:raise ValueError('Original native changed')
    if digest(fixed/'scene.blend')!=meta['native_sha256']:raise ValueError('Repair native changed')
    if meta.get('source_sha256')!=old['source_sha256']:raise ValueError('Repair not bound to original render')
    for row in meta['caches']:
        if digest((fixed/row['path']).resolve())!=row['sha256']:raise ValueError('Repair cache changed')
    # Result extras are written by the native save helper; reject unproven reuse.
    if meta.get('changed_camera_frames')!=[462] or meta.get('motion_blur') is not False or meta.get('body_material_cache_edits') is not False:
        raise ValueError('Missing camera-only invariance proof')
    parity={}
    for i in (244,246):
        a=np.asarray(Image.open(src/f'frame-{i:04d}.png')).astype(float)
        b=np.asarray(Image.open(fixed/f'frame-{i:04d}.png')).astype(float)
        if a.shape!=b.shape:raise ValueError('Neighbor shape mismatch')
        parity[str(i)]=float(np.max(abs(a-b)))
        if parity[str(i)]>1:raise ValueError('Neighbor render parity failure')
    rows=[]
    for row in old['frames']:
        p=src/f"frame-{row['index']:04d}.png"
        if digest(p)!=row['sha256']:raise ValueError('Original frame changed')
        actual=fixed/p.name if row['index']==245 else p
        rows.append(dict(row,sha256=digest(actual),reused=row['index']!=245,origin=str(actual),seconds=None if row['index']==245 else row['seconds']))
    out.mkdir()
    for row in rows:os.link(row['origin'],out/f"frame-{row['index']:04d}.png")
    result=dict(source_sha256=meta['native_sha256'],complete=True,frames=rows,
        reuse_evidence=dict(original_native_sha256=old['source_sha256'],repair_result_sha256=digest(fixed/'result.json'),neighbor_max_channel_delta=parity,
        unchanged_integer_camera_frames=305,motion_blur=False,rerendered_global_frame=245),
        status='COMPLETE_FRAMES_PENDING_INTEGRATED_VISUAL_REVIEW')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['reuse_evidence']))
if __name__=='__main__':main()
