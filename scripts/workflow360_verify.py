"""Assemble scoped offline evidence after tests; never invokes a model or Blender."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk, stage_routing, context_hygiene
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/workflow360'


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,indent=2)+'\n'
    if path.exists():assert path.read_text()==text,str(path)
    else:path.write_text(text)


def binding(path):return {'path':str(path.relative_to(ROOT)),'sha256':pk.file_hash(path)}


def main():
    log=ROOT/'.runtime/context-hygiene/runs/workflow360-final/stdout.log'
    assert '432 passed' in log.read_text()
    task=pk.read_json(ROOT,'results/workflow360/task.json')
    source_paths=['AGENTS.md','docs/knowledge/context/rules.json',
        'src/movie_factory/stage_routing.py','src/movie_factory/staged_runner.py',
        'docs/engineering-intelligence/STAGE_MODEL_ROUTING.md',
        'docs/engineering-intelligence/SOL_DEFAULT_ROUTING.json',
        'tests/test_stage_routing360.py','tests/test_staged_runner.py','tests/routing_fixtures360.py',
        'results/workflow360/REVIEW.md']
    task['inputs'].update({p:pk.file_hash(ROOT/p) for p in source_paths})
    write(OUT/'task-final.json',task)
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    write(OUT/'validation/packet.json',packet)
    routes={p:{a:stage_routing.resolve(stage_routing.policy(p),a,ROOT) for a in stage_routing.ACTORS}
            for p in ('general','specialist_3d')}
    assert all(r['model']==stage_routing.SOL and r['effort']=='high' for p in routes.values() for r in p.values())
    write(OUT/'validation/default-routes.json',routes)
    context,_=context_hygiene.load(ROOT)
    write(OUT/'validation/core-review.json',dict(original_rule_count=len(context['rules']),core=context['core'],
        original=context['original'],observation='Reviewed360 core amendment only;42 original routed rules and preserved snapshot retained.307 capsule not refreshed.'))
    c=Controller(ROOT,DATABASE)
    states={}
    for name in ('sikh335-supporting-appearance','sikh335-continuous-performance'):
        s=c.state(name);states[name]={k:s[k] for k in ('stage','cycle','max_corrections')}
    write(OUT/'validation/production-state.json',states)
    write(OUT/'validation/tests.json',dict(tests_passed=432,log=binding(log),external_paid_provider_calls=0,
        live_inference=False,native_dispatch=False,engineering_tokens=None,engineering_cost_usd=None,
        limits='Offline controls only; no model-quality or allowance-saving measurement.'))
    actions={
      'reuse_envelope':'Extended the existing policy/runner and canonical task history; no replacement harness or asset reuse qualification.',
      'authority':'Astra requires exact scoped Director approval and current retrospective evidence; call/correction caps unchanged. No live calls.',
      'strategy':'Bound strategy and fresh packet preceded construction; tested silent Astra routing, lost authority and restart/expiry before completion.',
      'visual_gate':'Engineering scope only. No media changed or artistic PASS; existing Director AV and known Nihang failures remain.',
      'anticipation':'Negative controls cover tampered approval, changed candidate/stage/cycle, another database, aborted retries and legacy policy history.',
      'stopping':'Scoped engineering result complete after432 passing controls. No extra production cycles or requirement relaxation.',
      'versioning':'Version2 explicit adoption preserves old policies and call records; scope/call expiry selects Sol without resetting authority.',
      'economics':'No external paid calls, renders or new services. Engineering quota/cost unknown; no projected savings from tests.',
      'retrieval':'Read initial task obligations and manually reconcile Director360 policy with326/187.42 original routed rules retained; current core points to360. Fresh final packet.',
      'current_state':'Accepted Pashtun and unresolved Nihang/crowd scope unchanged; original task states recorded. No production acceptance inferred.',
      'au_reuse':'No accepted masters changed; local commits are separate from remote/native protection.',
      'au_review':'Preserved failed controls and protocol mismatch checks; tests establish enforcement, not semantic truth or audiovisual judgment.'}
    evidence=[binding(ROOT/p) for p in source_paths]+[binding(log),binding(OUT/'validation/default-routes.json'),binding(OUT/'validation/production-state.json')]
    review=dict(packet_digest=packet['packet_digest'],scope='Offline routing engineering only',
        checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS',action_taken=actions[x['id']],
                     observation='Scoped software/evidence checks pass; no live model or artistic claim.',evidence=evidence) for x in packet['obligations']],
        hypotheses=[dict(prediction='A specialist label or restart could continue Astra without a current bounded approval.',
                         result='resolved',observation='Both defaults select Sol; expired/exhausted grants return to Sol; approval/database/restart controls pass.',
                         response='Retain source-bound grants and original accounting history.')],
        adjacent_regressions='432 affected workflow tests pass. Main-chat selector and semantic authorization remain trusted human/agent responsibilities.',
        stopping_reason='Approved policy implementation complete; no inference or production change authorized by this engineering package.')
    gate=pk.check_review(ROOT,packet,review)
    write(OUT/'validation/knowledge-review.json',review);write(OUT/'validation/knowledge-gate.json',gate)
    assert gate['ready_for_review'],gate
    print(json.dumps(dict(tests_passed=432,knowledge_gate=gate['ready_for_review'],live_inference=False,states=states)))


if __name__=='__main__':main()
