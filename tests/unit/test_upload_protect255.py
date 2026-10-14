import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from upload_protect255 import object_key

def test_fixed_content_address():
    assert object_key('a'*64)=='movie-factory/backup/objects/sha256/aa/'+'a'*64

@pytest.mark.parametrize('bad',['../x','a'*63,'A'*64,'a'*64+'\n',''])
def test_reject_invalid_content_address(bad):
    with pytest.raises(ValueError):object_key(bad)

@pytest.mark.parametrize('bad',['../outside','/tmp/out','a/../../out',''])
def test_restore_path_rejection(bad):
    from restore_protect255_remote import safe_destination
    with pytest.raises(ValueError):safe_destination(bad)

def test_restore_is_separate():
    from restore_protect255_remote import safe_destination,DEST
    assert safe_destination('.runtime/scene.blend')==DEST/'.runtime/scene.blend'
