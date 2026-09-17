# Movie Factory — SSD project handoff

Updated: 2026-09-16  
Workspace: `/Volumes/MovieFactorySSD/MovieUniverseFactory`  
Purpose: give a new Codex chat enough verified history and current state to
continue without reconstructing the project from conversation memory.

## Start here

1. Confirm `pwd` is `/Volumes/MovieFactorySSD/MovieUniverseFactory` and the
   volume is mounted at `/Volumes/MovieFactorySSD`.
2. Read the repository `AGENTS.md`; its instructions replace older copies.
3. Read this handoff, then use these current entry points as needed:
   - [Demonstrator 01 index](../../results/demonstrator-01/INDEX.md)
   - [Demonstrator learnings](../planning/DEMONSTRATOR_01_LEARNINGS.md)
   - [Roadmap](../planning/MOVIE_FACTORY_ROADMAP.md)
   - [Series 01 discovery](../planning/SERIES_01_DISCOVERY.md)
   - [Factory app and memory baseline](../planning/FACTORY_APP_AND_MEMORY_BASELINE.md)
   - [SSD migration record](SSD_MIGRATION_2026-09-16.md)
   - [Closed-3D S3 archive record](../../results/archive/CLOSED_3D_S3_PLAN.md)
4. Use this project's `.venv` for every outer Python command. Do not expose or
   copy `.env`, and never pass it to Blender.

## Current machine and repository state

- The 1 TB Samsung T7 was erased and reformatted as APFS under explicit
  Director approval. It has approximately 918 GiB free.
- The complete active project is on the SSD. It occupies about 13 GiB,
  including about 11 GiB under `runs/demonstrator-01` and 604 MiB under
  `.runtime/assets/demonstrator-01`.
- The SSD is not encrypted. Credentials remain on the internal disk at
  `/Users/adisharma/.config/movie-factory/.env` with mode `0600`; the SSD
  project `.env` is a symlink to it.
- `.venv` was rebuilt on the SSD from the repository's Python 3.12.11 runtime
  and `requirements.lock`. The package is installed editable from the SSD.
- Migration validation passed: Git object verification, content comparison,
  package/CLI resolution, **226 offline tests passed with 11 opt-in/native tests
  deselected**, and Blender 5.2.1 opened an active Demonstrator scene from the
  SSD with embedded scripts disabled. The scene emits pre-existing missing
  ear-bone dependency warnings.
- Trusted Demonstrator handlers now derive the repository root from
  `__file__`; they no longer execute against the old absolute project path.
  This repair is commit `c35fb87`.
- Migration portability commit: `c35fb87`. GitHub `main` was directly checked
  at `f05f0fa`; archival, accepted-camera, migration and handoff history after
  that commit remains local. No commits were pushed in this task.
- Existing uncommitted Director/planning work was preserved. Do not discard or
  overwrite it:
  - modified `README.md`
  - modified `docs/engineering-intelligence/README.md`
  - modified `docs/engineering-intelligence/events.json`
  - untracked `docs/planning/FACTORY_APP_AND_MEMORY_BASELINE.md`
  - untracked `docs/planning/MOVIE_FACTORY_ROADMAP.md`
  - untracked `docs/planning/SERIES_01_DISCOVERY.md`
  - untracked `docs/planning/SERIES_01_SIKH_FAMILY_OPTIONS.md`
  - untracked `.DS_Store` is incidental and not project evidence.

The active project now has a separate checksummed S3 recovery copy. The
20260917T021807Z snapshot contains 4,490 unique objects and 13,141,835,302
unique bytes. Exact remote inventory, manifest restoration, and a 104,734,964
byte streamed payload restore all passed. After that verification and explicit
authorization, the obsolete workspace at
`/Users/adisharma/projects/MovieUniverseFactory` was permanently removed. The
SSD workspace is the authoritative working copy. See the
[active-backup policy](ACTIVE_S3_BACKUP_POLICY.md) and
[verification receipt](../../results/backup/active-20260917T021807Z-verification.json).

