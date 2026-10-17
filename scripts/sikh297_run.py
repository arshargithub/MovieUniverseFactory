"""Fresh-packet local launcher; exact fixed operations and sanitized Blender."""
import sys,json,os,time,hashlib,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh297_contract import validate
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh297'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    op,ver=sys.argv[1:3];j=validate({'operation':op,'version':int(ver)})
    task=json.loads((ROOT/'results/sikh292/controls-3/task.json').read_text())
    paths=list(task['inputs'])+['results/sikh297/STRATEGY.md','results/sikh292/LEARNINGS.md','scripts/sikh297_run.py','scripts/sikh297_native.py','scripts/sikh297_layers.py','src/movie_factory/sikh297_contract.py','.runtime/art-direction/series01-sikh292/movie-01/sequence.blend']
    paths+=['scripts/sikh297_edit.py','.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4','.runtime/art-direction/series01-sikh292/edit-01/sikh-mix.wav','.runtime/art-direction/series01-sikh292/edit-01/joined-mix.wav']
    if op in ('movie','reopen'):paths+=['.runtime/art-direction/series01-sikh297/controls-05/sequence.blend']
    task.update(id=f'sikh297-{op}-{ver}',entities=['punjab_night','nihang_crowd','nihang_leader','nihang_horse','sikh_camera','renderer'],intent='Director297 reusable field trail supporting cast and torchlight; principal actor unchanged; explicit development scope',inputs={p:sha(ROOT/p) for p in paths},execution_authority={'source':'results/sikh297/STRATEGY.md','scope':'Local supporting-layer and torchlight work; no paid/cloud/hero work'},max_context_characters=48000)
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh297'/f'{op}-{ver}';proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]: (proof/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/f'{op}-{int(ver):02d}';out.mkdir(parents=True,exist_ok=False)
    jp=out/'job.json';jp.write_text(json.dumps(j));snap=out/'source';snap.mkdir()
    for rel,digest in task['inputs'].items():
        if Path(rel).suffix=='.py':
            dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
            if sha(dest)!=digest:raise ValueError('Source changed')
    (snap/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh297_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
