# Pashtun sequence production audit and improvement baseline

## Scope and method

Director250 requests a review of every conversation input and production pass from the first visual baseline images through the current finishing work. The purpose is to distinguish necessary creative direction from preventable technical feedback and unnecessary handovers, then measure whether subsequent sequences reach the same high quality bar more efficiently.

The audit uses the exact local task history, existing source-bound pass records and operating ledger. It excludes unrelated project conversations and earlier generic Blender experiments from the principal character-to-sequence baseline; those may be linked dependencies rather than charged as new sequence work. The precise starting exchange and endpoint will be identified from the history. Shared series look-development and Pashtun-specific production will be reported separately where evidence permits. The current fist/20-second delivery is still in progress; any interim total must name its cutoff.

Review each user input with the preceding assistant handoff and relevant following outcome. Classify legitimate creative discovery/selection, necessary authority/logistics, predictable escaped defect, repeated failed correction, unnecessary technical handover, process clarification and unrelated work. Mixed inputs retain multiple labels; count unique inputs separately from individual issues. A short “go ahead” is not automatically wasteful: inspect whether it followed a real choice or an avoidable stop. Preserve uncertainty and do not invent a counterfactual amount of time saved.

Time reconstruction will reconcile actual task boundaries, continuing jobs and explicit waits. Exclude Director/next-prompt idle gaps unless a recorded job continued. Report interval unions and overlaps, not summed concurrent durations. Distinguish task-active wall time, tool/native-job occupancy, render-loop time and human review time. Native jobs include build/verification and are not automatically pure rendering; unrecorded early periods remain unknown. No estimates based on calendar days or token counts. Subscription charges and engineering token totals are outside this requested time baseline unless complete scoped evidence can support them without additional investigation.

Execution path: retain a sanitized message/timing extract with stable source offsets; read all relevant user and assistant handoffs; reconcile stage boundaries with project records; build a traceable classification ledger; compute deduplicated timing/count metrics; test interval arithmetic and coverage; publish findings and a repeatable next-sequence scorecard. The audit must identify failures of the agent's judgment as well as missing process, and must not turn legitimate Director creativity into waste. Retrospective classifications are agent judgments, not independent ground truth.

Current implementation uses a local parser that copies no reasoning, tool arguments/results, image payloads or credential files. It records only the exact task's messages, lifecycle/tool timing metadata and source fingerprint. No paid calls, upload, new service or new production is authorized. Rendering proceeds separately; overlapping audit work will not be added again to the current task's total time.

## Findings and baseline — snapshot at exchange250

The largest recurring failure was **not missing instructions**. It was admitting a candidate after relative improvement without establishing that it met the already known screen requirement. The Director repeatedly supplied the failure-seeking visual review, technical coordination and continuation ownership that the agent should have supplied. Better retrieval helps with forgotten requirements; it cannot validate a fist, cloth route, performance or mix merely by retrieving the correct rule.

This is a retrospective process audit, not an independent artistic assessment or a declaration that the current20s finishing work is closed. All292 recorded input records in scope were classified; one is a product-generated realtime transcript tail, leaving **291 human Director inputs**. The source-indexed [case ledger](PASHTUN_PRODUCTION_AUDIT250_CASES.json) preserves message/turn IDs, timestamps, source byte offsets, excerpts, stage, classifications, rationale and handoff links. The [portable metrics](PASHTUN_PRODUCTION_AUDIT250_METRICS.json) preserve the numerical baseline and qualifications. Case numbers below are audit IDs, **not** planning-exchange numbers.

### Counts

| Measure | Historical baseline | Meaning / limitation |
|---|---:|---|
| Human Director inputs | **291** | Includes creative choices, approvals, corrections, logistics, explanations and this request; not291 formal reviews |
| Recorded execution turns | **266** |263 completed,2 interrupted,1 still open at cutoff; not identical to user-message count |
| Assistant final messages | **260** | Includes answers and technical handovers as well as review deliveries |
| Inputs containing a preventable defect or missed requirement | **93** |31.96% of inputs; mixed creative/defect messages count once; not93 unique defects or93 false visual passes |
| Inputs repeating a correction or identifying its adjacent regression | **58** | Subset of the93;19.93% of all human inputs |
| Avoidable handovers | **44** |44 distinct prior final messages;30 high-confidence,14 medium-confidence retrospective judgments;16.92% of260 finals |
| Inputs requiring process correction | **85** | Ownership, strategy, review discipline or momentum; overlaps other categories |
| Review-presentation corrections | **16** | Comparable views, size, navigation, missing render or unclear evidence |
| Inputs carrying genuine creative direction | **123** | Not waste; includes mixed messages |
| Inputs involving real authority | **39** | Scope, spending, installation or material creative choice; not all are pure approval-only messages |

