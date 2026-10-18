"""Matched static-source review only; reuse frozen301 cameras and materials."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/trellis303/review'
SOURCE=ROOT/'.runtime/trellis303/retrieved/evidence/head1024'
ALIASES=ROOT/'.runtime/trellis303/review-input'


def configure():
    sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
    import trellis301_export_inspect as shared
    shared.OUT=OUT;shared.SOURCE=ALIASES;shared.VARIANTS=('1024-4096',)
    for name,target in [('head-1024-4096.glb',SOURCE/'candidate.glb'),('head-1024-4096.json',SOURCE/'receipt.json')]:
        link=ALIASES/name
        if not link.is_symlink() or link.resolve()!=target.resolve():raise RuntimeError('Review input alias changed')
    return shared


def worker(job):
    if job not in ({'operation':'render','variant':'1024-4096'},{'operation':'reopen','variant':'1024-4096'}):
        raise ValueError('Unadmitted recovery review operation')
    configure().worker(job)


def main():
    from movie_factory import production_knowledge as pk
    from trellis301_prepare import sha,dump
    ALIASES.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    for name,target in [('head-1024-4096.glb',SOURCE/'candidate.glb'),('head-1024-4096.json',SOURCE/'receipt.json')]:
        if not target.is_file():raise RuntimeError('No successful1024 recovery export')
        link=ALIASES/name
        if not link.exists() and not link.is_symlink():link.symlink_to(target)
    shared=configure()
    task=json.loads((ROOT/'results/trellis303/task.json').read_text())
    task.update(id='trellis303-static-review',phase='execution',intent='Matched512 versus recovered1024 static source; not actor admission')
    for p in (Path(__file__),ROOT/'scripts/trellis301_export_inspect.py',shared.BASE,SOURCE/'candidate.glb',SOURCE/'receipt.json'):
        task['inputs'][str(p.relative_to(ROOT))]=sha(p)
    packet=pk.task_packet(ROOT,task);dump(OUT/'packet.json',packet)
    if not packet['dispatch_ready']:raise RuntimeError(packet['blockers'])
    if subprocess.run(['pgrep','-fl','/Applications/Blender.app/Contents/MacOS/Blender'],capture_output=True).returncode==0:
        raise RuntimeError('Blender slot occupied')
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for op in ('render','reopen'):
        started=time.monotonic()
        with (OUT/f'{op}.log').open('w') as log:
            result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode',
                '--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),
                '--',json.dumps({'operation':op,'variant':'1024-4096'})],env=env,stdout=log,stderr=subprocess.STDOUT)
        dump(OUT/f'{op}-job.json',{'returncode':result.returncode,'seconds':time.monotonic()-started})
        if result.returncode:raise RuntimeError(op+' failed')
    from PIL import Image,ImageDraw,ImageFont
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18)
    for view in [v[0] for v in shared.VIEWS]+['front-clay','left-quarter-clay','right-quarter-clay']:
        inputs=[ROOT/f'.runtime/trellis301/export-review/1000000-4096/{view}.png',OUT/f'1024-4096/{view}.png']
        images=[Image.open(p).convert('RGB') for p in inputs]
        if images[0].size!=images[1].size:raise RuntimeError('Unmatched review size')
        w,h=images[0].size;board=Image.new('RGB',(w*2,h+40),'#eeeeee');draw=ImageDraw.Draw(board)
        for i,(label,im) in enumerate(zip(['512 source / 1M / 4K','1024 recovered / 1M / 4K'],images)):
            draw.text((i*w+12,10),label,font=font,fill='#161616');board.paste(im,(i*w,40))
        board.save(OUT/f'comparison-{view}.jpg',quality=95)


if __name__=='__main__':
    worker(json.loads(sys.argv[sys.argv.index('--')+1])) if '--' in sys.argv else main()
