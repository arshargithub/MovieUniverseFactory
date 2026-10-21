"""Read-only media verification and derived failed-proof records; no render or egress."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh331'

def bind(path):return {'path':path,'sha256':pk.file_hash(ROOT/path)}
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')

def main():
    expected={
      '.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4':'1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b',
      '.runtime/art-direction/series01-sikh320/build-10/sequence.blend':'c7af07ec8ea14e1f321cf7bb7d5ec4e5cd6b8bbccabfaa886c3622e7cacc3a00',
      '.runtime/art-direction/series01-sikh256/references/reference-b.mov':'78d0d691e8712c02931876cf0bc405e4869de357f337f531708be7a7da4898e2'}
    protected={p:{'sha256':pk.file_hash(ROOT/p),'expected':h} for p,h in expected.items()}
    for row in protected.values():row['unchanged']=row['sha256']==row['expected']
    assert all(r['unchanged'] for r in protected.values())
    base=ROOT/'.runtime/art-direction/series01-sikh331';jobs={};evidence=[]
    for directory in ('inspect-01','inspect-02','pose-01','pose-02','pose-03'):
        folder=base/directory
        jobs[directory]=json.loads((folder/'receipt.json').read_text())
        for path in folder.glob('frames/*.png'):evidence.append(bind(str(path.relative_to(ROOT))))
    record={'protected':protected,'native_jobs':jobs,'native_seconds_sum':sum(j['seconds'] for j in jobs.values()),'phase_render_count':len(evidence),'phase_images':evidence,'tests':bind('.runtime/context-hygiene/runs/sikh331-final-tests/receipt.json'),'test_stdout':bind('.runtime/context-hygiene/runs/sikh331-final-tests/stdout.log'),'native_reopen':'NOT_RUN','full_clip':'NOT_RUN','direct_motion':'NOT_RUN','direct_audio':'NOT_RUN','remote_protection':'NOT_RUN','complete_turn_elapsed_seconds':None,'token_usage':None,'limits':'Native process sum is not total work, rendering-only time or viewer acceptance; early recovery capture gap retained.'}
    write('verification.json',record)
    packet=json.loads((OUT/'frozen-review02/knowledge.json').read_text())
    audit=bind('results/sikh331/PROOF_AUDIT.md')
    failed={'construction_interfaces','animal_coordination','strategy','versioning','representation','look','anatomy','motion','anticipation'}
    checks=[]
    for o in packet['obligations']:
        status='FAIL' if o['id'] in failed else 'PASS' if o['id'] in {'visual_gate','stopping'} else 'NOT_RUN'
        checks.append({'id':o['id'],'status':status,'kind':o['check_kind'],'observation':f"{status}: scoped negative proof; see P1–P7 and exclusions in audit, not a full production qualification.",'action_taken':'Preserved failed evidence, withheld crowd/full render and review queue; zero remaining corrections in retrospective controller.','evidence':[audit,bind('results/sikh331/verification.json')]})
    review={'packet_digest':packet['packet_digest'],'checks':checks,'hypotheses':[{'prediction':'Valid support targets can coexist with the wrong whole-pose family and shell-like supporting cast.','observation':'pose03 retains these visible failures.','response':'Reject candidate and close package; no Director AV waiver.','result':'unresolved'}],'adjacent_regressions':'Spine/root changes leave seat/reins/cloth/groom dependencies unqualified; no inherited pass.','stopping_reason':'Early proof failed after initial plus two corrections; native dispatch closed and scope replan required.'}
    write('knowledge-review.json',review)
    print(json.dumps({'protected_unchanged':all(r['unchanged'] for r in protected.values()),'native_process_seconds_sum':record['native_seconds_sum'],'phase_render_count':len(evidence)}))

if __name__=='__main__':main()
