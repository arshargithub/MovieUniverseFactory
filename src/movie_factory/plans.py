from __future__ import annotations

import copy


BASE_PLAN = {
    "schema_version":"1.0","scene_id":"apartment_living_room_01","seed":101,
    "room":{"size_m":[5.0,4.0,2.8],"wall_color_hex":"#C8BBAA","floor_color_hex":"#5A4030"},
    "entities":[
        {"id":"sofa_01","kind":"sofa","position":[0.0,0.85,0.0],"rotation_z":0.0,"dimensions":[2.3,0.9,0.9],"color_hex":"#536878","roughness":0.75},
        {"id":"coffee_table_01","kind":"coffee_table","position":[0.0,-0.65,0.0],"rotation_z":0.0,"dimensions":[1.25,0.65,0.42],"color_hex":"#6F4428","roughness":0.42},
        {"id":"floor_lamp_01","kind":"floor_lamp","position":[-1.75,0.75,0.0],"rotation_z":0.0,"dimensions":[0.5,0.5,1.75],"color_hex":"#D5B26F","roughness":0.35},
        {"id":"helmet_01","kind":"motorcycle_helmet","position":[0.55,0.78,0.486],"rotation_z":-0.25,"dimensions":[0.34,0.38,0.30],"color_hex":"#C62828","roughness":0.32}
    ],
    "cameras":[
        {"id":"camera_A","shot_id":"shot_A","position":[4.2,-5.6,3.2],"target":[0.0,0.0,0.8],"lens_mm":34},
        {"id":"camera_B","shot_id":"shot_B","position":[2.8,-3.6,1.8],"target":[0.15,0.15,0.72],"lens_mm":48},
        {"id":"camera_C","shot_id":"shot_C","position":[2.05,-1.7,1.55],"target":[0.55,0.78,0.77],"lens_mm":78}
    ],
    "lights":[
        {"id":"key_01","type":"AREA","position":[-2.0,-1.5,2.45],"target":[0.0,0.1,0.7],"color_hex":"#CFE4FF","energy_w":750,"size_m":2.0},
        {"id":"fill_01","type":"AREA","position":[2.0,-0.2,1.75],"target":[0.2,0.3,0.7],"color_hex":"#FFD5A3","energy_w":350,"size_m":1.2}
    ],
    "world_strength":0.16,"exposure":0.1
}


def fixture_plan(seed: int = 101) -> dict:
    plan = copy.deepcopy(BASE_PLAN)
    plan["seed"] = seed
    return plan


def canonical_revision() -> dict:
    return {"operations":[
        {"op":"translate_toward","entity_id":"coffee_table_01","target_entity_id":"sofa_01","distance_m":0.4},
        {"op":"set_base_color","entity_id":"helmet_01","material_id":"helmet_shell_01","color_hex":"#163D2A"}
    ]}
