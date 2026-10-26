import copy,json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh376';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==134

def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
new=['src/movie_factory/adapters/blender/nihang_multiform376.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_horse_multiform376.py','results/sikh376/REJECT134.md','.runtime/context-hygiene/runs/sikh376-multiform-tests/stdout.log']
t=p.read_json(r,'results/sikh376/task134.json');t['id']='sikh376-multiform135'
for q in new:t['inputs'][q]=p.file_hash(r/q)
write('task135.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet135.json',packet)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh376/task135.json')
for row in src:b['source_bindings'][row['id']]=row['binding']
for q in new:b['source_bindings'][q]=bind(q)
b['source_bindings']['results/sikh376/task135.json']=bind('results/sikh376/task135.json');b.update(knowledge_task='results/sikh376/task135.json',knowledge_digest=packet['packet_digest']);b['work_unit']['edit_kinds']=['mounted_horse_multiform376','mounted_horseform374_inspect','mounted_horseform374_contact']
e=b['expert_plan'];e['realizations']['form']['derivation']='134actual339compacttarget is insufficient: applyingits restoffset at333producescrease.135solves independentposedtargets333339346 through eachactualdeformer, notgeneric339key. Actualtargetfit<=1mmat each, explicitinitialBasis plusraw/oldshape/actionpreservation. C1complementaryenvelopes; wholeforms andinterstitial336342actualimages veto.';e['realizations']['preservation']['derivation']='Original129source, no failed134stack; onlythree newposecorrectivekeys, alloldsourcegeometry/shapes/primaryactions exact. Separateanatomicalkeytargets remainshot-specific, standing0. Nap hiddenforincompletebodyproof; finalcoupling/contact/AVstillrequired.';e['challenge']['plan_digest']=ep.plan_digest(b);write('revised135-brief.json',b)
cfg=p.read_json(r,'results/sikh376/appearance-c134.json');cfg.update(brief_path='results/sikh376/revised135-brief.json',method='Originalsource, independent333339346posed chest targets and actualdeformer inversion, .5landingextent; each <=8fixedtargetnumericiterations. InitialkeycoordinatesexplicitBasis, exactoldgeometry/actions; C1zero-slopecomplementaryenvelopes, standingzero. No generic339inverse appliedatcrest.',proof='Actual333targetfirst, then336339342346 and283367: no pendantmass, crease/web, shouldercollapse orplate. Allthreeactualfits<=1mm andoldsourcepreservation. EarlybodyFAILstaysinternal. Complete3views/intended/contact/coat/fullspeed remainrequired.',cause='134singlepose339corrective causes333crease despitevalid339fit. Needpose-specificactualdeformermap andtarget ownership, not changeacceptedprimarymotion orreducequalityfloor.',expected='Connectedcompactchest throughcrest/descent/compression andsmoothtransitions, preservedstanding. No artisticguarantee fromnumericfit.',sources=list(dict.fromkeys(cfg['sources']+new)),retrospective_evidence=['results/sikh376/appearance-c135.json','results/sikh376/appearance-c135-challenge.json','results/sikh376/REQUEST.md','results/sikh376/STRATEGY.md','results/sikh376/REJECT134.md'])
cfg['steps'][0]['recipe']['edits']=[dict(kind='mounted_horse_multiform376',target='horse')]
for row in cfg['steps']:
 if row['id'] in ('worst','worstfront','side'):row['recipe']['frames']=[333,336,339,342,346,283,367]
write('appearance-c135.json',cfg)
ch=p.read_json(r,'results/sikh376/appearance-c134-challenge.json');ch['checks']['method']['observation']='Actual134crease rejected, notincrementalpass. Reviewednewclosedhandler independentlysolves eachpose withactualfit, explicitBasisinitialization andthree complementarycurves.32focusedtests pass; no anatomicalqualification fromfitting.';ch['checks']['interfaces']['observation']='Originalsource retained, oldraw/shapes/actions exact; finalcoat/contact interfaces unresolved. Interstitial336342mustshow no blendingcrease inadditionto5mandatoryposes, thenfull92frameproof.';ch['strongest_counterexample']='Independenttargetposescanlookgoodwhile336/342blendpinches orchangedchestintersectsnearforeleg/saddle. Actualinterstitialanglesandfinalmovingproof required; source/fittinghashes cannotqualifyshape.';write('appearance-c135-challenge.json',ch)
c.revise(task,b,bind('results/sikh376/REQUEST.md'),'134creaseFAIL;135independentphasecorrectives andinterstitialproof, samefivecycleallowance.','sikh376-multiform135',grounding=dict(context_sources=src,reason='Actual134333crease vs339positivepart, reviewednewclosedhandler/tests andexplicitposeownership. No new authority orprimarymotionchange.',evidence={'failure':bind('results/sikh376/REJECT134.md'),'tests':bind('.runtime/context-hygiene/runs/sikh376-multiform-tests/stdout.log')}));print(c.state(task)['cycle'])
