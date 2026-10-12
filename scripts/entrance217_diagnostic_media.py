"""Review-only encoding of acknowledged Workbench frames; never final delivery."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from entrance193_media import sha, pixel_parity

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
OUT = ROOT / '.runtime/art-direction/series01-entrance217/motion-diagnostic'


def collect():
    records = {}
    complete = True
    for operation, source, expected in (
        ('diagnostic38', 'opening24', range(144)),
        ('diagnostic39', 'route25', range(144, 432)),
    ):
        folder = BASE / ('entrance214-' + operation)
        result = folder / 'result.json'
        if not result.exists():
            complete = False
            result = folder / 'progress.json'
        if not result.exists():
            continue
        data = json.loads(result.read_text())
        native = BASE / ('entrance217-' + source)
        bound = json.loads((native / 'result.json').read_text())
        if data['source_sha256'] != bound['native_sha256'] or sha(native / 'scene.blend') != bound['native_sha256']:
            raise ValueError('Native source mismatch')
        if data.get('complete') and (data.get('renderer') != 'WORKBENCH_MOTION_ONLY' or data['fps'] != 24 or data['resolution'] != [432, 768]):
            raise ValueError('Unexpected diagnostic renderer or clock')
        for row in data['frames']:
            i = row['index']
            if i not in expected or i in records or row['native_frame'] != i + 217:
                raise ValueError('Invalid chronology')
            paths = {k: folder / f'{k}-{i:04d}.png' for k in ('frame', 'L', 'R')}
            hashes = {'frame': row['sha256'], **row['contacts']}
            if any(not p.is_file() or sha(p) != hashes[k] for k, p in paths.items()):
                raise ValueError('Changed or unacknowledged diagnostic frame')
            if max(row[k] for k in ('protected_pose_error', 'camera_error', 'thumb_error', 'rein_error')) > 2e-5:
                raise ValueError('Motion preservation failure')
            records[i] = (row, paths)
    return records, complete


def layouts(records):
    OUT.mkdir(parents=True, exist_ok=True)
    for start in range(0, 432, 24):
        ids = list(range(start, start + 24))
        if not all(i in records for i in ids):
            continue
        for kind in ('frame', 'L', 'R'):
            target = OUT / f'{kind}-sheet-{start:04d}.jpg'
            if target.exists():
                continue
            size = (160, 284) if kind == 'frame' else (240, 240)
            canvas = Image.new('RGB', (size[0]*6, (size[1]+22)*4), '#eeeeee')
            draw = ImageDraw.Draw(canvas)
            for n, i in enumerate(ids):
                with Image.open(records[i][1][kind]) as im:
                    tile = ImageOps.contain(im.convert('RGB'), size)
                x, y = (n % 6)*size[0], (n // 6)*(size[1]+22)
                canvas.paste(tile, (x, y))
                draw.text((x+4, y+size[1]+3), f'{kind} f{i+217} {i/24:.2f}s', fill='black')
            canvas.save(target, quality=93)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--encode', action='store_true')
    args = parser.parse_args()
    records, complete = collect()
    layouts(records)
    print('Acknowledged diagnostic frames:', len(records), 'complete:', complete)
    if not args.encode:
        return
    if not complete or set(records) != set(range(432)):
        raise ValueError('Incomplete diagnostic chronology')
    parity = []
    for source, proof, frames in (
        ('opening24', 'proof26', (277,330,360)),
        ('route25', 'proof27', (390,427,472,550,620)),
    ):
        native = BASE / ('entrance217-' + source)
        reopened = BASE / ('entrance214-' + proof)
        result = json.loads((reopened / 'result.json').read_text())
        if not result['complete'] or result['source_sha256'] != sha(native/'scene.blend'):
            raise ValueError('Reopen evidence mismatch')
        for f in frames:
            parity.append({'frame': f, **pixel_parity(native/f'actual-{f}.png', reopened/f'frame-{f-217:04d}.png')})
    outputs = []
    for kind in ('frame', 'L', 'R'):
        target = OUT / kind
        if target.exists():
            raise ValueError('Preserve previous diagnostic encoding')
        target.mkdir()
        for i in range(432):
            os.link(records[i][1][kind], target / f'frame-{i:04d}.png')
        video = OUT / f'{kind}-motion-only.mp4'
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24',
            '-i',str(target/'frame-%04d.png'),'-frames:v','432','-c:v','libx264','-crf','18',
            '-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],check=True)
        probe = json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
        s = probe['streams'][0]
        if len(probe['streams']) != 1 or s['codec_name'] != 'h264' or s['pix_fmt'] != 'yuv420p' or s['nb_frames'] != '432' or s['avg_frame_rate'] != '24/1' or abs(float(probe['format']['duration'])-18) > .001:
            raise ValueError('Invalid diagnostic encoding')
        outputs.append({'kind':kind,'path':str(video.relative_to(ROOT)),'sha256':sha(video)})
    (OUT/'technical-review.json').write_text(json.dumps({
        'status':'PASS','scope':'432-frame motion diagnostic plus independent Cycles still parity; NOT a final Cycles clip',
        'frames':[records[i][0] for i in range(432)],'reopen':parity,'videos':outputs,
        'visual_gate':'NOT_RUN','fps':24,'duration':18},indent=2)+'\n')


if __name__ == '__main__':
    main()
