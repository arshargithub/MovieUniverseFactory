"""Independent207 rest-data and scoped skin-weight preservation check."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance207_inspect import SOURCES
def validate(job):
 if job!={'operation':'verify11'}:raise ValueError('Closed207 preservation check')
def capture(body):
 p=np.array([v.co[:] for v in body.data.vertices]);names=[g.name for g in body.vertex_groups];totals=[];protected=hashlib.sha256();keys=hashlib.sha256()
 for v in body.data.vertices:
  pairs=[(names[g.group],g.weight) for g in v.groups];totals.append(sum(w for n,w in pairs))
  x,y,z=v.co
  if not (-1.85<z<-.85 and abs(x)<1.05):protected.update(json.dumps(pairs,separators=(',',':')).encode())
 for k in body.data.shape_keys.key_blocks:
  a=np.empty((len(k.data),3),np.float32);k.data.foreach_get('co',a.ravel());keys.update(k.name.encode());keys.update(a.tobytes())
 return dict(vertices=p,totals=np.array(totals),protected_weights=protected.hexdigest(),shape_data=keys.hexdigest())
def main():
 import bpy
 job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job);out=base.BASE/'entrance207-verify11'
 if out.exists():raise ValueError('Preserve verification')
 out.mkdir();rows=[]
 for kind,selected in [('opening','opening09'),('route','threat10')]:
  original,sha=SOURCES[kind];src=base.BASE/original/'scene.blend';candidate=base.BASE/('entrance207-'+selected);record=json.loads((candidate/'result.json').read_text())
  if base.digest(src)!=sha or base.digest(candidate/'scene.blend')!=record['native_sha256']:raise ValueError('Source changed')
  captures=[]
  for p in (src,candidate/'scene.blend'):
   bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);base.check_protected();captures.append(capture(bpy.data.objects['MF_studio_adult_body']))
  a,b=captures
  error=float(abs(a['totals']-b['totals']).max())
  if not np.array_equal(a['vertices'],b['vertices']) or a['shape_data']!=b['shape_data'] or a['protected_weights']!=b['protected_weights'] or error>2e-7:raise ValueError('Undeclared body/rest/weight change')
  rows.append(dict(kind=kind,source_sha256=sha,selected_sha256=record['native_sha256'],rest_coordinate_error=0,shape_data_sha256=b['shape_data'],outside_cervical_weights_sha256=b['protected_weights'],max_weight_sum_error=error))
 (out/'result.json').write_text(json.dumps(dict(status='PASS',samples=rows,scope='Rest mesh, all shape coordinates and noncervical influences exact; cervical sums preserved. Not general pose or neutral-render qualification.'),indent=2)+'\n')
if __name__=='__main__':main()
