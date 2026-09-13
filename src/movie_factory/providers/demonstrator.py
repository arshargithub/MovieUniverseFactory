"""Bounded paid engineering proposals for Demonstrator 01; never execute outputs."""
import json
from pathlib import Path
from ..budget import BudgetLedger
from ..settings import load_settings
from ..packages import atomic_json
from .openai_provider import OpenAIProvider

CATEGORIES = {'feasibility':10,'implementation':40,'critique':15,'direction':20,'contingency':15}

def ledger(repo):
    return BudgetLedger(repo/'.runtime/demonstrator-01-api.jsonl',100,scope_limits=CATEGORIES,
        stage_limits={'api':(100,60)},request_limit=60,request_ceiling_usd=5,work_item_attempt_limit=3,additional_campaign_ceiling_usd=50)

def access(repo):
    settings=load_settings(repo)
    if not settings.get('OPENAI_API_KEY'):return {'credential_present':False,'models':[]}
    from openai import OpenAI
    client=OpenAI(api_key=settings['OPENAI_API_KEY'],base_url='https://api.openai.com/v1',max_retries=0,timeout=30)
    try:
        names={m.id for m in client.models.list()}
        return {'credential_present':True,'models':[m for m in ('gpt-6-astra','gpt-5.6-sol') if m in names]}
    except Exception as e:return {'credential_present':True,'error':type(e).__name__,'http_status':getattr(e,'status_code',None)}

def call(repo, *, work_item, model, effort, category, prompt, max_output_tokens=4096, images=None):
    if model not in ('gpt-6-astra','gpt-5.6-sol') or effort not in ('medium','high') or category not in CATEGORIES:
        raise ValueError('Unapproved route')
    images=[Path(p).resolve() for p in (images or [])]
    if len(images)>8 or any(not p.is_file() or repo.resolve() not in p.parents or p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp') for p in images):
        raise ValueError('Only selected local project images are admitted')
    settings=load_settings(repo);settings.update(MF_PLANNER_MODEL=model,MF_VISION_MODEL=model,
        MF_PLANNER_REASONING_EFFORT=effort,MF_VISION_REASONING_EFFORT=effort,MF_COST_SCOPE=category,
        MF_LLM_MAX_OUTPUT_TOKENS=16000,MF_API_TIMEOUT_SECONDS=300)
    books=json.loads((repo/'feasibility/demonstrator-01/pricebook.json').read_text())['bounding_pricebooks']
    budget=ledger(repo);out=repo/'runs/demonstrator-01/api';out.mkdir(parents=True,exist_ok=True)
    provider=OpenAIProvider(settings,budget,out,pricebooks=books)
    schema={'type':'object','additionalProperties':False,'properties':{'result':{'type':'string'}},'required':['result']}
    response=provider.generate_json(purpose=work_item,prompt=prompt,schema=schema,images=images,run_id='demonstrator-01',stage='api',max_output_tokens=max_output_tokens)
    response['reconciliation_status']='CONSERVATIVE_CALCULATED_ESTIMATE_NOT_PROVIDER_INVOICE'
    identity=response.get('reservation_id')
    if identity:atomic_json(out/(identity+'.json'),response)
    return response
