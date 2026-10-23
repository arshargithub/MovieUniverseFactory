# Director360 — implement Sol default and bounded Astra escalation

Director359: use Sol6.1 High as the default across planning, execution, review and retrospectives. Astra should be available only for narrowly scoped work supported by retrospective evidence and Director approval. The goal is sustainable usage with the existing quality bar.

Agent359 proposed: remove automatic Astra routing for specialist3D; require retrospective evidence, a specific assignment, Director approval, a bounded allowance and a success test; expire the escalation after the assignment and return to Sol. Preserve original task, correction and call limits. Keep enforced workflow stages without automatically creating a separate LLM session for every stage.

Director360: "Ok go ahead"

Scope: implement and test routing, approval and expiration controls; update workflow instructions and model records. Local mocked tests only, no new provider calls or spend. Production asset construction is outside this engineering change.