Labels overlap and must not be added. A brief “go ahead” is not itself evidence of waste. An intermediate comment is not automatically a rejection of a completed handoff. Earlier bounded-budget questions are judged against the authority then in force, not retroactively against the later no-arbitrary-time-limit rule. Fourteen uncertain handover judgments remain explicitly medium confidence; the defensible strict count is30, with44 the broader estimate. No counterfactual hours-saved figure is supported.

### How long did it take?

Scope starts with the first ensemble/base-image authorization on **September17,2026 at19:23 Toronto time**, and stops at this audit request on **October13 at13:19**. The present final render and the audit after that point are excluded from the historical snapshot. Earlier generic Blender experiments and pre-image story development are excluded. Shared look-development, authoring setup, knowledge/process work and sound discovery within this production conversation are included; this is not just render or animation labor.

| Time measure | Result | Interpretation |
|---|---:|---|
| Calendar span |25.75days | Context only; **not** production time |
| Reported completed-task runtime |**141.8h** | Sum of task runtime metadata, excluding gaps between turns |
| Current open task, observed to cutoff |**3.1h** | Censored elapsed interval, not a completed-task runtime |
| Practical recorded-runtime baseline |**about145h** |141.8+3.1; useful provisional baseline, **not exact net effort** |
| Task start/end timestamp union |149.9h | Includes tools, renders and unexplained in-turn stalls |
| Task OR recorded native-job union |150.8h | Adds0.9h of recorded native work continuing outside task intervals; does not double-count concurrency |
| Time outside both of those observed intervals |467.1h | Excluded; includes between-prompt/Director idle and other unobserved time, not all positively identified as Director waiting |
| Native Blender-job occupancy, interval union |**87.9h** | Construction, simulation, rendering and validation; part of the preceding totals, **not additional** |
| Native-job process-duration sum |89.3h | Different from87.9h because processes can overlap; not CPU-core hours |
| Recovered render/frame-loop timings |**19.9h across4,066 frames** | Partial instrumented subset only; not whole-history render time or an additional cost |

**The exact net number requested is not recoverable from the old records.** Nine task records disagree by more than five seconds between their start/end timestamps and reported runtime, accounting for roughly five hours of discrepancy. Some retrospective wait intervals overlap actual work and explicitly disclose capture gaps. Subtracting all of them would erase real work; treating all timestamp span as work would count unexplained stalls. The≈145h runtime baseline and150.8h observed envelope are two measured views, not certified lower/upper bounds on labor. Director active reviewing and off-platform Suno exploration are also unmeasured.

Waiting for a render is different from waiting for the Director: it remains a production dependency, but must be reported separately from active agent effort. Existing job occupancy cannot tell us how much of each render was critical-path waiting versus overlapped useful work. Outside native jobs, observed task occupancy is62.9h, but that includes API/I/O waits, tests, planning and other tasks; it is **not** a clean measure of agent reasoning time.

Starting only with the first individual Pashtun portrait on September18 at16:26 gives **276 human inputs,251 execution turns,245 finals,140.8h completed-task runtime plus3.1h open**, with the same native-job total. This alternative prevents the shared initial visual-language selection from being silently charged entirely to her. Neither total is a prediction for the Sikh or Gurkha: much of this work established reusable foundations, while their distinctive production risks remain unproved.

### Recorded engineering tokens — now measurable, not a price estimate

The exact local session also contains per-response usage records. Within the same broad first-image-to-audit interval, **14,383 distinct response records across263 turn IDs** report:

| Token measure | Recorded count | Interpretation |
|---|---:|---|
| Input tokens |2,374,033,902 | Includes repeated cached context; not unique content |
| Cached input subset |2,326,836,608 |98.01% of input; already included above |
| Uncached input |**47,197,294** | Input minus cached subset |
| Output tokens |**9,426,226** | Includes the reasoning subset below |
| Reasoning output subset |3,675,334 | Already included in output; do not add again |
| Total recorded throughput |2,383,460,128 | Input plus output; not2.38billion newly written tokens |

