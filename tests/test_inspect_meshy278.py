import importlib.util
import json
from pathlib import Path
import struct
import pytest

spec=importlib.util.spec_from_file_location('inspect_meshy278',Path(__file__).parents[1]/'scripts/inspect_meshy278.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def blob(doc):
    data=json.dumps(doc).encode();data+=b' '*(-len(data)%4)
    return struct.pack('<4sIIII',b'glTF',2,len(data)+20,len(data),0x4e4f534a)+data

@pytest.mark.parametrize('op',['inspect','reopen'])
def test_valid(op):assert m.validate({'operation':op})==op

@pytest.mark.parametrize('job',[{}, {'operation':'exec'}, {'operation':'inspect','path':'/tmp/x'}, None])
def test_invalid(job):
    with pytest.raises(ValueError):m.validate(job)

def test_embedded_data():assert m.glb_json(blob({'buffers':[{'byteLength':12}]}))['buffers'][0]['byteLength']==12

@pytest.mark.parametrize('group',['buffers','images'])
def test_reject_external(group):
    with pytest.raises(ValueError):m.glb_json(blob({group:[{'uri':'file:///private/secret'}]}))

def test_truncated():
    with pytest.raises(ValueError):m.glb_json(b'bad')

def test_source():
    assert m.sha(m.RAW)==m.EXPECTED
    assert m.glb_json(m.RAW.read_bytes())['asset']['version']=='2.0'
