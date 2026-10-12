"""Closed, non-destructive encoded preview and reopen checks for FINISH237."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from finish237_edit import digest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-finish237'

def encoded():
    out = BASE / 'encoded-qc01'
    out.mkdir(exist_ok=False)
    rows = {}
    selected = [0, 72, 114, 119, 124, 136, 160, 187, 194, 196, 197,
                198, 244, 245, 246, 326, 327, 390, 486, 503]
    for name in ('pashtun-21s-music-free', 'pashtun-21s-captioned'):
        p = BASE / 'edit01' / (name + '.mp4')
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
            '-show_streams', '-show_format', '-of', 'json', str(p)]))
        v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        assert (v['codec_name'], v['pix_fmt'], v['width'], v['height'],
                v['r_frame_rate'], int(v['nb_frames'])) == ('h264','yuv420p',432,768,'24/1',504)
        assert abs(float(probe['format']['duration']) - 21) < .02
        assert a['codec_name'] == 'aac' and a['sample_rate'] == '48000'
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        targets = selected if name.endswith('music-free') else [12,72,114,136,170,212]
        dest = out / name; dest.mkdir()
        for i in targets:
            subprocess.run(['ffmpeg','-v','error','-i',str(p),'-vf',f'select=eq(n\\,{i})',
                '-frames:v','1',str(dest/f'frame-{i:04d}.png')],check=True)
        for start in range(0,len(targets),6):
            group=targets[start:start+6]
            canvas=Image.new('RGB',(3*288,2*540),(245,242,230)); draw=ImageDraw.Draw(canvas)
            for j,i in enumerate(group):
                im=Image.open(dest/f'frame-{i:04d}.png').convert('RGB'); im.thumbnail((288,512))
                x=(j%3)*288;y=(j//3)*540;canvas.paste(im,(x,y))
                draw.text((x+6,y+516),f'{i} | {i/24:.3f}s',fill=(20,20,20))
            canvas.save(dest/f'sheet-{start:02d}.jpg',quality=95)
        rows[name]={'sha256':digest(p),'probe':probe,'decode':'PASS','sampled_frames':targets}
    (out/'result.json').write_text(json.dumps(rows,indent=2)+'\n')
    print('Both encoded previews: 504 frames / 21s / H264 AAC; full decode PASS')

def reopened():
    path = BASE/'reopen-parity.json'
    if path.exists(): raise ValueError('Preserve prior verification')
    rows=[]
    for kind in ('opening03','route05'):
        check=BASE/(kind+'-reopen'); source=BASE/(kind+'-full')
        meta=json.loads((check/'result.json').read_text())
        original=json.loads((source/'result.json').read_text())
        assert meta['complete'] and meta['source_sha256']==original['source_sha256']
        for row in meta['frames']:
            p=check/f"frame-{row['index']:04d}.png"; q=source/p.name
            assert digest(p)==row['sha256']
            a=np.asarray(Image.open(p)).astype(float); b=np.asarray(Image.open(q)).astype(float)
            assert a.shape==b.shape
            delta=float(np.max(abs(a-b)))
            rows.append({'kind':kind,'index':row['index'],'maximum_channel_delta':delta,
                         'reopened_sha256':digest(p),'original_sha256':digest(q)})
            assert delta<=1, (kind,row['index'],delta)
    path.write_text(json.dumps({'status':'PASS','tolerance':'1/255','samples':rows},indent=2)+'\n')
    print('Reopen parity PASS:',len(rows),'samples')

if __name__=='__main__':
    if sys.argv[1:]==['encoded']: encoded()
    elif sys.argv[1:]==['reopened']: reopened()
    else: raise ValueError('Choose closed encoded or reopened check')