The sum of per-response usage matches the difference in the session's cumulative thread counters exactly. There are zero duplicate response IDs and no malformed/inconsistent selected usage records. Cumulative turn/thread totals are **not** summed again. Records cover emitted Codex usage, not guaranteed unreported failed calls or separate image/video/audio provider consumption. Model responses are internal processing steps, not14,383 Director conversation turns.

This is a useful engineering baseline, **not a dollar charge, subscription-quota percentage, or equivalent API invoice**. No pricing conversion is justified without the actual model/routing, cache/pricing and billing terms. The new finding supersedes the earlier assumption that all engineering token counts were unavailable; billed/allocated cost remains unknown. Preserve the detailed usage metadata locally and the aggregate in the portable metrics.

The practical efficiency lever is to reduce failed reasoning/implementation loops and redundant context/tool interactions while retaining quality: use focused task packets, avoid repeated full-source scans after an adequate capture, reuse unchanged picture for editorial/audio variants, and prefer job-completion handling over frequent model-driven polling where the runtime supports it. The records do not quantify how much of the14,383 responses was avoidable, so no token-savings forecast is asserted.

### Where the work and interventions accumulated

Hours below are **chronological task-timestamp occupancy**, not pure labor, render cost, exact net time or waste. Stage boundaries follow the conversation and can include cross-disciplinary work. D=defect-related input, R=repeated correction, H=avoidable stop; labels overlap. The current closure is incomplete at the cutoff.

| Stage / audit cases | Inputs | D / R / H | Observed hours |
|---|---:|---:|---:|
| AU01 visual languages,1–9 |9 |2 /0 /2 |0.51 |
| AU02 first generated motion,10–13 |4 |1 /0 /0 |0.43 |
| AU03 portrait identity,14–28 |15 |0 /0 /1 |0.38 |
| AU04 entrance boards/realization,29–53 |25 |2 /0 /3 |3.14 |
| AU05 authoring setup,54–64 |11 |1 /0 /0 |0.56 |
| AU06 bust/anatomy/skin,65–114 |50 |20 /12 /14 |8.51 |
| AU07 expression readiness,115–117 |3 |0 /0 /0 |1.07 |
| AU08 hair/static acceptance,118–153 |36 |14 /11 /16 |11.90 |
| AU09 body/deformation,154–172 |19 |12 /9 /5 |11.03 |
| AU10 wardrobe/contact/motion,173–198 |26 |11 /7 /0 |46.72 |
| AU11 rider/horse/terrain/look,199–216 |18 |9 /5 /1 |23.16 |
| AU12 choreography/geography,217–226 |10 |4 /4 /0 |16.13 |
| AU13 props/knowledge/grip,227–240 |14 |3 /3 /1 |8.91 |
| AU14 narrative/music/audio,241–278 |37 |7 /1 /1 |7.09 |
| AU15 audiovisual finishing,279–288 |10 |6 /5 /0 |7.21 |
| AU16 current closure/audit request,289–292 |4 |1 /1 /0 |3.13 |

The contrast matters: hair/bust produced many unnecessary stops, while wardrobe consumed much more recorded time with no stop classified unnecessary in that stage. A stop count alone cannot measure efficiency. Nor is the46.7h wardrobe bucket proof that the double-wrap ambition was wrong; it includes foundational method development, moving integration and machine time.

## Forward learnings: what should have happened, and when to apply it

### AU01–AU04: art direction, identity and shot intent

- **Different visual languages must differ structurally, not just by filter.** Cases2/6: the first comparison did not test genuinely different design languages and presentation dimensions needed repair. Before an aesthetic review, vary shape/material/lighting/composition according to the stated option and supply matched, navigable comparisons. Preserve genuinely different choices for the Director.
- **Image approval has a scope.** Cases14–28 were largely valuable identity discovery: age, fullness, individuality and self-possession. Images are identity/art-direction material, not a demand for pixel-literal reconstruction. Record protected traits, flexible traits and unresolved unseen geometry. After accepted native152, do not quietly reverse accepted differences toward the illustration.
- **Motion evidence must show motion and identity through the difficult interval.** Cases13/30: held frames/zoom and distorted turned faces should not have been treated as useful motion alternatives. Review full motion and reveal angles before asking about style. Separate model limitation from prompt preference.
- **Block the complete causal shot before polishing isolated moments.** Cases31–53 established the aerial hook, face reveal and detour. Bind the whole chain, including what the audience sees and why she acts, before high-cost asset polish. A dramatic entrance is an audience goal, not just a horse-animation test.

