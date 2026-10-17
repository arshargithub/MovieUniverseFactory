"""Sequential bounded continuation; raw prior holds preserved, liability explicit."""
import argparse,json,tarfile,hashlib,io
from pathlib import Path
import trellis294_cloud as t
from movie_factory.budget import BudgetLedger
from movie_factory import production_knowledge as pk
c=t.c
ROOT=c.ROOT
OUT=ROOT/'results/trellis295'
ATTEMPT='a'
def ledger():
    return BudgetLedger(ROOT/'.runtime/trellis295/budget.jsonl',campaign_limit=13,
        scope_limits={'qualification':13},stage_limits={'gpu_session':(4,1)},request_limit=3,request_ceiling_usd=4)
def aggregate(add=0):
    for name in ('trellis293','trellis294'):
        receipt=json.loads((ROOT/'results'/name/'teardown-verification.json').read_text())
        if any(receipt['remaining'].values()):raise RuntimeError('Prior resources not cleared')
    new=ledger().summary();total=2+new['committed_usd']+add
    if total>15+1e-9:raise RuntimeError('Original USD15 ceiling exceeded; contingency not activated')
    return {'effective_ceiling_usd':15,'conditional_extra_usd_activated':0,'closed_liability_bound_usd':2,'closed_actual_bill_usd':None,
        'historical_holds_preserved_not_added_as_cost':{'293':10,'294':5},'new':new,'admission_total_usd':total,
        'basis':'results/trellis295/STRATEGY.md','teardown_bindings':{n:c.sha(ROOT/'results'/n/'teardown-verification.json') for n in ('trellis293','trellis294')}}
def packet():
    task=json.loads((ROOT/'results/trellis294/task.json').read_text());task.update(id='trellis295-'+ATTEMPT,
        intent='Complete synthetic exporter under original total15, then gated production candidate. Current dispatch synthetic only.',
        execution_authority={'source':'results/trellis295/STRATEGY.md','scope':'Sequential synthetic repair under original15; no actor/weights before access/rights/export gates'})
    for p in [OUT/'STRATEGY.md',Path(__file__),ROOT/'scripts/trellis294_cloud.py',ROOT/'scripts/trellis294_worker.py',ROOT/'scripts/trellis294_runtime.py']:
        task['inputs'][str(p.relative_to(ROOT))]=c.sha(p)
    result=pk.task_packet(ROOT,task);c.dump(c.OUT/'task.json',task);c.dump(c.OUT/'packet.json',result)
    (c.OUT/'packet.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:raise RuntimeError(result['blockers'])
    return result
def configure(attempt):
    global ATTEMPT
    assert attempt in ('a','b','c');ATTEMPT=attempt;t.configure()
    c.OUT=OUT/('cloud-'+attempt);c.LOCAL=ROOT/('.runtime/trellis295'+attempt);c.STATE=c.LOCAL/'cloud-state.json'
    c.JOB='trellis295'+attempt+'-synthetic';c.BUCKET='mf-trellis295'+attempt+'-281482331395'
    c.ROLE='mf-trellis295'+attempt+'-worker';c.GUARD='mf-trellis295'+attempt+'-guard'
    c.packet=packet;c.ledger=ledger;t.ledger=ledger;t.aggregate=aggregate;t.packet=packet
def no_prior_active():
    data=t.aws('ec2','describe-instances','--filters',c.j([{'Name':'tag:MovieFactoryJob','Values':['trellis293-synthetic','trellis294-synthetic','trellis295a-synthetic','trellis295b-synthetic','trellis295c-synthetic']},{'Name':'instance-state-name','Values':['pending','running','stopping','stopped','shutting-down']}]))
    assert not data['Reservations'],'No overlapping worker; finish prior cleanup first'
def prepare():
    no_prior_active();t.prepare(reservation_usd=4)
    original=c.LOCAL/'payload.tar.gz';original.rename(c.LOCAL/'payload-original.tar.gz')
    additions={name:ROOT/'scripts'/name for name in ('trellis294_worker.py','trellis294_runtime.py')}
    with tarfile.open(c.LOCAL/'payload-original.tar.gz') as src,tarfile.open(original,'w:gz') as dst:
        for m in src.getmembers():dst.addfile(m,src.extractfile(m))
        for name,p in additions.items():dst.add(p,arcname='scripts/'+name,recursive=False)
    manifest=json.loads((c.OUT/'payload-manifest.json').read_text())
    manifest.update({'scripts/'+n:c.sha(p) for n,p in additions.items()});c.dump(c.OUT/'payload-manifest.json',manifest)
    c.save('payload_sha256',c.sha(original));c.dump(c.OUT/'corrected-payload.json',{'sha256':c.sha(original),'files':len(manifest),'bytes':original.stat().st_size})
    # Fixed reviewed handler entrypoint; no arbitrary remote command channel.
    original_userdata=c.userdata
    c.save('corrected_handler','scripts/trellis294_worker.py')
    print('Corrected payload prepared')
def guards():
    no_prior_active();aggregate(4);c.guards(amount_usd=4,run_id='trellis295'+ATTEMPT);c.dump(c.OUT/'aggregate-reserved.json',aggregate())
def launch(zone):
    no_prior_active();original=c.userdata
    c.userdata=lambda:original().replace('scripts/trellis293_worker.py','scripts/trellis294_worker.py')
    t.launch(zone,reserved_usd=4,client_token='trellis295'+ATTEMPT+'-one-worker')
def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['prepare','guards','launch','status','retrieve','cleanup','packet']);p.add_argument('--attempt',default='a');p.add_argument('--zone',default='us-east-1a');a=p.parse_args();configure(a.attempt)
    if a.operation=='launch':launch(a.zone)
    elif a.operation in ('status','retrieve','cleanup'):getattr(c,a.operation)()
    else:globals()[a.operation]()
if __name__=='__main__':main()
