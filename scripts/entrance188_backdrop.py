"""Camera-frustum coverage of the bounded art cylinder, before more full rendering."""
import math
import numpy as np


def required_angles(origin,directions,floor,radius=4000.):
    """Conservatively ignore rays blocked by the opaque inner terrain domain."""
    d=directions.reshape(-1,3)
    with np.errstate(divide='ignore',invalid='ignore'):
        ground_t=(floor-origin[2])/d[:,2]
        ground=origin[None,:]+ground_t[:,None]*d
    blocked=(ground_t>0)&(d[:,2]<0)&(np.linalg.norm(ground[:,:2],axis=1)<600)
    d=d[~blocked]
    if not len(d):return None
    a=(d[:,:2]**2).sum(1);b=2*(d[:,:2]*origin[:2]).sum(1);c=(origin[:2]**2).sum()-radius**2
    if np.any(a<1e-20):raise ValueError('Required vertical ray misses finite art cylinder')
    t=(-b+np.sqrt(b*b-4*a*c))/(2*a)
    points=origin[None,:]+t[:,None]*d
    p=points
    angles=np.degrees(np.arctan2(p[:,1],p[:,0]))
    return {'pixels_requiring_background':len(p),'min_angle':float(angles.min()),'max_angle':float(angles.max()),
            'min_z':float(p[:,2].min()),'max_z':float(p[:,2].max())}


def orient(scene):
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance_astra_world import FLOOR
    rows=[]
    with render_geometry_paused():
        for frame in range(217,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            camera=scene.camera
            corners=np.array([tuple(v) for v in camera.data.view_frame(scene=scene)])
            xx,yy=np.meshgrid(np.linspace(corners[:,0].min(),corners[:,0].max(),289),
                              np.linspace(corners[:,1].min(),corners[:,1].max(),513))
            local=np.stack([xx,yy,np.full_like(xx,corners[0,2])],axis=-1)
            transform=np.array(camera.matrix_world)
            directions=local@transform[:3,:3].T
            center=np.array(bpy.data.objects['AS_world_travel'].matrix_world.translation)
            origin=transform[:3,3]-center
            # Every inner terrain point is above FLOOR; camera origins stay inside
            # its opaque650-unit disk. Using a600-unit ground-hit disk is conservative.
            if np.linalg.norm(origin[:2])>=649:raise ValueError('Opaque-domain premise changed')
            row=required_angles(origin,directions,FLOOR)
            rows.append({'frame':frame,'coverage':row})
    needed=[r['coverage'] for r in rows if r['coverage']]
    low=min(r['min_angle'] for r in needed);high=max(r['max_angle'] for r in needed)
    if high-low>130:raise ValueError('Existing140-degree art cannot cover frustum with margin')
    bottom=min(r['min_z'] for r in needed);top=max(r['max_z'] for r in needed)
    if bottom<FLOOR-500 or top>FLOOR+2500:raise ValueError('Art height is insufficient: '+str((bottom,top)))
    rotation=(low+high)/2-50
    bpy.data.objects['MF188_distant_art_arc'].rotation_euler.z=math.radians(rotation)
    return {'samples_per_frame':289*513,'frame_count':144,'required_angles':[low,high],
            'required_heights':[bottom,top],'rotation_degrees':rotation,
            'covered_angles':[-20+rotation,120+rotation],'angular_margin_degrees':(140-high+low)/2,
            'original_orientation_fails':low< -20 or high>120,'frames':rows,
            'scope':'Dense native camera-frustum ray grid plus conservative opaque-terrain bound; actual rendered edge checks remain required'}
