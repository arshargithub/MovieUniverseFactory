"""Fixed synthetic build/probe in disposable Linux worker, no model downloads."""
import hashlib,importlib.metadata,json,os,subprocess,sys,time
from pathlib import Path

BASE=Path('/opt/mf-trellis293')
OUT=BASE/'evidence'
BUCKET='mf-trellis293-281482331395'
def run(args,**kwargs):
    print('RUN',args,flush=True)
    return subprocess.run(args,check=True,**kwargs)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
    items=[]
    for d in importlib.metadata.distributions():
        notices=[]
        for f in d.files or []:
            if any(x in str(f).lower() for x in ('license','notice','copying')):
                p=Path(d.locate_file(f))
                if p.is_file():notices.append({'path':str(f),'sha256':sha(p)})
        items.append({'name':d.metadata['Name'],'version':d.version,'license_expression':d.metadata.get('License-Expression'),
            'license':d.metadata.get('License'),'notices':notices})
    (OUT/'packages.json').write_text(json.dumps(items,indent=2))
def main():
    OUT.mkdir(exist_ok=True)
    if '--inventory' in sys.argv:inventory();return
    candidates=[Path('/opt/pytorch/bin/python'),Path('/opt/pytorch/bin/python3')]
    py=next((p for p in candidates if p.exists()),None)
    if py is None:raise RuntimeError('Expected AWS PyTorch runtime absent; no guessed install')
    run([str(py),'-c','import torch; print(torch.__version__,torch.version.cuda,torch.cuda.get_device_name())'])
    run([str(py),'-m','venv','--system-site-packages',str(BASE/'venv')])
    vp=str(BASE/'venv/bin/python')
    # Official PyPI only; exact direct dependencies, install report records
    # resolved URLs and hashes. No third-party precompiled CUDA extension.
    run([vp,'-m','pip','install','--only-binary=:all:','--no-deps','--report',str(OUT/'pip-report.json'),
        'numpy==2.2.6','trimesh==4.7.4','opencv-python-headless==4.12.0.88','pillow==11.3.0','tqdm==4.67.1','ninja==1.11.1.4'])
    arch=subprocess.check_output([vp,'-c','import torch; print("%s.%s" % torch.cuda.get_device_capability())'],text=True).strip()
    if arch not in {'8.6','8.9'}:raise RuntimeError('Unreviewed GPU architecture: '+arch)
    env=dict(os.environ,MAX_JOBS='2',TORCH_CUDA_ARCH_LIST=arch,BUILD_TARGET='cuda',PYTHONPATH=str(BASE/'src'))
    # CUDA toolkit must agree with torch; select only a toolkit already in AMI.
    cuda=subprocess.check_output([vp,'-c','import torch; print(torch.version.cuda)'],text=True).strip()
    toolkit=Path('/usr/local')/('cuda-'+cuda)
    if not (toolkit/'bin/nvcc').exists():raise RuntimeError('Matching CUDA toolkit absent: '+str(toolkit))
    env['CUDA_HOME']=str(toolkit);env['PATH']=str(toolkit/'bin')+':'+env['PATH']
    for name in ('CuMesh','FlexGEMM'):
        run([vp,'-m','pip','install','--no-build-isolation','--no-deps',str(BASE/'sources'/name)],env=env)
    run([vp,str(BASE/'scripts/trellis293_worker.py'),'--inventory'],env=env)
    from movie_factory.trellis_adapter.patch import adapted_sources
    checkout=BASE/'patched'
    for name,text in adapted_sources(BASE/'results/sikh288/upstream').items():
        target=checkout/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    run([vp,str(BASE/'scripts/trellis288_cuda_probe.py'),'--checkout',str(checkout),'--output',str(OUT/'probe')],env=env)
    run([vp,'-m','pip','freeze'],stdout=(OUT/'freeze.txt').open('w'))
if __name__=='__main__':main()