## Experiment history and defensible claims

The long-running source conversation is “AI Movie Production System,” task
`6a82016c-3a88-83ea-a93b-b277f6526b97`. Repository evidence and this handoff
are authoritative for current status; conversation history is useful for
intent and Director wording, not as a replacement for manifests and reports.

| Experiment | Disposition | What it established | Main boundary |
| --- | --- | --- | --- |
| 3D-01 | YELLOW | Five persistent-scene/targeted-revision pairs passed structure, preservation, replay and Director review. | Revision API ratio was 0.9786; source binding was reconstructed after the live run. |
| 3D-01.1 | GREEN | Deterministic supported revisions with LLM escalation for ambiguity; five fresh pairs; median revision API ratio 0.5340. | No open-ended natural-language Blender control or autonomous cinematography claim. |
| 3D-02 | GREEN | Frozen external FBX/GLB import, normalization, material repair, packing, reopen and structured revision. | One qualified CC0 asset set, not arbitrary formats/assets or production rendering. |
| 3D-03 | YELLOW | Persistent character identity, rig/skin/action state and replay. | Full-motion addendum found severe early deformation, failed seams and no airborne jump; still review had been insufficient. |
| 3D-03.1 | GREEN, bounded | Fixed stale-parent-pose transfer for idle/run; separate deterministic authored jump; complete playback accepted. | Run scored 4/5 and read partly like fast walking. Jump is authored from reference poses, not a faithful complete source transfer. |
| 3D-04 | GREEN, bounded | One interval-local run-performance edit with protected outside state, boundary/contact checks, native negative controls and Director preference. | One admitted rig, action and interval; treadmill-relative support, not general world-planted locomotion. |
| 3D-05 | Closed YELLOW | Stationary sword reach, enclosed grasp, lift and hold eventually passed technical gates and minimum visual quality. | Both timing variants tied; grasp scored 4.5/5 and everything else 5/5. Timing preference was not demonstrated. No more iteration planned. |
| 3D-06A | Closed YELLOW | A small acknowledgement gesture passed its technical implementation checks. | Director saw little meaningful difference and stopped the line of work as low creative value. |

The closed experiment evidence from 3D-01 through 3D-06A was uploaded to the
private, versioned and encrypted-at-rest S3 bucket `movie-factory-archive` in
`ca-central-1`, prefix `movie-factory/history/closed-3d-v1/`. The archive holds
31,378 paths as 15,788 unique SHA-256 objects totaling 28.66 GiB. Exact remote
inventory and streamed restores passed. The conservative recurring storage
estimate is about $0.86/month; it is not a reconciled invoice. See the
[verification receipt](../../results/archive/closed-3d-v1-remote-verification.json).

Large local closed-3D runs/exports were then deleted under separate approval.
Two tiny frozen fixtures needed by the offline test contract were restored from
S3 into the SSD workspace and matched their recorded SHA-256 values. Preserve
the archive manifests; archived evidence links will require restore rather than
being immediately available locally.

## Engineering and process learnings

- The Blender CLI launches work; reviewed trusted repository handlers perform
  validated structured operations through `bpy`. Arbitrary generated Python,
  code strings and embedded asset scripts remain prohibited.
- Full playback and dense fractional-frame measurements are required for
  motion. Selected stills missed severe defects in 3D-03.
- Motion design precedes implementation. Use the repository motion brief,
  define coordinated body participation and constraint compatibility, inspect
  inexpensive full motion, then freeze one scored campaign.
- Correct anchors or attachment transforms do not prove a believable grasp.
  Grasp validation needs fit, enclosure, contact coverage, penetration,
  ownership and multiple views.
- Validate asset suitability before tuning motion. The original 3D-05 sword
  handle was physically incompatible with the hand after normalization.
- A real negative control must corrupt Blender state and fail for a reason
  absent from the positive case. JSON-number mutation alone is insufficient.
