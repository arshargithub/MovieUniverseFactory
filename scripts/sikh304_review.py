"""Local evidence assembly; no scene mutation or external service access."""
import hashlib,json,subprocess,sys
from pathlib import Path
import numpy as np
from PIL import Image
from movie_factory.sikh304_motion import source_name
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh304'
FF='/opt/homebrew/bin/ffmpeg'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run([FF,'-v','error',*args],check=True)
def proof(v):
    out=BASE/f'proof-{v:02d}'
    for name,start,end in [('stop',105,157),('rear',290,355),('launch',430,478)]:
        frames=out/name
        expected=[frames/f'frame-{i:04d}.png' for i in range(start,end+1)]
        if not all(p.exists() for p in expected):continue
        if not (out/f'{name}.mp4').exists():
            run(['-framerate','24','-start_number',str(start),'-i',str(frames/'frame-%04d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out/f'{name}.mp4')])
        if not (out/f'{name}-01.png').exists():
            filt=f"scale=180:320,drawtext=fontfile={FONT}:text='%{{eif\\:n+{start}\\:d}}':fontsize=16:fontcolor=white:box=1:boxcolor=black@0.7:x=4:y=4,tile=5x4"
            run(['-framerate','24','-start_number',str(start),'-i',str(frames/'frame-%04d.png'),'-vf',filt,str(out/f'{name}-%02d.png')])
def seal(v):
    out=BASE/f'movie-{v:02d}';native=BASE/source_name('movie',v)
    frames=[out/f'frames/frame-{f:04d}.png' for f in range(1,529)]
    if not all(p.exists() for p in frames):raise ValueError('Incomplete movie')
    record={'native':str(native.relative_to(ROOT)),'native_sha256':sha(native),'source_bindings_sha256':sha(out/'source/bindings.json'),'fps':24,'frames':[{'frame':f,'sha256':sha(p),'size':list(Image.open(p).size)} for f,p in enumerate(frames,1)]}
    (out/'frame-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
def compare(v):
    out=BASE/f'reopen-{v:02d}';movie=BASE/f'movie-{v:02d}/frames';rows=[]
    for f in (1,130,148,315,450):
        a=np.asarray(Image.open(movie/f'frame-{f:04d}.png').convert('RGB')).astype(int);b=np.asarray(Image.open(out/f'frame-{f:04d}.png').convert('RGB')).astype(int)
        if a.shape!=b.shape:raise ValueError('Unmatched review dimensions')
        d=np.abs(a-b);rows.append({'frame':f,'max_channel_error':int(d.max()),'mean_abs_error':float(d.mean()),'pixels_over_1':int(np.count_nonzero(d.max(axis=2)>1))})
    (out/'repeat-comparison.json').write_text(json.dumps({'scope':'Five fresh-process exact camera controls; not general renderer qualification','rows':rows,'strict_1_pass':all(r['max_channel_error']<=1 for r in rows)},indent=2)+'\n')
if __name__=='__main__':
    op=sys.argv[1];v=int(sys.argv[2])
    if op not in ('proof','seal','compare') or not 1<=v<=12:raise ValueError('Unsupported review operation')
    {'proof':proof,'seal':seal,'compare':compare}[op](v)
