"""Immutable per-frame assembly from proven repaired and equivalent shots."""
import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh300'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    repaired=BASE/'ground-rerender-01';old=BASE/'movie-01/frames';out=BASE/'final-01';frames=out/'frames'
    expected=list(range(1,276))+list(range(356,529))
    assert sorted(int(p.stem[-4:]) for p in repaired.glob('frame-*.png'))==expected
    task=json.loads((ROOT/'results/sikh300/ground-rerender-1/task.json').read_text())
    for rel,digest in task['inputs'].items():assert sha(ROOT/rel)==digest,rel
    out.mkdir(exist_ok=False);frames.mkdir();rows=[]
    for f in range(1,529):
        source=(old if 276<=f<=355 else repaired)/f'frame-{f:04d}.png';target=frames/source.name;shutil.copy2(source,target)
        digest=sha(source);assert sha(target)==digest
        rows.append({'frame':f,'source':str(source.relative_to(ROOT)),'sha256':digest,'basis':'Fixed leader camera excludes modified road/bank foot; matched endpoints/interiors tested' if 276<=f<=355 else 'Corrected native render'})
    manifest={'selected_native':'.runtime/art-direction/series01-sikh300/ground-fix-01/sequence.blend','native_sha256':sha(BASE/'ground-fix-01/sequence.blend'),'repaired_frames':448,'retained_frames':80,'frames':rows,'protected_pashtun_rendered':False}
    (out/'frame-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out)
if __name__=='__main__':main()
