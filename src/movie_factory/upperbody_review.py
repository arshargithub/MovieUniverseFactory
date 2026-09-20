"""Measure fixed matched facial review artifacts; never edit the images."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .packages import atomic_json

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def differences(a,b):
    if a.shape!=b.shape or a.shape!=(800,640,3):raise ValueError('Expected matched 640x800 RGB views')
    delta=np.abs(a[:592].astype(float)-b[:592].astype(float))
    return {'rgb_mae_0_255':float(delta.mean()),'rgb_max_0_255':float(delta.max()),
            'pixels_over_2':int((delta.max(axis=2)>2).sum())}


def measure(variant):
    if type(variant) is not int or not 1<=variant<=27:raise ValueError('Unsupported fixed variant')
    folder=BASE/f'upperbody-facecheck-{variant:02}'
    target=folder/'comparison.json'
    if target.exists():raise ValueError('Do not overwrite evidence')
    record=json.loads((folder/'result.json').read_text())
    report={'variant':variant,'native_sha256':record['verified_native_sha256'],
            'method':'Matched emission/base-color renders; first 592 image rows (orthographic z above approximately -0.84). Excludes authorized neck edits, not an aesthetic score.',
            'views':{},'sha256':{}}
    for angle in ('front','left','right'):
        arrays=[]
        for version in ('original','derivative'):
            path=folder/version/(angle+'.png')
            report['sha256'][str(path.relative_to(folder))]=hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as image:arrays.append(np.array(image.convert('RGB')))
        report['views'][angle]=differences(*arrays)
    atomic_json(target,report)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--variant',type=int,required=True)
    print(json.dumps(measure(parser.parse_args().variant),indent=2))
