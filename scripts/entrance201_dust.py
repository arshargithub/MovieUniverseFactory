"""Continuous path-history dust: shaded mass against the pale illustrated earth.

Authored volume field, not a fluid simulation. Same definition for straight
approach and curved continuation; fixed chronology and reproducible shape.
"""
import numpy as np
AGES=np.r_[np.linspace(.025,.75,12),np.linspace(.9,2.9,12)]

def cloud_centers(t,route=None):
    from entrance190_scene import path_sample
    points=[]
    for a in AGES:
        p=(np.array([0.,12*a,0.]) if route is None else path_sample(route,t-a))*8.3+np.array([0,.2,-20.931])
        # Expanding, lifting wake; lateral drift is continuous with age rather
        # than unrelated randomly positioned puffs.
        p+=np.array([2.5*a,0,2+10*np.sqrt(a)])
        points.append(p)
    return np.array(points)

def wake(scene,frames,route=None,profile='selected'):
    if profile not in ('selected','dense'):raise ValueError('Unknown authored dust profile')
    import bpy
    from entrance_astra_world import mesh_object
    for ob in scene.objects:
        if any(s in ob.name.lower() for s in ('dust','curved_wake')):ob.hide_render=True
    mat=bpy.data.materials.new('201 shaded sunlit earth wake');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    def scalar(op,a,b):
        q=n.new('ShaderNodeMath');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,(int,float)):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    def vector(op,a,b):
        q=n.new('ShaderNodeVectorMath');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,tuple):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q
    tc=n.new('ShaderNodeTexCoord');extent=vector('MULTIPLY',tc.outputs['Generated'],(1.,1.,1.));origin=vector('ADD',extent.outputs[0],(0.,0.,0.));world=origin.outputs[0]
    centers=[];total=0.;radii=[]
    for age in AGES:
        delta=vector('SUBTRACT',world,(0.,0.,0.));centers.append(delta.inputs[1])
        radius=(5+9*np.sqrt(age),12+10*age,4+12*np.sqrt(age));radii.append(radius)
        norm=vector('DIVIDE',delta.outputs[0],radius)
        d=vector('DOT_PRODUCT',norm.outputs[0],norm.outputs[0]).outputs['Value']
        field=scalar('POWER',scalar('MAXIMUM',scalar('SUBTRACT',1,d),0),1.7)
        total=scalar('ADD',total,scalar('MULTIPLY',field,float((1-age/3.6)**.85)))
    noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=.075;noise.inputs['Detail'].default_value=2.;noise.inputs['Roughness'].default_value=.6;l.new(world,noise.inputs[0])
    modulation=(scalar('MAXIMUM',scalar('ADD',scalar('MULTIPLY',noise.outputs['Fac'],2.5),-.55),.02) if profile=='selected'
                else scalar('ADD',scalar('MULTIPLY',noise.outputs['Fac'],.75),.25))
    density_gain=.09 if profile=='selected' else .16;emission_gain=.20 if profile=='selected' else .06
    density=scalar('MULTIPLY',scalar('MULTIPLY',total,modulation),density_gain)
    vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.95,.87,.69,1);vol.inputs['Anisotropy'].default_value=.12
    # Restrained authored ambient lift preserves lit earth colour without the old
    # .65*density emission that erased mass on pale ground. Not photometry.
    vol.inputs['Emission Color'].default_value=(.78,.65,.44,1);l.new(scalar('MULTIPLY',density,emission_gain),vol.inputs['Emission Strength']);l.new(density,vol.inputs['Density'])
    output=n.new('ShaderNodeOutputMaterial');l.new(vol.outputs[0],output.inputs['Volume'])
    verts=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]
    faces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    ob=mesh_object('MF201_dramatic_dust',verts,faces,scene.collection);ob.data.materials.append(mat)
    rows=[];radii=np.array(radii)
    for f in frames:
        points=cloud_centers((f-361)/24,route)
        noise.inputs['W'].default_value=f/24*.6;noise.inputs['W'].keyframe_insert(data_path='default_value',frame=f)
        lo=(points-radii).min(0)-1;hi=(points+radii).max(0)+1
        for p,s in zip(points,centers):s.default_value=tuple(p);s.keyframe_insert(data_path='default_value',frame=f)
        ob.location=(lo+hi)/2;ob.scale=(hi-lo)/2
        for prop in ('location','scale'):ob.keyframe_insert(data_path=prop,frame=f)
        extent.inputs[1].default_value=tuple(hi-lo);origin.inputs[1].default_value=tuple(lo)
        for node in (extent,origin):node.inputs[1].keyframe_insert(data_path='default_value',frame=f)
        rows.append({'frame':f,'bounds':[lo.tolist(),hi.tolist()]})
    return {'method':'Continuous overlapping path-history density, slow4D billowing, restrained ambient lift','profile':profile,'fluid_simulation':False,'emission_density_gain':emission_gain,'density_gain':density_gain,'history_seconds':2.9,'cells':len(AGES),'frames':rows}
