"""Record the fresh challenge's narrow delta without erasing earlier review."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'results/sikh335/look01'
verdict=json.loads((out/'challenge-verdict-c1.json').read_text())
verdict['checks']['method'].update(
    observation='Inspected exact finite-envelope change: clamp negative float32 endpoint sine before fractional power; force zero outside support and reject nonfinite input. Eighteen numerical/operation/motion regressions pass. No other construction method changed.',
    comparison='The first attempt saved no candidate. This correction removes that numerical blocker only; cone/ring turban, embossed garment and unsupported-pad counterexamples still veto the next actual images.')
verdict['checks']['authority'].update(
    observation='Existing task is correction2/max4; the failed first native attempt, original rejected reference plan and exact337 approval are retained.',
    comparison='No hidden retry, new spending, principal change or artistic acceptance. Motion is separately at newly approved7/max10 with incomplete prior extraction retained.')
verdict['checks']['interfaces']['observation']+=' The code change affects only garment-envelope evaluation; candidate5 remains the parent and primary motion is not rebaked.'
verdict['strongest_counterexample']='A finite saved model can still look like a mannequin in a cone hat. The numerical tests cannot pass the visual gate; retain all first-challenge form and same-film counterexamples.'
path=out/'challenge-verdict-c2.json'
assert not path.exists()
path.write_text(json.dumps(verdict,indent=2)+'\n')
