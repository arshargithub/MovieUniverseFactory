"""Read-only local delivery checks. No provider, Blender, or cloud execution."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
from scipy.io import wavfile
from movie_factory import sikh304_motion as motion

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-sikh304'
EXPECTED = '1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text())

def main():
    frames = read(BASE / 'movie-08/frame-provenance.json')
    binding = read(BASE / 'movie-08/source/bindings.json')
    drift = [p for p, h in binding.items() if sha(ROOT / p) != h]
    if drift:
        raise ValueError('Bound inputs drifted: ' + repr(drift))
    for row in frames['frames']:
        path = BASE / f"movie-08/frames/frame-{row['frame']:04d}.png"
        assert row['size'] == [720, 1280] and sha(path) == row['sha256']
    assert len(frames['frames']) == 528
    assert sha(ROOT / frames['native']) == frames['native_sha256']
    protected = ROOT / '.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
    assert sha(protected) == EXPECTED
    audio = read(BASE / 'audio-01/audio-manifest.json')
    for name, h in audio['files'].items():
        assert sha(BASE / 'audio-01' / name) == h
    rate, joined = wavfile.read(BASE / 'audio-01/joined-mix.wav')
    original_rate, original = wavfile.read(ROOT / '.runtime/art-direction/series01-finish248/audio02/unfaded-trailer-join.wav')
    assert rate == original_rate == 48000
    assert np.array_equal(joined[:20 * rate], original)
    trace = read(BASE / 'build-08/coordinated-motion.json')
    clearance = read(BASE / 'build-08/camera-bank-clearance.json')
    assert not clearance['occlusions']
    contact = {name: max(abs(r[name + '_gap']) for r in trace) for name in ('front', 'rear')}
    assert max(contact.values()) < .003
    support = [r['support_boot_gap'] for r in trace if r['support_hold'] == 1]
    assert support and max(abs(x) for x in support) < .003
    dt = .001
    accel = [-(motion.travel(t+dt)-2*motion.travel(t)+motion.travel(t-dt))/dt**2*motion.RATE**2
             for t in np.linspace(21.41, 25.99, 460)]
    assert min(accel) >= -.01 and max(accel) < 3.65
    braking = [-(motion.travel(t+dt)-2*motion.travel(t)+motion.travel(t-dt))/dt**2*motion.RATE**2
               for t in np.linspace(3.601, 7.499, 3900)]
    assert min(braking) > -7.4 and max(braking) < .01
    media = []
    for name, seconds in [('sikh-22s.mp4', 22), ('pashtun-sikh-42s.mp4', 42)]:
        path = BASE / 'edit-01' / name
        meta = json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
        assert abs(float(meta['format']['duration']) - seconds) < .05
        video = next(s for s in meta['streams'] if s['codec_type'] == 'video')
        sound = next(s for s in meta['streams'] if s['codec_type'] == 'audio')
        assert video['codec_name'] == 'h264' and video['pix_fmt'] == 'yuv420p'
        assert sound['codec_name'] == 'aac'
        subprocess.run(['/opt/homebrew/bin/ffmpeg', '-v', 'error', '-xerror', '-i', str(path), '-f', 'null', '-'], check=True)
        media.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'duration': float(meta['format']['duration']),
                      'width': video['width'], 'height': video['height'], 'decode': 'PASS'})
    record = {'status': 'TECHNICAL_DELIVERY_CHECKS_PASS', 'source_drift': drift, 'frame_count': 528,
              'source_size': [720, 1280], 'protected_pashtun_sha256': EXPECTED,
              'pashtun_join_pcm_exact': True, 'tire_contact_max_gap_m': contact,
              'support_boot_gap_m': [min(support), max(support)], 'bank_subject_ray_occlusions': 0,
              'launch_acceleration_m_s2': [min(accel), max(accel)], 'media': media,
              'braking_acceleration_m_s2': [min(braking), max(braking)],
              'reopen': read(BASE / 'reopen-08/repeat-comparison.json'),
              'limits': ['Not vehicle dynamics, visual acceptance, real-time perception or audio listening.',
                         'Joined picture is an editorial re-encode; accepted source bytes remain unchanged.',
                         'No new cloud backup or production-character admission.']}
    (ROOT / 'results/sikh304/verification.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))

if __name__ == '__main__':
    main()