- Use the default 20-net-minute diagnostic checkpoint, no more than three
  variants per hypothesis, and a 60-net-minute overall checkpoint unless a
  task has another explicit envelope. Run one planned full qualification suite
  after targeted development checks rather than duplicating every expensive
  control suite.
- The 3D-05 closure took about 2.5 hours and excessive Codex usage. Coupled
  defects, serial tuning, late measurement changes, duplicated full validation,
  storage work in the critical path and excessive polling/status narration all
  contributed. Paid API cost of $0 did not mean low engineering cost.
- Model routing evidence is observational, not a benchmark. Astra helped
  diagnose stale-parent evaluation in 3D-03.1; Sol implemented the bounded
  correction. Several Sol-era 3D-05 grasp attempts failed visually; Astra-led
  anatomy and coordinated-motion work improved them, but fixture changes,
  stronger controls and Director feedback changed at the same time. In the
  Demonstrator, Astra and Sol proposals both required supervisor correction.
  Consult `docs/engineering-intelligence/events.json`; do not claim model
  superiority from these episodes.
- The Director wants natural next steps anticipated and bundled, rather than a
  new approval every thirty minutes. For a complex authorized experiment,
  state expected process, cost, native-time, storage and external-action
  approvals up front, then work autonomously within them. Stop only at an
  agreed gate, exhausted ceiling, safety boundary or required creative review.

## Demonstrator 01: The Courier

The Director accepted **The Courier**, a 24-second development rough cut at
960×540, 24 fps and 576 frames, with provisional original hoofbeats, wind and
signal-bell sound. It uses one modified free horse/rider fixture, coordinated
authored gallop, a continuous 12 m/s world path, four camera shots, procedural
meadow scenery, bounded tail treatment and trailing dust. The user said: “I
think this is great. pass.”

The sequence contains an aerial-to-front opening, a lateral full-pace gallop,
a flag/head-turn signal beat and a departure shot. Material-point hoof travel,
floor penetration, rein gap, encoded timeline, selected scene preservation and
one independent frame replay passed. A legacy changing-centroid screen remains
failed and is retained as a diagnostic. The environment, dust, hair and sound
remain development quality; acceptance is not a photorealism claim.

Measured Demonstrator paid-model ledger: 17 requests and $3.736270001
calculated cumulative cost, including failures/retries; rough-cut increment
$0.513970. No unresolved reservation remained in that snapshot. It is not a
provider invoice and does not include Codex subscription use or complete human
engineering cost. The accepted cut used 81.4 native process-minutes within a
102.3-minute authorization-to-finalization envelope; those overlap and must
not be added.

Blender is **ADOPTED for the demonstrated persistent production backbone**.
That is separate from general reuse. The first parameter-only held-out reuse
attempt was not demonstrated. A later five-second continuous camera move was
accepted by the Director, but it required camera-code changes and is closed
YELLOW as **code-assisted reuse**. Do not relabel it as parameter-only success.

The accepted film, native scenes and active assets remain in the SSD project.
They have not yet received the same verified off-machine archive treatment as
the closed 3D experiments.

## Captured production request, not current authorization

The Director described a future 24–30-second horse sequence with:

- a higher centered-behind camera descending smoothly to a dynamic side view
  and then an offset frontal follow;
- racing-speed gallop and a more aggressive, coordinated rider stance;
- larger visible dust and higher-fidelity grass/terrain;
- a physically readable deceleration, halt, rear, settle and rider dismount.

The full brief is [NEXT_PRODUCTION_EXPERIMENT_BRIEF.md](../planning/NEXT_PRODUCTION_EXPERIMENT_BRIEF.md).
It is deliberately marked **captured, not authorized**. A previously proposed
ceiling was 8 active engineering hours, 12 native process-hours and $30 paid
API, with no purchases/cloud render/paid media. Those figures are historical
proposals, not current authority or guaranteed completion. Before any such
motion work, complete the motion brief and prove racing posture, deceleration,
rear and dismount in inexpensive full playback. Do not hide defects with dust
or camera cuts.

