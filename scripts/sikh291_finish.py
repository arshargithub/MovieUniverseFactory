"""Package the fixed 291 staging output; no automated artistic acceptance."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOVIE=ROOT/'.runtime/art-direction/series01-sikh291/movie-03'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    frames=sorted((MOVIE/'frames').glob('frame-*.png'))
    if [p.name for p in frames]!=[f'frame-{i:04d}.png' for i in range(1,529)]:raise ValueError('Incomplete frames')
    output=MOVIE/'sikh-staging-22s.mp4'
    if output.exists():raise ValueError('Preserve prior delivery')
    header=f"drawbox=x=0:y=0:w=iw:h=42:color=black@0.60:t=fill,drawtext=fontfile={FONT}:text='STAGING ONLY - ACTOR / CLOTH PROXIES':fontsize=17:fontcolor=white:x=(w-tw)/2:y=14"
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(MOVIE/'frames/frame-%04d.png'),'-vf',header,'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]))
    (MOVIE/'media-probe.json').write_text(json.dumps(probe,indent=2))
    vf=f"scale=120:214,drawtext=fontfile={FONT}:text='%{{n}}':fontsize=11:fontcolor=white:box=1:boxcolor=black@0.7:x=3:y=3,tile=8x8"
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(MOVIE/'frames/frame-%04d.png'),'-vf',vf,'-fps_mode','vfr',str(MOVIE/'chronology-%02d.png')],check=True)
    files=[MOVIE/n for n in ('sequence.blend','sikh-staging-22s.mp4','media-probe.json','bike-adaptation.json','horse-control.json')]+frames
    manifest={'scope':'22s silent corrected staging; no final actor, cloth, look or release admission','production_accepted':False,'remote_backed_up':False,'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files]}
    (ROOT/'results/sikh291/media-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(output)
if __name__=='__main__':main()
