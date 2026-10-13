"""Read only exact task history; export messages/timings, never reasoning/tools/secrets."""
import collections, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/adisharma/.codex/sessions/2026/09/09/rollout-2026-09-09T15-02-33-01a0878c-e7a2-75e0-873c-c31d97f879a1.jsonl')
OUT=ROOT/'.runtime/production-audit250'

def redact(text):
    text=re.sub(r'\b(?:sk-|AIza)[A-Za-z0-9_\-]{20,}', '[REDACTED_KEY]',text)
    text=re.sub(r'(?i)(bearer\s+)[A-Za-z0-9_.\-]{20,}',r'\1[REDACTED]',text)
    text=re.sub(r'(?i)((?:api[_-]?key|access[_-]?token|secret[_-]?key)\s*[=:]\s*)[^\s,;]{12,}',r'\1[REDACTED]',text)
    return text

def content_text(value):
    if isinstance(value,str):return value
    if isinstance(value,list):return '\n'.join(x.get('text','') for x in value if isinstance(x,dict) and 'text' in x)
    return ''

def capture():
    OUT.mkdir(exist_ok=False)
    limit=SOURCE.stat().st_size; sha=hashlib.sha256();types=collections.Counter();items=collections.Counter()
    messages={};tasks=[];tools={};contexts=[];bad=[];offset=0
    with SOURCE.open('rb') as f:
        while offset<limit:
            line=f.readline()
            if not line:break
            if offset+len(line)>limit:break
            at=offset;offset+=len(line);sha.update(line)
            try:r=json.loads(line)
            except (ValueError,UnicodeError):bad.append(at);continue
            types[r.get('type')]+=1;p=r.get('payload',{})
            if r.get('type')=='turn_context':
                contexts.append({k:p.get(k) for k in ('turn_id','model','effort')})
            if r.get('type')!='event_msg':continue
            if p.get('type') in ('task_started','task_complete','turn_aborted'):
                tasks.append({'timestamp':r.get('timestamp'),**{k:p.get(k) for k in ('type','turn_id','started_at','completed_at','duration_ms','reason')}})
            if p.get('type')!='item_completed':continue
            it=p.get('item',{});kind=it.get('type');items[kind]+=1
            meta={'id':it.get('id'),'turn_id':p.get('turn_id'),'timestamp':r.get('timestamp'),'source_byte_offset':at,'started_at_ms':p.get('started_at_ms'),'completed_at_ms':p.get('completed_at_ms')}
            if kind in ('UserMessage','AgentMessage'):
                text=content_text(it.get('content',it.get('text','')))
                messages[it['id']]={**meta,'role':'user' if kind=='UserMessage' else 'assistant','phase':it.get('phase'),'text':redact(text)}
            elif kind not in ('Reasoning',None):
                tools[it.get('id',str(at))]={**meta,'kind':kind,'server':it.get('server'),'tool':it.get('tool'),'status':it.get('status')}
    data={'source_path':str(SOURCE),'snapshot_bytes':offset,'sha256_prefix':sha.hexdigest(),'source_size_at_start':limit,'malformed_offsets':bad,'record_types':dict(types),'item_types':dict(items),'messages':list(messages.values()),'task_events':tasks,'tool_events':list(tools.values()),'model_contexts':contexts,'limits':'Exact task only; no reasoning, tool arguments/results, images or credential files copied. Current task remains open. Recorded task/tool intervals are not yet net effort.'}
    (OUT/'history.json').write_text(json.dumps(data,indent=2)+'\n')
    with (OUT/'dialogue.md').open('w') as f:
        for i,m in enumerate(data['messages']):
            f.write(f"\n## {i} {m['role']} {m['phase']} {m['timestamp']} {m['turn_id']}\n\n{m['text']}\n")
    print(json.dumps({'bytes':offset,'messages':len(messages),'tasks':len(tasks),'tools':len(tools),'item_types':dict(items),'malformed':len(bad)}))

if __name__=='__main__':capture()
