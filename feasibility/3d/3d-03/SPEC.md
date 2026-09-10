# 3D-03 — Persistent humanoid character

## Question

Can Movie Factory ingest an independently authored rigged humanoid and compatible animation clips, assign stable semantic identities to its mesh, armature, bones, material, skins, and actions, preserve that state through native save/reopen, and apply a targeted performance and wardrobe revision without rebuilding or drifting protected state?

## Frozen source and revision

Use Kenney's CC0 **Animated Characters Protagonists** pack. Admit only the license, generic `characterMedium.fbx`, cyborg and skater female skins, and idle/run/jump animation FBXs recorded in `assets.json`.

The baseline uses the cyborg skin and idle action. The revision switches only the material image from the verified cyborg skin to the verified skater skin and assigns the verified run action in place of idle. The mesh, vertex weights, armature, bone hierarchy/rest transforms, entity transform, cameras, lights, world, render profile, unused source actions, and all other material fields remain protected.

## Trust boundary

- The controller reproduces a fresh seven-file staging directory from the exact official archive and verifies every path, size, and SHA-256 digest.
- Blender receives only absolute, digest-paired FBX/PNG paths. Import formats, entity count, clip names, skin roles, frame range, camera rig, lighting, and revision operations are allowlisted.
- FBX import runs with arbitrary script execution disabled and no credentials in the worker environment.
- Animation FBXs may contribute only compatible actions. Their temporary objects and data are removed after the action curves are copied and named.
- The model never emits or executes Python.

## Qualification sequence

1. Verify provenance and reproduce the seven admitted files.
2. Probe the model and three clips in isolated Blender processes; record object types, topology, armature/bone hierarchy, actions, curve counts, frame ranges, and texture requirements.
3. Import the model, normalize it to 1.75 m, ground it, and assign stable entity/mesh/armature/bone/material/action identities.
4. Import the idle, run, and jump actions without retaining their temporary scene objects.
5. Link and pack both verified skins. Assign cyborg plus idle for the baseline.
6. Save, reopen in a fresh process, and require an exact semantic snapshot.
7. Render wide, medium, and close views at frozen representative frames with entity masks.
8. Apply exactly two structured operations: `set_character_skin(cyborg→skater)` and `set_character_action(idle→run)`.
9. Save and reopen. Require the mesh, weights, rig, rest pose, bone IDs, unused action, cameras, lighting, world, and every unapproved field to remain unchanged.
10. Render the same views/frames, prepare Director comparisons, and replay the revision from the sealed package without provider calls.

## Gates

- **GREEN:** source/license identity, rig import, skin/action mapping, normalization, both save/reopen checks, deny-by-default revision checks, renders, Director review, and zero-provider replay all pass.
- **YELLOW:** machine evidence is sound but Director review is pending, or a documented importer normalization is necessary without losing the qualified semantics.
- **RED:** skeleton/action compatibility fails; mesh, weights, bone hierarchy/rest pose, cameras, or lighting drift; a texture remains external; temporary import objects survive; replay differs; or required evidence is missing.

## Claim boundary

GREEN qualifies this one source skeleton, its three compatible clips, the two frozen skins, and the two supported structured revision operations. It does not qualify arbitrary skeleton retargeting, rig generation, facial performance, lip sync, cloth/hair simulation, motion capture cleanup, nonlinear animation editing, or production character quality.
