# Decision 0001 — Blender 5.2.1 with structured operations

Use the installed Blender 5.2.1 LTS build `9e2066aef7ef` as the first measured cohort. The trusted adapter translates a strict scene plan and two allowed revision operations into `bpy` calls. The model never supplies executable Python.

This qualifies semantic planning over the bounded structured interface. It does not qualify arbitrary LLM-generated Blender code. Blender runs in a credential-stripped child environment; because that is not an OS sandbox, arbitrary code remains out of scope.
