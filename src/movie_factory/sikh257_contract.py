"""Bounded local Sikh development operations; no executable job input."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.runtime/art-direction/series01-sikh257'
SOURCES = {
    '.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend': '3c121505651140ceb4d69fd1d8923f7788ffadd81672f5be14845a5f2c75c137',
    '.runtime/assets/demonstrator-01/horse.blend': 'b848037332fe62064989f250a94faa04c75e3fb21ae93f6a100f19079c1b21aa',
}
OPS = ('inspect', 'cloth_control', 'cloth_self_off', 'cloth_rest_off', 'cloth_contact_off', 'cloth_free', 'cloth_proxy', 'cloth_release', 'layout', 'layout_stills', 'layout_eevee_stills', 'layout_eevee')
OPS += ('hero', 'facebuilder_status')
HERO_SOURCES = {'.runtime/assets/series01-sikh261-turban/sikh_turban.glb':'7cd1afb48a62bbbac8a71cdc59da22a5fd8c07addfac5ddb8f80f49f0653eecb'}
LAYOUT_CACHE = '.runtime/art-direction/series01-sikh257/cloth_release-03/evaluated-cloth.npz'
LAYOUT_CACHE_SHA = 'd8cc6ec0b94eb21b2a3ea0260e28dc55a604383b05ae7314bcde0b0307d7e006'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(job, root=ROOT):
    if not isinstance(job, dict) or set(job) != {'operation','attempt'}:
        raise ValueError('Only operation and bounded integer attempt permitted')
    if job['operation'] not in OPS or type(job['attempt']) is not int or not 1 <= job['attempt'] <= 99:
        raise ValueError('Unadmitted operation/attempt')
    for relative, expected in SOURCES.items():
        p = root/relative
        if p.is_symlink() or p.resolve() != p.absolute() or digest(p) != expected:
            raise ValueError('Pinned input mismatch: '+relative)
    if job['operation']=='hero':
        for relative,expected in HERO_SOURCES.items():
            p=root/relative
            if p.is_symlink() or digest(p)!=expected:raise ValueError('Hero source mismatch')
    if job['operation'].startswith('layout'):
        p=root/LAYOUT_CACHE
        if p.is_symlink() or digest(p)!=LAYOUT_CACHE_SHA:raise ValueError('Cloth derivative changed')
    out=root/'.runtime/art-direction/series01-sikh257'/f"{job['operation']}-{job['attempt']:02d}"
    if out.exists() or out.parent.is_symlink():
        raise ValueError('Never overwrite evidence or redirect output')
    return out
