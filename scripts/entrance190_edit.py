"""Replace remaining entrance boards with reviewed native route coverage."""
import json
import shutil
from pathlib import Path
from entrance189_edit import ROOT,ART,BASE,FONT,run,digest


def admitted(folder,filename):
    media=json.loads((folder/'media.json').read_text());gate=json.loads((folder/'internal-review.json').read_text())
    result=json.loads((folder/'result.json').read_text())
    source=result.get('source_sha256')
    if gate.get('status')!='PROCEED_TO_EDIT' or gate.get('source_sha256')!=source or not source:raise ValueError('Integrated visual review missing')
    path=folder/filename
    if digest(path)!=media['video_sha256']:raise ValueError('Reviewed video changed')
    for r in media['frames']:
        if digest(folder/r['name'])!=r['sha256']:raise ValueError('Reviewed native frame changed')
    return path


def main():
    old=ART/'series01-trailer-edit189';out=ART/'series01-trailer-edit190'
    prior=json.loads((old/'manifest.json').read_text())
    action=admitted(BASE/'entrance190-motion33','motion-proof.mp4')
    geographic=admitted(BASE/'entrance190-geography23','geography-proof.mp4')
    opening=admitted(BASE/'entrance190-opening-review35','entrance-proof.mp4')
    blinkfolder=BASE/'entrance190-blink-review04';blink=blinkfolder/'decision-proof.mp4'
    br=json.loads((blinkfolder/'media.json').read_text());bg=json.loads((blinkfolder/'internal-review.json').read_text())
    if bg.get('status')!='PROCEED_TO_EDIT' or bg.get('source_sha256')!=br['source_sha256'] or digest(blink)!=br['video_sha256']:raise ValueError('Blink review missing')
    for row in br['frames']:
        if digest(blinkfolder/row['name'])!=row['sha256']:raise ValueError('Reviewed blink frame changed')
    if out.exists():raise ValueError('Preserve previous edit')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());clips={}
    removed={'pashtun-opening','route-reveal','route-decision','gather-and-turn','uphill-drive'}
    for row in prior['clips']:
        if row['name'] in removed:continue
        # Prior finished review edit is immutable; record exact copied hashes.
        source=old/row['path'];target=out/row['path'];shutil.copy2(source,target)
        clips[row['name']]={**row,'reused_from':str(source.relative_to(ROOT)),'sha256':digest(target)}
    def clip(name,source,frames,title,note,start_frame=0):
        target=out/(name+'.mp4')
        filters=[f'trim=start_frame={start_frame}:end_frame={start_frame+frames}','setpts=PTS-STARTPTS','scale=648:1152:force_original_aspect_ratio=decrease','pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0x202735','setsar=1','fps=24']
        for text,y,size in ((title,24,24),(note,1218,19)):
            if any(c in text for c in "':\\"):raise ValueError('Unsafe production caption')
            size=min(size,int(648/max(1,len(text))/.57))
            filters.append(f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:fontcolor=white:x=(w-tw)/2:y={y}")
        run(['-i',str(source),'-vf',','.join(filters),'-frames:v',str(frames),'-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(target)])
        clips[name]={'name':name,'frames':frames,'fps':24,'source_start_frame':start_frame,'status':'NATIVE_PREVIEW','source':str(source.relative_to(ROOT)),'source_sha256':digest(source),'path':target.name,'sha256':digest(target),'caption':title,'note':note}
    clip('pashtun-opening',opening,144,'NATIVE PREVIEW - riding entrance','Original opening with corrected blink timing')
    clip('route-reveal',geographic,48,'NATIVE PREVIEW - the route choice','Shared geography - neutral barrier remains provisional')
    clip('route-decision',blink,48,'NATIVE PREVIEW - attention and decision','Faster asymmetric blink - selected likeness preserved')
    clip('gather-turn-uphill',action,192,'NATIVE PREVIEW - gather turn and climb','Actual coordinated route - preview resolution - no sound')
    # Keep the complete18-second proof while respecting the established60-75s
    # trailer range. Excerpt actual motion, never accelerate or synthesize it.
    clip('route-reveal-trailer',geographic,36,'NATIVE PREVIEW - the route choice','Shared geography - neutral barrier remains provisional')
    clip('route-decision-trailer',blink,36,'NATIVE PREVIEW - attention and decision','Faster asymmetric blink - selected likeness preserved',start_frame=6)
    clip('gather-turn-uphill-trailer',action,144,'NATIVE PREVIEW - gather turn and climb','Native excerpt - complete maneuver in the entrance proof',start_frame=24)
    def assemble(name,names):
        listing=out/(name+'.ffconcat');listing.write_text('ffconcat version 1.0\n'+''.join("file '"+clips[n]['path']+"'\n" for n in names))
        target=out/(name+'.mp4');run(['-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(target)])
        cursor=0;timeline=[]
        for n in names:
            row=clips[n];timeline.append({'clip':n,'start_frame':cursor,'end_frame_exclusive':cursor+row['frames'],'status':row['status']});cursor+=row['frames']
        return {'path':target.name,'frames':cursor,'duration_seconds':cursor/24,'timeline':timeline,'sha256':digest(target)}
    continuation=['route-reveal','route-decision','gather-turn-uphill']
    entrance=assemble('pashtun-entrance-rough-v03',['pashtun-opening',*continuation])
    trailer_continuation=['route-reveal-trailer','route-decision-trailer','gather-turn-uphill-trailer']
    trailer=assemble('trailer-timing-rough-v02',['pashtun-opening','archival-contrast','sikh-confrontation','gurkha-protection','missing-informant',*trailer_continuation,'action-and-chemistry','three-before-the-officer','the-martials'])
    if entrance['frames']!=432 or trailer['frames']!=1800:raise ValueError('Unexpected editorial duration')
    (out/'manifest.json').write_text(json.dumps({'exchange':190,'clips':list(clips.values()),'entrance':entrance,'trailer':trailer,'audio':False,'release_ready':False,'visual_review':'NOT_RUN','limits':['18-second entrance now entirely native preview coverage, not final-resolution film','75-second whole-trailer timing rough uses15seconds of native excerpts and retains60seconds of explicitly unbuilt/art-direction/archival cards','Provisional neutral obstruction does not establish guard affiliation or story canon','No final sound, voice, music, quotation rights or release qualification']},indent=2)+'\n')

if __name__=='__main__':main()
