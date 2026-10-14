import importlib
import sys
from pathlib import Path
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
d=importlib.import_module('finalize_protect255_delta')

def test_final_upload_refuses_credential_finding(monkeypatch,tmp_path):
    file=tmp_path/'receipt.json';file.write_text('{}')
    monkeypatch.setattr(d,'ROOT',tmp_path)
    monkeypatch.setattr(d,'scanned',lambda p:('a'*64,['provider_key']))
    monkeypatch.setattr(d.subprocess,'run',lambda *a,**kw:pytest.fail('Must not upload'))
    with pytest.raises(ValueError,match='Unscreened'):d.put(file,'test')

@pytest.mark.parametrize('remote',[(2,'b'*64),(3,'a'*64)])
def test_final_upload_requires_remote_bytes_and_digest(monkeypatch,tmp_path,remote):
    file=tmp_path/'receipt.json';file.write_text('{}')
    monkeypatch.setattr(d,'scanned',lambda p:('a'*64,[]))
    monkeypatch.setattr(d.subprocess,'run',lambda *a,**kw:None)
    monkeypatch.setattr(d,'stream_sha256',lambda *a:remote)
    with pytest.raises(ValueError,match='verification mismatch'):d.put(file,'test')

def test_final_upload_streams_after_checksum_upload(monkeypatch,tmp_path):
    file=tmp_path/'receipt.json';file.write_text('{}')
    calls=[]
    monkeypatch.setattr(d,'scanned',lambda p:('a'*64,[]))
    monkeypatch.setattr(d.subprocess,'run',lambda args,**kw:calls.append(args))
    monkeypatch.setattr(d,'stream_sha256',lambda *a:(2,'a'*64))
    d.put(file,'test')
    assert '--checksum-algorithm' in calls[0] and 'SHA256' in calls[0]
    assert '--delete' not in calls[0] and '--acl' not in calls[0]
