"""Fixed source-bound205 horse contact rebuild, not an arbitrary executor."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    from entrance190_horse import build
    from entrance205_motion import trajectory
    from wardrobe_riding_fit import HORSE, HORSE_SHA
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'horse01'},{'operation':'horse07'}):raise ValueError('Fixed205 horse operation required')
    out=base.BASE/('entrance205-'+job['operation'])
    if out.exists() or base.digest(HORSE)!=HORSE_SHA:raise ValueError('Source/output mismatch')
    out.mkdir()
    for n in ('entrance205_horse.py','entrance205_motion.py','entrance190_horse.py'):
        (out/n).write_bytes((ROOT/'scripts'/n).read_bytes())
    build(out,corrected=True,route_data=trajectory(),tighten_stance=job['operation']=='horse07')
    (out/'result.json').write_text(json.dumps({'source_sha256':HORSE_SHA,
        'native_sha256':base.digest(out/'horse-route.blend'),
        'route_sha256':base.digest(out/'route.npz'), 'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
