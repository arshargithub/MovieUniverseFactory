"""Read-only, fixed-source material ownership inspection for terrain198."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE_HASH='8c9a738210f5d461abbb47360ddb95b3e2e12d29a9fead265fc97b51f51aefeb'

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'inspect01'}: raise ValueError('Fixed inspection only')
    source=base.BASE/'entrance196-particles40/scene.blend'; out=base.BASE/'entrance198-inspect01'
    if out.exists() or base.digest(source)!=SOURCE_HASH: raise ValueError('Source or destination mismatch')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    base.check_protected();out.mkdir()
    owners={}; meshes={}
    for o in bpy.context.scene.objects:
        if not hasattr(o.data,'materials'):continue
        for m in o.data.materials:
            if m:owners.setdefault(m.name,[]).append(o.name)
        if o.type=='MESH': meshes.setdefault(o.data.name,{'objects':[],'materials':[m.name if m else None for m in o.data.materials]})['objects'].append(o.name)
    mats={}
    for name,obs in owners.items():
        m=bpy.data.materials[name];ns=[]
        if m.use_nodes:
            for n in m.node_tree.nodes:
                ns.append({'name':n.name,'type':n.type,'image':getattr(getattr(n,'image',None),'name',None),'inputs':{s.name:{'value':list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value,'links':[l.from_node.name+'.'+l.from_socket.name for l in s.links]} for s in n.inputs if hasattr(s,'default_value')},'outputs':{s.name:[l.to_node.name+'.'+l.to_socket.name for l in s.links] for s in n.outputs}})
        mats[name]={'owners':obs,'nodes':ns}
    (out/'materials.json').write_text(json.dumps(mats,indent=2)+'\n');(out/'meshes.json').write_text(json.dumps(meshes,indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_HASH,'objects':len(bpy.context.scene.objects),'materials':len(mats),'native_modified':False},indent=2)+'\n')
    base.check_protected()

if __name__=='__main__': main()