### AU05–AU07: access, bust, surface and expression

- **Recommend tools with lifecycle costs and usable access.** Case54: trial availability alone is insufficient. Case91: search free candidates rigorously using functional/garment synonyms and inspect what the asset actually contains. Verify license, separability, topology/rig suitability and editing cost; do not infer a scarf from a filename or treat any free mesh as a good donor.
- **Separate geometry, projected texture and lighting.** Cases69/85/89: compare both sides with matched relative lighting before diagnosing asymmetry or skin darkness. Cases99–106: inspect neck/shoulder silhouette, throat/clavicles and transitions in clay from front, sides, back and three-quarter before surface work. Do not erase anatomy to remove a seam.
- **Extend the approved surface character; do not smooth it away.** Cases108/111/113: local paint-like repair erased the cheek's texture language or left a boundary. Check low-frequency tone, medium-scale marks, fine texture and seam continuity independently under the intended light. A numerical blend is not a visual blend.
- **Test expression capability before detailed finishing, but with a meaningful action.** Cases115–117 legitimately established recognizable facial movement. Later neutral riding and unreadable recognition show that deformation capability is not an acting performance. Re-test intent, timing and visibility in the actual shot.

### AU08: hair and achievable production design

- **Choose the representation before tuning the silhouette indefinitely.** Cases118–144: competing painted/new hair, cap-like crown, hairline and uniform clumps survived many adjacent changes. Run a discriminating control for roots/scalp, volume, directional flow, material and strands; do not repeatedly patch one visible edge while the representation remains wrong.
- **Unseen views need interpretation; they are legitimate creative input.** Case140's uncovered front/side/back references were useful. The eventual capability-first native hair direction in145 was also a real choice, not a failure by the Director to specify enough.
- **Judge the whole hair–face interface.** Cases147/150–152: temples, ear definition, sideburns, roots, forehead exposure and spikes must be checked together at review size. Controlled variation must occur at several scales, not indiscriminate noise. Preserve the accepted face and native hair master.
- **No micro-improvement handover when rejection is predictable.** Sixteen hair-stage handovers were judged avoidable. A method change, meaningful creative choice or completed integrated result warrants a handoff; another partly repaired hat-like front does not.

### AU09–AU10: body, rig and moving wardrobe

- **Reuse must pass fit-to-purpose admission.** Case155: a knight donor's existence did not establish adult feminine proportions. Use measured proportions plus standing/seated silhouettes before committing to integration. Preserve the accepted bust's anatomy during scale and attachment changes.
- **Inspect deformation interiors, not only endpoint poses.** Cases157–170: neck bands, lost clavicles, shoulders, elbows, knees, hip folds, abdomen and gluteal volume required Director correction repeatedly. Test standing, seated and transition poses, multiple views and joint crops. Joint origin, skin weights and corrective deformation are separate hypotheses. Clothes are not permission to hide a structural failure.
- **Design cloth routes, supports and layer order as a whole.** Cases174–196: repeated shoulder clipping, sleeve webs, rigid strips, stuffed rear folds and vanishing routes exposed the limits of prescribing surfaces then correcting collisions locally. Start with the double-wrap route/support/contact strategy; trace both edges through shoulders and back; keep shawl above harness; prove mounted motion before polish. A connected mesh can still disappear visually.
- **Scope a model escalation around a failed hypothesis.** Cases189–198: Astra is the top tier, not a guarantee of success. Reassess method/input/representation and run a representative control; do not just apply more reasoning to the same compensating patches. Preserve failed evidence and model attribution without claiming a controlled benchmark.

### AU11–AU12: performance, physical response, style and geography

