"""Assemble local diagnostic evidence; no visual-pass inference from hashes."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-sikh279/control-11'
RESULT=ROOT/'results/sikh279'
sys.path.insert(0,str(ROOT/'src'))

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def media():
    frames=[OUT/'motion'/f'{i:04d}.png' for i in range(1,97)]
    if not all(p.is_file() for p in frames):raise ValueError('Full native sequence required')
    target=OUT/'diagnostic-not-approved.mp4'
    if target.exists():raise ValueError('Preserve existing media')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(OUT/'motion/%04d.png'),'-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    for name,ids in [('motion-sheet',[1,12,20,21,26,36,42,48,54,60,66,78,84,90,96]),('blink-sheet',list(range(17,29)))]:
        sheet=Image.new('RGB',(240*5,312*((len(ids)+4)//5)),(242,242,242));draw=ImageDraw.Draw(sheet)
        for k,f in enumerate(ids):
            im=Image.open(frames[f-1]).convert('RGB');im.thumbnail((240,288));x=(k%5)*240;y=(k//5)*312;sheet.paste(im,(x,y));draw.text((x+8,y+292),f'Frame {f} | diagnostic FAIL',fill=(25,25,25))
        sheet.save(OUT/(name+'.jpg'),quality=90)
    report=dict(video_sha256=sha(target),fps=24,frames=96,duration_seconds=4,claim='Diagnostic only; not a character or performance pass',frame_hashes={p.name:sha(p) for p in frames})
    (RESULT/'media.json').write_text(json.dumps(report,indent=2))
    print(target)

def review():
    from movie_factory import production_knowledge as pk
    original=json.loads((RESULT/'sikh279-motion-11.json').read_text());task=original['task']
    task['id']='sikh279-final-disposition'
    # Only the reviewed strategy outcome changed after dispatch. Other source
    # drift must block rather than be silently rehashed.
    strategy='docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md'
    for name,digest in task['inputs'].items():
        if name!=strategy and sha(ROOT/name)!=digest:raise ValueError('Unreviewed input changed: '+name)
    task['inputs'][strategy]=sha(ROOT/strategy)
    task['inputs']['results/sikh279/ASSESSMENT.md']=sha(RESULT/'ASSESSMENT.md')
    packet=pk.task_packet(ROOT,task)
    (RESULT/'disposition-packet.json').write_text(json.dumps(packet,indent=2));(RESULT/'disposition-packet.md').write_text(pk.packet_markdown(packet))
    files=[RESULT/'ASSESSMENT.md',OUT/'build.json',OUT/'reopen.json',RESULT/'media.json',OUT/'front.png',OUT/'profile.png',OUT/'rear.png',OUT/'pose-021.png',OUT/'pose-054.png',OUT/'crown-component-front.png',OUT/'crown-component-rear.png',OUT/'motion-sheet.jpg',OUT/'blink-sheet.jpg']
    evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in files]
    process={'authority','strategy','economics','rights','current_state','sikh_scope','versioning'}
    fail={'visual_gate','representation','anatomy','motion','secondary','look','au_reference','au_deformation','au_performance','au_surface','sikh_cloth','sikh_motion'}
    checks=[]
    for o in packet['obligations']:
        status='PASS' if o['id'] in process else 'FAIL' if o['id'] in fail else 'NOT_RUN'
        checks.append(dict(id=o['id'],kind=o['check_kind'],status=status,
            action_taken='Performed two local conversion strategies, protected masters, rejected failed controls and withheld actor/cloth admission.',
            observation='See assessment: exact nine-state reopen is technical only; eyelid integration, groom boundaries and neck/collar deformation fail. Actual release/contact, hero identity and ensemble finish remain unqualified.',evidence=evidence))
    r=dict(packet_digest=packet['packet_digest'],checks=checks,
        hypotheses=[dict(prediction='Depth projection may transfer facial structure onto clean topology.',observation='Controls02-05 corrupt landmarks and transfer crown geometry into forehead.',response='Rejected depth-only transfer and retained evidence.',result='unresolved'),
            dict(prediction='Local eyelid replacement and rooted hair may suffice for a limited actor conversion.',observation='Controls06-11 move but retain visible eyelid seams, synthetic beard boundaries and collar deformation.',response='Do not extend into cloth release or promote as foundation; reassess input and representation.',result='unresolved')],
        adjacent_regressions='Head rotation exposes beard/skin registration and neck/collar defects. Crown extraction retains useful primary folds but rough cut boundary. Protected approved assets remain hash-identical.',
        stopping_reason='Method boundary, not time limit: completed negative conversion evaluation. No review-ready actor, clean full facial topology or one-cloth performance was produced. New input strategy recommended before further conversion.')
    (RESULT/'review.json').write_text(json.dumps(r,indent=2));gate=pk.check_review(ROOT,packet,r);(RESULT/'gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate,indent=2))

if __name__=='__main__':
    if sys.argv[1:]==['media']:media()
    elif sys.argv[1:]==['review']:review()
    else:raise ValueError('Fixed media or review operation')
