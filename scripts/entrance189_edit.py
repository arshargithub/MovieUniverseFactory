"""Source-linked offline rough edits. Boards/cards are visibly not finished footage."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'.runtime/art-direction'
BASE=ART/'series01-facebuilder-trial-01'
FFMPEG='/opt/homebrew/bin/ffmpeg'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'


def run(args):
    subprocess.run([FFMPEG,'-nostdin','-n','-hide_banner','-loglevel','error',*args],check=True)


def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def admit_review(folder,video):
    gate=json.loads((folder/'internal-review.json').read_text())
    media=json.loads((folder/'media.json').read_text())
    source=json.loads((folder/'result.json').read_text())
    if (gate.get('status')!='PROCEED_TO_EDIT' or
        gate.get('source_sha256')!=source.get('source_sha256') or
        not source.get('source_sha256') or media['video_sha256']!=digest(video)):
        raise ValueError('Source-bound integrated motion review required')
    for row in media['frames']:
        path=folder/row['name']
        if path.parent!=folder or digest(path)!=row['sha256']:
            raise ValueError('Reviewed frame changed')


def main():
    motion=BASE/'entrance189-motion16';native=motion/'entrance-proof.mp4'
    admit_review(motion,native)
    decision=BASE/'entrance189-decision-motion20';decision_native=decision/'decision-proof.mp4'
    admit_review(decision,decision_native)
    out=ART/'series01-trailer-edit189'
    if out.exists():raise ValueError('Preserve existing edit')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    board=ART/'series01-entrance-boards-v01/storyboard-v02.png'
    direction=ART/'series01-entrances-v04/C-illustrated-landscape.png'
    animatic=json.loads((ROOT/'docs/planning/SERIES_01_PASHTUN_ANIMATIC_V01.json').read_text())
    from PIL import Image
    with Image.open(direction) as im:w,h=im.size
    rows=[]
    def clip(name,frames,title,note,source=None,crop=None,video=False):
        path=out/(name+'.mp4')
        input_args=['-i',str(source)] if video else ['-loop','1','-framerate','24','-i',str(source)] if source else ['-f','lavfi','-i','color=c=0x202735:s=720x1280:r=24']
        transform=[]
        if crop:
            cw,ch,cx,cy=crop;transform.append(f'crop={cw}:{ch}:{cx}:{cy}')
        transform+=['scale=648:1152:force_original_aspect_ratio=decrease','pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0x202735','setsar=1','fps=24']
        # Captions are production status, not invented dialogue or historical quotations.
        for text,y,size in ((title,24,27),(note,1218,22)):
            if any(c in text for c in "':\\"):raise ValueError('Unsafe caption')
            size=min(size,int(648/max(1,len(text))/.57))
            transform.append(f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:fontcolor=white:x=(w-tw)/2:y={y}")
        if not source:
            transform.append(f"drawtext=fontfile={FONT}:text='{name.replace('-', ' ').upper()}':fontsize=40:fontcolor=0xdbc59e:x=(w-tw)/2:y=(h-th)/2")
        run([*input_args,'-vf',','.join(transform),'-frames:v',str(frames),'-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(path)])
        row={'name':name,'frames':frames,'fps':24,'status':'NATIVE_PREVIEW' if video else 'STORYBOARD' if source else 'UNBUILT_TIMING_CARD',
            'source':str(source.relative_to(ROOT)) if source else None,'source_sha256':digest(source) if source else None,'crop':crop,'caption':title,'note':note,'path':path.name}
        rows.append(row);return row
    opening=clip('pashtun-opening',144,'NATIVE MOTION - riding proof','Preview resolution - not final release render',native,video=True)
    continuation=[]
    for i,p in enumerate(animatic['panels'][4:]):
        if i==1:
            continuation.append(clip('route-decision',48,'NATIVE MOTION - attention coverage','New close camera - unchanged validated acting',decision_native,video=True))
            continue
        continuation.append(clip(('route-reveal','route-decision','gather-and-turn','uphill-drive')[i],int(p['seconds']*24),
            'STORYBOARD - NOT ANIMATION',('Provisional blockade and geography','Attention shifts toward the harder route','Gather before the broad uphill turn','Renewed drive - no destination revealed')[i],board,p['crop']))
    archive=clip('archival-contrast',168,'UNBUILT - archival counterpoint','Verified quotation and rights still unresolved')
    sikh=clip('sikh-confrontation',192,'ART DIRECTION - NOT ANIMATION','Mounted presence becomes decisive commitment',direction,[int(w*.330),h,int(w*.335),0])
    gurkha=clip('gurkha-protection',192,'ART DIRECTION - NOT ANIMATION','Stillness - ferocity - attention to the protected person',direction,[w-int(w*.672),h,int(w*.672),0])
    mission=clip('missing-informant',264,'UNBUILT - mission promise','Dialogue and exact mission imagery are not locked')
    chemistry=clip('action-and-chemistry',192,'UNBUILT - action and mutual reliance','Scene selection must protect the episode outcome')
    assembly=clip('three-before-the-officer',264,'UNBUILT - the assembly','Three different relationships to authority')
    title=clip('the-martials',168,'WORKING TITLE - NOT CLEARED','End question and release call to action unresolved')
    def assemble(name,sequence):
        listing=out/(name+'.ffconcat')
        listing.write_text('ffconcat version 1.0\n'+''.join("file '"+r['path']+"'\n" for r in sequence))
        run(['-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(out/(name+'.mp4'))])
        cursor=0;timeline=[]
        for row in sequence:
            timeline.append({'clip':row['name'],'start_frame':cursor,'end_frame_exclusive':cursor+row['frames'],'status':row['status']});cursor+=row['frames']
        return {'path':name+'.mp4','frames':cursor,'duration_seconds':cursor/24,'timeline':timeline,'sha256':digest(out/(name+'.mp4'))}
    entrance=assemble('pashtun-entrance-rough-v02',[opening,*continuation])
    trailer=assemble('trailer-timing-rough-v01',[opening,archive,sikh,gurkha,mission,*continuation,chemistry,assembly,title])
    if entrance['frames']!=360 or trailer['frames']!=1800:raise ValueError('Editorial duration mismatch')
    manifest={'version':1,'exchange':189,'clips':rows,'entrance':entrance,'trailer':trailer,
        'audio':False,'release_ready':False,'visual_review':'NOT_RUN',
        'limits':['Eight seconds native proof across opening and decision; all remaining action explicitly boards or timing cards',
            '15-second entrance retains native six seconds rather than accelerating it to fit old five-second slot',
            '75-second trailer redistributes one second from archival/start boundaries and places route continuation in action montage',
            'No identity/costume/affiliation/dialogue/quote/title/rights lock or completed trailer claim']}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'entrance':entrance['path'],'trailer':trailer['path'],'release_ready':False}))


if __name__=='__main__':main()
