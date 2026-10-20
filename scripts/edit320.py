"""Encode only the authorized shot window, using existing music/effect sources."""
import json,sys,subprocess,types
import numpy as np
from pathlib import Path
from PIL import Image
from movie_factory import production_knowledge as pk
from sikh320 import ROOT,BASE,START,END
from sikh305_delivery import sheets
FF='/opt/homebrew/bin/ffmpeg'
RATE=26/22
def retime(t):
    xs=(0,14.28,14.79,15.08,15.42,15.61,15.93,16.14,16.28)
    ys=(0,14.28,14.65,14.84,15.02,15.29,15.70,15.94,16.15)
    if t<=16.28:return float(np.interp(t,xs,ys))
    if t<17.10:
        u=(t-16.28)/.82
        return 16.15+.95*(1-(1-u)**2)
    return t
def prepare(v):
    task=json.loads((ROOT/f'results/sikh320/motion-{v}/task.json').read_text())
    task.update(id=f'sikh320-edit-{v}',operation='audio')
    task['entities']=sorted(set(task['entities']+['music_reference','officer']))
    task['query']='Isolated authorized Sikh supporting cast edit, unchanged accepted music, retimed existing recorded hoof and neigh effects; no new narration or sources'
    task['preserve_accepted_artifact']='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    paths=[Path(__file__),ROOT/'scripts/edit317.py',ROOT/'scripts/sikh305_recorded_audio.py',ROOT/'results/sikh305/audio-4/source-rights.json',ROOT/'results/sikh305/audio-4/verification.json',ROOT/'.runtime/art-direction/series01-sikh318/build-04/impact-events.json',ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4',ROOT/'docs/knowledge/CURRENT_PRODUCTION_STATE.md']
    manifest=json.loads((ROOT/'.runtime/art-direction/series01-sikh305/audio-04/manifest.json').read_text())
    paths.extend(ROOT/r['file'] for r in manifest['source_rights'])
    paths.extend((ROOT/'.runtime/art-direction/series01-sikh305/audio-04').glob('*.wav'))
    for p in paths:task['inputs'][str(p.relative_to(ROOT))]=pk.file_hash(p)
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh320/delivery-{v}';record.mkdir(exist_ok=True)
    for name,value in [('task',task),('packet',packet)]: (record/(name+'.json')).write_text(json.dumps(value,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    return task
def audio(v):
    import edit317
    events=json.loads((ROOT/'.runtime/art-direction/series01-sikh318/build-04/impact-events.json').read_text())
    for e in events['events']:
        e['original_source_t']=e['source_t'];e['source_t']=retime(e['source_t'])
        e['frame']=round(e['source_t']/RATE*24)+1;e['edit_seconds']=(e['frame']-1)/24
    (BASE/f'build-{v:02d}/impact-events.json').write_text(json.dumps(events,indent=2))
    edit317.BASE=BASE;edit317.m=types.SimpleNamespace(RATE=RATE)
    edit317.audio(v,neigh_source_time=retime(15.61))
def run(*a):subprocess.run([FF,'-v','error',*a],check=True)
def main():
    v=int(sys.argv[1]);assert 1<=v<=20
    task=prepare(v)
    if '--prepare' in sys.argv:print(ROOT/f'results/sikh320/delivery-{v}/packet.md');return
    native=BASE/f'build-{v:02d}/sequence.blend';frames=BASE/f'motion-{v:02d}/frames'
    paths=sorted(frames.glob('frame-*.png'));assert [p.name for p in paths]==[f'frame-{f:04d}.png' for f in range(START,END+1)]
    audio(v)
    soundtrack=BASE/f'audio-{v:02d}/sikh-mix.wav'
    out=BASE/f'delivery-{v:02d}';out.mkdir(exist_ok=False)
    count=END-START+1;seconds=count/24;offset=(START-1)/24
    clip=out/'nihang-crowd-review.mp4'
    run('-framerate','24','-start_number',str(START),'-i',str(frames/'frame-%04d.png'),'-ss',str(offset),'-i',str(soundtrack),'-frames:v',str(count),'-t',str(seconds),'-map','0:v','-map','1:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(clip))
    run('-xerror','-i',str(clip),'-f','null','-')
    info=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_format','-show_streams','-of','json',str(clip)]));assert abs(float(info['format']['duration'])-seconds)<.05
    sheets(frames,out/'chronology',columns=6,rows=4,width=240)
    controls=out/'encoded-controls';controls.mkdir()
    for f in (252,275,276,298,315,321,333,344,348,350,355,365,381,400,417,418,441):
        run('-i',str(clip),'-vf',f'select=eq(n\\,{f-START})','-frames:v','1',str(controls/f'frame-{f:04d}.png'))
    sheets(controls,out/'encoded-review',columns=4,rows=2,width=260)
    assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    (out/'verification.json').write_text(json.dumps({'native_sha':pk.file_hash(native),'clip_sha':pk.file_hash(clip),'audio_source':str(soundtrack.relative_to(ROOT)),'audio_sha':pk.file_hash(soundtrack),'audio_retimed':True,'start_frame':START,'end_frame':END,'core_frames':[276,417],'handles_frames':24,'seconds':seconds,'frames':[{'name':p.name,'sha256':pk.file_hash(p)} for p in paths],'decode':'PASS','direct_motion':False,'direct_audio':False,'production_pass':False},indent=2))
    print(clip)
if __name__=='__main__':main()
