"""Fixed garment-only underarm review, with no loose shawl obscuring joins."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as foundation

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in ('inspect01','repair01'):
        raise ValueError('Fixed underarm inspection only')
    if foundation.SOURCE.is_symlink() or foundation.digest(foundation.SOURCE)!=foundation.SOURCE_SHA:
        raise ValueError('Protected foundation mismatch')
    out=foundation.BASE/('wardrobe179-underarm-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Never overwrite evidence')
    return out

def main():
    import bpy
    from mathutils import Vector
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_riding_fit import fit_render
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
    foundation.check_protected()
    rig,_,_=foundation.clean_foundation();dress_actor(rig)
    correction=None
    if job['operation']=='repair01':
        from wardrobe_underarm179_repair import repair
        correction=repair(rig)
        (out/'wardrobe_underarm179_repair.py').write_bytes((ROOT/'scripts/wardrobe_underarm179_repair.py').read_bytes())
    controls.animate(rig,neutral_entry=True)
    # Record the actual protected-hair exclusion contour alongside the views;
    # a cloth silhouette is not evidence that a proxy matches visible hair.
    proxy=bpy.data.objects['MF_173_static_groom_clearance']
    sections=[]
    for z in (1.,.5,0.,-.5,-1.,-1.5,-2.,-2.5,-3.):
        section=[v.co for v in proxy.data.vertices if abs(v.co.z-z)<.15]
        if section:sections.append({'z':z,'count':len(section),
            'min':[min(p[k] for p in section) for k in range(3)],
            'max':[max(p[k] for p in section) for k in range(3)]})
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU'
    scene.cycles.samples=8;scene.render.use_persistent_data=True
    for frame in (97,121,145):
        scene.frame_set(frame);bpy.context.view_layer.update()
        target=studio.torso_matrix(-2.7)@Vector((0,.15,-3.))
        for label,angle in (('front',0),('rear',180),('left-side',90),('right-side',270)):
            fit_render(out,'%s-%s'%(label,frame),angle,tuple(target),6.0,(720,720))
    foundation.check_protected()
    (out/'result.json').write_text(json.dumps({'protected_exact':True,'visual_gate':'NOT_RUN',
        'scope':'Both underarm joins without shawl: upper neutral, partial and full riding lean',
        'neutral_groom_proxy_sections':sections,
        'garment_correction':correction,
        'source_sha256':foundation.SOURCE_SHA,'handler_sha256':foundation.digest(Path(__file__))},indent=2)+'\n')

if __name__=='__main__':main()
