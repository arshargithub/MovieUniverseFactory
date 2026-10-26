"""Explicitly synthetic input contracts, never production reference judgments."""
from copy import deepcopy
from movie_factory import production_knowledge as pk,expert_planning as ep


def attach_transport(root,b):
    scope=dict(version=1,id='synthetic-transport',kind='production',needs=[dict(id='transport',purpose='technical_validation',question='Does mock save/reopen transport retain bound state?',critical=True,coverage=['mock transport'])])
    b['reference_readiness']=dict(version=1,scope=scope,decisions={'transport':dict(decision='none_needed',status='not_needed',reason='Synthetic deterministic transport fixture, no physical/artistic claim.',reopen_when='A real visual or motion claim is introduced.',references=[])})
    b['reference_mapping']={r['id']:['transport'] for r in b['requirements']};b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);return b


def challenge(ready):
    return dict(readiness_digest=pk.digest(ready),checks={k:dict(status='PASS',observation='Synthetic qualification decision inspected; not real audiovisual proof.',counterexample='A dishonest adequacy assertion is still possible.',evidence=[e for q in d['references'] for e in q['evidence']]) for k,d in ready['decisions'].items()})


def application(ready):
    return dict(readiness_digest=pk.digest(ready),aspects={k:'Synthetic explicit reference-purpose application' for k in ready['decisions']})


def review(ready):
    return dict(readiness_digest=pk.digest(ready),aspects={k:dict(status='PASS',observation='Synthetic bound-aspect comparison',comparison='Synthetic reference purpose, not artistic truth',evidence=['frame']) for k in ready['decisions']})
