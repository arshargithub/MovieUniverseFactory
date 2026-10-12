"""Local level-matched music-only auditions; picture stream copied unchanged."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.runtime/art-direction/series01-music231'
PROVIDER = ROOT / '.runtime/art-direction/series01-audio223/provider'
VIDEO = ROOT / '.runtime/art-direction/series01-entrance209/director-preview/pashtun-complete-entrance.mp4'


def run(args):
    return subprocess.run(args, check=True, text=True, capture_output=True)


def meter(path):
    r=run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-18:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
    return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}',r.stderr,re.S)[-1])


def main():
    evidence=[]
    for name in ('harmonica','synth'):
        source=PROVIDER/f'music231-{name}-1.wav'
        wav=OUT/f'audition-{name}.wav'
        mp3=OUT/f'audition-{name}.mp3'
        video=OUT/f'audition-{name}.mp4'
        probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]).stdout)
        if abs(float(probe['format']['duration'])-18)>0.1:
            raise ValueError('Music needs deliberate duration edit; do not silently stretch/truncate')
        m=meter(source)
        af=(f"loudnorm=I=-18:TP=-1.5:LRA=11:measured_I={m['input_i']}:"
            f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json")
        run(['ffmpeg','-n','-hide_banner','-i',str(source),'-af',af,'-ar','48000','-c:a','pcm_s24le',str(wav)])
        run(['ffmpeg','-n','-hide_banner','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(mp3)])
        run(['ffmpeg','-n','-hide_banner','-i',str(VIDEO),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(video)])
        run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'])
        def vhash(p):
            return run(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-c','copy','-f','hash','-hash','sha256','-']).stdout.strip()
        assert vhash(VIDEO)==vhash(video)
        evidence.append({'name':name,'source':str(source.relative_to(ROOT)),'duration':probe['format']['duration'],
                         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                         'source_loudness':m,'normalized_loudness':meter(wav),'mp3_loudness':meter(mp3),
                         'video_packets_identical':True,'outputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [wav,mp3,video]}})
    (OUT/'packaging.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))


if __name__=='__main__':main()
