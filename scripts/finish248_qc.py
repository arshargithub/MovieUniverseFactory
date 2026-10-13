"""Read-only native/media checks and inspection sheets; no perceptual PASS."""
import json,sys,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from finish248_delivery import OUT,sha
from finish245_qc import differences
def raw(kind):
    import finish245_qc as q
    q.OUT=OUT;q.sheets(kind+'-final')
def reopen():
    rows=[]
    for kind in ('opening','route'):
        final=json.loads((OUT/(kind+'-final')/'result.json').read_text())
        replay=json.loads((OUT/(kind+'-reopen')/'result.json').read_text())
        if not replay['complete'] or replay['source_sha256']!=final['source_sha256'] or replay['profile']!=final['profile']:raise ValueError('Different source/profile')
        expected={r['index']:r for r in final['frames']}
        for r in replay['frames']:
            a=OUT/(kind+'-final')/r['file'];b=OUT/(kind+'-reopen')/r['file']
            if sha(a)!=expected[r['index']]['sha256'] or sha(b)!=r['sha256']:raise ValueError('Changed control')
            rows.append(dict(index=r['index'],source_sha256=sha(a),replay_sha256=sha(b),**differences(a,b)))
    if len(rows)!=11:raise ValueError('Missing control')
    path=OUT/'reopen-verification.json'
    if path.exists():raise ValueError('Preserve evidence')
    report={'controls':rows,'all_strict_one_level':all(r['strict_one_level'] for r in rows),'scope':'Eleven source-bound1080x1920/16sample Metal fresh-process controls; no historical failure waived.'}
    path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    if not report['all_strict_one_level']:raise ValueError('Strict replay failed; inspect before handoff')
def encoded():
    from finish245_audio import measure
    delivery=OUT/'delivery01';record=json.loads((delivery/'manifest.json').read_text())
    for r in record['deliveries']:
        if sha(delivery/r['file'])!=r['sha256']:raise ValueError('Changed delivery')
    d=OUT/'encoded-qc01';d.mkdir(exist_ok=False)
    small=d/'chronology';small.mkdir();controls=d/'controls';controls.mkdir();sheets=d/'sheets';sheets.mkdir()
    clean=delivery/'pashtun-20s.mp4'
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf','scale=216:384','-start_number','0',str(small/'frame-%04d.png')],check=True)
    selected=[0,35,60,91,98,140,143,156,173,198,204,233,234,258,281,282,306,363,414,459,479]
    expr='+'.join('eq(n,'+str(i)+')' for i in selected)
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf',"select='"+expr+"'",'-fps_mode','vfr','-start_number','0',str(controls/'clean-%02d.png')],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(delivery/'pashtun-20s-captioned.mp4'),'-vf',"select='eq(n,60)+eq(n,110)+eq(n,150)'",'-fps_mode','vfr','-start_number','0',str(controls/'caption-%02d.png')],check=True)
    frames=sorted(small.glob('frame-*.png'))
    if len(frames)!=480:raise ValueError('Incomplete encoded chronology')
    changes=[];last=None
    for offset in range(0,480,20):
        canvas=Image.new('RGB',(1080,1632),(235,230,215));draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(frames[offset:offset+20]):
            im=Image.open(p).convert('RGB');v=np.asarray(im).astype(float)
            if last is not None:changes.append({'index':offset+j,'mean_rgb_step':float(abs(v-last).mean())})
            last=v;x=j%5*216;y=j//5*408;canvas.paste(im,(x,y));draw.text((x+5,y+387),f'{offset+j} | {(offset+j)/24:.3f}s',fill=(20,20,20))
        canvas.save(sheets/f'sheet-{offset:04d}.jpg',quality=94)
    report={'frames':480,'control_indices':selected,'caption_indices':[60,110,150],'levels':measure(clean),'largest_frame_steps':sorted(changes,key=lambda r:-r['mean_rgb_step'])[:20],'direct_listening':'NOT_RUN; unchanged Director-accepted247 sound before19.75s fade','visual_review':'NOT_RUN until inspected','artifacts':{str(p.relative_to(d)):sha(p) for p in d.rglob('*') if p.is_file()}}
    (d/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':
    op=sys.argv[1]
    if op in ('opening','route'):raw(op)
    elif op=='reopen':reopen()
    elif op=='encoded':encoded()
    else:raise ValueError('Closed QC operation')
