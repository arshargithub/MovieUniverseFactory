"""Secret-screen tests use synthetic strings, never live credentials."""
import importlib.util
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import protect255 as p

def test_known_credential_classes():
    for data,kind in [(b'ASIA'+b'A'*16,'aws_temporary_access'),(b'AIza'+b'B'*35,'google_key'),(b'sk-'+b'C'*32,'provider_key'),(b'X-Amz-Signature='+b'a'*64,'signed_url'),(b'Bearer '+b'Z'*40,'bearer')]:
        assert kind in p.scan(data)

def test_no_values_in_scan_output():
    secret=b'sk-'+b'C'*32
    assert p.scan(secret)==['provider_key']

def test_unprefixed_provider_assignment():
    assert 'credential_assignment' in p.scan(b'runway_api_key='+b'Q'*40)
    assert 'credential_assignment' in p.scan(b'GEMINI_API_KEY="'+b'Q'*40+b'"')

def test_github_fine_grained_token_prefilter():
    assert 'github_token' in p.scan(b'github_' + b'pat_' + b'A'*40)

def test_false_positive_disposition_is_content_bound():
    from freeze_protect255 import reviewed_false_positive
    row={'sha256':'7519ee9c40d3b896db2212ce6647734d12d289568ea446a0d274a581d605ba55','paths':['.runtime/brushstroke-tools-1.2.3-inspection/icons/random.svg']}
    assert reviewed_false_positive(row,['provider_key'])
    assert not reviewed_false_positive({**row,'sha256':'changed'},['provider_key'])
    assert not reviewed_false_positive(row,['provider_key','github_token'])

def test_private_paths_excluded():
    for name in ['.env','.env.local','.aws/credentials','.runtime/a/private-link.txt','.runtime/protection255-restore/a','.runtime/protection255-frozen/a']:
        assert p.excluded(Path(name))
    assert not p.excluded(Path('.runtime/art-direction/series01-finish248/opening08/scene.blend'))

def test_scan_large_file_and_chunk_boundary(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'ROOT',tmp_path)
    f=tmp_path/'large.log'
    with f.open('wb') as out:
        out.write(b'x'*(8*1024*1024-2));out.write(b'sk-'+b'D'*40)
    row,flags=p.inspect_file(f)
    assert 'provider_key' in flags and row['bytes']>2_000_000

def test_independent_copy_and_refuse_overwrite(tmp_path):
    import pytest
    from freeze_protect255 import copy_independent,scanned
    src=tmp_path/'source';dst=tmp_path/'frozen';src.write_bytes(b'initial bytes')
    copy_independent(src,dst);initial=scanned(dst)
    src.write_bytes(b'changed source')
    assert dst.read_bytes()==b'initial bytes' and scanned(dst)==initial
    assert src.stat().st_ino!=dst.stat().st_ino
    with pytest.raises(RuntimeError,match='Refuse overwrite'):copy_independent(src,dst)
