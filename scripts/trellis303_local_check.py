"""Read plain safetensors with NumPy locally; no model execution or installs."""
import hashlib
import json
from pathlib import Path
import struct
import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def inspect(path):
    raw=path.read_bytes()
    length=struct.unpack('<Q',raw[:8])[0]
    if length>1024*1024 or length+8>len(raw):raise ValueError('Invalid safetensors header')
    header=json.loads(raw[8:8+length]);arrays={};records={};ranges=[]
    for key,entry in header.items():
        if key=='__metadata__':continue
        dtype={'F32':'<f4','I32':'<i4'}[entry['dtype']]
        start,end=entry['data_offsets'];ranges.append((start,end))
        if start<0 or end<start or end>len(raw)-8-length:raise ValueError('Invalid tensor range')
        array=np.frombuffer(raw[8+length+start:8+length+end],dtype=dtype).reshape(entry['shape'])
        if not np.isfinite(array).all():raise ValueError('Nonfinite tensor')
        arrays[key]=array;records[key]={'shape':list(array.shape),'dtype':str(array.dtype),
                                      'min':float(array.min()),'max':float(array.max())}
    ranges.sort()
    if ranges[0][0]!=0 or ranges[-1][1]!=len(raw)-8-length or any(a[1]!=b[0] for a,b in zip(ranges,ranges[1:])):
        raise ValueError('Gap/overlap in tensor data')
    if set(arrays)!={'shape_feats','shape_coords','texture_feats','texture_coords'}:raise ValueError('Unexpected keys')
    assert np.array_equal(arrays['shape_coords'],arrays['texture_coords'])
    for label in ('shape','texture'):
        c=arrays[label+'_coords'];f=arrays[label+'_feats']
        assert c.shape==(len(f),4) and f.shape[1]==32 and (c[:,0]==0).all()
        assert len(np.unique(c,axis=0))==len(c)
    return {'sha256':hashlib.sha256(raw).hexdigest(),'records':records,
            'coordinates_match':True,'unique_coordinates':True,'finite':True,
            'gpu_reconstruction':'NOT_RUN','decoder_equivalence':'NOT_RUN'}


if __name__=='__main__':
    from trellis301_prepare import dump
    path=ROOT/'.runtime/trellis301/cascade/retrieved/evidence/predecode/latents.safetensors'
    result=inspect(path)
    dump(ROOT/'results/trellis303/local-checkpoint-check.json',result)
    print(json.dumps(result,indent=2))
