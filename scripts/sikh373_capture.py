"""Serial dispatch of already-admitted80 recipes. Availability is not artistic review."""
import subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
groups={'early':['early_side','early_oblique'],'final':['final_side','reverse','production','prefix'],'chronology':['phase01','phase02','phase03']}
steps=groups[sys.argv[1]]
for step in steps:
 subprocess.run([sys.executable,'-m','movie_factory.experiment_ops','job','--experiment','sikh335','--episode','leader369','--phase','landing373','--id','sikh373-native80-'+step,'--kind','native','--',sys.executable,'scripts/sikh373_plan.py',step],cwd=r,check=True)
 subprocess.run([sys.executable,'scripts/sikh373_plan.py','review',step,'Actualreturnedsource-boundimages/manifests verifiedbybridge; availabilityonly. Parent mustinspectreference/wholephase beforeartisticqualification orDirectorqueue.'],cwd=r,check=True)
 print('AVAILABLE',step,flush=True)
