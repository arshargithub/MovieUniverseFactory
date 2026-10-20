"""Read-only full protected-object comparison for the scoped320 derivative."""
import sys,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from movie_factory import production_knowledge as pk
from sikh320 import BASE,SOURCE

def worker(v):
    import bpy
    from sikh319_verify import digest_object
    baseline={};summary={}
    for path in (SOURCE,BASE/f'build-{v:02d}/sequence.blend'):
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        bpy.context.scene.frame_set(283);bpy.context.view_layer.update()
        roots=[o for o in bpy.context.scene.objects if o.name in ('HORSE hind support pivot','mounted leader','LEADER spear world contact owner') or o.name.startswith('FOOT WARRIOR ')]
        excluded={o.name for root in roots for o in (root,*root.children_recursive)}
        excluded.update(o.name for o in bpy.context.scene.objects if o.name.startswith(('leader supported rein292','305 hoof earth puff','305 kicked soil clod')))
        objects={o.name:digest_object(o) for o in bpy.context.scene.objects if o.name not in excluded}
        if path==SOURCE:baseline=objects;summary['source_excluded_objects']=len(excluded)
        else:summary.update(protected_objects=len(baseline),changed=[n for n,h in baseline.items() if objects.get(n)!=h],unexpected_added=[n for n in objects if n not in baseline])
    summary.update(status='PASS' if not summary['changed'] and not summary['unexpected_added'] else 'FAIL',limits='Object transforms, actions, mesh coordinates/topology and material slot identities; not shader graphs or perceptual acceptance.',source_sha=pk.file_hash(SOURCE),candidate_sha=pk.file_hash(path))
    summary['tack_inventory']=[{'name':o.name,'parent':o.parent.name if o.parent else None,'hidden':o.hide_render} for o in bpy.context.scene.objects if any(w in o.name.lower() for w in ('stirrup','saddle','girth'))]
    (BASE/f'audit-{v:02d}/protection.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary),flush=True)

def main():
    v=int(sys.argv[1]);assert 1<=v<=20
    if sys.argv[-1]=='worker':worker(v);return
    task=json.loads((ROOT/f'results/sikh320/motion-{v}/task.json').read_text());task['id']=f'sikh320-protection-{v}'
    for p in (Path(__file__),SOURCE):task['inputs'][str(p.relative_to(ROOT))]=pk.file_hash(p)
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh320/audit-{v}';record.mkdir(exist_ok=True)
    for name,value in [('task',task),('packet',packet)]: (record/(name+'.json')).write_text(json.dumps(value,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(record/'packet.md');return
    out=BASE/f'audit-{v:02d}';out.mkdir(exist_ok=False)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    with (out/'worker.log').open('x') as log:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',str(v),'worker'],env=env,stdout=log,stderr=subprocess.STDOUT)
    assert r.returncode==0,out/'worker.log'
    assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    print(out/'protection.json')

if __name__=='__main__':
    if '--' in sys.argv:sys.argv=[sys.argv[0]]+sys.argv[sys.argv.index('--')+1:]
    main()
