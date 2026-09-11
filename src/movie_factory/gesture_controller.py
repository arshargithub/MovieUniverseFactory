"""Bounded provider-free 3D-06A fixture screen; scoring is a separate stage."""
from __future__ import annotations

import argparse
import json
import subprocess
import shutil
import hashlib
import time
import uuid
from pathlib import Path

from .adapters.blender.runner import run_blender
from .experiment_ledger import Ledger
from .packages import atomic_json, file_digest
from .telemetry import utc_now


def screen(repo: Path, plan_path: Path):
    campaign = json.loads((repo/'feasibility/3d/3d-04/campaign.json').read_text())
    parent = repo/campaign['baseline']['relative_path']
    if file_digest(parent) != campaign['baseline']['sha256']:
        raise ValueError('Accepted native fixture changed')
    plan = json.loads(plan_path.read_text())
    identity = 'screen-'+time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())+'-'+uuid.uuid4().hex[:8]
    output = repo/'runs/3d06a'/identity; output.mkdir(parents=True, exist_ok=False)
    source = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    package = {'experiment_id': '3D-06A', 'stage': 'FIXTURE_SCREEN', 'scored': False,
               'run_id': identity, 'source_commit': source, 'reference_plan_sha256': file_digest(plan_path),
               'baseline_native_sha256': file_digest(parent), 'provider_calls': 0, 'known_api_cost_usd': 0,
               'worktree_clean': not subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True).stdout.strip()}
    atomic_json(output/'work-package.json', package)
    ledger = Ledger(repo/'.runtime/experiment-ops.sqlite3')
    context = {'experiment_id': '3D-06A', 'episode_id': 'first', 'phase': 'fixture_screen',
               'job_id': identity, 'job_kind': 'native', 'clock_id': identity, 'run_id': identity,
               'evidence_ref': str(output.relative_to(repo)/'work-package.json')}
    ledger.append({**context, 'event_id': identity+'-start', 'event_type': 'job_started',
                   'utc': utc_now(), 'monotonic_seconds': time.monotonic()})
    try:
        status = run_blender({'mode': 'gesture_screen', 'output_dir': str(output), 'parent_native': str(parent),
            'baseline_sha256': package['baseline_native_sha256'], 'plan': plan,
            'profile': {'name': 'gesture_fixture', 'width': 480, 'height': 360, 'samples': 4, 'device': 'CPU', 'shots': ['shot_A', 'shot_B']}},
            blender_bin='/Applications/Blender.app/Contents/MacOS/Blender', timeout=180)
    except Exception:
        ledger.append({**context, 'event_id': identity+'-end', 'event_type': 'job_completed',
                       'utc': utc_now(), 'monotonic_seconds': time.monotonic(), 'outcome': 'FAILED'})
        raise
    ledger.append({**context, 'event_id': identity+'-end', 'event_type': 'job_completed',
                   'utc': utc_now(), 'monotonic_seconds': time.monotonic(), 'outcome': 'PASSED' if status['ok'] else 'FAILED'})
    print(json.dumps({'run': str(output), 'worker_ok': status['ok'], 'elapsed': status['elapsed'], 'error': status.get('error')}))
    return output, status


