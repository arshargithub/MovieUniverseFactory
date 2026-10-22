"""Trusted Director-authorized allowance amendment, never a planner capability.

Original authority, failures, cycles and task identity are retained. A fresh
router-classified administrative amendment and explicit decision are mandatory. Full
regrounding follows; an amendment is not approval of an old plan or candidate.
"""
from . import production_knowledge as pk, review_control as rc, planning_pipeline as pp
from .production_workflow import require, nonempty
from . import retrospective as retro


def extend(controller, task, admission, decision, event_id):
    rc.binding(controller.root, decision)
    approved=pk.read_json(controller.root,decision['path'])
    require(approved.get('task')==task and approved.get('decision')=='approve_additional_corrections', 'ALLOWANCE_EXPLICIT_DECISION')
    count=approved.get('additional_corrections')
    require(type(count) is int and 1<=count<=20 and nonempty(approved.get('director_reply'))
            and nonempty(approved.get('question')), 'ALLOWANCE_DECISION_FIELDS')
    routed=controller.routing(admission)
    require(routed['route']=='engineering' and routed['request'].get('amendment_task')==task
            and routed.get('continuation_task') is None and routed['request']['authority']==decision,
            'ALLOWANCE_ROUTED_AUTHORITY')
    def apply(con):
        state=controller._state(con,task)
        retro.fresh(con,state)
        require(state['route']=='production' and state['stage']=='REPLAN_REQUIRED','ALLOWANCE_BLOCKED_TASK_ONLY')
        require(not con.execute('SELECT 1 FROM heavy_job').fetchone(),'JOB_STILL_ACTIVE')
        require(state['cycle']==approved.get('prior_cycle') and state['max_corrections']==approved.get('prior_max_corrections'),
                'ALLOWANCE_STALE_COUNTERS')
        require(state['cycle']==state['max_corrections'], 'ALLOWANCE_NOT_EXHAUSTED')
        require(not any(h['decision']==decision for h in state.get('allowance_history',[])), 'ALLOWANCE_ALREADY_USED')
        rc.binding(controller.root,state['authority'])
        if state.get('revision_authority'):rc.binding(controller.root,state['revision_authority'])
        pp.sources(controller.root,state['direction']);pp.source_context(controller.root,state['direction'])
        for ref in state['direction']['references']:rc.binding(controller.root,ref['binding'])
        state.setdefault('allowance_history',[]).append({'decision':decision,'admission':admission,
            'prior_cycle':state['cycle'],'prior_max_corrections':state['max_corrections'],
            'additional_corrections':count,'prior_engine':state['planning_engine'],
            'prior_fingerprint':state.get('fingerprint'),'prior_stage':state['stage']})
        state['max_corrections']+=count
        state['cycle']+=1  # first newly authorized correction, never cycle zero
        state['allowance_authority']=decision
        state['planning_engine']=pp.engine_digest()
        pp.invalidate(state,'GROUNDING')
        state['planning_feedback']=['Explicit Director allowance amendment. Preserve all original constraints and failures; reground before another native attempt.']
        return controller._stage(state,'BRIEFING')
    return controller._change(task,event_id,'extend_allowance',[admission,decision],apply)
