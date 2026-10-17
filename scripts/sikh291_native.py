"""Fixed derivative dispatcher. No runtime code or embedded scripts accepted."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from movie_factory.sikh291_motion import validate_job
from sikh291_scene import controls,movie,reopen,diagnose,BASE

def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);job=validate_job(json.loads(path.read_text()))
    out=BASE/f"{job['operation']}-{job['version']:02d}"
    if path.resolve()!=out/'job.json':raise ValueError('Unadmitted path')
    {'controls':controls,'movie':movie,'reopen':reopen,'diagnose':diagnose}[job['operation']](out)

if __name__=='__main__':main()

