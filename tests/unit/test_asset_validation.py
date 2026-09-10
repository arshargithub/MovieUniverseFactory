from copy import deepcopy

from movie_factory.validators.assets import validate_external_revision


def fixture():
    objects = {}
    entities = {}
    for entity_id in ("courtyard_01", "motorcycle_01", "sword_01"):
        objects[entity_id] = {"location":[0,0,0],"rotation_euler":[0,0,0],"matrix_local":[],"matrix_world":[],"bounds_world":None,"dimensions":[0,0,0],"geometry_hash":None}
        part = entity_id + "_part"
        objects[part] = {"location":[0,0,0],"rotation_euler":[0,0,0],"matrix_local":[],"matrix_world":[],"bounds_world":{"min":[0,0,0],"max":[1,1,1]},"dimensions":[1,1,1],"geometry_hash":"x"}
        entities[entity_id] = {"root_id":entity_id,"object_ids":[entity_id,part],"position":[0,0,0],"rotation_euler":[0,0,0],"bounds_world":{"min":[0,0,0],"max":[1,1,1]}}
    return {"scene_id":"x","objects":objects,"entities":entities,"materials":{},"cameras":{},"lights":{},"world":{},"render":{},"external_files":[],"unsupported":[]}


OPS = [{"op":"translate_entity","entity_id":"motorcycle_01","delta_m":[0.6,0,0]}, {"op":"rotate_entity_z","entity_id":"sword_01","degrees":25}]


def test_revision_accepts_only_root_world_changes():
    before=fixture(); after=deepcopy(before)
    after["objects"]["motorcycle_01"]["location"][0]=.6
    after["objects"]["sword_01"]["rotation_euler"][2]=0.436332313
    assert validate_external_revision(before,after,OPS)["passed"]


def test_revision_rejects_geometry_change():
    before=fixture(); after=deepcopy(before)
    after["objects"]["motorcycle_01"]["location"][0]=.6
    after["objects"]["sword_01"]["rotation_euler"][2]=0.436332313
    after["objects"]["motorcycle_01_part"]["geometry_hash"]="changed"
    assert not validate_external_revision(before,after,OPS)["passed"]
