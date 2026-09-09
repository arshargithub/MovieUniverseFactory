# Later Blender → Unreal complement

Import one qualified Blender scene into a pinned Unreal Editor project. Preserve stable IDs through an explicit import registry and assign ownership: Blender owns source geometry/material intent; Unreal may own level staging, Sequencer cameras and render configuration. Test a Blender-side table/color revision and reimport without overwriting Unreal-owned shot state.

Measure import/reimport time, mapping failures, material and light changes, preview latency, final render time, LLM/API cost and Director quality. Qualify Editor Python and Movie Render Queue on the actual Mac. This is a complement experiment; packaged-runtime Python and cross-engine pixel equality are out of scope.
