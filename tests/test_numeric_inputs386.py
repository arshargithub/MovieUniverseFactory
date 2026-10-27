import importlib.util
from pathlib import Path
import hashlib
import pytest
s=importlib.util.spec_from_file_location('numeric386',Path(__file__).resolve().parents[1]/'scripts/sikh386_numeric_run.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def test_inputs_must_be_declared_bound_and_current(tmp_path):
 script=tmp_path/'scripts/anatomy386_test.py';script.parent.mkdir();script.write_text('pass\n');data=tmp_path/'input.npz';data.write_bytes(b'opaque arrayfixture')
 def b(p):return dict(path=str(p.relative_to(tmp_path)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 a,d=b(script),b(data);brief=dict(source_bindings={'script':a,'data':d});step=dict(numeric_script=a,numeric_inputs=[d]);assert m.verify_inputs(tmp_path,step,brief)==(a,[d])
 with pytest.raises(ValueError,match='EXPLICIT_INPUTS'):m.verify_inputs(tmp_path,dict(numeric_script=a),brief)
 with pytest.raises(ValueError,match='UNBOUND_INPUT'):m.verify_inputs(tmp_path,step,dict(source_bindings={'script':a}))
 data.write_bytes(b'changed')
 with pytest.raises(Exception):m.verify_inputs(tmp_path,step,brief)
