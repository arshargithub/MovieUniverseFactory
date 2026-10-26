"""Acquisition routing and bounded host-side paid-video adapter; no live provider."""
from pathlib import Path
import math
from . import production_knowledge as pk, review_control as rc
from .production_workflow import require, nonempty


def route(method):
    require(method in {'director','reuse_existing','image_search','built_in_image','video_search','generated_video'},'REFERENCE_ACQUISITION_METHOD')
    return dict(method=method,requires_director_spend=method=='generated_video',requires_persistent_budget=method=='generated_video',qualification_required=True,
                boundary='Routing is not publication, new-tool, provider qualification or model-switch authority.')


def dispatch_video(root,plan,approval_binding,ledger,provider):
    """Only trusted host provider adapters belong here; tests inject mocks.

    A dedicated approval-bound campaign prevents another run ID/path resetting
    the video allowance. Unknown/failed provider charges remain reserved.
    Raw chat connectors are not OS-intercepted by this wrapper.
    """
    root=Path(root).resolve();require(plan.get('method')=='generated_video','REFERENCE_VIDEO_PLAN')
    for k in ('id','purpose','question','provider','model','prompt','ledger_stage','ledger_scope'):
        require(nonempty(plan.get(k)),'REFERENCE_VIDEO_PLAN_'+k.upper())
    amount=plan.get('max_request_usd');require(type(amount) in {int,float} and math.isfinite(amount) and amount>0,'REFERENCE_VIDEO_COST')
    for b in plan.get('inputs',[]):rc.binding(root,b)
    rc.binding(root,plan['qualification']);q=pk.read_json(root,plan['qualification']['path'])
    require(all(q.get(k)=='confirmed' for k in ('commercial_output_rights','input_privacy','deployment_export','cost_bound')),'REFERENCE_VIDEO_UNQUALIFIED_PROVIDER')
    rc.binding(root,approval_binding);approval=pk.read_json(root,approval_binding['path'])
    require(approval.get('decision')=='approve_reference_video' and approval.get('request_digest')==pk.digest(plan),'REFERENCE_VIDEO_APPROVAL_SCOPE')
    require(nonempty(approval.get('director_reply')),'REFERENCE_VIDEO_HUMAN_SOURCE');rc.binding(root,approval['source'])
    cap=approval.get('max_total_usd');calls=approval.get('max_calls')
    require(type(cap) in {int,float} and math.isfinite(cap) and cap>0 and type(calls) is int and calls>0,'REFERENCE_VIDEO_APPROVAL_LIMIT')
    require((root/approval['ledger_path']).resolve()==ledger.path.resolve() and ledger.path.resolve().is_relative_to(root),'REFERENCE_VIDEO_LEDGER_SCOPE')
    require(ledger.policy['campaign_limit_units']<=round(cap*1e9) and ledger.policy.get('request_limit',float('inf'))<=calls,'REFERENCE_VIDEO_LEDGER_LIMIT')
    reservation=ledger.reserve(run_id=pk.digest(plan),stage=plan['ledger_stage'],amount_usd=amount,scope=plan['ledger_scope'],purpose='reference-video:'+pk.digest(plan))
    try:
        result=provider(plan)
    except Exception:
        ledger.settle(reservation,cost_usd=None,error='Reference video provider failed; charge unknown')
        raise
    ledger.settle(reservation,cost_usd=result.get('cost_usd'),response_id=result.get('id'))
    return dict(kind='reference_video_receipt',plan_digest=pk.digest(plan),reservation_id=reservation,director_approval=approval_binding,ledger_path=str(ledger.path.relative_to(root)),result=result,status='candidate_not_qualified_reference')