The newer roadmap says this horse sequence should proceed only if it serves the
selected series/release. Do not automatically make it the next task solely
because storage is now available.

## Series and product direction

The working Series 01 seed is provisionally **The Martials**: a Jatt Sikh, a
Gurkha and a strong Muslim female lead—possibly Pashtun—undertake unofficial
missions for a British officer on the British India/Afghan frontier roughly
150 years ago. Colonial martial-race ideology, conflicted service, adventure,
trust and internal disagreement are central. Exact title, year, institutional
mechanism and the female lead's background remain open and require research.

Accepted creative direction so far:

- The team already works together at the opening, but trust is incomplete.
- Episode one should show competence, chemistry and friction before an order
  or discovery exposes a deeper divide.
- The Sikh protagonist has a father and younger sister. Names, ages, mother and
  detailed histories remain unset.
- The father helped steer his son into British service; their relationship is
  based on affection, shared responsibility, pride and accommodation rather
  than a simple father-condemns-collaborator conflict.
- Trailer development is paused at the Director's request because the Director
  plans to bring their own ideas. Do not force a trailer treatment or release
  length decision during current character work.

The roadmap and character documents are still working drafts unless they mark
a Director decision explicitly. Do not promote proposals to canon.

The product goal is a standalone Movie Factory application with selectable
API-billed conversational models and project-owned durable knowledge. It should
own conversations, canon/drafts, approvals, jobs, artifact references and
budgets so normal production does not depend on a signed-in Codex session.
Codex remains a development tool. The proposed baseline is a private,
single-user local application that reuses existing controller/worker code; it
is not yet an authorized implementation project.

The roadmap proposes three integrated readiness checks rather than another
long sequence of isolated 3D experiments: portable memory/conversation, one
actual-series visual/performance proof, and app-to-production repeatability.
The immediate creative task can continue character motives and relationships
without expensive rendering.

## Budget and authorization policy

- Use Codex/subscription capacity for engineering. Use paid model API calls
  only when they are part of an explicitly authorized experiment or evaluation
  and record them in the persistent campaign ledger before dispatch.
- Previous Demonstrator or experiment allowances do not roll into future work.
- Asset purchases, paid media generation, cloud rendering, new S3 transfers,
  and public/native-asset uploads require separate explicit approval.
- No current authorization exists for the racing/rear/dismount experiment,
  the standalone app implementation, or a new production campaign. The
  completed 20260917T021807Z S3 backup and old-workspace deletion were separately
  and explicitly authorized; that authorization does not roll forward.
- Routine local inspection, tests, reversible code fixes and planning do not
  require repeated permission when they are within an authorized task.

## Recommended first actions in the new SSD chat

1. Verify the task's project path is the SSD path and run `git status` without
   modifying the preserved working files.
2. Read the current `AGENTS.md` and this handoff.
3. Confirm the latest active-backup receipt remains available; do not repeat
   the completed local-workspace deletion.
4. Ask the Director for **one** current priority:
   - continue Series 01 character/concept development;
   - freeze the portable-memory/standalone-app work package; or
   - authorize a production experiment tied to the intended release.
5. Once that priority is chosen, produce one bounded work package with an
   explicit endpoint, aggregate approval needs and the next Director review
   gate. Do not restart 3D-01–06, reopen 3D-05 or resume 3D-06A.

## Ready-to-send opening instruction

> Work only from `/Volumes/MovieFactorySSD/MovieUniverseFactory`. Read
> `AGENTS.md` and `docs/operations/SSD_PROJECT_HANDOFF.md`, then verify the SSD
> mount, Git status and project-local `.venv` without printing `.env`. Preserve
> all existing uncommitted planning work. Summarize the current safe operating
> state and recommend one concrete next work package based on the roadmap and
> Series 01 decisions. The obsolete internal workspace has already been removed
> after the active S3 backup passed restore verification; do not recreate or
> repeat that migration step. Do not start paid calls, purchases, cloud
> rendering, public uploads or the racing/rear/dismount experiment without new
> explicit authorization.
