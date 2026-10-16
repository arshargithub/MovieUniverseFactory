"""Package fixed local blink evidence; no perceptual pass inferred from files."""
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-sikh281/control-04'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    frames=[OUT/'motion'/f'{f:04d}.png' for f in range(1,37)]
    if not all(p.exists() for p in frames):raise ValueError('Complete sequence required')
    video=OUT/'single-eye-proof.mp4'
    if video.exists():raise ValueError('Preserve previous video')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(OUT/'motion/%04d.png'),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    for name,ids in [('all-frames',list(range(1,37))),('transition',list(range(12,23)))]:
        width=240; height=264;cols=6 if name=='all-frames' else 4
        sheet=Image.new('RGB',(width*cols,height*((len(ids)+cols-1)//cols)),(235,235,235));draw=ImageDraw.Draw(sheet)
        for k,f in enumerate(ids):
            im=Image.open(frames[f-1]).convert('RGB');im.thumbnail((width,240));x=k%cols*width;y=k//cols*height
            sheet.paste(im,(x,y));draw.text((x+8,y+243),f'Frame {f}',fill=(20,20,20))
        sheet.save(OUT/(name+'.jpg'),quality=93)
    info=dict(video_sha256=sha(video),frames=36,fps=24,duration_seconds=1.5,decode_passed=True,
        frame_hashes={p.name:sha(p) for p in frames},claim='Single-eye component proof, not approved hero or full performance')
    (ROOT/'results/sikh281/media.json').write_text(json.dumps(info,indent=2))
    print(video)

if __name__=='__main__':main()
