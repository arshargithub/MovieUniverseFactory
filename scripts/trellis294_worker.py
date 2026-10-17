"""Proposed corrected worker; remote validation still required after294 failure."""
import json,os,subprocess
from pathlib import Path
import trellis293_worker as w
from trellis294_runtime import link_parent_packages

def main():
    # Keep original reviewed exporter/source handling; replace only environment
    # creation. This adapter intercepts the one trusted, fixed venv command.
    original=w.run
    def run(args,**kwargs):
        result=original(args,**kwargs)
        if len(args)>=4 and args[1:3]==['-m','venv']:
            parent=Path(args[0]);vp=w.BASE/'venv/bin/python'
            record=link_parent_packages(parent,vp,Path('/opt/pytorch'),w.BASE/'venv')
            (w.OUT/'runtime-link.json').write_text(json.dumps(record,indent=2))
            # Falsify the former failure before downloads or extension builds.
            original([str(vp),'-c','import torch; assert torch.cuda.is_available(); print(torch.__version__, torch.__file__, torch.cuda.get_device_name())'])
        return result
    w.run=run
    w.main()
if __name__=='__main__':main()
