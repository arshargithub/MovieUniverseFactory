"""Preserve the developed sketch; package an explicitly chosen excerpt without retiming."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from package_music231 import run, meter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-music233'
SOURCE=ROOT/'.runtime/art-direction/series01-audio223/provider/music233-sketch-1.wav'
VIDEO=ROOT/'.runtime/art-direction/series01-entrance209/director-preview/pashtun-complete-entrance.mp4'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def duration(p):
    return float(json.loads(run(['ffprobe','-v','error','-show_format','-of','json',str(p)]).stdout)['format']['duration'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['sketch','excerpt']);ap.add_argument('--start',type=float);a=ap.parse_args()
    if a.phase=='sketch':
        d=duration(SOURCE)
        if not 30<=d<=120:raise ValueError('Insufficient development length or provider limit exceeded; reassess, do not loop.')
        m=meter(SOURCE)
        af=(f"loudnorm=I=-18:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        wav=OUT/'sketch.wav';mp3=OUT/'sketch.mp3'
        run(['ffmpeg','-n','-v','error','-i',str(SOURCE),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(wav)])
        run(['ffmpeg','-n','-v','error','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(mp3)])
        result={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':sha(SOURCE),'duration':d,'source_loudness':m,'normalized_loudness':meter(wav),'outputs':{p.name:sha(p) for p in [wav,mp3]}}
    else:
        source=OUT/'sketch.wav';d=duration(source);start=a.start
        if start is None or not math.isfinite(start) or start<0 or start+18>d:raise ValueError('Explicit valid18s source interval required')
        wav=OUT/'excerpt.wav';video=OUT/'entrance-music-sketch.mp4'
        # Tiny boundary fades remove clicks only. No internal rhythmic edits or time stretching.
        run(['ffmpeg','-n','-v','error','-i',str(source),'-af',f'atrim=start={start}:duration=18,asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st=17.96:d=0.04','-c:a','pcm_s24le',str(wav)])
        run(['ffmpeg','-n','-v','error','-i',str(VIDEO),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(video)])
        run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'])
        def vh(p):return run(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
        assert vh(video)==vh(VIDEO)
        assert abs(duration(wav)-18)<.02
        result={'source_interval':[start,start+18],'picture_unchanged':True,'duration':duration(video),'excerpt_loudness':meter(wav),'outputs':{p.name:sha(p) for p in [wav,video]},'disclosure':'Music-only audition, protected209 picture with older grip; no final voice, hooves or mix. Excerpt boundary is not a proposed trailer ending.'}
    with (OUT/f'packaging-{a.phase}.json').open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
