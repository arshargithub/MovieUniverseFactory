"""Current rooted beard, irregular coherent clumps, no face edits."""
import math
import json
import importlib.util
from pathlib import Path
import numpy as np


def guide(root, eye, index, kind, steps=40):
    r = np.asarray(root, dtype=float)
    t = np.linspace(0, 1, steps)
    p = np.tile(r, (steps, 1))
    a = abs(r[0])
    side = 1 if r[0] >= 0 else -1
    # Neighboring follicles share a clump, not one phase per independent hair.
    gx = round(r[0] / .014)
    gz = round((eye - r[2]) / .014)
    phase = gx * 2.13 + gz * .83
    individual = math.sin(index * 2.399)
    if kind == 'lip':
        p[:, 0] += side * (.010 + .003 * individual) * t
        p[:, 1] -= .003 * np.sin(np.pi * t)
        p[:, 2] -= (.009 + .005 * a / .034) * t
    else:
        end = eye - .222 + .033 * (a / .071)**2
        end += .013 * math.sin(phase) + .005 * individual
        envelope = np.sin(np.pi * t) * t**.65
        flow = .0045 + .002 * math.sin(phase * 1.9)
        p[:, 0] += -.28 * r[0] * t**2
        p[:, 0] += (gx * .014 - r[0]) * .65 * envelope
        p[:, 0] += flow * np.sin(12*t + phase) * envelope
        p[:, 1] -= .026*t + .014*np.sin(np.pi*t)
        p[:, 1] += .005 * np.sin(13*t + phase + .8) * envelope
        p[:, 2] -= (r[2] - end) * t
        p[:, 2] += .002 * np.sin(16*t + phase) * envelope
        # A restrained free-tip split avoids a clipped, solid beard boundary.
        p[:, 0] += .002 * individual * t**3
        p[:, 1] += .0015 * math.sin(index * 1.7) * t**3
    p[0] = r
    return p


def run(bpy, out):
    spec = importlib.util.spec_from_file_location(
        'tack354', Path(__file__).with_name('nihang_tack354.py'))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    signature = helper.action_signature(bpy)
    rig = bpy.data.objects['MF coherent Nihang rig']
    beard = bpy.data.objects['MF347 integrated beard and moustache']
    if not rig.get('groom357') or rig.get('beard361'):
        raise ValueError('BEARD361_PARENT')
    roots = [np.array(s.points[0].co[:3]) for s in beard.data.splines]
    if len(roots) < 4000:
        raise ValueError('BEARD361_ROOTS')
    eye = float(rig.data.bones['eye.L'].head_local.z)
    data = bpy.data.curves.new('361 rooted irregular beard clumps', 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = .00012
    data.bevel_resolution = 1
    rng = np.random.default_rng(36187)
    for i in range(16):
        material = bpy.data.materials.new('361 chestnut beard fiber ' + str(i))
        material.use_nodes = True
        bs = material.node_tree.nodes.get('Principled BSDF')
        v = .65 + .9 * (i / 15)**1.5
        bs.inputs['Base Color'].default_value = (.022*v, .012*v, .006*v, 1)
        bs.inputs['Roughness'].default_value = .43
        bs.inputs['Specular IOR Level'].default_value = .31
        data.materials.append(material)
    root_error = []
    for i, root in enumerate(roots):
        kind = 'lip' if abs(root[0]) < .034 and eye-root[2] < .065 else 'cheek'
        # Preserve the retained357 volume/length field. The87 quantized-clump
        # reconstruction opened vertical gaps and was rejected before use.
        old=np.array([p.co[:3] for p in beard.data.splines[i].points])
        path=refine(old,i)
        spline = data.splines.new('POLY')
        spline.points.add(len(path)-1)
        spline.material_index = int(rng.integers(0, 16))
        width = float(rng.uniform(.65, 1.15))
        for j, (point, co) in enumerate(zip(spline.points, path)):
            point.co = (*co, 1)
            point.radius = width * (.025 + .975*(1-j/(len(path)-1))**.58)
        root_error.append(float(np.linalg.norm(path[0]-root)))
    # The old data remain as an explicit retained datablock, not a second
    # rendered solid underneath this groom. Existing head owner/action stay.
    beard.data.use_fake_user = True
    beard.data = data
    rig['beard361'] = 1
    bpy.context.view_layer.update()
    if helper.action_signature(bpy) != signature:
        raise ValueError('BEARD361_ACTION_DRIFT')
    report = dict(changed=True, source_preserved=True, actions_unchanged=True,
                  action_signature=signature, roots=len(roots),
                  maximum_root_change=max(root_error),
                  scope='Existing anatomical roots and head action; coherent irregular wavy clumps. Shape/contact and intended-view review remain required; not hair simulation or whole actor acceptance.')
    (out/'beard361.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def refine(points,index):
    p=np.asarray(points,dtype=float).copy()
    t=np.linspace(0,1,len(p));root=p[0].copy()
    phase=root[0]*170+root[2]*19
    window=np.sin(np.pi*t)*t**.65
    p[:,0]+=.0028*np.sin(19*t+phase)*window
    p[:,1]+=.0030*np.sin(17*t+phase*1.7)*window
    p[:,2]+=.0009*np.sin(23*t+phase)*window
    if index%37==0:
        p[:,0]+=.003*math.sin(index*2.399)*t**3
        p[:,1]-=.002*t**3
    p[0]=root
    return p
