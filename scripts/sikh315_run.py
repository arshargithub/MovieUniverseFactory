"""Fixed offline operations for Director315; no runtime code or secrets."""
import sys,json,os,time,subprocess,hashlib,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh315'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh314/build-07/sequence.blend'
OPS=('inspect','build','finish','proof','movie','reopen','profile')
def source_for(op,v):
    if op in ('inspect','build'):return SOURCE
    if op=='finish':
        if v<3:raise ValueError('Finish requires a prior315 derivative')
        candidate=BASE/f'finish-{v-1:02d}/sequence.blend'
        return candidate if candidate.exists() else BASE/f'build-{v-1:02d}/sequence.blend'
    candidate=BASE/f'finish-{v:02d}/sequence.blend'
    return candidate if candidate.exists() else BASE/f'build-{v:02d}/sequence.blend'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def main():
    op,v=sys.argv[1],int(sys.argv[2])
    if op not in OPS or not 1<=v<=16:raise ValueError('Unadmitted fixed operation')
    source=source_for(op,v)
    task=json.loads((ROOT/'results/sikh305/build-4/task.json').read_text())
    task.update(id=f'sikh315-{op}-{v}',intent='Director315 integrated supporting-scene correction: reference rear, actual ground relief, coupled traction launch, world-space wake, supporting cast',execution_authority={'source':'results/sikh315/STRATEGY.md','scope':'Local reversible correction only; no providers cloud installs uploads principal admission'})
    paths=[source,ROOT/'results/sikh315/STRATEGY.md',ROOT/'docs/knowledge/review_control/README.md',ROOT/'docs/knowledge/SIKH305_REVIEW_FAILURE_AUDIT306.md',ROOT/'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov',ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4']
    paths.append(ROOT/'.runtime/assets/demonstrator-01/horse.blend')
    paths+=sorted((ROOT/'scripts').glob('sikh315_*.py'))
    paths+=sorted((ROOT/'src/movie_factory').glob('sikh315_*.py'))
    for stem in ('sikh305_scene','sikh305_land','sikh305_impacts','sikh304_scene','sikh299_scene','sikh314_scene','sikh297_layers','sikh292_assets','sikh257_layout','sikh257_native'):paths.append(ROOT/'scripts'/f'{stem}.py')
    task['inputs']={str(p.relative_to(ROOT)):sha(p) for p in paths}
    packet=pk.task_packet(ROOT,task);dest=ROOT/f'results/sikh315/{op}-{v}';dest.mkdir(parents=True,exist_ok=True)
    for name,data in (('task',task),('packet',packet)):(dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False)
    path=out/'job.json';path.write_text(json.dumps({'operation':op,'version':v}));(out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    for name in task['inputs']:
        if name.endswith(('.py','.md')):
            destfile=out/'source-snapshot'/name;destfile.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,destfile)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for key,folder in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[key]=str(out/'sandbox'/folder)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh315_native.py'),'--',str(path)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest']},indent=2))
    if r.returncode:raise RuntimeError(out/'worker.log')
    print(out)
if __name__=='__main__':main()
