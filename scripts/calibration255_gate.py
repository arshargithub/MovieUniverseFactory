"""Evidence-bound review for255. Pending remote recovery intentionally blocks full exit."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/knowledge-pilot213/calibration255'

def recovery_ready(root):
    folder=root/'results/backup/protect255'
    try:
        final=json.loads((folder/'final-verification.json').read_text())
        restore=json.loads((folder/'remote-capsule-restore.json').read_text())
        return (final.get('recovery_copy_verified') is True
            and final.get('snapshot_id')=='protect255-20261013-final'
            and final.get('inventory',{}).get('all_expected_keys_and_sizes_match') is True
            and restore.get('all_hashes_match') is True
            and restore.get('native_dependency_checks_pass') is True
            and restore.get('files')==61 and restore.get('native_reopens')==2
            and restore.get('clean_sha256')=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b')
    except (OSError,ValueError):
        return False

def main():
    packet=json.loads((OUT/'packet.json').read_text())
    items={
      'authority':('PASS','Kept approved unit unchanged; requested exact remote scope before broad egress. No new production, paid provider or release.', 'docs/planning/PROTECTION_CALIBRATION_255.md'),
      'strategy':('PASS','Defined recovery/retrieval/application/judgment chain and separate proof boundaries before execution; adjusted freeze method after measured scanner issue.', 'docs/planning/PROTECTION_CALIBRATION_255.md'),
      'visual_gate':('PASS','Re-inspected13 familiar controls. Four historical structural failures rejected; other judgments restricted to visible/static scope or NOT_RUN. No new full-motion/audio pass asserted.', '.runtime/knowledge-pilot213/calibration255/visual-controls.json'),
      'anticipation':('PASS','Tested stale approval, missing retrospective rules, misleading formal PASS, bad fist/cloth/anatomy, over-rejection of accepted differences and absent temporal evidence.', '.runtime/knowledge-pilot213/calibration255/visual-controls.json'),
      'stopping':('PASS','No routine reopening of253. Calibration remains finite and shadow-reviewed on next task. Protection exits only on final remote verification and actual capsule restore evidence.', 'docs/planning/PROTECTION_CALIBRATION_255.md'),
      'versioning':('PASS','61-file capsule downloaded from S3 only, all hashes matched and both native cache closures verified in isolated remote-source root. Original production untouched; no re-render claimed.', 'results/backup/protect255/remote-capsule-restore.json'),
      'economics':('PASS','Isolated measurement demo subtracts eligible waits; tests preserve overlapping work and review/issue IDs, unknown tokens. This turn recording defect disclosed.', '.runtime/knowledge-pilot213/calibration255/measurement-demo/summary.json'),
      'retrieval':('PASS','114 required case/obligation pairs now present; initial27 misses retained; scope11 sources/38 records, no unknown-entity empty success.', '.runtime/knowledge-pilot213/calibration255/retrieval-after.json'),
      'current_state':('PASS','Current253 provisional exact-unit acceptance and255 prerequisites routed globally; strict replay FAIL and release authority separate.', 'docs/knowledge/CURRENT_PRODUCTION_STATE.md'),
      'au_reuse':('PASS' if recovery_ready(ROOT) else 'NOT_RUN','Final private snapshot inventory, checksum/stream checks and separate61-file remote native restore are required. Source history pushed; final closure records follow separately. Rights and strict pixel replay are not waived.', 'results/backup/protect255/final-verification.json'),
      'au_review':('PASS','Structural gate and semantic judgment explicitly separated; false well-formed synthetic assertion is a disclosed limit, not visual qualification.', 'tests/test_calibration255.py'),
    }
    review={'packet_digest':packet['packet_digest'],'checks':[],
       'hypotheses':[{'prediction':'Old regressions omit new lessons/current approval','observation':'27 of114 new required pairs initially absent','response':'Reviewed source reconciliation; preserve initial misses','result':'resolved'},
          {'prediction':'Valid evidence shape can hide wrong judgment','observation':'Synthetic unsupported assertion passes structural gate; known-bad visual controls separately rejected','response':'Resolved the unsafe reliance by applying manual controls and restricting claims, not by claiming the semantic limitation is eliminated. Temporal evidence remains separately required.','result':'resolved'}],
       'adjacent_regressions':'Original nine pins unchanged; historical voice tests explicitly synthetic; current accepted film remains untouched; no broad authority inherited.',
       'stopping_reason':'Protection and finite calibration have evidence-backed exits. No new production, artistic approval, release or universal visual-judgment claim follows from this gate.'}
    for rule in packet['obligations']:
        status,observation,path=items[rule['id']]
        review['checks'].append({'id':rule['id'],'kind':rule['check_kind'],'status':status,
          'action_taken':observation,'observation':observation,'evidence':[{'path':path,'sha256':pk.file_hash(ROOT/path)}]})
    (OUT/'review.json').write_text(json.dumps(review,indent=2)+'\n')
    result=pk.check_review(ROOT,packet,review)
    (OUT/'gate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))

if __name__=='__main__':main()
