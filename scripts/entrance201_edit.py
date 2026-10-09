"""Update established entrance/trailer timing without inventing finished scenes."""
import json,shutil
from pathlib import Path
from entrance189_edit import ROOT,ART,BASE,FONT,run,digest

def admitted(stage):
    folder=BASE/('entrance201-'+stage);media=json.loads((folder/'media.json').read_text());gate=json.loads((folder/'internal-review.json').read_text());r=json.loads((folder/'result.json').read_text())
    if gate.get('status')!='PROCEED_TO_EDIT' or gate.get('source_sha256')!=r['source_sha256'] or media['source_sha256']!=r['source_sha256']:raise ValueError('Missing source-bound visual review')
    p=folder/'proof.mp4'
    if digest(p)!=media['sha256']:raise ValueError('Video changed')
    for row in media['frames']:
        if digest(folder/f"frame-{row['frame']:04d}.png")!=row['sha256']:raise ValueError('Frame changed')
    return p

def main():
    opening=admitted('opening06');attention=admitted('attention07');route=admitted('route08');geography=admitted('geography09')
    old=ART/'series01-trailer-edit190';prior=json.loads((old/'manifest.json').read_text());out=ART/'series01-trailer-edit201'
    if out.exists():raise ValueError('Preserve prior edit')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());clips={}
    retained=('archival-contrast','sikh-confrontation','gurkha-protection','missing-informant','action-and-chemistry','three-before-the-officer','the-martials')
    for row in prior['clips']:
        if row['name'] not in retained:continue
        source=old/row['path']
        if digest(source)!=row['sha256']:raise ValueError('Prior card changed')
        target=out/row['path'];shutil.copy2(source,target);clips[row['name']]={**row,'reused_from':str(source.relative_to(ROOT))}
    def clip(name,source,count,title,note,start=0):
        target=out/(name+'.mp4');filters=[f'trim=start_frame={start}:end_frame={start+count}','setpts=PTS-STARTPTS','scale=648:1152:force_original_aspect_ratio=decrease','pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=0x202735','setsar=1','fps=24']
        for text,y,size in ((title,24,24),(note,1218,19)):
            if any(c in text for c in "':\\"):raise ValueError('Unsafe caption')
            size=min(size,int(648/max(1,len(text))/.57));filters.append(f"drawtext=fontfile={FONT}:text='{text}':fontsize={size}:fontcolor=white:x=(w-tw)/2:y={y}")
        run(['-i',str(source),'-vf',','.join(filters),'-frames:v',str(count),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)])
        clips[name]={'name':name,'frames':count,'fps':24,'source_start_frame':start,'status':'NATIVE_PREVIEW','source':str(source.relative_to(ROOT)),'source_sha256':digest(source),'path':target.name,'sha256':digest(target),'caption':title,'note':note}
    clip('pashtun-opening',opening,144,'NATIVE PREVIEW - riding entrance','Painted earth and dramatic dust - revised head covering')
    clip('route-reveal',geography,48,'NATIVE PREVIEW - the route choice','Shared geography - neutral barrier remains provisional')
    clip('route-decision',attention,48,'NATIVE PREVIEW - attention and decision','Integrated rider and costume treatment')
    clip('gather-turn-uphill',route,192,'NATIVE PREVIEW - gather turn and climb','Coordinated route and path-following dust - no sound')
    clip('route-reveal-trailer',geography,36,'NATIVE PREVIEW - the route choice','Shared geography - neutral barrier remains provisional')
    clip('route-decision-trailer',attention,36,'NATIVE PREVIEW - attention and decision','Integrated rider and costume treatment',6)
    clip('gather-turn-uphill-trailer',route,144,'NATIVE PREVIEW - gather turn and climb','Native excerpt - complete maneuver in entrance proof',24)
    def assemble(name,names):
        listing=out/(name+'.ffconcat');listing.write_text('ffconcat version 1.0\n'+''.join("file '"+clips[n]['path']+"'\n" for n in names));target=out/(name+'.mp4');run(['-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(target)])
        cursor=0;timeline=[]
        for n in names:
            row=clips[n];timeline.append({'clip':n,'start_frame':cursor,'end_frame_exclusive':cursor+row['frames'],'status':row['status']});cursor+=row['frames']
        return {'path':target.name,'frames':cursor,'duration_seconds':cursor/24,'timeline':timeline,'sha256':digest(target)}
    entrance=assemble('pashtun-entrance-v201',['pashtun-opening','route-reveal','route-decision','gather-turn-uphill'])
    trailer=assemble('trailer-timing-v201',['pashtun-opening','archival-contrast','sikh-confrontation','gurkha-protection','missing-informant','route-reveal-trailer','route-decision-trailer','gather-turn-uphill-trailer','action-and-chemistry','three-before-the-officer','the-martials'])
    if entrance['frames']!=432 or trailer['frames']!=1800:raise ValueError('Editorial timing changed')
    (out/'manifest.json').write_text(json.dumps({'exchange':201,'clips':list(clips.values()),'entrance':entrance,'trailer':trailer,'audio':False,'release_ready':False,'visual_review':'NOT_RUN','limits':['18-second native preview;432x768 source presented in720x1280 review frame, not final-resolution film','75-second timing rough retains60seconds of explicitly unfinished cards and15seconds of native excerpts','No new story affiliation, quotation, sound or release qualification']},indent=2)+'\n')

if __name__=='__main__':main()
