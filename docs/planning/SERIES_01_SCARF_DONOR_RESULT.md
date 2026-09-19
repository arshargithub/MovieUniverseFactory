# Scarf scan: acquisition and bounded fit result

## Authorized reconstruction and cheek/jaw diagnostic — latest

Director approved one capped 20-minute reconstruction diagnostic and explicitly requested investigation/correction of apparent cheek/jaw roundness. This authorizes a new **candidate**, not replacement of the accepted original. Director described the hair as a good close match; ambiguity retained: the latest scarf renders contain painted scalp hair, not the downloaded hair mesh. No blanket approval of the occluding donor fringe is inferred.

Three reconstruction renders retained under `scarf-reconstruct-01/` through `scarf-reconstruct-03/`. The front neck bib was opened, three shaped shoulder fold strips added, and 02/03 tested smoothed scan boundaries and an inner lining. **Garment result rejected:** the open framing exposes the neck/jaw, but cut gaps, overlapping crown surfaces and artificial layered fold strips remain. Do not promote these derivatives or call the shawl fixed. Further variants on this cut-and-patch approach are not justified by the evidence; garment needs coherent topology/modeling rather than additional rough masks.

The matched `framing-only-*` images retain original face geometry; `jaw-candidate-*` add one reversible `MF_lower_cheek_definition_candidate` shape key. 01/02's localized cheek displacement caused an unwanted crease and is rejected. 03 uses reduced smooth sinusoidal feathering (maximum Y adjustment .030 model units, lateral factor .025), leaving eyes, nose, lips, upper face and jaw-bottom region protected by the analytic mask. Front and left-angle images inspected: smaller lower-cheek fullness change with less creasing; not Director-approved likeness. A visible crease remains a visual-review concern, not a test-suite pass. Opening the neck region is a larger visual change than this small shape adjustment; comparison does not establish geometry as the sole cause of perceived roundness.

03 working diagnostic: `.runtime/art-direction/series01-facebuilder-trial-01/scarf-reconstruct-03/head-reconstruction-candidate.blend`. Base vertices retained in Basis, original head file hash unchanged; effective evaluated face is deliberately different while shape key is enabled. Original geometry digest equivalence must not be claimed for this candidate's evaluated mesh. No paid calls, no new hair integration, no blink/rig work. This is a diagnostic with failed cloth work and provisional facial work, not completed delivery. Native jobs succeeded; input/mask tests do not qualify aesthetics. Local implementation/documentation commits only.

2026-09-19. Director supplied the GLB and attribution. Original preserved at `.runtime/assets/series01-dressing-source/scarf-original.glb`, SHA-256 `b34727d6d989d33cef5fb77c84bb34194bf8045e4d01ac4a4d7c48c93319e7c7`. Download original remains untouched. Embedded metadata agrees with Director credit:

“Balaclava - scarf as a hood - 3D scan” by Tijerín Art Studio, [source](https://skfb.ly/oP7Yu), [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/).

Derivatives by MovieUniverseFactory: fit transforms, lower-neck stretching, tail trim in 02/03 and plain indigo replacement material. Preserve this attribution with any derivative distribution. No endorsement implied.

## Verified technical facts

One imported mesh, 11,670 vertices / 22,574 triangles in the original import, two embedded images, no external image/buffer URIs. Original shader uses the color texture as emission as well as base color. The diagnostic deliberately replaces it with plain rough indigo to judge geometric folds without plaid or emissive shading. No imported scripts executed; fixed hash-pinned GLB through reviewed/tested handler. Head geometry/primary UV/shape keys/transforms are preserved. No watertightness, interior-thickness, retopology, collision or deformation qualification yet.

Three inexpensive variants retained under `.runtime/art-direction/series01-facebuilder-trial-01/scarf-fit-01/` through `scarf-fit-03/`, each with native scene, front/±30° renders and result metadata. 01 is uniform fit; 02 widens and moves back and lowers wrap; 03 lowers/widens further. 02 was rendered before code's tail-trim cutoff changed from -1.95 to -2.4 for 03, so final code is not an exact replay of 02. All original inputs preserved. Tail trim is a rough open boundary, not finished topology.

## Visual disposition

**YELLOW donor feasibility, not accepted dressing.** Front and both angles of 03 inspected. Crown/back geometry and some folds are useful, but closed neck wrap remains enclosing, ears sit awkwardly against side cloth, rear scalp coverage still needs hair, and trimmed hem is ragged. It is not the approved portrait's open, broad shoulder shawl. Texture removal makes folds less visually rich than the screenshot. Do not solve that by restoring plaid or declaring illustrated styling achieved.

Three-variant fit checkpoint reached. Simple fit transforms are insufficient. Recommended scope reassessment: use only the hood/back portion as donor geometry and reconstruct the open front and shoulder wrap, retaining approved face/costume intent. This is more substantial garment modeling, not another scaling tweak. Alternative is continue searching for a closer complete shawl donor. Do not silently accept a more enclosing costume or spend indefinitely on deformation variants.

31 previous tests plus 4 scarf input-rejection tests; native fit jobs exited successfully. Input rejection tests do not certify visual or geometric fitness. No paid calls, remote push or new software. Planning counter unchanged; experiment/character gates remain open.
