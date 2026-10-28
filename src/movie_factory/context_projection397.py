"""Narrow versioned status projection. No semantic field selection by a model."""
import json
from pathlib import Path
from . import production_knowledge as pk

PATH = 'docs/planning/RELEASE_01_STATUS.json'
COSMETIC = {'updated_date', 'substantive_exchange_count'}


def facts(value):
    return {k:v for k,v in value.items() if k not in COSMETIC}


def validate(root, binding):
    from .review_control import path, Blocked
    p = binding.get('projection397', {})
    if set(binding) != {'path','sha256','projection397'} or binding['path'] != PATH:
        raise Blocked('UNSUPPORTED_STATUS_PROJECTION397')
    if p.get('version') != 1 or set(p.get('excluded', [])) != COSMETIC:
        raise Blocked('STATUS_PROJECTION_FIELDS397')
    frozen=p.get('snapshot', {})
    if set(frozen) != {'path','sha256'} or pk.file_hash(path(root,frozen['path'])) != frozen['sha256']:
        raise Blocked('STALE_STATUS_SNAPSHOT397')
    baseline=json.loads(path(root,frozen['path']).read_text())
    current=json.loads(path(root,PATH).read_text())
    if pk.digest(facts(baseline)) != binding['sha256'] or facts(current) != facts(baseline):
        raise Blocked('STATUS_AUTHORITY_OR_FACTS_CHANGED397')


def bind(root):
    """Trusted explicit operation; does not amend an existing source pin."""
    root=Path(root); raw=(root/PATH).read_bytes()
    folder=root/'.runtime/context-projections397';folder.mkdir(parents=True,exist_ok=True)
    file=folder/(pk.file_hash(root/PATH)+'.json')
    if not file.exists():file.write_bytes(raw)
    return dict(path=PATH,sha256=pk.digest(facts(json.loads(raw))),projection397=dict(
        version=1,excluded=sorted(COSMETIC),snapshot=dict(path=str(file.relative_to(root)),sha256=pk.file_hash(file))))
