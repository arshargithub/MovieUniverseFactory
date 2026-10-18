"""Offline299 integrity checks; never substitutes for visual or audio judgment."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh299';RESULT=ROOT/'results/sikh299'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    movie=BASE/'movie-02';edit=BASE/'edit-01';reopen=BASE/'reopen-01'
    frames=sorted((movie/'frames').glob('frame-*.png'))
    assert [p.name for p in frames]==[f'frame-{i:04d}.png' for i in range(1,529)]
    task=json.loads((RESULT/'movie-2/task.json').read_text())
    for p,d in task['inputs'].items():assert sha(ROOT/p)==d,p
    source=json.loads((movie/'source/bindings.json').read_text())
    for p,d in source.items():
        if Path(p).suffix=='.py':assert sha(movie/'source'/p)==d,p
    diffs=[]
    for f in (1,120,148,215,335,435):
        a=np.asarray(Image.open(movie/f'frames/frame-{f:04d}.png')).astype(int);b=np.asarray(Image.open(reopen/f'frame-{f:04d}.png')).astype(int)
        diffs.append({'frame':f,'maximum_channel_difference':int(abs(a-b).max()),'mean_channel_difference':float(abs(a-b).mean())})
    probes={}
    for name,n in [('pashtun-sikh-42s.mp4',1008),('sikh-22s.mp4',528)]:
        p=edit/name;probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,nb_frames,sample_rate','-of','json',str(p)]))
        assert abs(float(probe['format']['duration'])-n/24)<.05
        assert int(next(s for s in probe['streams'] if s['codec_type']=='video')['nb_frames'])==n
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True);probes[name]=probe
    pashtun=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
    assert sha(pashtun)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    old=ROOT/'.runtime/art-direction/series01-sikh292/edit-01/sikh-music.wav';new=BASE/'audio-01/sikh-music.wav'
    sr,a=wavfile.read(old);srb,b=wavfile.read(new);assert sr==srb and np.array_equal(a,b)
    trace=json.loads((BASE/'controls-05/motion-trace.json').read_text())
    extrema={k:[min(r[k] for r in trace),max(r[k] for r in trace)] for k in ('front_gap','rear_gap','lean_deg','yaw_deg')}
    assert max(abs(v) for k in ('front_gap','rear_gap') for v in extrema[k])<.002
    assert 45<trace[179]['yaw_deg']<60
    gaze=json.loads((BASE/'controls-07/greeting-eyeline.json').read_text())
    hold=[r for r in gaze if r['hold']==1]
    gaze_check={'maximum_full_hold_horizontal_error_deg':max(abs(r['after_error_deg']) for r in hold),'original_full_hold_error_deg':max(abs(r['before_error_deg']) for r in hold),'scope':'Horizontal head aim only; not final face/eye performance'}
    assert gaze_check['maximum_full_hold_horizontal_error_deg']<1
    receipts=[{'job':p.parent.name,**json.loads(p.read_text())} for p in RESULT.glob('*/receipt.json')]
    result={'sampled_reopen_pixels':diffs,'strict_sampled_reopen_pass':all(d['maximum_channel_difference']<=1 for d in diffs),'movie_source_snapshot_verified':True,'pashtun_source_hash_unchanged':True,'pashtun_native_rerendered':False,'music_pcm_bit_exact':True,'contact_trace_extrema':extrema,'contact_numeric_scope':'Measured tire mesh support, not a visual pass; localized stylized occlusion separately reviewed','native_receipts':receipts,'native_process_seconds':sum(r['process_seconds'] for r in receipts),'native_time_definition':'Setup, scene construction, save and render process occupancy; not additive to assistant activity or pure waiting','engineering_tokens':None,'direct_listening':'NOT_RUN','realtime_perceptual_playback':'NOT_RUN','provider_calls':0,'new_cloud_jobs':0,'new_media_off_device_backup':False,'encoded_streams':probes,'delivery_hashes':{p.name:sha(p) for p in edit.glob('*.mp4')}}
    result['greeting_eyeline']=gaze_check
    (RESULT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
