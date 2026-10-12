"""Regenerate corrected vector overlay only; inspect actual encoded output."""
import json
import subprocess
from pathlib import Path

from finish242_audition import ROOT, manuscript, sha
from movie_factory import production_knowledge as pk

BASE=ROOT/'.runtime/art-direction/series01-finish242'
SRC=BASE/'audition01'
OUT=BASE/'edit03'


def main():
    task=json.loads((ROOT/'docs/knowledge/pilot/tasks/finish242-audio.json').read_text())
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if OUT.exists():raise ValueError('Preserve prior proof')
    OUT.mkdir()
    (OUT/'packet.json').write_text(json.dumps(packet,indent=2)+'\n')
    (OUT/'packet.md').write_text(pk.packet_markdown(packet))
    (OUT/'manuscript.ass').write_text(manuscript())
    # PNG demuxing otherwise defaults to25fps, which can quantize per-image PTS
    # before the24fps output stage. Bind each still to the intended time base.
    manifest=json.loads((SRC/'manifest.json').read_text())
    entries=['ffconcat version 1.0']
    for index in manifest['source_frame_indices']:
        entries.extend([f"file '{manifest['source_frames'][index]['path']}'",'option framerate 24','duration 0.0416666666667'])
    entries.extend([f"file '{manifest['source_frames'][-1]['path']}'",'option framerate 24'])
    (OUT/'picture.ffconcat').write_text('\n'.join(entries)+'\n')
    movie=OUT/'pashtun-music-first-audition.mp4'
    subprocess.run(['ffmpeg','-v','warning','-safe','0','-f','concat','-i',str(OUT/'picture.ffconcat'),
        '-i',str(SRC/'integrated-mix.wav'),'-vf',f'ass={OUT}/manuscript.ass','-af','volume=2dB',
        '-r','24','-frames:v','540','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-t','22.5',str(movie)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True)
    for second in (0,1.7,4,5.75,6.7,7.4,8.5,9.4,9.75,11.75,15.125,19,22.25):
        subprocess.run(['ffmpeg','-v','error','-ss',str(second),'-i',str(movie),'-frames:v','1',str(OUT/f'qc-{second:g}.png')],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-vf','fps=1,scale=216:384,tile=6x4','-frames:v','1',str(OUT/'chronology.png')],check=True)
    # Entire excerpt levels and high-resolution sample-peak audit, not a listening pass.
    metrics=subprocess.run(['ffmpeg','-hide_banner','-i',str(movie),'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
    (OUT/'loudness.txt').write_text(metrics.stderr)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    (OUT/'probe.json').write_text(json.dumps(probe,indent=2)+'\n')
    result=dict(status='DIAGNOSTIC_AUDITION; NOT_RUN actual listening and native extension',
        corrections='01 paper anchor corrected in02;03 explicitly fixes PNG demuxer time base24fps. +2dB output trim, no limiter. Earlier derivatives retained.',
        inputs={str(p.relative_to(ROOT)):sha(p) for p in [SRC/'picture.ffconcat',SRC/'integrated-mix.wav',SRC/'manifest.json']},
        outputs={p.name:sha(p) for p in OUT.iterdir() if p.is_file()},
        direct_agent_listening=False,paid_calls=0)
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(str(movie))


if __name__=='__main__':main()
