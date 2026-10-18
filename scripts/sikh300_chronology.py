"""Immutable chronological contact sheets from completed frame ranges."""
import subprocess,sys,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh300'
def main():
    chunk=int(sys.argv[1])
    if not 1<=chunk<=9:raise ValueError('Chunk1–9 only')
    start=1+(chunk-1)*64;end=min(528,start+63);frames=BASE/'movie-01/frames';out=BASE/'movie-01/review'
    if len(sys.argv)>2:
        if sys.argv[2]!='repaired':raise ValueError('Only repaired alternative admitted')
        out=BASE/'repair-review';frames=out/'frames';frames.mkdir(parents=True,exist_ok=True)
        for f in range(start,end+1):
            source=(BASE/'movie-01/frames' if 276<=f<=355 else BASE/'ground-rerender-01')/f'frame-{f:04d}.png'
            if not source.is_file():raise ValueError('Requested repaired range not rendered')
            target=frames/source.name
            if not target.exists():shutil.copy2(source,target)
    if any(not (frames/f'frame-{f:04d}.png').is_file() for f in range(start,end+1)):raise ValueError('Requested range not rendered')
    out.mkdir(exist_ok=True);dest=out/f'frames-{start:03d}-{end:03d}.png'
    if dest.exists():print(dest);return
    filt=f"scale=144:256,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='%{{eif\\:n+{start}\\:d}}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.6:x=3:y=3,tile=8x8"
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-start_number',str(start),'-i',str(frames/'frame-%04d.png'),'-vf',filt,'-frames:v','1',str(dest)],check=True);print(dest)
if __name__=='__main__':main()
