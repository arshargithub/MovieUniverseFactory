"""Offline reconstruction of one task's observed intervals, not inferred labor."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.runtime/production-audit250'

def stamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()

def merge(intervals):
    out = []
    for a, b in sorted(intervals):
        if b <= a:
            continue
        if out and a <= out[-1][1]:
            out[-1][1] = max(b, out[-1][1])
        else:
            out.append([a, b])
    return out

def seconds(intervals):
    return sum(b-a for a,b in merge(intervals))

def clip(intervals, start, end):
    return [(max(a,start), min(b,end)) for a,b in intervals if b>start and a<end]

def subtract(intervals, excluded):
    pieces=merge(intervals)
    for x,y in merge(excluded):
        next_pieces=[]
        for a,b in pieces:
            if y<=a or x>=b:next_pieces.append((a,b))
            else:
                if a<x:next_pieces.append((a,x))
                if y<b:next_pieces.append((y,b))
        pieces=next_pieces
    return pieces

def paired_events(events, start_type, end_type, key):
    superseded={e['supersedes'] for e in events if e.get('supersedes')}
    starts={};pairs=[];unmatched=[]
    for e in events:
        if e['event_id'] in superseded:continue
        ident=(e['experiment_id'],e['episode_id'],e.get(key))
        if e['event_type']==start_type:
            if ident in starts:raise ValueError(f'Duplicate start {ident}')
            starts[ident]=e
        elif e['event_type']==end_type:
            a=starts.pop(ident,None)
            if a is None:unmatched.append(e)
            else:pairs.append((a,e))
    return pairs,list(starts.values()),unmatched

def read():
    return json.loads((OUT/'history.json').read_text())

def cases():
    d=read();msgs=d['messages'];rows=[]
    for i,m in enumerate(msgs):
        if i<333 or m['role']!='user':continue
        previous=next((x for x in reversed(msgs[:i]) if x['role']=='assistant' and x['phase']=='final_answer'),None)
        following=next((x for x in msgs[i+1:] if x['role']=='assistant' and x['phase']=='final_answer'),None)
        rows.append({'case':len(rows)+1,'message_index':i,**m,'previous_final':previous,'following_final':following})
    (OUT/'cases.json').write_text(json.dumps(rows,indent=2)+'\n')
    return rows

def packet():
    paths=['docs/knowledge/PASHTUN_PRODUCTION_AUDIT250.md', 'docs/engineering-intelligence/OPERATING_LEDGER.md', '.runtime/production-audit250/history.json']
    paths += ['docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_CASES.json','docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_METRICS.json','scripts/audit_pashtun250.py','scripts/audit250_metrics.py','scripts/audit250_classification.py','tests/unit/test_audit250_metrics.py']
    paths.append('.runtime/production-audit250/token-usage.json')
    task={'id':'audit250','operation':'knowledge','entities':['knowledge'], 'query':'retrospective review director handovers knowledge application time intervals operating ledger baseline metrics', 'intent':'Audit source-indexed Director inputs and observed time without charging Director idle gaps or inventing visual judgments.', 'phase':'planning','inputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},'open_decisions':[], 'hypotheses_to_test':['Process rules existed but application and visual judgment failed; retrieval alone does not repair this.','Task intervals and native jobs overlap and must not be summed as net elapsed time.']}
    (OUT/'task.json').write_text(json.dumps(task,indent=2)+'\n')

def metrics():
    d=read();boundary=stamp(d['messages'][3456]['timestamp'])
    starts={};complete=[];aborted=[];unmatched=[];duration_deltas=[];reported=[];anomalies=[]
    for e in d['task_events']:
        t=stamp(e['timestamp']);id=e['turn_id']
        if e['type']=='task_started':starts[id]=t
        elif id in starts:
            a=starts.pop(id)
            if t<a:raise ValueError('clock reversal')
            (complete if e['type']=='task_complete' else aborted).append((a,t,id))
            if e['duration_ms'] is not None:
                delta=(t-a)-e['duration_ms']/1000
                duration_deltas.append(abs(delta));reported.append((a,t,e['duration_ms']/1000,id))
                if abs(delta)>5:anomalies.append({'turn_id':id,'start':a,'end':t,'wall_seconds':t-a,'reported_seconds':e['duration_ms']/1000,'unexplained_delta_seconds':delta})
        else:unmatched.append(e)
    # Open turn is censored at the audit request, never fabricated complete.
    active=[(a,min(boundary,stamp(d['messages'][-1]['timestamp'])),id) for id,a in starts.items() if a<boundary]
    turns=complete+aborted+active
    conn=sqlite3.connect(f'file:{ROOT}/.runtime/experiment-ops.sqlite3?mode=ro',uri=True)
    events=[json.loads(x[0]) for x in conn.execute('select payload from events order by seq')];conn.close()
    (OUT/'operating-events.json').write_text(json.dumps(events,indent=2)+'\n')
    allowed={'SERIES01-LIKENESS-ASSET','SERIES01-MOTION-PREVIEW','SERIES01-FINISHED-UNIT','SERIES01-LOCAL-RENDER','REIN-214','KNOWLEDGE-213','AUDIO-220','MUSIC233','MUSIC-231','MUSIC231','FINISH237','FINISH242','FINISH243','FINISH245'}
    selected=[e for e in events if e['experiment_id'] in allowed]
    jobs,open_jobs,orphan_jobs=paired_events(selected,'job_started','job_completed','job_id')
    activities,open_activities,orphan_activities=paired_events(selected,'work_started','work_ended','activity_id')
    waits,open_waits,orphan_waits=paired_events(selected,'wait_started','wait_ended','wait_id')
    native=[];native_rows=[]
    for a,b in jobs:
        if a.get('job_kind')!='native':continue
        begin,end=stamp(a['utc']),stamp(b['utc'])
        if begin>=boundary:continue
        native.append((begin,min(end,boundary)))
        mono=(b['monotonic_seconds']-a['monotonic_seconds']) if a.get('clock_id')==b.get('clock_id') and a.get('clock_id') and isinstance(a.get('monotonic_seconds'),(int,float)) and isinstance(b.get('monotonic_seconds'),(int,float)) else None
        native_rows.append({'job_id':a['job_id'],'experiment':a['experiment_id'],'episode':a['episode_id'],'start':a['utc'],'end':b['utc'],'outcome':b.get('outcome') if end<=boundary else 'RUNNING_AT_CUTOFF','wall_seconds':min(end,boundary)-begin,'monotonic_seconds':mono if end<=boundary else None,'censored_at_cutoff':end>boundary})
    for a in open_jobs:
        if a.get('job_kind')=='native' and stamp(a['utc'])<boundary:
            # Do not presume an old orphan ran until today.
            if a['job_id']=='finish248-opening-final':native.append((stamp(a['utc']),boundary))
    profiles={}
    for name,idx in [('shared_visual_development',333),('individual_portrait_baseline',398)]:
        begin=stamp(d['messages'][idx]['timestamp']);intervals=clip([(a,b) for a,b,_ in turns],begin,boundary)
        relevant=[m for m in d['messages'][idx:] if stamp(m['timestamp'])<=boundary]
        native_clip=clip(native,begin,boundary);nr=[r for r in native_rows if stamp(r['end'])>begin]
        matched_activity=clip([(stamp(a['utc']),stamp(b['utc'])) for a,b in activities],begin,boundary)
        matched_wait=clip([(stamp(a['utc']),stamp(b['utc'])) for a,b in waits if a.get('reason') in ('director_response','next_prompt','user_pause')],begin,boundary)
        profiles[name]={'start':d['messages'][idx]['timestamp'],'cutoff':d['messages'][3456]['timestamp'],'calendar_seconds':boundary-begin,'observed_task_active_union_seconds':seconds(intervals),'reported_completed_task_runtime_seconds':sum(duration for a,b,duration,_ in reported if a>=begin-2 and b<=boundary),'open_task_observed_seconds':seconds(clip([(a,b) for a,b,_ in active],begin,boundary)),'outside_recorded_task_seconds':boundary-begin-seconds(intervals),'completed_turns':sum(a<boundary and b>begin for a,b,_ in complete),'aborted_turns':sum(a<boundary and b>begin for a,b,_ in aborted),'open_turns':sum(a<boundary and b>begin for a,b,_ in active),'user_inputs_raw':sum(m['role']=='user' for m in relevant),'assistant_final_messages':sum(m['phase']=='final_answer' for m in relevant),'native_matched_jobs':len(nr),'native_outcomes':dict(collections.Counter(r['outcome'] for r in nr)),'native_union_seconds':seconds(native_clip),'native_sum_seconds':sum(b-a for a,b in native_clip),'native_outside_tasks_seconds':seconds(subtract(native_clip,intervals)),'task_or_native_union_seconds':seconds(intervals+native_clip),'recorded_activity_union_seconds':seconds(matched_activity),'recorded_wait_union_seconds_untrusted':seconds(matched_wait),'wait_overlap_task_seconds_untrusted':seconds(intervals)-seconds(subtract(intervals,matched_wait)), 'task_intervals':merge(intervals)}
    result={'profiles':profiles,'task_pairing':{'completed':len(complete),'aborted':len(aborted),'open':starts,'unmatched':unmatched,'maximum_duration_ms_vs_timestamp_delta_seconds':max(duration_deltas),'anomalies_over_5_seconds':anomalies},'ledger_pairing':{'open_jobs':open_jobs,'orphan_job_ends':orphan_jobs,'open_activities':open_activities,'orphan_activity_ends':orphan_activities,'open_waits':open_waits,'orphan_wait_ends':orphan_waits},'native_jobs':native_rows,'caveats':['Observed task-active wall time includes reasoning, tools, rendering waits and any stalls inside a task; it is not active labor.','Outside-task gaps are excluded here, not all proven Director wait. Continuing native work is separately unioned.','This cutoff is the audit request, before current final render completion and before Director acceptance.','Retrospectively entered waits explicitly contain capture gaps; they are not a trustworthy exact idle-time subtraction.','Native job occupancy includes construction/simulation/render/replay, not pure render time.'], 'source_sha256':hashlib.sha256((OUT/'history.json').read_bytes()).hexdigest()}
    (OUT/'metrics-initial.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:{a:b for a,b in v.items() if a!='task_intervals'} for k,v in profiles.items()},indent=2));print('anomalies',len(anomalies),'open_jobs',len(open_jobs),'orphans',len(orphan_jobs))

def frame_costs():
    """Measured frame loops only; never infer frames from filenames/job names."""
    rows=[];seen=set();duplicate=0;reused=0
    # These handlers were inspected: their seconds fields surround frame
    # evaluation/render/write, not necessarily just the GPU kernel.
    prefixes=('entrance205-','entrance206-','entrance207-','entrance209-', 'entrance214-','entrance217-','entrance218-')
    for p in sorted((ROOT/'.runtime/art-direction').rglob('progress.json')):
        rel=str(p.relative_to(ROOT))
        if 'series01-finish248/' in rel:continue # active at historical cutoff
        if not (p.parent.name.startswith(prefixes) or any('/'+x+'/' in rel for x in ('series01-finish237','series01-finish245','series01-render210'))):continue
        data=json.loads(p.read_text())
        fs=data.get('frames',[])
        if not isinstance(fs,list):continue
        for f in fs:
            if not isinstance(f,dict):continue
            if f.get('reused_from') or f.get('reused'):
                reused+=1;continue
            duration=f.get('render_seconds',f.get('seconds'))
            if not isinstance(duration,(float,int)):continue
            if duration<0:raise ValueError('Negative frame duration')
            ident=(data.get('source_sha256'),f.get('index',f.get('frame')),f.get('sha256'),duration)
            if ident in seen:duplicate+=1;continue
            seen.add(ident)
            rows.append({'progress':rel,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frame':f.get('index',f.get('frame')),'seconds':duration,'kind':'render_call' if 'render_seconds' in f else 'frame_loop','image_sha256':f.get('sha256')})
    report={'scope':'Partial known-handler frame timing recovery. Excludes active248 and earlier uninstrumented asset work; no whole-history pure-render claim. Render/frame-loop times include evaluation/write as indicated and are process-seconds, not additive to task/native union. Identical copied timing records and explicit reused frames excluded.', 'frames':len(rows),'sum_seconds':sum(r['seconds'] for r in rows),'copied_records_excluded':duplicate,'reused_records_excluded':reused,'records':rows}
    (OUT/'frame-costs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))

def usage():
    """Read only per-response usage metadata within the existing snapshot."""
    history=read();begin=stamp(history['messages'][333]['timestamp']);end=stamp(history['messages'][3456]['timestamp'])
    fields=('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')
    responses={};duplicates=0;bad=[];offset=0
    with Path(history['source_path']).open('rb') as source:
        while offset<history['snapshot_bytes']:
            line=source.readline()
            if not line or offset+len(line)>history['snapshot_bytes']:break
            at=offset;offset+=len(line)
            if b'"type":"token_usage_record"' not in line[:220]:continue
            event=json.loads(line)
            if event.get('type')!='token_usage_record' or not begin<=stamp(event['timestamp'])<=end:continue
            p=event['payload']
            if p.get('thread_id')!='01a0878c-e7a2-75e0-873c-c31d97f879a1':raise ValueError('Wrong task usage')
            ident=p.get('response_id');u=p.get('usage',{})
            if not ident or any(not isinstance(u.get(k),int) or u[k]<0 for k in fields):
                bad.append(at);continue
            if u['input_tokens']+u['output_tokens']!=u['total_tokens'] or u['cached_input_tokens']>u['input_tokens'] or u['reasoning_output_tokens']>u['output_tokens']:
                raise ValueError(('Inconsistent usage',at))
            row={'timestamp':event['timestamp'],'turn_id':p.get('turn_id'),'response_id':ident,'source_byte_offset':at,'usage':{k:u[k] for k in fields}}
            if ident in responses:
                if responses[ident]['usage']!=row['usage']:raise ValueError('Conflicting duplicate usage')
                duplicates+=1;continue
            responses[ident]=row
    totals={k:sum(r['usage'][k] for r in responses.values()) for k in fields}
    cumulative_check=None
    if responses:
        selected=list(responses.values())
        with Path(history['source_path']).open('rb') as source:
            source.seek(selected[0]['source_byte_offset']);first=json.loads(source.readline())['payload']
            source.seek(selected[-1]['source_byte_offset']);last=json.loads(source.readline())['payload']
        if all(k in first.get('thread_token_usage',{}) and k in last.get('thread_token_usage',{}) for k in fields):
            delta={k:last['thread_token_usage'][k]-(first['thread_token_usage'][k]-first['usage'][k]) for k in fields}
            cumulative_check={'matches_per_response_sum':delta==totals,'thread_counter_delta':delta}
    result={'scope':'Recorded per-response Codex usage in fixed historical snapshot and first-image-to-audit interval; excludes cumulative turn/thread counters and all subsequent audit work.',
        'responses':len(responses),'distinct_turns':len({r['turn_id'] for r in responses.values()}),'duplicate_records_excluded':duplicates,'invalid_record_offsets':bad,'totals':totals,
        'uncached_input_tokens':totals['input_tokens']-totals['cached_input_tokens'],
        'cached_input_fraction':totals['cached_input_tokens']/totals['input_tokens'] if totals['input_tokens'] else None,
        'cumulative_cross_check':cumulative_check,
        'limitations':['Recorded token throughput is not unique text, plan quota percentage, billed API dollars or human labor.','Cached input is included in input; reasoning is included in output. Do not add subsets again.','Only emitted records are measured; completeness of unreported/failed provider requests is not certified.','No API-pricing conversion or inferred subscription allocation is made.'],
        'records':list(responses.values())}
    (OUT/'token-usage.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))

def publish():
    """Small portable baseline; detailed local captures stay out of Git."""
    from audit250_classification import STAGES
    raw=json.loads((OUT/'metrics-initial.json').read_text())
    classified=json.loads((ROOT/'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_CASES.json').read_text())
    frame=json.loads((OUT/'frame-costs.json').read_text())
    token_usage=json.loads((OUT/'token-usage.json').read_text())
    rows=classified['cases'];p=raw['profiles']['shared_visual_development']
    avoidable={r['prior_final_id'] for r in rows if r['avoidable_final_id']}
    defect_followed={r['prior_final_id'] for r in rows if 'defect_or_missed_requirement' in r['labels'] and r['fresh_final_since_prior_input']}
    stages=[]
    for lo,hi,name,lesson in STAGES:
        members=rows[lo-1:hi]
        begin=stamp(members[0]['timestamp'])
        end=stamp(rows[hi]['timestamp']) if hi<len(rows) else stamp(p['cutoff'])
        stages.append({'id':lesson,'name':name,'first_case':lo,'last_case':hi,
            'human_inputs':sum('system_handoff' not in r['labels'] for r in members),
            'labels':dict(collections.Counter(k for r in members for k in r['labels'])),
            'task_wall_seconds':seconds(clip(p['task_intervals'],begin,end))})
    report={
        'schema_version':1,'status':'HISTORICAL_SNAPSHOT_NOT_SEQUENCE_CLOSURE',
        'thread_id':'01a0878c-e7a2-75e0-873c-c31d97f879a1',
        'capture_sha256':raw['source_sha256'],'capture_bytes':9470427510,
        'source_prefix_sha256':read()['sha256_prefix'],
        'start_message_id':rows[0]['message_id'],'cutoff_message_id':rows[-1]['message_id'],
        'profiles':{name:{k:v for k,v in value.items() if k!='task_intervals'} for name,value in raw['profiles'].items()},
        'classification':{k:classified[k] for k in ('method','counts','human_inputs','distinct_avoidable_final_ids')},
        'handover_confidence':dict(collections.Counter(r['confidence'] for r in rows if r['avoidable_final_id'])),
        'handover_burden':{'fresh_final_messages_followed_by_defect_related_feedback':len(defect_followed),'overlap_with_avoidable_process_stops':len(avoidable&defect_followed),'union_not_all_wholly_unnecessary':len(avoidable|defect_followed),'qualification':'Defect-bearing review can also contain necessary creative decisions or planned listening; do not label the union wholly wasteful.'},
        'rates':{'defect_related_inputs_per_human_input':classified['counts']['defect_or_missed_requirement']/classified['human_inputs'],'repeat_related_inputs_per_human_input':classified['counts']['repeated_correction']/classified['human_inputs'],'avoidable_stops_per_assistant_final':classified['distinct_avoidable_final_ids']/p['assistant_final_messages']},
        'partial_frame_timings':{k:v for k,v in frame.items() if k!='records'},
        'recorded_codex_usage':{k:v for k,v in token_usage.items() if k!='records'},
        'stages':stages,'timing_anomalies_over_5_seconds':raw['task_pairing']['anomalies_over_5_seconds'],
        'unknowns':['Exact net human/agent effort after all in-turn wait subtraction','Whole-history pure render time','Distinct defect count and first-pass review acceptance rate','Director active review and music-discovery time','Unreported provider usage and engineering dollar cost or subscription quota allocation','Counterfactual hours saved by a better process'],
        'caveats':raw['caveats']+['Classifications overlap; input counts are not independent defects or visual review rounds.','The reported runtime sum and timestamp envelope disagree; neither establishes exact net working time.','Stage timing is chronological task occupancy, not discipline-specific labor or waste.'],
        'source_artifacts':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('history.json','metrics-initial.json','frame-costs.json','operating-events.json','token-usage.json')}
    }
    destination=ROOT/'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_METRICS.json'
    destination.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'stages':stages,'handover_confidence':report['handover_confidence']},indent=2))

def review():
    """Persist the agent's actual audit review, not a production visual pass."""
    import xml.etree.ElementTree as ET
    from movie_factory.production_knowledge import check_review
    packet_path=ROOT/'.runtime/knowledge-pilot213/audit250.json'
    p=json.loads(packet_path.read_text())
    tests=OUT/'tests.xml';suites=ET.parse(tests).getroot()
    if sum(int(s.get('tests',0)) for s in suites.iter('testsuite'))!=11 or any(int(s.get(k,0)) for s in suites.iter('testsuite') for k in ('failures','errors')):
        raise ValueError('Audit tests missing or failed')
    evidence_paths=['docs/knowledge/PASHTUN_PRODUCTION_AUDIT250.md','docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_CASES.json','docs/knowledge/PASHTUN_PRODUCTION_AUDIT250_METRICS.json','.runtime/production-audit250/tests.xml']
    evidence=[{'path':path,'sha256':hashlib.sha256((ROOT/path).read_bytes()).hexdigest()} for path in evidence_paths]
    observations={
        'authority':('process','Kept the requested retrospective local and separated legitimate choices from avoidable handovers.','No new paid service, upload, remote push or other-character production; current248 native work has separate prior authority.'),
        'strategy':('process','Used an exact-task capture, explicit classifications and interval reconstruction before writing conclusions.','Every292 input record maps to a stage/lesson; one generated transcript tail is excluded from291 human inputs.'),
        'visual_gate':('review','Reviewed source-linked feedback and handoff wording without claiming fresh historical-image or listening evidence.','Report distinguishes documented Director judgments, current still inspection and unperformed historical visual replay. No production visual pass follows from this audit.'),
        'anticipation':('review','Tested counting ambiguities, intermediate feedback, repeated transcript content, runtime disagreement and concurrent jobs.','44 unique avoidable final IDs split30 high/14 medium;93 defect-related inputs are not unique defects; nine clock anomalies and unreliable waits remain disclosed.'),
        'stopping':('review','Completed source-indexed findings and a prospective scorecard rather than inventing exact net effort or saved hours.','Audit deliverable is complete at a fixed cutoff;248 sequence closure remains separate and pending, with accepted quality unchanged.'),
        'versioning':('technical','Bound scripts, report, cases, metrics and source capture in the fresh task packet.','Stable message IDs/offsets and snapshot prefix/extract hashes are retained. Existing native originals and failed evidence remain unchanged by audit.'),
        'economics':('process','Unioned task/native intervals, excluded between-task idle and separately reported partial render-loop process time.','Approximately145h reported runtime is provisional;87.9h native occupancy overlaps it. Exact net labor, complete render time and usage cost remain unknown.'),
        'retrieval':('technical','Read the fresh eight-obligation packet and reconciled manual history beyond its finite corpus.','The audit is not automatically covered by the nine-source pilot; AGENTS now requires applicable AU lessons at new work-package start. Retrieval correctness is separated from perceptual judgment.')}
    checks=[{'id':key,'kind':kind,'status':'PASS','action_taken':action,'observation':observation,'evidence':evidence} for key,(kind,action,observation) in observations.items()]
    r={'packet_digest':p['packet_digest'],'scope':'Source-indexed retrospective and qualified metrics only; no character/audio/sequence acceptance.', 'checks':checks,
       'hypotheses':[{'prediction':'Known requirements can still fail through application and visual judgment.','observation':'Repeated fist, neck and garment feedback persisted despite recorded rules.','response':'Separate requirement/retrieval/method/evidence/judgment causes and require actual review evidence.','result':'resolved'},
        {'prediction':'Summing jobs and calendar intervals would inflate net work.','observation':'Native jobs overlap tasks; reported runtime differs from timestamp spans and waits contain capture gaps.','response':'Publish distinct measured views, exclude outside-task idle, retain unknown exact net effort.','result':'resolved'}],
       'adjacent_regressions':'Preserved legitimate creative authority, early budget boundaries, intermediate versus final feedback, current unfinished native scope, source privacy and local-only durability. Eleven accounting/coverage tests pass, including recorded-token subset arithmetic and cumulative cross-check; no artistic judgment accuracy claim.',
       'stopping_reason':'Every in-scope input classified with provenance; report and repeatable baseline complete with uncertainty. Additional database/semantic platform or inferred time saved would not improve this scoped answer.'}
    (OUT/'review.json').write_text(json.dumps(r,indent=2)+'\n')
    result=check_review(ROOT,p,r)
    (OUT/'gate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not result.get('ready_for_review'):raise ValueError('Audit evidence gate blocked')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['cases','packet','metrics','frame_costs','usage','publish','review']);args=p.parse_args();globals()[args.mode]()
