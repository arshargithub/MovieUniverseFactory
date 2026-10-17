"""Explicit parent-venv package inheritance; a nested venv does not imply it."""
import json,subprocess
from pathlib import Path

def describe(python):
    return json.loads(subprocess.check_output([str(python),'-c',
        'import json,sys,sysconfig; print(json.dumps({"prefix":sys.prefix,"version":list(sys.version_info[:2]),"purelib":sysconfig.get_path("purelib")}))'],text=True))

def link_parent_packages(parent_python,child_python,allowed_parent,allowed_child):
    parent=describe(parent_python);child=describe(child_python)
    pp=Path(parent['purelib']);cp=Path(child['purelib'])
    if parent['version']!=child['version']:raise ValueError('Parent/child Python ABI mismatch')
    if Path(parent['prefix']).resolve()!=Path(allowed_parent).resolve() or Path(child['prefix']).resolve()!=Path(allowed_child).resolve():raise ValueError('Unexpected environment prefix')
    if not pp.resolve().is_relative_to(Path(allowed_parent).resolve()) or not cp.resolve().is_relative_to(Path(allowed_child).resolve()):raise ValueError('Package path outside isolated environments')
    if not pp.is_dir() or not cp.is_dir() or any(c in str(pp) for c in '\r\n'):raise ValueError('Invalid package directory')
    # A literal directory, never executable import lines or copied startup code.
    pth=cp/'movie_factory_parent_packages.pth'
    if pth.exists():raise ValueError('Do not overwrite existing environment configuration')
    pth.write_text(str(pp)+'\n')
    return {'parent':parent,'child':child,'link':str(pth)}
