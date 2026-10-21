"""Actual deformed-hoof landmark audit; not full mesh contact or AV approval."""
import json,math,sys
from pathlib import Path
from movie_factory import production_knowledge as pk
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01';cycle=int(sys.argv[1])
run=pk.read_json(root,f'results/sikh335/motion01/save-run-c{cycle}.json')
patch=pk.read_json(root,run['artifacts']['patch']['path']);rows=patch['support'][1]['motion']['frames']
by_frame={r['frame']:r for r in rows};report={'cycle':cycle,'source':run['artifacts']['patch'],'legs':{},'passed':True,
    'limits':'DEF hoof bone landmarks, not a whole deformed mesh collision test. Proposed shot-specific anti-braking threshold; phase silhouettes and full-speed AV still required.'}
for index,(side,contact) in enumerate((('L',350),('R',351))):
    ground=by_frame[contact]['hind_support'][index]['fore_visible_hoof'][2]
    samples=[]
    for f in range(contact-8,contact+5):
        point=by_frame[f]['hind_support'][index]['fore_visible_hoof']
        previous=by_frame[f-1]['hind_support'][index]['fore_visible_hoof']
        samples.append({'frame':f,'height':point[2]-ground,'vertical_velocity':24*(point[2]-previous[2])})
    landing=[s for s in samples if contact-3<=s['frame']<=contact]
    speed=-landing[-1]['vertical_velocity'];prior=max(-s['vertical_velocity'] for s in landing[:-1])
    passed=(speed>=1 and speed>=.85*prior and all(s['vertical_velocity']<0 for s in landing)
            and all(s['height']>=-.002 for s in samples)
            and all(abs(s['height'])<.001 for s in samples if s['frame']>=contact))
    report['legs'][side]={'contact_frame':contact,'contact_speed':speed,'preceding_peak_speed':prior,
        'ratio':speed/prior if prior else None,'passed':passed,'samples':samples}
    report['passed'] &= passed
report['maximum_hind_error']=max(math.dist(s['support_target'],s['visible_hoof']) for r in rows for s in r['hind_support'])
report['maximum_flight_retraction']=max(s['flight_wrist_adjustment'] for r in rows for s in r['hind_support'])
report['passed'] &= report['maximum_hind_error']<.001 and report['maximum_flight_retraction']<.02
(out/f'landing-audit-c{cycle}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 2)
