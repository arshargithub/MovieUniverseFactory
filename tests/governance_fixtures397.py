"""Explicit synthetic migration/contract fixtures; never production authority."""
from movie_factory import production_governance as gov, production_knowledge as pk


def binding(root, name='authority.md'):
    return dict(path=name,sha256=pk.file_hash(root/name))


def attach(root, controller, brief, *, recipes=None, task='t'):
    authority=binding(root)
    for name,kind,parent in [('release','release',None),('milestone','milestone','release'),
                              ('capability','capability','milestone'),('family','family','capability')]:
        controller.governance(task,'node',dict(id=name,kind=kind,parent=parent,limit=100,
            purpose='Synthetic bounded qualification',authority=authority),name+'-node')
    state=controller.state(task)
    controller.governance(task,'migrate',dict(task=task,state_digest=pk.digest(state),authority=authority,
        baseline_slots=state['cycle'],original_limit=state['max_corrections'],features=['appearance','temporal'],
        historical_age={'appearance':0,'temporal':0},history_evidence={'fixture':authority},unknowns=[],
        profile=gov.DEFAULTS,node='family',remaining_allocation=state['max_corrections']),'fixture-migrate')
    scope=dict(question='Does this source preserve the controlled fixture?',first_operation='proof',
        success_next='Inspect the next bound output',failure_next='Reject and replan',
        smaller_proof='One actual bound output',coupling_counterexample='Synthetic loss of source state',
        discriminator='Compare source and returned output',decision='keep',prerequisites=[],
        changes=[dict(domain='source',control='one controlled native operation')],
        invariants=[dict(owner='consumer',condition='Preserve synthetic source')],evidence={'source':authority})
    criteria=[]
    for r in brief['requirements']:
        criteria.append(dict(id=r['id'],critical=True,kind='judgment',anchor=r['criterion'],assessor='Director' if r['director_av'] else 'agent',
            coordinate_space='synthetic',profile='fixture',invalidation='Any candidate change',references=[brief['references'][0]['id']],
            cells=['playback' if r['director_av'] else 'front'],human_av=r['director_av'],threshold=None,comparator=None))
    ops=[dict(id=name,**{'class':'control'},requires=[] if name=='proof' else ['transport'],
        produces=['transport'],prerequisite_steps=[] if name=='proof' else ['proof'],
        recipe=(recipes or {}).get(name)) for name in ['proof','build']]
    brief['production_contract397']=dict(version=1,family='family',capability='capability',criteria=criteria,
        feature_map={r['id']:[r['id']] for r in brief['requirements']},scope=scope,operations=ops)
    return brief


def checks(brief, result):
    result['contract_checks397']=[]
    for old in result['checks']:
        criterion=next(c for c in brief['production_contract397']['criteria'] if c['id']==old['id'])
        result['contract_checks397'].append(dict(id=old['id'],status=old['status'],observation=old['observation'],
            cells=[dict(id=cell,status=old['status'],evidence=old['evidence']) for cell in criterion['cells']]))
    return result
