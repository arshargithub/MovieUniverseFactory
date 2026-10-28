import copy
import hashlib
import json
from pathlib import Path
import pytest
from movie_factory import active_backup397 as b


class Fake:
    def __init__(self):self.objects={};self.versions=[];self.deleted=[];self.fail=False
    def inventory(self,prefix):return {k:{'Key':k,'Size':len(v)} for k,v in self.objects.items() if k.startswith(prefix)}
    def put(self,path,key,digest=None):
        data=Path(path).read_bytes();self.objects[key]=data
        self.versions.append(dict(Key=key,VersionId=str(len(self.versions)),Size=len(data),IsLatest=True))
        return {}
    def get(self,key,path):
        if self.fail:raise ValueError('Restore failed')
        Path(path).write_bytes(self.objects[key]);return {}
    def call(self,op,**kwargs):
        if op=='list-object-versions':return dict(Versions=copy.deepcopy(self.versions))
        if op=='delete-objects':
            for x in kwargs['delete']['Objects']:
                self.deleted.append(x)
                self.versions=[v for v in self.versions if (v['Key'],v['VersionId'])!=(x['Key'],x['VersionId'])]
                if not any(v['Key']==x['Key'] for v in self.versions):self.objects.pop(x['Key'],None)
            return {}
        raise AssertionError(op)


@pytest.fixture
def recovery(tmp_path):
    client=Fake();snap='new';data=b'Native file proof';digest=hashlib.sha256(data).hexdigest();objkey=b.key(digest)
    manifest=dict(schema_version=2,snapshot_id=snap,git_head='fixture',path_count=1,unique_bytes=len(data),
        objects=[dict(key=objkey,sha256=digest,bytes=len(data),paths=['native.blend'])])
    b.save(tmp_path/'manifest.json',manifest);mk=b.SNAPSHOTS+snap+'/manifest.json'
    client.put(tmp_path/'manifest.json',mk);client.objects[objkey]=data
    client.versions.append(dict(Key=objkey,VersionId='body',Size=len(data),IsLatest=True))
    b.save(tmp_path/'uploaded.json',dict(manifest_key=mk,manifest_sha256=b.sha(tmp_path/'manifest.json')))
    old=b.SNAPSHOTS+'old/manifest.json';client.objects[old]=b'old';client.versions.append(dict(Key=old,VersionId='old',Size=3,IsLatest=True))
    return client,tmp_path,objkey


def test_failed_restore_never_deletes_previous(recovery):
    c,p,_=recovery;c.fail=True
    with pytest.raises(ValueError):b.verify(c,p)
    with pytest.raises((ValueError,FileNotFoundError)):b.retention_plan(c,p)
    assert not c.deleted


def test_keep_one_deletes_only_old_and_preserves_shared_payload(recovery):
    c,p,k=recovery;b.verify(c,p);plan=b.retention_plan(c,p)
    assert all(x['Key']!=k for x in plan['delete'])
    result=b.cleanup(c,p)
    assert result['one_active_generation'] and k in c.objects
    assert {x['Key'] for x in c.deleted}=={b.SNAPSHOTS+'old/manifest.json'}


def test_tampered_plan_cannot_delete_latest_payload(recovery):
    c,p,k=recovery;b.verify(c,p);plan=b.retention_plan(c,p)
    plan['delete'].append(dict(Key=k,VersionId='body',bytes=17));b.save(p/'retention-plan.json',plan)
    with pytest.raises(ValueError,match='REFERENCED_COPY'):b.cleanup(c,p)
    assert not c.deleted


def test_noncurrent_duplicate_body_versions_are_removed(recovery):
    c,p,k=recovery;c.versions.append(dict(Key=k,VersionId='obsolete',Size=17,IsLatest=False))
    b.verify(c,p);plan=b.retention_plan(c,p)
    assert any(x['VersionId']=='obsolete' for x in plan['delete'])
    b.cleanup(c,p);assert k in c.objects


def test_archive_references_prevent_payload_gc(recovery):
    c,p,_=recovery;data=b'archive';digest=hashlib.sha256(data).hexdigest();key=b.key(digest)
    c.objects[key]=data;c.versions.append(dict(Key=key,VersionId='arch',Size=7,IsLatest=True))
    c.objects['movie-factory/history/closed/manifest.json']=json.dumps(dict(schema_version=1,objects=[dict(sha256=digest)])).encode()
    b.verify(c,p);plan=b.retention_plan(c,p)
    assert key not in {x['Key'] for x in plan['delete']}


def test_unknown_retained_archive_schema_blocks_gc(recovery):
    c,p,_=recovery;c.objects['movie-factory/history/closed/manifest.json']=b'{}'
    b.verify(c,p)
    with pytest.raises(ValueError,match='UNKNOWN_RETAINED'):b.retention_plan(c,p)
    assert not c.deleted


@pytest.mark.parametrize('path',['.env','.env.local','dir/secret.env','.aws/config','.git/config','.runtime/backup397/copy','x/id_rsa'])
def test_sensitive_or_staging_paths_excluded(path):assert b.excluded(path)


def test_native_runtime_assets_not_excluded():
    assert not b.excluded('.runtime/factory-native/master/scene.blend')
    assert not b.excluded('.runtime/art-direction/accepted/clip.mp4')
    assert not b.excluded('.env.example')