def campaign(repo, screened, stage):
    screen_data=json.loads((screened/'fixture-screen.json').read_text())
    if not all(screen_data['checks'].values()):raise ValueError('Fixture screen did not pass')
    identity=stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8]
    output=repo/'runs/3d06a'/identity;output.mkdir(parents=True,exist_ok=False)
    source=subprocess.run(['git','rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
    files=['src/movie_factory/adapters/blender/worker.py','src/movie_factory/adapters/blender/gesture.py','src/movie_factory/gesture.py','src/movie_factory/gesture_controller.py','feasibility/3d/3d-06a/reference-plan.json']
    dependencies={p:file_digest(repo/p) for p in files}
    frozen=None
    if stage=='qualification':
        frozen=json.loads((repo/'feasibility/3d/3d-06a/campaign.json').read_text())
        if frozen['status']!='FROZEN' or any(file_digest(repo/p)!=h for p,h in frozen['dependencies'].items()):
            raise ValueError('Qualification source differs from frozen dependencies')
        if subprocess.run(['git','status','--porcelain'],capture_output=True,text=True,check=True).stdout.strip():
            raise ValueError('Scored qualification requires a clean worktree')
        if file_digest(screened/'scene.blend')!=frozen['screen_native_sha256']:
            raise ValueError('Screened fixture differs from frozen native')
    package={'run_id':identity,'stage':stage,'source_commit':source,'dependencies':dependencies,'baseline_native_sha256':file_digest(screened/'scene.blend'),'screen_metrics_sha256':file_digest(screened/'fixture-screen.json'),'scored':stage=='qualification','provider_calls':0,'known_api_cost_usd':0,'frozen_campaign_sha256':file_digest(repo/'feasibility/3d/3d-06a/campaign.json') if frozen else None}
    atomic_json(output/'work-package.json',package)
    ledger=Ledger(repo/'.runtime/experiment-ops.sqlite3')
    context={'experiment_id':'3D-06A','episode_id':'first','phase':stage,'job_id':identity,'job_kind':'native','clock_id':identity,'run_id':identity,'evidence_ref':str(output.relative_to(repo)/'work-package.json')}
    ledger.append({**context,'event_id':identity+'-start','event_type':'job_started','utc':utc_now(),'monotonic_seconds':time.monotonic()})
    status=run_blender({'mode':'gesture_campaign','stage':stage,'scored':package['scored'],'output_dir':str(output),'parent_native':str(screened/'scene.blend'),'baseline_sha256':package['baseline_native_sha256'],'screen_metrics':str(screened/'fixture-screen.json'),'render_frames':True,
        'profile':{'name':'gesture_preview','width':640,'height':480,'samples':16,'device':'CPU','shots':['shot_A','shot_B']}},blender_bin='/Applications/Blender.app/Contents/MacOS/Blender',timeout=900)
    ledger.append({**context,'event_id':identity+'-end','event_type':'job_completed','utc':utc_now(),'monotonic_seconds':time.monotonic(),'outcome':'PASSED' if status['ok'] else 'FAILED'})
    print(json.dumps({'run':str(output),'worker_ok':status['ok'],'elapsed':status['elapsed'],'error':status.get('error')}))
    return output,status


def write_review(run, preview):
    review=run/'review';review.mkdir(parents=True,exist_ok=True)
    if (review/'video-provenance.json').exists():raise ValueError('Review already sealed')
    candidate_first=int(hashlib.sha256(run.name.encode()).hexdigest()[:2],16)%2==0
    labels={'A':'candidate','B':'baseline'} if candidate_first else {'A':'baseline','B':'candidate'}
    atomic_json(run/'blind-key.json',{'labels':labels})
    videos=[]
    for view,title in [('camera_A','Primary'),('camera_B','Side')]:
        command=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error']
        inputs=[]
        for label,role in labels.items():
            folder=preview/'frames'/role/view
            expected=[folder/f'frame-{i:04d}.png' for i in range(96)]
            if any(not f.is_file() for f in expected):raise ValueError('Complete playback frames required')
            for f in expected:inputs.append({'path':str(f.relative_to(preview)),'sha256':file_digest(f)})
            command += ['-framerate','24','-start_number','0','-i',str(folder/'frame-%04d.png')]
        output=review/(title.lower()+'-AB.mp4')
        command += ['-filter_complex',"[0:v][1:v]hstack=inputs=2,drawbox=x=0:y=ih-8:w=iw:h=8:color=cyan:t=fill:enable='eq(n,44)'[out]",'-map','[out]','-frames:v','96','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
        subprocess.run(command,check=True)
        meta=json.loads(subprocess.check_output([shutil.which('ffprobe'),'-v','error','-show_entries','stream=nb_frames,r_frame_rate','-show_entries','format=duration','-of','json',str(output)],text=True))
        if meta['streams'][0]['nb_frames']!='96' or abs(float(meta['format']['duration'])-4)>1e-6:raise ValueError('Incorrect playback timing')
        videos.append({'view':view,'file':output.name,'sha256':file_digest(output),'metadata':meta,'inputs':inputs})
    atomic_json(review/'video-provenance.json',{'encoding':'H264 CRF14; original PNGs retained','fps':24,'frames':96,'source_preview':str(preview),'videos':videos})
    page='''<!doctype html><meta charset="utf-8"><title>3D-06A gesture review</title>
<style>body{background:#202124;color:#eee;font:17px system-ui;margin:2rem auto;max-width:1280px}video{width:100%}.labels{display:flex;justify-content:space-around}p{line-height:1.5}</style>
<h1>3D-06A — small acknowledgement gesture</h1><p>Clip A is left; Clip B is right. Each four-second video shows the complete gesture. The cyan marker flashes at requested frame 44. The original reference cue was frame 48; one clip advances the timing. Both clips should retain the same quality. Replay resets to the start; this is not a seamless loop.</p>'''
    for view in ('primary','side'):
        page+=f'<h2>{view.title()} view</h2><div class="labels"><b>Clip A</b><b>Clip B</b></div><video controls playsinline preload="metadata" src="{view}-AB.mp4"></video>'
    page+='<p>For each clip, score readability, natural movement, transition smoothness and finish (1–5, half points allowed). Note defects and approximate review duration. Preference is optional; a tie is valid. The numerical cue and preservation checks are evaluated separately.</p>'
    (review/'index.html').write_text(page)
    atomic_json(run/'director-review.json',{'status':'PENDING','clips':{label:{key:None for key in ('readability','natural_movement','transition_smoothness','finish')} for label in labels},'review_seconds':None,'preference':None,'major_defects':None})
    return review/'index.html'


def recover_preview(repo, preview):
    missing=[i for i in range(96) if not (preview/'frames/candidate/camera_B'/f'frame-{i:04d}.png').is_file()]
    if not missing or min(missing)<80 or len(missing)>16:raise ValueError('Not a bounded final-frame recovery')
    output=repo/'runs/3d06a'/('preview-complete-'+uuid.uuid4().hex[:8]);output.mkdir(parents=True)
    tail=output/'tail-recovery'
    ledger=Ledger(repo/'.runtime/experiment-ops.sqlite3')
    c={'experiment_id':'3D-06A','episode_id':'first','phase':'preview_recovery','job_kind':'native','job_id':output.name,'clock_id':output.name,'reason':'Complete only final frames after the initial 480-second preview deadline'}
    ledger.append({**c,'event_id':output.name+'-start','event_type':'job_started','utc':utc_now(),'monotonic_seconds':time.monotonic()})
    status=run_blender({'mode':'gesture_tail','output_dir':str(tail),'parent_native':str(preview/'scene.blend'),'baseline_sha256':file_digest(preview/'scene.blend'),'frames':missing,'profile':{'name':'gesture_preview','width':640,'height':480,'samples':16,'device':'CPU','shots':['shot_A','shot_B']}},blender_bin='/Applications/Blender.app/Contents/MacOS/Blender',timeout=60)
    ledger.append({**c,'event_id':output.name+'-end','event_type':'job_completed','utc':utc_now(),'monotonic_seconds':time.monotonic(),'outcome':'PASSED' if status['ok'] else 'FAILED'})
    if not status['ok']:raise RuntimeError('Tail recovery failed')
    for role in ('baseline','candidate'):
        for view in ('camera_A','camera_B'):
            for frame in range(96):
                relative=Path('frames')/role/view/f'frame-{frame:04d}.png'
                source=preview/relative if (preview/relative).is_file() else tail/relative
                target=output/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    for name in ('positive.json','scene.blend','work-package.json'):shutil.copy2(preview/name,output/name)
    atomic_json(output/'recovery.json',{'original_attempt':str(preview),'original_status':'TIMED_OUT','recovered_frames':missing,'remaining_frames_reused_without_rerender':384-len(missing),'scene_sha256':file_digest(preview/'scene.blend'),'status':'COMPLETE_PREVIEW_ONLY'})
    print(json.dumps({'complete_preview':str(output),'recovered_frames':missing}));return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan', type=Path, default=Path('feasibility/3d/3d-06a/reference-plan.json'))
    parser.add_argument('--stage',choices=['screen','preview','qualification'],default='screen')
    parser.add_argument('--screen',type=Path)
    args = parser.parse_args()
    if args.stage!='screen' and args.screen is None:parser.error('--screen is required')
    _, status = screen(Path.cwd(), args.plan) if args.stage=='screen' else campaign(Path.cwd(),args.screen.resolve(),args.stage)
    raise SystemExit(0 if status['ok'] else 1)
