"""Fixed local Director317 operations. No arbitrary code, credentials or network."""
import sys,json,os,subprocess,time,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from sikh315_run import sha
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh317'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh315/finish-11/sequence.blend'
OPS=('inspect','build','proof','movie','reopen')
def validate(job):
    if set(job)!={'operation','version'} or job['operation'] not in OPS or type(job['version']) is not int or not 1<=job['version']<=9:raise ValueError('Unadmitted structured operation')
    return job['operation'],job['version']
def main():
    op,v=validate({'operation':sys.argv[1],'version':int(sys.argv[2])})
    source=SOURCE if op in ('build','inspect') else BASE/f'build-{v:02d}/sequence.blend'
    task=json.loads((ROOT/'results/sikh305/build-4/task.json').read_text())
    task.update(id=f'sikh317-{op}-{v}',intent='Integrated316 repair plus bounded reuse learning extension',execution_authority={'source':'results/sikh317/STRATEGY.md','scope':'Director317 local reversible integrated repair, no new services spending uploads or principal admission'})
    paths=[source,ROOT/'results/sikh317/STRATEGY.md',ROOT/'results/review316/REVIEW.md',ROOT/'docs/knowledge/review_control/README.md',ROOT/'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov',ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4']
    paths+=sorted((ROOT/'scripts').glob('sikh317_*.py'))+sorted((ROOT/'src/movie_factory').glob('sikh317_*.py'))
    for family in ('sikh315','sikh314','sikh305','sikh304','sikh300','sikh299','sikh297','sikh292','sikh291','sikh289','sikh257'):
        paths+=sorted((ROOT/'scripts').glob(f'{family}_*.py'))+sorted((ROOT/'src/movie_factory').glob(f'{family}_*.py'))
    task['inputs']={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))}
    packet=pk.task_packet(ROOT,task);dest=ROOT/f'results/sikh317/{op}-{v}';dest.mkdir(parents=True,exist_ok=True)
    for name,data in (('task',task),('packet',packet)):(dest/f'{name}.json').write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False)
    job=out/'job.json';job.write_text(json.dumps({'operation':op,'version':v}))
    (out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    for name in task['inputs']:
        if name.endswith(('.py','.md')):
            target=out/'source-snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    tick=time.monotonic()
    with (out/'worker.log').open('w') as log:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh317_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[name for name,h in task['inputs'].items() if sha(ROOT/name)!=h]
    (dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-tick,'packet_digest':packet['packet_digest'],'changed_inputs':changed},indent=2))
    if changed:raise ValueError('Bound sources changed during job: '+str(changed))
    if r.returncode:raise RuntimeError(out/'worker.log')
    print(out)
if __name__=='__main__':main()
