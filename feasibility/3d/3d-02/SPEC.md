# 3D-02 — External/generated asset persistence

## Question

Can Movie Factory acquire independently authored motorcycle, sword, and environment assets; verify provenance; import and normalize their scale, axes, origins, materials, and hierarchy; assign stable semantic identities; save and reopen the native scene; and apply a targeted revision without losing or silently changing protected asset state?

## Frozen asset set

- Textured low-poly motorcycle FBX by Esteban Lopez, distributed as CC0 through OpenGameArt.
- Textured sword GLB from Kenney Mini Dungeon, CC0.
- Modular Castle Kit GLBs from Kenney, CC0, assembled as a small courtyard environment.

`assets.json` records official source pages, direct acquisition URLs, licenses, original archive hashes, the only admitted archive members, and each selected member hash. Raw downloads and staged files remain under the ignored project `.runtime/` directory. Evidence exports include the admitted source files and provenance record.

## Trust boundary

The controller verifies the manifest, archive digests, member paths, member sizes, and member hashes before writing a fresh staging directory. It rejects links, traversal, absolute paths, duplicates, unlisted members, oversized files, and existing destinations. Blender receives only absolute staged paths paired with exact SHA-256 digests and an allowlisted `fbx` or `glb` format. Blender runs with factory settings, auto-execution disabled, and the existing credential-free environment.

## Qualification sequence

1. Reproduce the 20-file staged set from the three frozen source archives.
2. Probe each source in a fresh Blender process and record raw topology, dimensions, materials, and images.
3. Build a courtyard scene from the admitted external files only.
4. Normalize the motorcycle to a 2.4 m longest dimension and the sword to a 1.0 m longest dimension; ground the motorcycle, support the sword on an imported stone plinth, and preserve uniform scaling.
5. Assemble the modular environment at recorded metre-scale transforms.
6. Relink the motorcycle PBR textures, pack every texture into the `.blend`, assign stable entity/part/material IDs, and record source hashes as custom properties.
7. Save, reopen in a fresh process, and require exact semantic snapshot equality.
8. Render three frozen views and per-entity masks.
9. Apply exactly two structured revisions: translate only the motorcycle root by 0.6 m on X and rotate only the sword root by 25 degrees around Z.
10. Save and reopen again. Require unchanged identities, topology, materials, packed images, cameras, lights, environment transforms, and all non-authorized state.
11. Render the revised views and prepare Director comparison evidence.
12. Replay the revision from the sealed package without a provider call.

## Gates

- **GREEN:** all three sources have verified CC0 provenance and byte identity; every import/normalization/reopen/revision/replay check passes; no texture remains unpacked; the combined scene renders; Director accepts the result; acquisition and repair time/cost are recorded.
- **YELLOW:** technically reproducible but Director review is pending, a material requires a documented lossy repair, or one source has license/provenance evidence that is clear but not bundled durably.
- **RED:** source identity/license cannot be established, import fails, scale/origin is materially wrong, topology or material state drifts, an unapproved entity changes, a texture remains externally dependent, replay fails, or required evidence is missing.

## Claim boundary

GREEN will qualify this frozen FBX/GLB asset set and the recorded normalization/revision vocabulary. It will not establish arbitrary-format ingestion, automatic rigging, animation retargeting, topology repair, photoreal production quality, or unrestricted model control of Blender.
