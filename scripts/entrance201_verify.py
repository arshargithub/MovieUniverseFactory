"""Fixed201 delivery checks; numerical evidence is not an artistic pass."""
import json
from pathlib import Path
from entrance193_media import pixel_parity,sha
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'

def main():
    out=BASE/'entrance201-verification'
    if out.exists():raise ValueError('Preserve earlier verification')
    out.mkdir();rows=[]
    for stage,verify,start,count in [('opening06','openverify10',217,144),('route08','routeverify11',361,192)]:
        folder=BASE/('entrance201-'+stage);control=BASE/('entrance201-'+verify)
        r=json.loads((folder/'result.json').read_text());v=json.loads((control/'result.json').read_text())
        if r['source_sha256']!=v['source_sha256'] or r['fingerprint']!=v['fingerprint'] or r['cache_hashes']!=v['cache_hashes']:raise ValueError('Reopened structure/source/cache changed')
        if [x['frame'] for x in r['frames']]!=list(range(start,start+count)):raise ValueError('Missing output frames')
        for name in ('cache-parity.json','pose-parity.json'):
            if json.loads((control/name).read_text())['status']!='PASS':raise ValueError('Evaluated reopen failed')
        for row in r['frames']:
            if sha(folder/f"frame-{row['frame']:04d}.png")!=row['sha256']:raise ValueError('Source image changed')
        for row in v['frames']:
            f=row['frame'];first=folder/f'frame-{f:04d}.png';second=control/first.name
            try:pixel=pixel_parity(first,second)
            except ValueError as exc:
                (out/'failure.json').write_text(json.dumps({'stage':stage,'frame':f,'error':str(exc),'first_sha256':sha(first),'second_sha256':sha(second)},indent=2)+'\n')
                raise
            rows.append({'stage':stage,'frame':f,**pixel})
    (out/'result.json').write_text(json.dumps({'status':'PASS','reopen_pixels':rows,'limits':'Strict one8-bit-level pixel comparison plus source/structure/cache/pose checks. No inherited200 exception. Does not grant visual or Director approval.'},indent=2)+'\n')

if __name__=='__main__':main()
