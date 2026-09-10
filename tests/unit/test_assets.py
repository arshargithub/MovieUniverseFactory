import hashlib
import zipfile

import pytest

from movie_factory.assets import prepare_assets


def manifest(archive, member="model.glb", payload=b"glb"):
    return {"schema_version":"1.0","experiment_id":"3D-02","assets":[
        {"asset_id":asset_id,"archive_filename":archive.name,"archive_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),
         "members":[{"archive_path":member,"sha256":hashlib.sha256(payload).hexdigest()}]}
        for asset_id in ("motorcycle","sword","environment")
    ]}


def test_prepare_assets_verifies_and_stages_only_selected_members(tmp_path):
    archive=tmp_path/"source.zip"
    with zipfile.ZipFile(archive,"w") as package:
        package.writestr("model.glb",b"glb")
        package.writestr("ignored.txt",b"ignored")
    result=prepare_assets(tmp_path,manifest(archive),tmp_path/"staged")
    assert result["selected_bytes"]==9
    assert len(result["artifacts"])==3
    assert not list((tmp_path/"staged").rglob("ignored.txt"))


@pytest.mark.parametrize("member",["../escape.glb","/absolute.glb"])
def test_prepare_assets_rejects_unsafe_selected_member(tmp_path,member):
    archive=tmp_path/"source.zip"
    with zipfile.ZipFile(archive,"w") as package: package.writestr(member,b"glb")
    with pytest.raises(ValueError): prepare_assets(tmp_path,manifest(archive,member),tmp_path/"staged")


def test_prepare_assets_rejects_archive_digest_mismatch(tmp_path):
    archive=tmp_path/"source.zip"
    with zipfile.ZipFile(archive,"w") as package: package.writestr("model.glb",b"glb")
    value=manifest(archive); value["assets"][1]["archive_sha256"]="0"*64
    with pytest.raises(ValueError): prepare_assets(tmp_path,value,tmp_path/"staged")


def test_prepare_assets_accepts_single_3d03_source(tmp_path):
    archive=tmp_path/"character.zip"
    with zipfile.ZipFile(archive,"w") as package:
        package.writestr("model.fbx",b"model")
        package.writestr("clip.fbx",b"clip")
    payload={
        "schema_version":"1.0","experiment_id":"3D-03","assets":[{
            "asset_id":"character_source_01","archive_filename":"character.zip",
            "archive_sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"members":[
                {"archive_path":"model.fbx","sha256":hashlib.sha256(b"model").hexdigest()},
                {"archive_path":"clip.fbx","sha256":hashlib.sha256(b"clip").hexdigest()},
            ],
        }],
    }
    result=prepare_assets(tmp_path,payload,tmp_path/"staged")
    assert result["experiment_id"]=="3D-03"
    assert len(result["artifacts"])==2
