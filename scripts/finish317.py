"""Fixed local diagnostic and finish runner; no dynamic code/provider inputs."""
import sys,os,json,subprocess,time
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317'
def validate(j):
    if set(j)!={'operation'} or j['operation'] not in ('jointstudy','jointstudy2','jointstudy3','hoofprobe','finish','verify'):raise ValueError('Invalid fixed operation')
    return j['operation']
def main():
    op=validate({'operation':sys.argv[1]});out=BASE/({'jointstudy':'jointstudy-04','jointstudy2':'jointstudy-05','jointstudy3':'jointstudy-06','hoofprobe':'hoofprobe-05','finish':'build-04','verify':'verify-04'}[op])
    source=BASE/('build-04' if op in ('verify','hoofprobe') else 'build-03')/'sequence.blend'
    task=json.loads((ROOT/'results/sikh317/build-3/task.json').read_text());task['id']='sikh317-'+op+'-4'
    paths=[source,ROOT/'scripts/finish317.py',ROOT/'scripts/finish317_native.py',ROOT/'src/movie_factory/sikh317_motion.py',ROOT/'results/sikh317/STRATEGY.md']
    task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths};packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    dest=ROOT/'results/sikh317'/('build-4' if op=='finish' else op+'-4');dest.mkdir(exist_ok=True,parents=True)
    for name,data in [('task',task),('packet',packet)]:(dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out.mkdir(exist_ok=False);job=out/'job.json';job.write_text(json.dumps({'operation':op}));(out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/finish317_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[p for p,h in task['inputs'].items() if pk.file_hash(ROOT/p)!=h]
    (dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-start,'changed_inputs':changed},indent=2))
    if changed or r.returncode:raise RuntimeError(out/'worker.log')
    print(out)
if __name__=='__main__':main()
