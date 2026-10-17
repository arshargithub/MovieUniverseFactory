"""Reuse fixed synthetic inspection without modifying historical294 evidence."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import trellis294_inspect as v

def configure(attempt):
    if attempt not in ('a','b','c'):raise ValueError('Unknown attempt')
    v.SOURCE=v.ROOT/('.runtime/trellis295'+attempt+'/retrieved/evidence/probe')
    v.OUT=v.ROOT/('.runtime/trellis295'+attempt+'/blender')
    v.RECORD=v.ROOT/('results/trellis295/cloud-'+attempt)

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:];assert len(args)==1
        job=json.loads(args[0]);attempt=job.pop('attempt');configure(attempt);v.worker(job)
    else:
        p=argparse.ArgumentParser();p.add_argument('--attempt',default='a');a=p.parse_args();configure(a.attempt)
        import trellis295_cloud as c
        c.configure(a.attempt)
        # Inject a validated attempt into fixed structured child operations.
        original=v.subprocess.run
        def run(args,**kwargs):
            if args and args[0].endswith('/Blender'):
                job=json.loads(args[-1]);v.validate(job);job['attempt']=a.attempt
                args=[*args[:-1],json.dumps(job)]
            return original(args,**kwargs)
        v.subprocess.run=run
        def packet():
            c.packet()
            task=json.loads((v.RECORD/'task.json').read_text())
            task['inputs'][str(Path(__file__).relative_to(v.ROOT))]=v.sha(Path(__file__))
            (v.RECORD/'task.json').write_text(json.dumps(task,indent=2))
        v.main(packet_loader=packet,worker_path=Path(__file__).resolve())
