"""Decode and inspect exact offline edit boundaries; no automatic visual pass."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-trailer-edit189'


def main():
    from entrance189_media import sheet
    manifest=json.loads((OUT/'manifest.json').read_text())
    qa=OUT/'qa'
    if qa.exists():raise ValueError('Preserve previous edit review')
    qa.mkdir();checks=[]
    for kind in ('entrance','trailer'):
        record=manifest[kind];video=OUT/record['path']
        with video.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
        if sha!=record['sha256']:raise ValueError('Edit changed')
        probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error',
            '-show_streams','-show_format','-of','json',str(video)]))
        streams=probe['streams']
        if len(streams)!=1 or streams[0]['codec_type']!='video':raise ValueError('Unexpected streams')
        stream=streams[0]
        if int(stream['nb_frames'])!=record['frames'] or stream['avg_frame_rate']!='24/1':
            raise ValueError('Frame/rate mismatch')
        if abs(float(probe['format']['duration'])-record['duration_seconds'])>.001:
            raise ValueError('Duration mismatch')
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],check=True)
        frames=sorted({n for row in record['timeline'] for n in
            (row['start_frame'],(row['start_frame']+row['end_frame_exclusive']-1)//2,row['end_frame_exclusive']-1)})
        paths=[]
        for f in frames:
            target=qa/(kind+'-%04d.png'%f)
            subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-ss',str(f/24),
                '-i',str(video),'-frames:v','1',str(target)],check=True)
            paths.append(target)
        for i in range(0,len(paths),12):sheet(paths[i:i+12],qa/(kind+'-sheet-%02d.png'%(i//12)))
        checks.append({'kind':kind,'sha256':sha,'frames':record['frames'],'duration_seconds':record['duration_seconds'],
            'width':stream['width'],'height':stream['height'],'full_decode':'PASS','sampled_frames':frames})
    (qa/'technical-review.json').write_text(json.dumps({'checks':checks,'visual_review':'NOT_RUN',
        'limits':'Timing/caption assembly review only; unfinished boards/cards remain explicitly unfinished'},indent=2)+'\n')


if __name__=='__main__':main()
