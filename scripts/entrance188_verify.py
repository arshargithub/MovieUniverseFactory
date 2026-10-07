"""Read-only source/reopen checks; emits a separate technical receipt, not art approval."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    import argparse
    parser=argparse.ArgumentParser();choice=parser.add_mutually_exclusive_group()
    choice.add_argument('--final',action='store_true');choice.add_argument('--selected',action='store_true');args=parser.parse_args()
    selected=BASE/('entrance188-seal12' if args.selected else 'entrance188-finish09' if args.final else 'entrance188-transport06')
    fresh=BASE/('entrance188-reopen13' if args.selected else 'entrance188-reopen10' if args.final else 'entrance188-reopen07')
    source=json.loads((selected/'result.json').read_text())
    reopened=json.loads((fresh/'result.json').read_text())
    audit=json.loads((BASE/'entrance188-audit07/result.json').read_text())
    if digest(selected/'scene.blend')!=source['native_sha256']:raise ValueError('Native changed')
    if source['native_sha256']!=reopened['native_sha256']:raise ValueError('Wrong reopened native')
    if reopened['frames']!=([217,265,276,309,360] if args.selected else [217,265,309,360]):raise ValueError('Incomplete reopen')
    caches=[]
    for row in source['caches']:
        path=(selected/row['path']).resolve()
        if not path.is_relative_to(BASE.resolve()) or digest(path)!=row['sha256']:raise ValueError('Cache changed')
        caches.append({**row,'bytes':path.stat().st_size})
    if args.final or args.selected:
        previous=json.loads((BASE/'entrance188-transport06/result.json').read_text())
        if {r['object']:r['sha256'] for r in source['caches']}!={r['object']:r['sha256'] for r in previous['caches']}:
            raise ValueError('World-only edit changed a motion cache')
    protected={
        'natural152-seal-16/natural-hair.blend':'9a204ec2e3951274aeff52aeb554de6b8bc7fa169933e27bfea7073bb62f323f',
        'body168-hip66/adult-body-fit.blend':'1ed613b16dc5b618ae601b9645f6042927e036f60f74314a31fc07e3c5e5c327',
        'wardrobe186-delivery06/riding-corrected.blend':'2dffaf976e1e2e9848f832c149c4578a4a65bbdbaefca67ba1c7e8703db8340e',
        'wardrobe185-seal02/neutral-look-master.blend':'8efd1cfee9684d2b479bc6b24e1e993d0f1a1147ad62f72c72cf82a611f313aa'}
    for name,expected in protected.items():
        if digest(BASE/name)!=expected:raise ValueError('Protected source changed: '+name)
    pixel=[]
    for frame in reopened['frames']:
        name='frame-%04d.png'%frame
        with Image.open(selected/name) as im:a=np.asarray(im).astype(np.int16)
        with Image.open(fresh/name) as im:b=np.asarray(im).astype(np.int16)
        error=np.abs(a-b)
        if error.max()>1:raise ValueError('Reopened appearance changed')
        pixel.append({'frame':frame,'max_channel_difference_8bit':int(error.max()),'mean_channel_difference_8bit':float(error.mean())})
    rows=audit['root_attachment_samples']
    if [r['frame'] for r in rows]!=list(range(217,361)):raise ValueError('Incomplete attachment audit')
    art=ROOT/'.runtime/art-direction/series01-entrance-art188'
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in sorted(art.iterdir()) if p.is_file()]
    output=BASE/'entrance188-operating';output.mkdir(exist_ok=True)
    target=output/('technical-verification-selected.json' if args.selected else 'technical-verification-final.json' if args.final else 'technical-verification.json')
    if target.exists():raise ValueError('Preserve existing verification')
    result={'native_sha256':source['native_sha256'],'caches':caches,'protected_files':protected,
        'reopen_pixel_differences':pixel,'appearance_tolerance':'One 8-bit channel level; not bit-identical',
        'attachment_frames':144,'max_fuzz_root_ring_distance_native':max(r['max_radial_root_distance_native'] for r in rows),
        'generated_inputs':inputs,'builtin_generation_calls':3,'generation_tokens':None,'generation_cost_usd':None,
        'groom_scope':'Fixed surface transport and authored flutter; not physical hair dynamics',
        'record_correction':'transport06 inherited an obsolete root-lag motion label from guide construction. Its method field and captured code establish fixed transport without root lag.',
        'visual_gate':'NOT_RUN_BY_THIS_SCRIPT','scope':'Technical source/attachment/reopen only. Separate human-proxy visual review required.'}
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'receipt':str(target),'caches':len(caches),'reopen_max':max(r['max_channel_difference_8bit'] for r in pixel)}))


if __name__=='__main__':main()
