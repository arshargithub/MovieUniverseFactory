"""Local sidecar to existing provenance manifests; no asset or perceptual oracle.

Explicit caller enforcement is required. Evidence declarations do not establish
semantic truth or grant rights. No provider, installation or execution is invoked.
"""
import argparse
import json
import math
from pathlib import Path
from movie_factory.production_knowledge import file_hash,safe_path,KnowledgeError

STATES={'investigated','in_progress','rejected','qualified'}
MODES={'exact','adapt','reference_only'}

def validate(root, record, requested=None):
    required={'schema_version','id','state','reuse_mode','source','provenance',
              'rights','dependencies','tested_conditions','evidence','failures','effort'}
    if required-set(record) or record['schema_version']!=1:
        raise ValueError('Incomplete or unsupported resource record')
    if record['state'] not in STATES or record['reuse_mode'] not in MODES:
        raise ValueError('Unknown state or reuse mode')
    if not isinstance(record['id'],str) or not record['id'].strip():raise ValueError('Missing ID')
    for name in ('source','provenance','dependencies','evidence','failures'):
        if not isinstance(record[name],list):raise ValueError(name+' must be a list')
    if not isinstance(record['tested_conditions'],dict):raise ValueError('Conditions must be explicit')
    rights=record['rights'];effort=record['effort']
    if rights.get('status') not in {'verified_for_use','unresolved','incompatible'} or not rights.get('scope'):
        raise ValueError('Invalid rights status/scope')
    seconds=effort.get('active_seconds')
    if seconds is not None and (type(seconds) not in (int,float) or not math.isfinite(seconds) or seconds<0):
        raise ValueError('Effort must be measured nonnegative seconds or null')
    blockers=[]
    if record['state']!='qualified':blockers.append('NOT_QUALIFIED:'+record['state'])
    for group in ('source','provenance','dependencies','evidence'):
        if not record[group]:blockers.append('MISSING_'+group.upper())
        for item in record[group]:
            if not isinstance(item,dict) or not item.get('path') or not item.get('sha256'):
                raise ValueError('Binding requires path and sha256')
            try:
                if file_hash(safe_path(root,item['path']))!=item['sha256']:blockers.append('STALE:'+item['path'])
            except (KnowledgeError,OSError):blockers.append('MISSING_OR_UNSAFE:'+item['path'])
    if rights['status']!='verified_for_use':blockers.append('RIGHTS:'+rights['status'])
    if not rights.get('evidence_paths') or not set(rights['evidence_paths'])<=set(x['path'] for x in record['provenance']):
        blockers.append('UNBOUND_RIGHTS_EVIDENCE')
    if seconds is not None and not effort.get('evidence_path'):blockers.append('UNSOURCED_EFFORT')
    if effort.get('evidence_path') and effort['evidence_path'] not in {x['path'] for x in record['evidence']}:
        blockers.append('UNBOUND_EFFORT')
    for failure in record['failures']:
        if failure.get('status') not in {'open','closed','out_of_scope'} or not failure.get('id'):
            raise ValueError('Invalid failure')
        if failure['status']=='open':blockers.append('OPEN_FAILURE:'+failure['id'])
        if failure['status']!='open' and not failure.get('disposition_evidence'):
            blockers.append('UNSUPPORTED_DISPOSITION:'+failure['id'])
        elif failure.get('disposition_evidence') and failure['disposition_evidence'] not in {x['path'] for x in record['evidence']}:
            blockers.append('UNBOUND_DISPOSITION:'+failure['id'])
    if not record['tested_conditions']:blockers.append('NO_TESTED_CONDITIONS')
    if requested is None:blockers.append('NO_REQUESTED_USE')
    elif not isinstance(requested,dict) or not requested:raise ValueError('Requested use must be explicit')
    else:
        # Exact scoped matching: omission is not a wildcard and a new rig is
        # not admitted because an asset worked on a different rig.
        for key,value in requested.items():
            if record['tested_conditions'].get(key)!=value:blockers.append('UNTESTED_CONDITION:'+key)
        for key in record['tested_conditions']:
            if key not in requested:blockers.append('UNSPECIFIED_CONDITION:'+key)
    return {'schema_valid':True,'resource_id':record['id'],'reuse_admissible':not blockers,
            'blockers':blockers,'limit':'Hash/schema/scope checks only; manual rights and perceptual review still required.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('manifest');p.add_argument('--use',required=True)
    a=p.parse_args();root=Path(__file__).resolve().parents[2]
    record=json.loads(safe_path(root,a.manifest).read_text());requested=json.loads(safe_path(root,a.use).read_text())
    result=validate(root,record,requested);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['reuse_admissible'] else 2)
if __name__=='__main__':main()
