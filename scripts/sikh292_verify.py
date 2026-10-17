"""Offline delivery verification; no substitute for visual/audio judgment."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh292'
RESULT=ROOT/'results/sikh292'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    movie=BASE/'movie-01';edit=BASE/'edit-01';reopen=BASE/'reopen-01'
    frames=sorted((movie/'frames').glob('frame-*.png'));assert len(frames)==528
    packet=json.loads((RESULT/'movie-1/task.json').read_text())
    for p,digest in packet['inputs'].items():assert sha(ROOT/p)==digest,p
    source=json.loads((movie/'source/bindings.json').read_text())
    for p,digest in source.items():
        if Path(p).suffix=='.py':assert sha(movie/'source'/p)==digest,p
    diffs=[]
    for f in (1,99,150,245,315,445):
        a=np.asarray(Image.open(movie/f'frames/frame-{f:04d}.png')).astype(int)
        b=np.asarray(Image.open(reopen/f'frame-{f:04d}.png')).astype(int)
        diffs.append({'frame':f,'maximum_channel_difference':int(abs(a-b).max()),'mean_channel_difference':float(abs(a-b).mean())})
    trace=json.loads((reopen/'contact-trace.json').read_text())
    assert max(abs(r['front_ground_gap']) for r in trace)<1e-5
    assert max(abs(r['rear_ground_gap']) for r in trace)<1e-5
    strike=[r for r in trace if 15.5<=r['source_t']<=17.0]
    assert max(abs(r['spear_actual_ground_gap']) for r in strike)<1e-5
    assert max(r['rein_length'] for r in trace)<2.0
    pause=[r for r in trace if 8<=r['source_t']<=12]
    assert min(r['crowd_longitudinal_clearance'] for r in pause)>12
    probes={}
    for name in ('pashtun-sikh-42s.mp4','sikh-22s.mp4'):
        p=edit/name
        probes[name]=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,nb_frames,sample_rate','-of','json',str(p)]))
    assert abs(float(probes['pashtun-sikh-42s.mp4']['format']['duration'])-42)<.05
    assert abs(float(probes['sikh-22s.mp4']['format']['duration'])-22)<.05
    rate,mix=wavfile.read(edit/'joined-mix.wav');assert rate==48000 and len(mix)==42*rate
    assert np.isfinite(mix).all() and np.abs(mix).max()<1
    pashtun=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
    assert sha(pashtun)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    comparison=subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','info','-i',str(pashtun),'-i',str(edit/'pashtun-sikh-42s.mp4'),
        '-filter_complex','[1:v]trim=end_frame=480,setpts=PTS-STARTPTS[b];[0:v][b]ssim=shortest=1[out]',
        '-map','[out]','-an','-f','null','-'],capture_output=True,text=True,check=True)
    ssim=[x for x in comparison.stderr.splitlines() if 'SSIM Y:' in x]
    if len(ssim)!=1:raise ValueError('Missing picture comparison')
    receipts=[{'job':p.parent.name,**json.loads(p.read_text())} for p in RESULT.glob('*/receipt.json')]
    evidence={'sampled_reopen_pixels':diffs,'front_rear_ground_max_m':max(abs(r[k]) for r in trace for k in ('front_ground_gap','rear_ground_gap')),
        'spear_bank_max_m':max(abs(r['spear_actual_ground_gap']) for r in strike),'minimum_stopped_crowd_clearance_m':min(r['crowd_longitudinal_clearance'] for r in pause),
        'rein_length_range_m':[min(r['rein_length'] for r in trace),max(r['rein_length'] for r in trace)],
        'movie_source_snapshot_verified':True,'pashtun_source_hash_unchanged':True,'pashtun_editorial_reencode_ssim':ssim[0],
        'native_receipts':receipts,'native_process_seconds':sum(r['process_seconds'] for r in receipts),
        'native_time_definition':'Worker setup, save and rendering occupancy; not total net effort or pure render wait.',
        'engineering_tokens':None,'direct_listening':'NOT_RUN','realtime_perceptual_playback':'NOT_RUN','provider_calls':0,'new_cloud_jobs':0,'new_media_off_device_backup':False,'encoded_streams':probes,
        'delivery_hashes':{p.name:sha(p) for p in edit.glob('*.mp4')}}
    (RESULT/'verification.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