- **Skilled control is not stiffness.** Cases200/203/206/212/226: rider upper torso, neck and head should coordinate to absorb motion; a stable gaze is not a rigid neck/chest block. Brief joint contributions, phase and amplitudes in the actual framing; inspect performance and anatomy together.
- **Secondary motion needs a physical story.** Mane, tail, hair, cloth, tack and dust require support, forcing, lag, inertia and recovery consistent with speed/turn/grade. A moving controller is not proof of believable response; tail floating, stringy mane and still hair must be sought before handoff.
- **Style lives in the whole scene and its interactions.** Cases204–216: painted background plus comparatively realistic foreground, washed-out skin and low-contrast dust needed integration. Use sun-bleached forms, selective darks, designed surface detail, costume palette and dramatic wake as one system. Lighting/terrain changes invalidate dust readability and skin/material review.
- **Performance tells a thought process.** Cases217/220/224: neutral baseline → recognition → alternate-route glance → decisive action → checking glance → determined continuation. Establish screen-side coordinates and threat/detour geography before final cameras; verify both options are visible. The face-versus-checkpoint framing question in223 was a legitimate Director tradeoff.
- **Larger than life does not mean physically incoherent or constantly maximal.** Preserve extraordinary speed, weight and musical payoff with contrasting moments that make them legible. Do not slow a forceful turn merely to display work or replace the opening hook with a book prologue.

### AU13: grip, contact and knowledge application

- **A contact constraint is not anatomy.** Cases236–240 and289: touching reins did not establish a fist. Backward thumb, separated hooks and fingers bending beyond apparent knuckles persisted despite correct verbal intent. First verify hand structure and articulation in a bare control, then fist silhouette, thumb placement, rein route and actual sleeve/mane integration. Include a known-bad control so a metric cannot accidentally bless both.
- **Tolerated defects remain defects.** Case240 permitted a preview compromise, not universal acceptance. Track the exact limitation and reopening trigger. After larger distractions are repaired, re-rank what now breaks believability; final contact was reopened289 for that reason.
- **Retrieval success and execution success are separate.** The rein work had retrieved appropriate rules. Its false admissions require better evidence and judgment, not merely another rule or larger context window. Preserve whether the failure was missing requirement, retrieval miss, unsuitable method, missing evidence, or wrong interpretation of evidence.

### AU14–AU15: music, narration, sound and finishing

- **Music taste needs concrete Director discovery.** Cases255–274: genre tags and model analysis did not predict enthusiasm. Do not over-literalize “train” or infer ethnic instrumentation. User-led Suno exploration was effective; bring chosen material/stems into an editable beat map and use the agent for rights records, timing and integration. Rejected taste auditions are not inherently avoidable failures.
- **Listen to the combined result, not just inspect levels.** Cases279–285: excessive ducking, then obscured “races”/“impeccable,” expose the limits of signal-only checks. Preserve actual pronunciation acceptance. Short private narration, a hoof-led opening and rising music require auditory review in context. If direct hearing is unavailable, disclose it and use a planned listening gate; another model's description is not personal hearing or Director taste acceptance.
- **Protect the hook and allocate the music over the trailer.** Cases253/286–288: no book-only opening; use manuscript overlays with readable text, safe boundaries and worn material. Save later musical peaks for other entrances; selected B demonstrates how an earlier surge can carry her turn. Sound needs weight, rhythm, synchronization and space, not only louder gain.
- **Keep finishing cheap when picture is unchanged.** Music-only A/B variants, overlays and mix changes should reuse the same locked picture. Separate clean/captioned versions, stems and unfaded trailer-join audio. Native rerender only when geometry, motion, lighting or camera actually changes.

### AU16: closure, reuse and operations

- Fix the reopened fist and20s ending without reopening accepted identity/style. Closure requires the integrated deliverable, not a tests/commit milestone.
- Efficient quality means maintaining the high accepted bar while reducing escaped defects, repeated work and review burden through evidence and reuse—not lowering the bar or imposing arbitrary time limits.
- Reuse a versioned asset **with its tested-use envelope and dependencies**. Standing acceptance does not qualify riding; local replay does not establish recovery from a lost SSD. Current remote durability is a separate unresolved risk, documented in the248 recovery audit.

## The revised operating mechanism

