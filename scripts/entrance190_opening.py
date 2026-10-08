"""Carry corrected blink timing into every reused native entrance coverage."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SHA='7038eaf08e1349478841d02604e2b025d76650c1a5c402d7eb76065ffab62812'


def render():
    import bpy
    from entrance190_blink import blink
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'blink-opening34'}:raise ValueError('Fixed opening blink coverage required')
    source=base.BASE/'entrance190-blink03/scene.blend';out=base.BASE/'entrance190-blink-opening34'
    if out.exists() or base.digest(source)!=SHA:raise ValueError('Changed source or prior output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    # The saved03 native retains the original animated opening camera;
    # its close-camera override happened only after saving that native.
    if not scene.camera.animation_data or not scene.camera.animation_data.action:raise ValueError('Opening camera missing')
    rows=[]
    for f in range(309,316):
        scene.frame_set(f);bpy.context.view_layer.update()
        values={n:bpy.data.objects['MF_studio_adult_body'].data.shape_keys.key_blocks[n].value for n in ('eyeBlinkLeft','eyeBlinkRight')}
        if max(abs(v-blink(f)) for v in values.values())>1e-5:raise ValueError('Actual blink differs')
        scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        rows.append({'frame':f,'values':values,'camera':list(scene.camera.matrix_world.translation)})
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':SHA,'frames':rows,'visual_gate':'NOT_RUN','native_modified':False},indent=2)+'\n')


def assemble():
    from PIL import Image
    from entrance190_verify import compare
    from entrance189_media import sheet
    new=base.BASE/'entrance190-blink-opening34';old=base.BASE/'entrance189-motion16';out=base.BASE/'entrance190-opening-review35'
    result=json.loads((new/'result.json').read_text());prior=json.loads((old/'media.json').read_text())
    if out.exists() or result['source_sha256']!=SHA or base.digest(base.BASE/'entrance190-blink03/scene.blend')!=SHA:raise ValueError('Source mismatch or prior assembly')
    parity=[]
    for f in (309,315):
        p=new/f'frame-{f:04d}.png';q=old/p.name
        parity.append({'frame':f,**compare(np.asarray(Image.open(p)),np.asarray(Image.open(q)))})
    if any(r['status']!='PASS' for r in parity):raise ValueError('Unchanged opening boundary differs')
    for r in prior['frames']:
        if base.digest(old/r['name'])!=r['sha256']:raise ValueError('Prior native frame changed')
    out.mkdir();rows=[]
    for f in range(217,361):
        p=(new if 310<=f<=314 else old)/f'frame-{f:04d}.png';target=out/p.name;shutil.copy2(p,target)
        rows.append({'name':target.name,'sha256':base.digest(target),'source':str(p.relative_to(base.BASE))})
    sheet([out/f'frame-{f:04d}.png' for f in range(309,316)],out/'blink-sheet.png')
    video=out/'entrance-proof.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error','-framerate','24','-start_number','217','-i',str(out/'frame-%04d.png'),'-frames:v','144','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],check=True)
    (out/'media.json').write_text(json.dumps({'source_sha256':SHA,'frames':rows,'video_sha256':base.digest(video),'fps':24,'frame_count':144,'duration_seconds':6,'visual_gate':'NOT_RUN'},indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'source_sha256':SHA,'unchanged_boundary_parity':parity,'replaced_frames':list(range(310,315)),'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':
    if sys.argv[1:]==['--assemble']:assemble()
    else:render()
