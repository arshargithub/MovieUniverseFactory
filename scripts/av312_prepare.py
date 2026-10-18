"""Local bounded review fixtures, never uploads or changes production masters."""
import json
from pathlib import Path
import subprocess
from movie_factory import production_knowledge as pk
from movie_factory import review_control as rc

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/av312'
OUT = ROOT / '.runtime/av312/controls'


def main():
    capsule = rc.capsule(ROOT)
    task = {'id': 'av312-channel-qualification', 'operation': 'knowledge',
            'entities': ['knowledge'], 'query': 'review evidence modalities capability calibration authority',
            'intent': 'Qualify existing local media review path; no production or external model authority.',
            'phase': 'execution', 'open_decisions': [],
            'inputs': {p: pk.file_hash(ROOT / p) for p in ['results/av312/STRATEGY.md', 'docs/knowledge/review_control/README.md']},
            'execution_authority': {'source': 'results/av312/STRATEGY.md', 'scope': 'Director312 local capability probe and fixture preparation'},
            'max_context_characters': 48000}
    packet = pk.task_packet(ROOT, task)
    if not packet['dispatch_ready']:
        raise RuntimeError('Knowledge packet blocked')
    for name, data in [('task.json', task), ('knowledge-packet.json', packet)]:
        with (BASE / name).open('x') as f:
            json.dump(data, f, indent=2); f.write('\n')
    OUT.mkdir(parents=True, exist_ok=False)
    ref = ROOT / capsule['references']['rear_reference']['path']
    sikh = ROOT / capsule['artifacts']['sikh']['path']
    pashtun = ROOT / capsule['references']['pashtun']['path']
    configs = [('C01', ref, 15.5, 3.5, None), ('C02', sikh, 11.5, 3.5, None),
               ('C03', pashtun, 11, 4, None),
               ('C04', OUT / 'C03.mp4', 0, 4, 'slow'),
               ('C05', OUT / 'C03.mp4', 0, 4, 'delay'),
               ('C06', OUT / 'C03.mp4', 0, 4, 'mute'),
               ('C07', sikh, 5, 3, None), ('C08', sikh, 24, 5, None)]
    rows = []
    for label, source, start, duration, transform in configs:
        dest = OUT / (label + '.mp4')
        cmd = ['/opt/homebrew/bin/ffmpeg', '-v', 'error', '-nostdin', '-n', '-ss', str(start), '-t', str(duration), '-i', str(source)]
        vf = 'scale=540:-2'
        if transform == 'slow':
            vf += ',setpts=1.5*PTS'
            cmd += ['-af', 'atempo=0.6666666667']
        elif transform == 'delay':
            cmd += ['-af', 'adelay=450:all=1,atrim=duration=4']
        elif transform == 'mute':
            cmd += ['-af', 'volume=0']
        cmd += ['-vf', vf, '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-map_metadata', '-1',
                '-movflags', '+faststart', str(dest)]
        subprocess.run(cmd, check=True)
        probe = json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe', '-v', 'error',
            '-show_entries', 'format=duration,size:stream=codec_type,r_frame_rate,sample_rate,channels', '-of', 'json', str(dest)]))
        subprocess.run(['/opt/homebrew/bin/ffmpeg', '-v', 'error', '-nostdin', '-i', str(dest), '-f', 'null', '-'], check=True)
        rows.append({'id': label, 'path': str(dest.relative_to(ROOT)), 'sha256': pk.file_hash(dest),
                     'source': str(source.relative_to(ROOT)), 'source_sha256': pk.file_hash(source),
                     'start': start, 'source_duration': duration, 'transform': transform, 'probe': probe})
    assert rc.capsule(ROOT)['fingerprint'] == capsule['fingerprint']
    data = {'status': 'LOCAL_ONLY_NOT_SENT', 'controls': rows,
            'total_bytes': sum(int(r['probe']['format']['size']) for r in rows),
            'production_fingerprint_unchanged': capsule['fingerprint'],
            'limits': 'Decode and transform provenance only. Not personally heard or viewed as continuous video. Synthetic modifications are known controls, not independent natural defects.'}
    with (BASE / 'controls.json').open('x') as f:
        json.dump(data, f, indent=2); f.write('\n')
    print(json.dumps({'count': len(rows), 'bytes': data['total_bytes'], 'protected_unchanged': True}))


if __name__ == '__main__':
    main()
