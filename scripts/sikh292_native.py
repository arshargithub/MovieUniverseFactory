"""Exact structured operation dispatcher; no code strings or asset scripts."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from movie_factory.sikh292_motion import validate_job
from sikh292_scene import BASE,controls,movie,reopen
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);j=validate_job(json.loads(p.read_text()));out=BASE/f"{j['operation']}-{j['version']:02d}"
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted path')
    {'controls':controls,'movie':movie,'reopen':reopen}[j['operation']](out)
if __name__=='__main__':main()