Use the existing [strategy brief](../decisions/0005-production-strategy-before-execution.md), [shot/beat brief](../planning/SHOT_BEAT_QUALITY_BRIEF.md), [learning index](PRODUCTION_LEARNING_APPLICATION_INDEX.md), [knowledge bridge](pilot/README.md) and [operating ledger](../engineering-intelligence/OPERATING_LEDGER.md). This audit is not a new platform or a mandate to read every historical message before every task.

1. **At work-package start:** declare protected intent and accepted sources, identify the critical audience-visible behaviors and applicable expertise lenses, then retrieve their requirements plus adjacent interfaces. Manually reconcile relevant AU lessons above and source documents. Unknown domains are gaps to resolve, not empty successful retrieval.
2. **Before expensive execution:** demonstrate the riskiest interface in representative motion/framing. A prototype must discriminate between methods and expose failure, not merely make an attractive still. Record what would make the method unsuitable. Repeated neighboring regressions trigger method reassessment, not another cosmetic pass name.
3. **During implementation:** maintain one issue record per distinct defect, linking repeat inputs and affected versions. Distinguish new preference, implementation defect, regression, missing knowledge and evidence/judgment failure. Keep a tolerated defect open with its screen-use limit; do not silently turn it into PASS.
4. **Internal review:** first cold audience read, then failure-seeking technical read. Use full/partial motion, revealing controls and the actual delivery artifact. Compare to the quality floor and approved sources, not the last rejected candidate. Record observation and uncertainty, not just hashes or scores. Judge anatomy/contact, physical response, style/geography and audio with their relevant evidence. Stills, real-time playback and direct listening are different modalities.
5. **Before a handover:** name the actual Director choice or completed review deliverable. If neither exists and authorized repair remains, continue. A diagnosed technical fix, elapsed checkpoint or local commit is not a new approval gate. Planned creative reviews remain: intent/meaningful look choice, complete staging/performance, integrated audiovisual acceptance. A genuinely new consequential choice may add a review; do not force everything into a fixed count.
6. **At closure/checkpoints:** publish the same scorecard below, retain contradictory/rejected evidence, update the lesson and its trigger/test, and distinguish local commit, remote source durability and verified media recovery. Knowledge coverage is measured against manual source review; perceptual success is measured against what actually escapes to the Director.

For the Sikh and Gurkha, reuse style/material/camera/audio/delivery patterns and tested infrastructure, not the Pashtun's personality, body or action assumptions. Each requires its own signature-beat risks. Parallel lightweight planning/asset suitability is sensible; full animation depends on agreed intent and available render capacity. This audit authorizes neither new character dispatch nor paid services.

## Prospective scorecard — same quality bar, better efficiency

Start with the next authorized work package and aggregate per sequence and release checkpoint. Use stable work-package/shot/beat/issue/review IDs. Extend records in the existing ledger and work package; do not create an additional management system.

| Metric | Definition / recording rule | Baseline and desired direction |
|---|---|---|
| Director burden | Actual human inputs; separate creative, authority, logistics and defect/process labels |291 broad inputs; reduce avoidable categories, **not** legitimate direction |
| Unnecessary handovers | Distinct final stops with no completed scope, real choice or blocker |30 definite/44 broad; target zero deliberate routine stops; report ambiguous cases separately |
| Escaped defects | Unique issue first detected by Director after internal admission; severity and screen importance required | Historical93 defect-related **inputs**, unique issue denominator not reconstructed; establish true defect rate prospectively |
| Repeat escapes/regressions | Existing issue or affected neighbor reappears after claimed correction |58 related inputs historically; target zero known blocking issues knowingly presented as complete |
| First-pass review acceptance | Planned integrated review passed without technical rework / eligible reviews; creative change reported separately | UNKNOWN historically; start prospective denominator, do not call260 finals260 reviews |
| Anticipation effectiveness | Important Director-discovered issue was predicted/tested, predicted but wrongly passed, or missed entirely | Qualitative evidence exists; no reliable retrospective percentage. Improve both coverage and accuracy |
| Retrieval effectiveness | Required source obligations recalled against manual source audit; unsupported extra obligations also tracked | Existing109/109 finite regression pairs is **not** whole-production recall. Add held-out cases from actual misses; freeze expected sets before testing |
| Net observed work | Union of reliable task/work/job intervals minus verified no-work Director/next-prompt pauses; retain continuing jobs |≈145h recorded runtime, exact old netUNKNOWN. Future gaps make exact metricUNKNOWN, not zero |
| Render burden | Native occupancy union and sum; render-call/frame-loop durations separately; peak concurrent jobs and critical-path waiting when observed |87.9h native union;19.9h partial frame loops. Never add concurrent time twice |
| Rework cost | Time/jobs linked to issue cause: defect/regression, changed creative decision, capability exploration or infrastructure | UNKNOWN retrospectively; avoid treating all exploration as failure |
| Reuse benefit | Reused component, accepted version, tested scope and adaptation time; new defects introduced by reuse | Record actual adaptation, not imagined “hours saved” |
| Engineering tokens | Deduplicated per-response input, cached subset, output and reasoning subset; preserve actual provenance and separate provider ledgers |47.2M uncached input +9.43M output, plus2.327B cached input historically; compare scoped work packages, not raw context throughput alone |
| Cost per accepted output | Net observed work and native process time per accepted sequence/shot; output seconds as secondary context | Current20s unit not closed at cutoff; amortize shared foundation separately, do not forecast by dividing145h by20s |
| Durability | Last verified remote source commit and media recovery snapshot, age, missing active dependencies |248 found sourceOct3/mediaSept17; current work not protected off-device. Do not substitute commit counts for a restore test |

