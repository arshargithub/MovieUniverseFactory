"""Allowlisted reversible bank-apron/road-normal correction and shot controls."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src')]
import bpy,bmesh
from movie_factory.sikh300_motion import ground_height
BASE=ROOT/'.runtime/art-direction/series01-sikh300'
FRAMES=(1,72,99,112,148,215,300,335,360,435,467,470,528)
def fix(out):
    road=bpy.data.objects['irregular packed farm track'];bm=bmesh.new();bm.from_mesh(road.data)
    assert sum(f.normal.z for f in bm.faces)<0
    bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(road.data);bm.free();road.data.update()
    bank=bpy.data.objects['low field bank for leader'];old=bank.data;vs=[];fs=[];protected=[]
    for v in old.vertices:
        x,y,z=v.co;newz=z
        if z<.5:
            u=max(0,min(1,(z+.01)/.51));weight=u*u*(3-2*u)
            newz=ground_height(x,y)*(1-weight)+z*weight-.004*(1-weight)
        if z>3:protected.append([v.index,list(v.co)])
        vs.append((x,y,newz))
    removed=0
    for face in old.polygons:
        if max(old.vertices[i].co.z for i in face.vertices)<=.001:removed+=1
        else:fs.append(tuple(face.vertices))
    data=bpy.data.meshes.new('300 bank footprint integrated into terrain');data.from_pydata(vs,[],fs);data.update()
    mat=old.materials[0].copy();mat.name='300 bank terrain transition';data.materials.append(mat);bank.data=data
    for f in data.polygons:f.use_smooth=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];bankcolor=b.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.8;noise.inputs['Detail'].default_value=3;l.new(tc.outputs['Object'],noise.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[0].color=(.055,.044,.027,1);ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.22,.18,.105,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
    sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0]);absolute=n.new('ShaderNodeMath');absolute.operation='ABSOLUTE';l.new(sep.outputs['X'],absolute.inputs[0])
    shoulder=n.new('ShaderNodeMapRange');shoulder.inputs['From Min'].default_value=1.65;shoulder.inputs['From Max'].default_value=3.7;l.new(absolute.outputs[0],shoulder.inputs[0]);tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[2].default_value=(.48,.49,.37,1);l.new(shoulder.outputs[0],tint.inputs[0]);l.new(ramp.outputs[0],tint.inputs[1])
    height=n.new('ShaderNodeMapRange');height.interpolation_type='SMOOTHSTEP';height.inputs['From Min'].default_value=.05;height.inputs['From Max'].default_value=.5;l.new(sep.outputs['Z'],height.inputs[0]);mix=n.new('ShaderNodeMixRGB');l.new(height.outputs[0],mix.inputs[0]);l.new(tint.outputs[0],mix.inputs[1]);l.new(bankcolor,mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    for i,co in protected:assert (data.vertices[i].co[:]==tuple(co))
    (out/'repair.json').write_text(json.dumps({'removed_flat_apron_polygons':removed,'protected_plateau_vertices':len(protected),'plateau_identical':True,'road_normal_z_minmax':[min(p.normal.z for p in road.data.polygons),max(p.normal.z for p in road.data.polygons)],'scope':'Remove old rectangular zero-height apron; blend low bank into shared terrain; retain plateau and all actors/actions'},indent=2))
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=json.loads(p.read_text())
    if j not in ({'operation':'ground-fix','version':1},{'operation':'ground-rerender','version':1},{'operation':'ground-reopen','version':1}):raise ValueError('Unadmitted operation')
    s=bpy.context.scene
    if j['operation']=='ground-fix':
        bpy.ops.wm.open_mainfile(filepath=str(BASE/'controls-08/sequence.blend'),use_scripts=False);s=bpy.context.scene;fix(p.parent);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(p.parent/'sequence.blend'))
        frames=FRAMES
    else:
        bpy.ops.wm.open_mainfile(filepath=str(BASE/'ground-fix-01/sequence.blend'),use_scripts=False);s=bpy.context.scene
        # Winding correction affects every road-view shot. Only the fixed
        # leader camera excludes the modified bank foot and road surface.
        frames=tuple(range(1,276))+tuple(range(356,529)) if j['operation']=='ground-rerender' else (1,120,148,215,276,300,335,355,435,470)
    for f in frames:
        s.frame_set(f);s.render.filepath=str(p.parent/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
