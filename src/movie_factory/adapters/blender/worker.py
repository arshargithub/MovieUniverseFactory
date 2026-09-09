"""Trusted, data-only procedural Blender adapter for Movie Factory 3D-01.

No generated Python, shell, downloads, arbitrary paths in plans, or dynamic
add-ons are executed. Entity dimensions are total envelopes. Sofa seat cushion
support is exactly 0.54 * sofa height above its root, with local front at -Y.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import traceback

import bpy
from mathutils import Vector


def load_inspector():
    spec = importlib.util.spec_from_file_location("mf_blender_inspect", Path(__file__).with_name("inspect.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def srgb_channel(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def color(hex_color):
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith("#"):
        raise ValueError("Expected a six-digit RGB hex color")
    return tuple(srgb_channel(int(hex_color[i:i + 2], 16) / 255) for i in (1, 3, 5)) + (1.0,)


def identify(obj, oid, entity, kind):
    obj.name = oid
    obj["mf_id"] = oid
    obj["mf_entity"] = entity or ""
    obj["mf_kind"] = kind
    obj["mf_creation_id"] = hashlib.sha256((bpy.context.scene["mf_scene_id"] + ":" + str(bpy.context.scene["mf_seed"]) + ":procedural-v1:" + oid).encode()).hexdigest()
    if obj.data:
        obj.data.name = oid + "_data"
        obj.data["mf_id"] = oid + "_data"
    return obj


def material(mid, rgb, roughness=.5, metallic=0, emission=0):
    mat = bpy.data.materials.new(mid)
    mat["mf_id"] = mid
    mat.use_nodes = True
    p = mat.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = color(rgb)
    p.inputs["Roughness"].default_value = roughness
    p.inputs["Metallic"].default_value = metallic
    if emission:
        p.inputs["Emission Color"].default_value = color(rgb)
        p.inputs["Emission Strength"].default_value = emission
    # Keep diffuse_color at a neutral fixed value: shell revision changes exactly
    # its Principled Base Color, and the inspector preserves every other value.
    return mat


def root(entity):
    obj = bpy.data.objects.new(entity["id"], None)
    bpy.context.collection.objects.link(obj)
    identify(obj, entity["id"], entity["id"], entity["kind"])
    obj["mf_is_entity"] = True
    obj.location = entity["position"]
    obj.rotation_euler[2] = entity["rotation_z"]
    return obj


def finish(obj, parent, suffix, mat, location, scale=None, bevel=0, smooth=False):
    identify(obj, parent["mf_id"] + "_" + suffix, parent["mf_id"], parent["mf_kind"])
    if scale:
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new("baked_edge_rounding", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if smooth:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    obj.data.materials.append(mat)
    obj.parent = parent
    obj.location = location
    return obj


def box(parent, suffix, dims, location, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1)
    return finish(bpy.context.object, parent, suffix, mat, location, dims, bevel=bevel)


def cylinder(parent, suffix, radius, depth, location, mat, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth)
    return finish(bpy.context.object, parent, suffix, mat, location, bevel=min(radius / 6, .008), smooth=True)


def meshpart(parent, suffix, verts, faces, mat, smooth=True):
    mesh = bpy.data.meshes.new(suffix)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(suffix, mesh)
    bpy.context.collection.objects.link(obj)
    identify(obj, parent["mf_id"] + "_" + suffix, parent["mf_id"], parent["mf_kind"])
    obj.parent = parent
    mesh.materials.append(mat)
    if smooth:
        for p in mesh.polygons:
            p.use_smooth = True
    return obj


def curve_tube(parent, suffix, points, radius, mat):
    # Explicit mesh tube, avoiding persistent procedural curve dependencies.
    verts, faces = [], []
    sides = 8
    for i, point in enumerate(points):
        tangent = Vector(points[min(i + 1, len(points) - 1)]) - Vector(points[max(0, i - 1)])
        tangent.normalize()
        normal = tangent.cross(Vector((0, 0, 1)))
        if normal.length < .01:
            normal = tangent.cross(Vector((1, 0, 0)))
        normal.normalize()
        binormal = tangent.cross(normal).normalized()
        for j in range(sides):
            offset = radius * (math.cos(j * math.tau / sides) * normal + math.sin(j * math.tau / sides) * binormal)
            verts.append(tuple(Vector(point) + offset))
        if i:
            for j in range(sides):
                a = (i - 1) * sides + j
                b = (i - 1) * sides + (j + 1) % sides
                faces.append((a, b, b + sides, a + sides))
    faces += [tuple(reversed(range(sides))), tuple(range((len(points) - 1) * sides, len(points) * sides))]
    return meshpart(parent, suffix, verts, faces, mat)


def build_sofa(e):
    r = root(e)
    w, d, h = e["dimensions"]
    fabric = material(e["id"] + "_fabric", e["color_hex"], e["roughness"])
    seam = material(e["id"] + "_piping", "#8B9995", .85)
    wood = material(e["id"] + "_feet", "#4C3023", .4)
    for i, x in enumerate((-.40 * w, .40 * w)):
        for j, y in enumerate((-.36 * d, .36 * d)):
            cylinder(r, f"foot_{i}_{j}", .033, .13 * h, (x, y, .065 * h), wood)
    box(r, "base", (.96 * w, .94 * d, .29 * h), (0, 0, .255 * h), fabric, .04)
    box(r, "back", (.96 * w, .17 * d, .62 * h), (0, .415 * d, .69 * h), fabric, .06)
    for i, x in enumerate((-.43 * w, .43 * w)):
        box(r, f"arm_{i}", (.14 * w, .94 * d, .43 * h), (x, -.02 * d, .545 * h), fabric, .045)
    for i, x in enumerate((-.18 * w, .18 * w)):
        box(r, f"seat_cushion_{i}", (.345 * w, .70 * d, .14 * h), (x, -.085 * d, .47 * h), fabric, .027)
        box(r, f"back_cushion_{i}", (.345 * w, .15 * d, .40 * h), (x, .235 * d, .755 * h), fabric, .035)
        # Delicate front cushion seam makes the upholstery read at room scale.
        curve_tube(r, f"seat_piping_{i}", [(x-.15*w, -.439*d, .505*h), (x+.15*w, -.439*d, .505*h)], .0025, seam)


def build_table(e):
    r = root(e)
    w, d, h = e["dimensions"]
    wood = material(e["id"] + "_wood", e["color_hex"], e["roughness"])
    metal = material(e["id"] + "_legs", "#252928", .3, .55)
    top_thickness = min(.07, h * .16)
    box(r, "top", (w, d, top_thickness), (0, 0, h - top_thickness/2), wood, .025)
    for i, x in enumerate((-.40 * w, .40 * w)):
        for j, y in enumerate((-.35 * d, .35 * d)):
            box(r, f"leg_{i}_{j}", (.045, .045, h - top_thickness), (x, y, (h - top_thickness)/2), metal, .008)
    # Under-top apron remains part of the translated assembly.
    box(r, "apron", (.83*w, .74*d, .045), (0, 0, h-top_thickness-.0225), wood, .009)


def build_lamp(e):
    r = root(e)
    w, d, h = e["dimensions"]
    metal = material(e["id"] + "_metal", "#36332E", .28, .65)
    shade = material(e["id"] + "_shade", e["color_hex"], e["roughness"], emission=.15)
    bulb = material(e["id"] + "_bulb", "#FFE1AD", .2, emission=3)
    cylinder(r, "base", min(w,d)*.37, .035, (0,0,.0175), metal)
    cylinder(r, "stem", .013, h*.78, (0,0,h*.39+.035), metal)
    segments=48
    verts, faces=[],[]
    # Open fabric frustum with thickness: visible shade and actual illuminated interior.
    for z, rx, ry in ((.72*h,w/2,d/2), (h,.34*w,.34*d), (.72*h,.48*w,.48*d), (h,.32*w,.32*d)):
        verts += [(rx*math.cos(i*math.tau/segments),ry*math.sin(i*math.tau/segments),z) for i in range(segments)]
    for i in range(segments):
        j=(i+1)%segments
        faces += [(i,j,segments+j,segments+i), (2*segments+i,3*segments+i,3*segments+j,2*segments+j),
                  (i,2*segments+i,2*segments+j,j), (segments+i,segments+j,3*segments+j,3*segments+i)]
    meshpart(r,"shade",verts,faces,shade)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=.045)
    finish(bpy.context.object,r,"bulb",bulb,(0,0,.84*h),smooth=True)
    data=bpy.data.lights.new(e["id"]+"_practical_data", "POINT")
    obj=bpy.data.objects.new(e["id"]+"_practical",data)
    bpy.context.collection.objects.link(obj)
    identify(obj,e["id"]+"_practical",e["id"],e["kind"])
    obj.parent=r
    obj.location=(0,0,.82*h)
    data.energy=35
    data.color=color("#FFD39B")[:3]
    data.shadow_soft_size=.10


def build_helmet(e):
    r=root(e)
    w,d,h=e["dimensions"]
    shell=material("helmet_shell_01",e["color_hex"],e["roughness"],metallic=.12)
    visor=material("helmet_visor_01","#172731",.12,metallic=.5)
    trim=material("helmet_trim_01","#151719",.5)
    chrome=material("helmet_hardware_01","#9BA6AB",.24,.8)
    # Full-face shell: dome, side cheeks and chin bar share one dedicated shell
    # material. The eye opening is a real cutout with a separate curved visor.
    rows, cols=28,64
    pmax=.86*math.pi
    def surface(phi,theta,expand=1):
        return (expand*w*.5*math.sin(phi)*math.cos(theta),
                expand*d*.5*math.sin(phi)*math.sin(theta),
                h*.5+h*.5*math.cos(phi))
    verts=[surface(i*pmax/rows,j*math.tau/cols) for i in range(rows+1) for j in range(cols)]
    faces=[]
    for i in range(rows):
        phi=(i+.5)*pmax/rows
        for j in range(cols):
            theta=(j+.5)*math.tau/cols
            front=abs(math.atan2(math.sin(theta+math.pi/2),math.cos(theta+math.pi/2)))
            if .37*math.pi < phi < .61*math.pi and front < .90:
                continue
            faces.append((i*cols+j,i*cols+(j+1)%cols,(i+1)*cols+(j+1)%cols,(i+1)*cols+j))
    meshpart(r,"shell",verts,faces,shell)
    vr,vc=10,32
    pv=[surface(.37*math.pi+i*(.24*math.pi)/vr,-math.pi/2-.91+j*1.82/vc,1.009) for i in range(vr+1) for j in range(vc+1)]
    pf=[(i*(vc+1)+j,i*(vc+1)+j+1,(i+1)*(vc+1)+j+1,(i+1)*(vc+1)+j) for i in range(vr) for j in range(vc)]
    meshpart(r,"visor",pv,pf,visor)
    for name,phi in (("visor_upper_rim",.37*math.pi),("visor_lower_rim",.61*math.pi)):
        points=[surface(phi,-math.pi/2-.93+j*1.86/40,1.018) for j in range(41)]
        curve_tube(r,name,points,.006,trim)
    for side,theta in (("left",-math.pi/2-.92),("right",-math.pi/2+.92)):
        points=[surface(.37*math.pi+j*.24*math.pi/16,theta,1.018) for j in range(17)]
        curve_tube(r,"visor_"+side+"_rim",points,.005,trim)
        # Flat pivot discs orient normal to the curved visor side.
        pos=surface(.49*math.pi,theta,1.022)
        cap=cylinder(r,"visor_"+side+"_pivot",.020,.010,pos,chrome,24)
        cap.rotation_euler=(math.pi/2,0,theta+math.pi/2)
    # Bottom gasket meets the supporting cushion exactly at root Z.
    pts=[(w*.30*math.cos(j*math.tau/64),d*.30*math.sin(j*math.tau/64),.007) for j in range(65)]
    curve_tube(r,"bottom_gasket",pts,.007,trim)
    # Chin vent and top vent distinguish the prop from a colored sphere.
    chin=box(r,"chin_vent",(.24*w,.016,.07*h),(0,-d*.43,.19*h),trim,.006)
    chin.rotation_euler[0]=-.16
    for i,x in enumerate((-.055*w,.055*w)):
        top=box(r,f"top_vent_{i}",(.055*w,.16*d,.012),(x,-.055*d,.965*h),trim,.003)
        top.rotation_euler[0]=-.20


def aim(obj,target):
    direction=Vector(target)-obj.location
    if direction.length < .00001:
        raise ValueError("Camera/light target equals its position")
    obj.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()


def apply_profile(profile,seed):
    s=bpy.context.scene
    if profile.get("device") != "CPU":
        raise ValueError("Only explicitly qualified CPU renderer is implemented")
    width,height,samples=profile["width"],profile["height"],profile["samples"]
    if not (64<=width<=4096 and 64<=height<=2160 and 1<=samples<=256):
        raise ValueError("Render resource limits exceeded")
    s.render.engine="CYCLES"
    s.cycles.device="CPU"
    s.cycles.samples=samples
    s.cycles.seed=seed
    s.cycles.use_animated_seed=False
    s.cycles.use_adaptive_sampling=False
    s.cycles.use_denoising=False
    s.cycles.max_bounces=8
    s.cycles.diffuse_bounces=4
    s.cycles.glossy_bounces=4
    s.cycles.transmission_bounces=4
    s.render.resolution_x=width
    s.render.resolution_y=height
    s.render.resolution_percentage=100
    s.render.pixel_aspect_x=s.render.pixel_aspect_y=1
    s.render.film_transparent=False
    s.render.image_settings.file_format="PNG"
    s.render.image_settings.color_mode="RGB"
    s.render.image_settings.color_depth="8"
    s.render.image_settings.compression=30
    s.render.use_file_extension=True
    s.view_settings.view_transform="AgX"
    s.view_settings.look="AgX - Medium High Contrast"
    s.view_settings.gamma=1
    s.display_settings.display_device="sRGB"
    s.frame_set(1)


def build(plan,profile):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene
    s["mf_scene_id"]=plan["scene_id"]
    s["mf_seed"]=plan["seed"]
    s["mf_builder_version"]="procedural-v1"
    s["mf_room_interior_bounds"]=list(plan["room"]["size_m"])
    s.unit_settings.system="METRIC"
    s.unit_settings.scale_length=1
    collection=bpy.data.collections.new("MovieFactory")
    collection["mf_id"]="collection_scene_01"
    s.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    room=root({"id":"room_01","kind":"room","position":[0,0,0],"rotation_z":0})
    rw,rd,rh=plan["room"]["size_m"]
    wall=material("room_wall_01",plan["room"]["wall_color_hex"],.88)
    floor=material("room_floor_01",plan["room"]["floor_color_hex"],.46)
    trim=material("room_baseboard_01","#E4DED1",.6)
    box(room,"floor",(rw,rd,.10),(0,0,-.05),floor,.0)
    box(room,"back_wall",(rw+.20,.10,rh),(0,rd/2+.05,rh/2),wall,.0)
    for side,x in (("left",-rw/2-.05),("right",rw/2+.05)):
        box(room,side+"_wall",(.10,rd,rh),(x,0,rh/2),wall,.0)
        box(room,side+"_baseboard",(.025,rd,.09),(math.copysign(rw/2-.0125,x),0,.045),trim,.002)
    box(room,"back_baseboard",(rw,.025,.09),(0,rd/2-.0125,.045),trim,.002)
    builders={"sofa":build_sofa,"coffee_table":build_table,"floor_lamp":build_lamp,"motorcycle_helmet":build_helmet}
    if len(plan["entities"]) != 4 or len(plan["cameras"]) != 3 or not 1 <= len(plan["lights"]) <= 6:
        raise ValueError("Plan exceeds bounded entity/camera/light vocabulary")
    for e in plan["entities"]:
        if e["kind"] not in builders:
            raise ValueError("Unsupported entity builder")
        builders[e["kind"]](e)
    for c in plan["cameras"]:
        data=bpy.data.cameras.new(c["id"]+"_data")
        obj=bpy.data.objects.new(c["id"],data)
        collection.objects.link(obj)
        identify(obj,c["id"],None,"camera")
        obj["mf_shot_id"]=c["shot_id"]
        obj.location=c["position"]
        aim(obj,c["target"])
        data.lens=c["lens_mm"]
        data.sensor_width=36
        data.sensor_fit="HORIZONTAL"
        data.clip_start=.01
        data.clip_end=100
        data.dof.use_dof=False
    for l in plan["lights"]:
        if l["type"] not in {"AREA","POINT"}:
            raise ValueError("Unsupported light type")
        data=bpy.data.lights.new(l["id"]+"_data",l["type"])
        obj=bpy.data.objects.new(l["id"],data)
        collection.objects.link(obj)
        identify(obj,l["id"],None,"light")
        obj.location=l["position"]
        aim(obj,l["target"])
        data.energy=l["energy_w"]
        data.color=color(l["color_hex"])[:3]
        if l["type"] == "AREA":
            data.shape="DISK"
            data.size=l["size_m"]
        else:
            data.shadow_soft_size=l["size_m"]
    world=bpy.data.worlds.new("world_01")
    world["mf_id"]="world_01"
    world.use_nodes=True
    world.node_tree.nodes["Background"].inputs["Color"].default_value=color("#D5E3FF")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value=plan["world_strength"]
    s.world=world
    apply_profile(profile,plan["seed"])
    s.view_settings.exposure=plan["exposure"]
    s.camera=bpy.data.objects[plan["cameras"][0]["id"]]
    bpy.context.view_layer.update()


def revise(operations):
    if len(operations) != 2:
        raise ValueError("Canonical revision requires exactly two operations")
    objects={o.get("mf_id"):o for o in bpy.context.scene.objects}
    initial_ids=set(objects)
    applied=[]
    seen=set()
    for operation in operations:
        op=operation["op"]
        if op in seen:
            raise ValueError("Duplicate operation")
        seen.add(op)
        if op=="translate_toward":
            if set(operation)!={"op","entity_id","target_entity_id","distance_m"} or operation["entity_id"]!="coffee_table_01" or operation["target_entity_id"]!="sofa_01":
                raise ValueError("Unsupported translation target or fields")
            if abs(operation["distance_m"]-.4)>.0000001:
                raise ValueError("Canonical translation must be 0.4 meters")
            table,sofa=objects["coffee_table_01"],objects["sofa_01"]
            origin=table.location.copy()
            direction=sofa.location-origin
            direction.z=0
            if direction.length<.001:
                raise ValueError("Cannot compute table direction")
            target=origin+direction.normalized()*.4
            table.location=target
            applied.append({"op":op,"entity_id":"coffee_table_01","parent_position":list(origin),"absolute_target":list(target)})
        elif op=="set_base_color":
            if set(operation)!={"op","entity_id","material_id","color_hex"} or operation["entity_id"]!="helmet_01" or operation["material_id"]!="helmet_shell_01":
                raise ValueError("Unsupported material target or fields")
            if operation["color_hex"].upper()!="#163D2A":
                raise ValueError("Canonical helmet target must be #163D2A")
            mat=bpy.data.materials.get("helmet_shell_01")
            if not mat or not mat.use_nodes:
                raise ValueError("Missing dedicated helmet shell material")
            users=[o for o in objects.values() if hasattr(o.data,"materials") and mat.name in o.data.materials]
            if not users or any(o.get("mf_entity")!="helmet_01" for o in users):
                raise ValueError("Helmet shell material is not private")
            mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value=color(operation["color_hex"])
            applied.append({"op":op,"material_id":"helmet_shell_01","base_color_linear":list(color(operation["color_hex"]))})
        else:
            raise ValueError("Unsupported revision operation")
    if initial_ids!={o.get("mf_id") for o in bpy.context.scene.objects}:
        raise RuntimeError("Revision changed object identity set")
    bpy.context.view_layer.update()
    return applied


PALETTE={"helmet_01":[255,0,0],"coffee_table_01":[0,255,0],"sofa_01":[0,0,255],
         "floor_lamp_01":[255,255,0],"room_01":[128,128,128]}


def render(native,out,profile,seed):
    shots=profile["shots"]
    if not shots or set(shots)-{"shot_A","shot_B","shot_C"}:
        raise ValueError("Unknown render shot")
    for folder in ("renders","masks"):
        (out/folder).mkdir(exist_ok=True)
    times={}
    artifacts=[]
    # Reload parent for each beauty/mask pass. Transient material overrides never
    # touch the saved native scene or leak into a later shot.
    for shot in shots:
        t=time.monotonic()
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        apply_profile(profile,seed)
        s=bpy.context.scene
        s.camera=next(o for o in s.objects if o.type=="CAMERA" and o.get("mf_shot_id")==shot)
        s.render.filepath=str(out/"renders"/(shot+".png"))
        bpy.ops.render.render(write_still=True)
        times[shot+"_beauty_seconds"]=time.monotonic()-t
        artifacts.append("renders/"+shot+".png")
        t=time.monotonic()
        maskmats={}
        for entity,rgb in PALETTE.items():
            mat=bpy.data.materials.new("__mask_"+entity)
            mat.use_nodes=True
            mat.node_tree.nodes.clear()
            emit=mat.node_tree.nodes.new("ShaderNodeEmission")
            emit.inputs["Color"].default_value=tuple(srgb_channel(c/255) for c in rgb)+(1,)
            emit.inputs["Strength"].default_value=1
            output=mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
            mat.node_tree.links.new(emit.outputs["Emission"],output.inputs["Surface"])
            maskmats[entity]=mat
        for obj in s.objects:
            if obj.type=="MESH":
                mat=maskmats[obj["mf_entity"]]
                obj.data.materials.clear()
                obj.data.materials.append(mat)
                for face in obj.data.polygons:
                    face.material_index=0
        s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0
        s.view_settings.view_transform="Standard"
        s.view_settings.look="None"
        s.view_settings.exposure=0
        s.view_settings.gamma=1
        s.cycles.samples=1
        s.cycles.max_bounces=0
        s.cycles.use_denoising=False
        s.render.filepath=str(out/"masks"/(shot+".png"))
        bpy.ops.render.render(write_still=True)
        times[shot+"_mask_seconds"]=time.monotonic()-t
        artifacts.append("masks/"+shot+".png")
    write_json(out/"mask-legend.json",{"schema_version":"1.0","encoding":"rgb8","entities":PALETTE,
        "background":[0,0,0],"method":"opaque emission Cycles CPU one-sample pass; edge antialiasing; stable entity colors"})
    return artifacts+["mask-legend.json"],times


def write_json(path,data):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
    temporary.replace(path)


def main():
    args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    parser=argparse.ArgumentParser()
    parser.add_argument("--job",required=True)
    parsed=parser.parse_args(args)
    job=json.loads(Path(parsed.job).read_text())
    out=Path(job["output_dir"])
    out.mkdir(parents=True,exist_ok=True)
    status={"ok":False,"mode":job["mode"],"artifacts":[],"timings":{}}
    start=time.monotonic()
    try:
        inspector=load_inspector()
        mode=job["mode"]
        profile=job["profile"]
        if mode=="build":
            build(job["plan"],profile)
        elif mode in {"revise","inspect","render"}:
            native=Path(job["parent_native"])
            if native.resolve()==(out/"scene.blend").resolve():
                raise ValueError("Parent native may never be overwritten")
            bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
            if mode=="revise":
                mutations=revise(job["operations"])
                write_json(out/"mutations.json",mutations)
                status["artifacts"].append("mutations.json")
        else:
            raise ValueError("Unknown worker mode")
        if mode in {"build","revise"}:
            bpy.context.preferences.filepaths.save_version=0
            bpy.ops.wm.save_as_mainfile(filepath=str(out/"scene.blend"),check_existing=False,compress=True)
            status["artifacts"].append("scene.blend")
        if mode in {"build","revise","inspect"}:
            state=inspector.snapshot()
            write_json(out/"snapshot.json",state)
            status["artifacts"].append("snapshot.json")
        if mode=="render":
            artifacts,times=render(Path(job["parent_native"]),out,profile,job["seed"])
            status["artifacts"].extend(artifacts)
            status["timings"].update(times)
        status["ok"]=True
    except Exception as exc:
        status["error"]=type(exc).__name__+": "+str(exc)
        traceback.print_exc()
        raise
    finally:
        status["timings"]["worker_total_seconds"]=time.monotonic()-start
        status["toolchain"]={"blender":bpy.app.version_string,"build_hash":bpy.app.build_hash.decode(),"python":sys.version.split()[0]}
        write_json(out/"worker-status.json",status)


if __name__=="__main__":
    main()
