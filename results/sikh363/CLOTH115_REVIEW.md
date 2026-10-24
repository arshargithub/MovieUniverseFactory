# Fixed causal isolation after mass control failed

114 failed stationary warmup249, maximum strain1.82948, pins exact. The corrected
vertex-mass interpretation is retained, but mass was not the sole cause. No cache
or native from114 is usable. Preserve full handler version and captured failure.

115 is a diagnostic suite, not a production candidate: same source40 moving pole,
mesh/ties/settings, sequential230..418, mass.001 and unchanged guards.
A gravity-only has wind0 and all collisions off.
B breeze has wind3 and all collisions off.
C collision has wind0 and pole/self collisions on.
Each fixed case saves either cache/data or full first-failure mesh/rest/goals.
No production flag added by these controls, no automatic artistic result.
This separates basic mesh/goal integration, external force and collision response.
If all fail, investigate solver inputs/shape goals rather than further stiffness.
If C alone fails, isolate pole versus self collision before choosing repair.
Only bounded internal fixed configurations, never user/code/string/path recipes.
