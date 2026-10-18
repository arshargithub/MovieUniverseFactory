"""Offline300 integrity checks; never substitutes for visual or audio judgment."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.io import wavfile
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh300';RESULT=ROOT/'results/sikh300'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    movie=BASE/'movie-01';edit=BASE/'edit-01';reopen=BASE/'ground-reopen-01';final=BASE/'final-01'
    frames=sorted((final/'frames').glob('frame-*.png'))
    assert [p.name for p in frames]==[f'frame-{i:04d}.png' for i in range(1,529)]
    task=json.loads((RESULT/'movie-1/task.json').read_text())
    for p,d in task['inputs'].items():assert sha(ROOT/p)==d,p
    source=json.loads((movie/'source/bindings.json').read_text())
    for p,d in source.items():
        if Path(p).suffix=='.py':assert sha(movie/'source'/p)==d,p
    diffs=[]
    provenance=json.loads((final/'frame-provenance.json').read_text())
    assert sha(ROOT/provenance['selected_native'])==provenance['native_sha256']
    for row in provenance['frames']:
        assert sha(ROOT/row['source'])==row['sha256']==sha(final/f"frames/frame-{row['frame']:04d}.png")
    for f in (1,120,148,215,276,300,335,355,435,470):
        a=np.asarray(Image.open(final/f'frames/frame-{f:04d}.png')).astype(int);b=np.asarray(Image.open(reopen/f'frame-{f:04d}.png')).astype(int)
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
    trace=json.loads((BASE/'controls-06/motion-trace.json').read_text())
    extrema={k:[min(r[k] for r in trace),max(r[k] for r in trace)] for k in ('front_gap','rear_gap','lean_deg','yaw_deg')}
    assert max(abs(v) for k in ('front_gap','rear_gap') for v in extrema[k])<.002
    assert 40<=trace[179]['yaw_deg']<=45
    gaze=json.loads((BASE/'controls-06/greeting-eyeline.json').read_text())
    hold=[r for r in gaze if r['hold']==1]
    gaze_check={'maximum_full_hold_horizontal_error_deg':max(abs(r['after_error_deg']) for r in hold),'original_full_hold_error_deg':max(abs(r['before_error_deg']) for r in hold),'scope':'Horizontal head aim only; not final face/eye performance'}
    assert gaze_check['maximum_full_hold_horizontal_error_deg']<1
    hind=json.loads((BASE/'inspect-04/hind-contact.json').read_text())
    hind_support=json.loads((BASE/'controls-08/hind-support.json').read_text())
    assert max(r['hind_min_z'] for r in hind)-min(r['hind_min_z'] for r in hind)<.0001
    assert 'target_world' in hind_support and len(hind_support['target_world'])==2
    assert '.runtime/art-direction/series01-sikh300/controls-08/sequence.blend' in task['inputs']
    rig_ownership=json.loads((BASE/'reopen-01/rig-ownership.json').read_text());assert rig_ownership['checks_passed']
    receipts=[{'job':p.parent.name,**json.loads(p.read_text())} for p in RESULT.glob('*/receipt.json')]
    result={'sampled_reopen_pixels':diffs,'strict_sampled_reopen_pass':all(d['maximum_channel_difference']<=1 for d in diffs),'movie_source_snapshot_verified':True,'pashtun_source_hash_unchanged':True,'pashtun_native_rerendered':False,'music_pcm_bit_exact':True,'contact_trace_extrema':extrema,'contact_numeric_scope':'Measured tire mesh support, not a visual pass; localized stylized occlusion separately reviewed','native_receipts':receipts,'native_process_seconds':sum(r['process_seconds'] for r in receipts),'native_time_definition':'Setup, scene construction, save and render process occupancy; not additive to assistant activity or pure waiting','engineering_tokens':None,'direct_listening':'NOT_RUN','realtime_perceptual_playback':'NOT_RUN','provider_calls':0,'new_cloud_jobs':0,'new_media_off_device_backup':False,'encoded_streams':probes,'delivery_hashes':{p.name:sha(p) for p in edit.glob('*.mp4')}}
    result['greeting_eyeline']=gaze_check
    result['evaluated_rig_ownership']=rig_ownership
    result['selected_native']={'path':provenance['selected_native'],'sha256':provenance['native_sha256'],'motion_trace_inherited_from':'controls-06','crop_representation_inherited_from':'controls-07','hind_support_inherited_from':'controls-08','hind_support':hind_support,'evaluated_hind_toe_samples':hind,'scope':'Ground-fix preserves all actors/actions/plateau; seven sampled full evaluated-mesh minimum heights, separate matched crops and chronology, not a general rig qualification'}
    result['final_frame_provenance']={'path':'.runtime/art-direction/series01-sikh300/final-01/frame-provenance.json','sha256':sha(final/'frame-provenance.json'),'repaired_frames':448,'retained_leader_frames':80}
    result['ground_repair']=json.loads((BASE/'ground-fix-01/repair.json').read_text())
    (RESULT/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