At the first Sikh/Gurkha review, report counts and causes before claiming improvement. Compare similar stages and screen demands; show shared foundation separately. A lower turn count achieved by hiding defects or skipping review is failure, not efficiency. A longer successful foundational proof may be better than many short failed passes. No arbitrary time limit follows from these metrics.

### Recording changes required now

The ledger already supports work/wait/job events, monotonic job timing, review duration and proxy counts. Its weakness was inconsistent capture/reconciliation, not lack of a database. At every actual handover, close the work interval and open the appropriate wait; on resumption close that wait; leave genuinely continuing jobs running. Reconcile unclosed events before a metric is called exact. Do not retrospectively label a whole multi-hour interval Director waiting if tools ran in it. Append corrections with provenance rather than overwrite old evidence.

Record review admission and its artifact version, issue IDs, new-versus-repeat status, cause and disposition in the work package. Current audit scripts reproduce the historical extraction/classification/interval baseline; they do **not** implement universal event capture, automatically identify defects, or enforce future review quality. These prospective controls are an adopted operating procedure within this request; automatic orchestration remains separate future implementation.

## Evidence, reproducibility and limits

- Exact task: `01a0878c-e7a2-75e0-873c-c31d97f879a1`, local session snapshot9,470,427,510bytes; captured prefixSHA256 `89e0a0729cffaf5d3789a3f2ba354059001c3f5a51a037fc50ad4d7b569948a6`. Sanitized extractionSHA256 `d60b8e5ccb23657a33eb24d1686cd5a9c27ea1142cbf327a355f0c61ad5d2975`.
- Local detailed evidence: `.runtime/production-audit250/history.json`, `cases.json`, `operating-events.json`, `metrics-initial.json`, `frame-costs.json`, `token-usage.json`. Portable Git artifacts are the report, abbreviated source-indexed case ledger and compact metrics. This is not a lossless conversation backup.
- Scripts: `scripts/audit_pashtun250.py` captures exact-task message/lifecycle/tool metadata without copying reasoning, tool arguments/results, image payloads or credential files; `scripts/audit250_classification.py` holds explicit human-readable case judgments; `scripts/audit250_metrics.py` computes unions/censoring and publishes the baseline. Classification is manual agent judgment, not model-independent ground truth.
- Review covers every in-scope Director input, linked assistant handovers, documented methods/outcomes and source records. It does **not** claim a fresh visual inspection of every historical render or replay of every failed native file. Historical visual failures are grounded in the Director's actual feedback and records. Present finishing images have separate current review evidence.
- Tests cover interval union, excluded gaps with continuing jobs, clipping at cutoff, overlap subtraction, superseded/orphan ledger events, complete case coverage and unique handover IDs. A passing test proves bookkeeping behavior, not that all artistic classifications are correct.
- Unknowns remain exact net labor, complete pure-render time, Director active review time, distinct historical defect count, first-pass review denominator, unreported provider usage, engineering dollar cost/quota allocation and counterfactual saved effort. No guesses are substituted. No new paid call, external upload or remote push was performed for this audit.
