"""Serial admitted view extraction, without assigning artistic verdicts."""
import subprocess,sys
from pathlib import Path
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1]
cycle=Controller(r,DATABASE).state('sikh335-supporting-appearance')['cycle']
assert cycle==8
for step in ('leader_front','leader_reverse','render','crowd_front'):
    subprocess.run([sys.executable,'-m','movie_factory.experiment_ops','job',
       '--experiment','SIKH335','--episode','representation','--phase','supporting-appearance',
       '--id',f'sikh338-look-c{cycle}-'+step,'--kind','native','--',sys.executable,
       'scripts/sikh338_look_dispatch.py',step],cwd=r,check=True)
