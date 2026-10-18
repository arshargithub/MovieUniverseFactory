"""Fresh-packet, fixed native entry and isolated local Blender operations."""
import json,sys,os,subprocess,hashlib,time
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh314_motion import validate
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh314'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh305/build-13/sequence.blend'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8388608),b''):h.update(block)
    return h.hexdigest()
def main():
    op,v=sys.argv[1],int(sys.argv[2]);job=validate(dict(operation=op,version=v))
    source=SOURCE if op=='build' else BASE/f'build-{v:02d}/sequence.blend'
    task=json.loads((ROOT/'results/sikh305/build-4/task.json').read_text())
    task.update(id=f'sikh314-{op}-{v}',intent='Integrated Sikh correction after306; independent rear performance, earth drainage and field bunds, persistent debris; Director313 audiovisual review',execution_authority={'source':'results/sikh314/STRATEGY.md','scope':'Authorized local derivative correction; no paid calls uploads installs principal changes'})
    paths=[source,ROOT/'results/sikh314/STRATEGY.md',ROOT/'docs/knowledge/review_control/README.md',ROOT/'docs/knowledge/SIKH305_REVIEW_FAILURE_AUDIT306.md',ROOT/'docs/planning/SHOT_BEAT_QUALITY_BRIEF.md',ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov',ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4']
    paths += [ROOT/'scripts'/f'{name}.py' for name in ('sikh314_run','sikh314_native','sikh314_scene','sikh314_audit','sikh305_scene','sikh305_land','sikh297_layers','sikh257_layout','sikh257_native','sikh292_assets')]
    paths += [ROOT/'src/movie_factory'/f'{name}.py' for name in ('sikh314_motion','sikh305_motion','sikh257_geometry')]
    task['inputs']={str(p.relative_to(ROOT)):sha(p) for p in paths}
    packet=pk.task_packet(ROOT,task);dest=ROOT/f'results/sikh314/{op}-{v}';dest.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]: (dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False)
    path=out/'job.json';path.write_text(json.dumps(job));(out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for key,folder in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[key]=str(out/'sandbox'/folder)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh314_native.py'),'--',str(path)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (dest/'receipt.json').write_text(json.dumps({'returncode':result.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest']},indent=2))
    if result.returncode:raise RuntimeError(out/'worker.log')
    print(out)
if __name__=='__main__':main()
