import json
from pathlib import Path
D=json.loads(Path('runs/demonstrator-01/realism-audit/audit.json').read_text());print(D['tail']);print(D['rays_last_frame'])
samples=D['source_samples'][:-1];groups={}
for name in samples[0]['hooves']:
 hits=[x for x in samples if x['hooves'][name]['min_z']<=.04]
 ts=[x['frame'] for x in hits]
 # unwrap through largest gap in the circular support set
 pairs=sorted(ts);gaps=[((pairs[(i+1)%len(pairs)]-t)%10,i) for i,t in enumerate(pairs)];_,i=max(gaps);a=pairs[(i+1)%len(pairs)];rows=[((x['frame']-a)%10+a,x['hooves'][name]['center']) for x in hits];rows.sort();groups[name]=rows
num=den=0
for rows in groups.values():
 mt=sum(t for t,c in rows)/len(rows);my=sum(c[1] for t,c in rows)/len(rows)
 num+=sum((t-mt)*(c[1]-my) for t,c in rows);den+=sum((t-mt)**2 for t,c in rows)
ls=num/den*24
print('Least squares speed',ls)
def objective(speed):
 maxima=[]
 for rows in groups.values():
  pts=[(c[0],c[1]-speed*t/24) for t,c in rows];cx=(min(p[0] for p in pts)+max(p[0] for p in pts))/2;cy=(min(p[1] for p in pts)+max(p[1] for p in pts))/2
  maxima.append(max(((x-cx)**2+(y-cy)**2)**.5 for x,y in pts))
 return max(maxima)
best=min([i/100 for i in range(100,1601)],key=objective);print('minimax',best,objective(best),'LS correction',objective(ls))
plan={'method':'Joint dense-source minimax stance correction; speed chosen over 1–16 m/s at .01 m/s spacing, preserving source cadence. Not an equine performance reference.','selected_speed_mps':best,'least_squares_speed_mps':ls,'stance_max_required_correction_m':objective(best),'intervals':{n:[r[0][0]-.03125,r[-1][0]+.03125] for n,r in groups.items()},'source_step':.03125,'max_correction_m':.3,'preview_head_scale':.67}
Path('feasibility/demonstrator-01/realism-config.json').write_text(json.dumps(plan,indent=2)+'\n');print(plan)
