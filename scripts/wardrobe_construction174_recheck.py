"""Fixed fresh-open verification repair; no selected scene mutation or rebuild."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job,dict) or job!={'operation':'verify02'}:
        raise ValueError('Fixed verify02 operation only')
    out = BASE/'wardrobe174-verify02'
    if out.exists():raise ValueError('Never overwrite failed or selected evidence')
    binding_path = BASE/'wardrobe174-operating/source-binding.json'
    repair_path = BASE/'wardrobe174-operating/verification-binding.json'
    repair = json.loads(repair_path.read_text())
    import package_wardrobe_construction174 as package
    expected = {str(p.relative_to(ROOT)) for p in package.source_paths()}
    expected.update({'scripts/wardrobe_construction174_recheck.py',
                     'tests/unit/test_wardrobe_construction174_recheck.py'})
    rows = repair['source_files']
    if len(rows)!=len(expected) or {r['path'] for r in rows}!=expected:
        raise ValueError('Unexpected verification source paths')
    for row in rows:
        path = ROOT/row['path']
        if path.is_symlink() or sha(path)!=row['sha256']:
            raise ValueError('Verification source changed')
    assert not binding_path.is_symlink() and sha(binding_path)==repair['selected_binding_sha256']
    original = json.loads(binding_path.read_text())
    for row in original['inputs']:
        path = ROOT/row['path']; assert not path.is_symlink() and sha(path)==row['sha256']
    native = BASE/'wardrobe174-seal01/dressed-fit.blend'
    assert not native.is_symlink() and sha(native)==repair['selected_native_sha256']
    assert json.loads((native.parent/'result.json').read_text())['native_sha256']==sha(native)
    return out,original


def main():
    job = json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out,binding = validate(job);out.mkdir()
    import wardrobe_construction174 as construction
    from wardrobe_construction174_verify import verify
    construction.install()
    verify(out,BASE,construction.SOURCE,construction.SOURCE_SHA,binding)


if __name__=='__main__':main()
