"""Create an unscored, single-performance player from complete 3D-05 previews.

Usage: .venv/bin/python tools/interaction_motion_player.py /absolute/run/path
Keeps every existing evidence artifact intact. No provider calls.
"""
import json
import sys
from pathlib import Path


def write_player(run: Path) -> Path:
    output=run/'motion-playback'/'index.html'
    if output.exists():
        raise ValueError('Preserve existing players; output already exists')
    views=('primary','side','rear')
    sources={v:[f'preview/{v}/frame-{f:04d}.png' for f in range(1,97)] for v in views}
    for paths in sources.values():
        for path in paths:
            if not (output.parent/path).is_file():
                raise ValueError('Incomplete playback: '+path)
    panels=''.join(f'<section class="{v}"><h2>{v.title()}</h2><img id="{v}" src="{sources[v][0]}" alt="{v} motion view"></section>' for v in views)
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>3D-05 coordinated lift prototype</title>
<style>body{background:#171b20;color:#edf1f5;font:16px system-ui;margin:24px auto;max-width:1320px;padding:0 20px}h1{font-size:26px}p{max-width:1000px;line-height:1.5}button,select{font:inherit;padding:8px;margin-right:8px}button{cursor:pointer}input[type=range]{width:320px;max-width:90%}.controls{position:sticky;top:0;background:#171b20ee;padding:12px 0;z-index:1}.views{display:grid;grid-template-columns:1fr 1fr;gap:18px}.primary{grid-column:1/-1;max-width:800px;justify-self:center;width:100%}h2{font-size:18px}img{width:100%;height:auto;display:block}textarea{width:95%;min-height:80px;font:inherit}.status{color:#ffce80}@media(max-width:700px){.views{display:block}}</style>
<h1>Coordinated lift — development preview</h1>
<p>One complete performance, synchronized across three views. This is an <strong>unscored prototype</strong>, not the earlier anonymous timing comparison. Watch the reach, elbow/forearm lift, wrist and sword moving together, and head attention. Torso and lower body remain still.</p>
<p class="status">Validation caveat: the new elbow edge-length probe flags the earlier reach around frame 20 (1.82× versus the 1.50× diagnostic ceiling). The repaired lift is below that ceiling. Naturalness and acceptance remain pending; this preview does not claim GREEN.</p>
<div class="controls"><button id="play" disabled>Play</button><button id="restart" disabled>Restart</button><select id="speed" aria-label="Playback speed"><option value="1">1× speed</option><option value="0.5">½ speed</option><option value="0.25">¼ speed</option></select><label><input id="scrub" type="range" min="1" max="96" value="1" disabled> <span id="frame">Frame 1 / 96</span></label><p id="status">Loading complete sequence…</p></div>
<div class="views">PANELS</div>
<p>The clip plays once at 24 fps and stops at the hold. Restart explicitly to repeat. Slow motion is available for contact inspection. Preview noise comes from the inexpensive four-sample render.</p>
<h2>Review notes</h2><p>Comment on the complete movement, including any reach or elbow deformation. The visible-page timer is a review-time proxy, not proof of attention: <span id="timer">0</span> seconds.</p><textarea id="notes" aria-label="Review notes"></textarea><p><button id="save">Download notes and timing</button></p>
<script>
const paths=SOURCES, runId=RUNID, cache={};let ready=false,playing=false,frame=1,anchorFrame=1,anchorTime=0,visibleMs=0,lastClock=performance.now();
const play=document.getElementById('play'), scrub=document.getElementById('scrub'), status=document.getElementById('status');
function show(f){frame=f;for(const v of Object.keys(paths))document.getElementById(v).src=cache[v][f-1].src;scrub.value=f;document.getElementById('frame').textContent=`Frame ${f} / 96`;}
function stop(){playing=false;play.textContent='Play';}
function begin(){if(frame===96)show(1);playing=true;anchorFrame=frame;anchorTime=performance.now();play.textContent='Pause';}
play.onclick=()=>playing?stop():begin();document.getElementById('restart').onclick=()=>{show(1);begin();};scrub.oninput=()=>{stop();show(Number(scrub.value));};document.getElementById('speed').onchange=()=>{anchorFrame=frame;anchorTime=performance.now();};
function tick(now){if(!document.hidden)visibleMs+=now-lastClock;lastClock=now;document.getElementById('timer').textContent=Math.floor(visibleMs/1000);if(ready&&playing){const f=Math.min(96,anchorFrame+Math.floor((now-anchorTime)/1000*24*Number(document.getElementById('speed').value)));if(f!==frame)show(f);if(f===96)stop();}requestAnimationFrame(tick);}requestAnimationFrame(tick);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
let loaded=0;Promise.all(Object.entries(paths).map(async([v,list])=>{cache[v]=await Promise.all(list.map(async src=>{const img=new Image();img.src=src;await img.decode();status.textContent=`Loading ${++loaded} / 288 frames`;return img;}));})).then(()=>{ready=true;play.disabled=false;scrub.disabled=false;document.getElementById('restart').disabled=false;status.textContent='Ready — all 288 frames loaded. Press Play.';show(1);}).catch(e=>{status.textContent='Playback could not load completely: '+e.message;});
document.getElementById('save').onclick=()=>{const data={run_id:runId,scored:false,status:'DIRECTOR_NOTES_NOT_AUTOMATIC_ACCEPTANCE',notes:document.getElementById('notes').value,visible_page_seconds:visibleMs/1000,timing_basis:'visible page duration; user attention not independently verified',recorded_at_utc:new Date().toISOString()};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));a.download='prototype-review-notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
</script></html>'''
    page=page.replace('PANELS',panels).replace('SOURCES',json.dumps(sources)).replace('RUNID',json.dumps(run.name))
    output.write_text(page)
    return output


if __name__=='__main__':
    print(write_player(Path(sys.argv[1]).resolve()))