def test_prepare_captures_consistent_database_and_no_secrets(tmp_path):
    import sqlite3
    root=tmp_path/'project';root.mkdir();(root/'.env').write_text('SECRET')
    with sqlite3.connect(root/'state.sqlite3') as c:c.execute('CREATE TABLE demo(x)');c.execute('INSERT INTO demo VALUES(1)')
    # No Git repository needed for this filesystem-only test.
    from unittest.mock import patch
    class R:stdout='fake-head\n'
    with patch.object(b.subprocess,'run',return_value=R()):m=b.prepare(root,tmp_path/'work',snapshot_id='fixture')
    assert {x['path'] for x in m['paths']}=={'state.sqlite3'}
    with sqlite3.connect(m['objects'][0]['source']) as c:assert c.execute('SELECT x FROM demo').fetchone()==(1,)


def test_bulk_upload_uses_checksum_transfer_without_delete(tmp_path,monkeypatch):
    import types
    c=Fake();c.profile='fixture';source=tmp_path/'source';source.write_bytes(b'new native')
    digest=b.sha(source);st=source.stat();o=dict(key=b.key(digest),sha256=digest,bytes=st.st_size,
       paths=['native.blend'],source=str(source),stat=[st.st_size,st.st_mtime_ns,st.st_ctime_ns])
    m=dict(schema_version=2,snapshot_id='new',git_head='fixture',path_count=1,unique_bytes=st.st_size,objects=[o])
    b.save(tmp_path/'manifest-local.json',m);b.save(tmp_path/'manifest.json',m)
    monkeypatch.setattr(b,'inspect_controls',lambda c:{'mock':True})
    original=c.inventory
    def inventory(prefix):return {k:dict(v,ChecksumAlgorithm=['SHA256']) for k,v in original(prefix).items()}
    c.inventory=inventory
    def run(cmd,**kwargs):
        assert '--checksum-algorithm' in cmd and '--delete' not in cmd
        c.objects[o['key']]=source.read_bytes()
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(b.subprocess,'run',run)
    assert b.upload_bulk(c,tmp_path)['verified']
    assert not c.deleted


def test_bulk_failure_retains_previous_backup(tmp_path,monkeypatch):
    import types
    c=Fake();c.profile='fixture';b.save(tmp_path/'manifest-local.json',dict(objects=[]))
    monkeypatch.setattr(b,'inspect_controls',lambda c:{})
    monkeypatch.setattr(b.subprocess,'run',lambda *a,**k:types.SimpleNamespace(returncode=1))
    with pytest.raises(ValueError,match='RETAIN_OLD_BACKUP'):b.upload_bulk(c,tmp_path)
    assert not c.deleted and not (tmp_path/'uploaded.json').exists()


@pytest.mark.parametrize('large',[False,True])
def test_bulk_validates_frozen_bytes_not_live_or_hardlink_ctime(tmp_path,monkeypatch,large):
    import types
    c=Fake();c.profile='fixture';source=tmp_path/'source'
    source.write_bytes(b'a'*(16*1024**2+1 if large else 20));digest=b.sha(source);st=source.stat()
    o=dict(key=b.key(digest),sha256=digest,bytes=st.st_size,paths=['native.blend'],
      source=str(source),stat=[st.st_size,st.st_mtime_ns,st.st_ctime_ns])
    m=dict(schema_version=2,snapshot_id='new',git_head='fixture',path_count=1,unique_bytes=st.st_size,objects=[o])
    b.save(tmp_path/'manifest-local.json',m);b.save(tmp_path/'manifest.json',m)
    monkeypatch.setattr(b,'inspect_controls',lambda c:{})
    original=c.inventory
    c.inventory=lambda p:{k:dict(v,ChecksumAlgorithm=['SHA256']) for k,v in original(p).items()}
    def run(cmd,**kwargs):
        frozen=tmp_path/'transfer-payload'/digest[:2]/digest
        c.objects[o['key']]=frozen.read_bytes()
        if not large:source.write_bytes(b'Post-freeze edit to a live file')
        else:assert source.stat().st_nlink>=2
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(b.subprocess,'run',run)
    assert b.upload_bulk(c,tmp_path)['verified']


def test_bulk_mutated_frozen_payload_never_publishes_manifest(tmp_path,monkeypatch):
    import types
    c=Fake();c.profile='fixture';source=tmp_path/'source';source.write_bytes(b'original')
    digest=b.sha(source);st=source.stat();o=dict(key=b.key(digest),sha256=digest,bytes=st.st_size,
      paths=['native.blend'],source=str(source),stat=[st.st_size,st.st_mtime_ns,st.st_ctime_ns])
    b.save(tmp_path/'manifest-local.json',dict(objects=[o]));monkeypatch.setattr(b,'inspect_controls',lambda c:{})
    original=c.inventory;c.inventory=lambda p:{k:dict(v,ChecksumAlgorithm=['SHA256']) for k,v in original(p).items()}
    def run(*a,**k):
        frozen=tmp_path/'transfer-payload'/digest[:2]/digest;c.objects[o['key']]=frozen.read_bytes();frozen.write_bytes(b'changed!')
        return types.SimpleNamespace(returncode=0)
    monkeypatch.setattr(b.subprocess,'run',run)
    with pytest.raises(ValueError,match='FROZEN_PAYLOAD_CHANGED'):b.upload_bulk(c,tmp_path)
    assert not (tmp_path/'uploaded.json').exists() and not c.deleted
