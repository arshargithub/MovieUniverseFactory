"""Read-only media verification plus derived encoded-frame review evidence."""
import json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from finish245_edit import OUT,sha
from finish245_audio import measure

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(path)]))

def main():
    delivery=OUT/'delivery01';out=OUT/'encoded-qc01'
    if out.exists():raise ValueError('Preserve QC evidence')
    record=json.loads((delivery/'manifest.json').read_text())
    for name,digest in record['deliveries'].items():
        if sha(delivery/name)!=digest:raise ValueError('Changed delivery')
    out.mkdir();small=out/'chronology';small.mkdir();controls=out/'controls';controls.mkdir()
    probes={}
    for name in ('pashtun-entrance-complete.mp4','pashtun-entrance-captioned.mp4'):
        p=delivery/name;info=probe(p);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],int(v['nb_read_frames']))==(1080,1920,540)
        assert v['avg_frame_rate']=='24/1' and abs(float(v['duration'])-22.5)<.001
        assert a['sample_rate']=='48000' and a['channels']==2
        assert v['pix_fmt']=='yuv420p' and v['color_space']=='bt709'
        probes[name]=info
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    clean=delivery/'pashtun-entrance-complete.mp4'
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf','scale=216:384','-start_number','0',str(small/'frame-%04d.png')],check=True)
    selected=[0,35,36,87,91,98,140,156,161,190,198,204,233,234,281,282,320,414,483,539]
    expr='+'.join('eq(n,'+str(i)+')' for i in selected)
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf',"select='"+expr+"'",'-fps_mode','vfr','-start_number','0',str(controls/'clean-%02d.png')],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(delivery/'pashtun-entrance-captioned.mp4'),'-vf',"select='eq(n,60)+eq(n,110)+eq(n,150)'",'-fps_mode','vfr','-start_number','0',str(controls/'caption-%02d.png')],check=True)
    frames=sorted(small.glob('frame-*.png'));assert len(frames)==540
    sheets=out/'sheets';sheets.mkdir();diffs=[];last=None
    for offset in range(0,540,20):
        canvas=Image.new('RGB',(1080,1632),(235,230,215));draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(frames[offset:offset+20]):
            im=Image.open(p).convert('RGB');v=np.asarray(im).astype(float)
            if last is not None:diffs.append({'index':offset+j,'mean_rgb_step':float(abs(v-last).mean())})
            last=v;x=j%5*216;y=j//5*408;canvas.paste(im,(x,y));draw.text((x+5,y+387),f'{offset+j} | {(offset+j)/24:.3f}s',fill=(20,20,20))
        canvas.save(sheets/f'sheet-{offset:04d}.jpg',quality=94)
    result={'media':probes,'control_index_map':selected,'caption_index_map':[60,110,150],
            'encoded_loudness':measure(clean),'chronological_frames':540,
            'largest_frame_steps':sorted(diffs,key=lambda r:-r['mean_rgb_step'])[:24],
            'direct_listening':'NOT_RUN; technical checks are not auditory acceptance',
            'visual_review':'NOT_RUN until actual generated sheets and controls are inspected',
            'artifacts':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()}}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('chronological_frames','encoded_loudness','largest_frame_steps')}))

if __name__=='__main__':main()
