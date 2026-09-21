"""Fixed local preview encoding and frame-by-frame review contact sheets."""
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01/face-surface-motion-02'
OUT=BASE/'review'
if OUT.exists():raise ValueError('Review already exists')
record=json.loads((BASE/'result.json').read_text())
if record.get('rendering')!='COMPLETE' or record.get('frames_per_view')!=120:raise ValueError('Incomplete sequence')
for view in ('front','oblique'):
    paths=sorted((BASE/view).glob('*.png'))
    if [p.name for p in paths]!=[f'{i:04}.png' for i in range(120)]:raise ValueError('Frame gap/extra')
OUT.mkdir()
subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-n','-framerate','12','-i',str(BASE/'front/%04d.png'),
                '-framerate','12','-i',str(BASE/'oblique/%04d.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]',
                '-map','[v]','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'acting-front-oblique.mp4')],check=True)
frames={view:[Image.open(BASE/view/f'{i:04}.png').convert('RGB') for i in range(120)] for view in ('front','oblique')}
stats={}
for view,images in frames.items():
    arrays=[np.asarray(im,dtype=float) for im in images]
    stats[view]={'first_last_max_8bit_delta':float(np.abs(arrays[0]-arrays[-1]).max()),
                 'frame_to_frame_mean_8bit_delta':[float(np.abs(b-a).mean()) for a,b in zip(arrays,arrays[1:])]}
for page in range(6):
    sheet=Image.new('RGB',(1280,1100),(32,32,32));draw=ImageDraw.Draw(sheet)
    for cell,index in enumerate(range(page*20,(page+1)*20)):
        x=(cell%4)*320;y=(cell//4)*220
        draw.text((x+4,y+2),f'{index/12:0.3f}s / native frame {index*2+1}',fill='white')
        for j,view in enumerate(('front','oblique')):sheet.paste(frames[view][index].resize((160,200)),(x+160*j,y+18))
    sheet.save(OUT/f'contact-{page+1:02}.jpg',quality=92)
files=[p for p in OUT.iterdir() if p.is_file()]
manifest={'source_native_sha256':record['native_sha256'],'source_render_count':240,'duration_seconds':10,
          'preview_fps':12,'stats':stats,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          'director_accepted':False,'engineering_token_usage':None,'paid_api_calls':0}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
