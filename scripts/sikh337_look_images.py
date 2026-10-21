"""Run the admitted appearance evidence views serially; no artistic verdict."""
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for step in ('render','leader_front','leader_reverse','crowd_front'):
    subprocess.run([sys.executable,'-m','movie_factory.experiment_ops','job',
        '--experiment','SIKH335','--episode','representation','--phase','supporting-appearance',
        '--id','sikh337-look-c3-'+step,'--kind','native','--',sys.executable,
        'scripts/sikh337_look_dispatch.py',step],cwd=root,check=True)
