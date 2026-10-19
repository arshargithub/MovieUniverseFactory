"""Local318 sound synchronization, protected join and strict replay comparison."""
import sys,json
from pathlib import Path
import numpy as np
from PIL import Image
import edit317 as previous
import sikh315_delivery as delivery
from movie_factory import sikh318_motion as motion
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh318'

def main():
    op,v=sys.argv[1],int(sys.argv[2])
    assert op in ('audio','edit','controls','reopencheck','rearproof') and 1<=v<=4
    if op=='audio':
        previous.BASE=BASE;previous.m=motion;previous.audio(v,neigh_source_time=15.61);return
    delivery.BASE=BASE;delivery.source_for=lambda *args:BASE/f'build-{v:02d}/sequence.blend'
    out=BASE/f'delivery-{v:02d}'
    if op=='rearproof':
        dest=BASE/f'rearproof-{v:02d}';dest.mkdir(exist_ok=False)
        delivery.run('-framerate','24','-start_number','275','-i',str(BASE/f'movie-{v:02d}/frames/frame-%04d.png'),'-frames:v','84','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(dest/'rear.mp4'))
        from shutil import copy2
        frames=dest/'frames';frames.mkdir()
        for f in range(275,359):copy2(BASE/f'movie-{v:02d}/frames'/f'frame-{f:04d}.png',frames)
        delivery.sheets(frames,dest/'chronology',columns=6,rows=4,width=240);return
    if op=='controls':
        dest=out/'encoded-controls';dest.mkdir(exist_ok=False)
        for f in (1,80,126,150,283,294,306,315,324,333,342,350,375,390,402,415,420,430,435,450,465,480,500,600,680,696):
            delivery.run('-i',str(out/'sikh-29s.mp4'),'-vf',f'select=eq(n\\,{f-1})','-frames:v','1',str(dest/f'frame-{f:04d}.png'))
        delivery.sheets(dest,out/'encoded-review',columns=4,rows=2,width=260);return
    if op=='reopencheck':
        rows=[]
        for p in sorted((BASE/f'reopen-{v:02d}/frames').glob('frame-*.png')):
            q=BASE/f'movie-{v:02d}/frames'/p.name
            a=np.asarray(Image.open(q)).astype(np.int16);b=np.asarray(Image.open(p)).astype(np.int16)
            assert a.shape==b.shape
            rows.append({'frame':p.name,'maximum_channel_difference':int(np.max(abs(a-b))),'different_channels':int(np.count_nonzero(a-b)),'original_sha':delivery.sha(q),'reopen_sha':delivery.sha(p)})
        assert len(rows)==8
        p=ROOT/f'results/sikh318/reopen-{v}/comparison.json'
        p.write_text(json.dumps({'threshold':1,'status':'PASS' if all(r['maximum_channel_difference']<=1 for r in rows) else 'FAIL','controls':rows},indent=2));return
    delivery.main()
if __name__=='__main__':main()
