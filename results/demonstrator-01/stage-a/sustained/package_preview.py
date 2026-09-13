from pathlib import Path
import json,hashlib,math,sqlite3,time,subprocess
from PIL import Image,ImageDraw,ImageStat
root=Path('/Users/adisharma/projects/MovieUniverseFactory');base=root/'runs/demonstrator-01';out=root/'results/demonstrator-01/stage-a/sustained';review=base/'sustained-preview'
media={};render_summary={}
for view in ('hero','contact'):
 rows=[];folder=review/(view+'-frames');folder.mkdir(exist_ok=True)
 for part in ('cycle','rest'):
  run=base/f'smooth-{view}-{part}'
  assert json.loads((run/'worker-status.json').read_text())['ok']
  data=json.loads((run/'render-times.json').read_text());rows+=data['frames']
  assert data['scene_sha256']==json.loads((out/'current-scene.json').read_text())['sha256']
 assert [r['frame'] for r in rows]==list(range(144))
 for f in range(144):
  source=base/f'smooth-{view}-{"cycle" if f<24 else "rest"}'/f'{f:04d}.png'
  destination=folder/source.name
  if not destination.exists():destination.symlink_to(Path('..')/'..'/source.parent.name/source.name)
  assert destination.resolve()==source.resolve()
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','0','-i',str(folder/'%04d.png'),'-frames:v','144','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(review/(view+'.mp4'))],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,nb_frames,duration','-show_entries','format=duration','-of','json',str(review/(view+'.mp4'))]))
 assert probe['streams'][0]['nb_frames']=='144' and abs(float(probe['format']['duration'])-6)<.001
 brightness=[]
 for f in range(144):
  with Image.open(folder/f'{f:04d}.png') as frame:brightness.append(sum(ImageStat.Stat(frame.convert('RGB')).mean)/3)
 probe['frame_brightness']={'minimum':min(brightness),'maximum':max(brightness),'last':brightness[-1],'last_to_mean_ratio':brightness[-1]/(sum(brightness)/144),'screen_no_black_frames':min(brightness)>20}
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-i',str(review/(view+'.mp4')),'-f','null','-'],check=True)
 media[view]=probe
 values=[r['seconds'] for r in rows];render_summary[view]={'frames':144,'seconds':sum(values),'mean_seconds_per_frame':sum(values)/144,'max_seconds_per_frame':max(values)}
# Sample complete duration and final frame in one inspection artifact.
canvas=Image.new('RGB',(1280,1080),'white');draw=ImageDraw.Draw(canvas)
frames=[0,16,32,48,64,80,96,112,128,143]
for row,view in enumerate(('hero','contact')):
 for i,f in enumerate(frames):
  im=Image.open(review/(view+'-frames')/f'{f:04d}.png');im.thumbnail((256,144));x=i%5*256;y=(row*2+i//5)*180;canvas.paste(im,(x,y));draw.text((x+5,y+145),f'{view} frame {f}',fill='black')
canvas.crop((0,0,1280,720)).save(out/'full-duration-contact-sheet.jpg')
(out/'media-validation.json').write_text(json.dumps(media,indent=2)+'\n');(out/'render-summary.json').write_text(json.dumps(render_summary,indent=2)+'\n')
validation=json.loads((base/'smooth-reopen/reopen.json').read_text());compact={k:v for k,v in validation.items() if k!='samples'};compact['native_control']=json.loads((base/'smooth-contact-control/contact-control.json').read_text());compact['source_closure_ref']='runs/demonstrator-01/sustained-closure/closure.json';(out/'validation-summary.json').write_text(json.dumps(compact,indent=2)+'\n')
auth=json.loads((out/'authorization.json').read_text());events=[json.loads(r[0]) for r in sqlite3.connect(root/'.runtime/experiment-ops.sqlite3').execute('select payload from events order by seq')];starts={};jobs=[]
for e in events:
 if e.get('experiment_id')!='DEMONSTRATOR-01':continue
 if e.get('event_type')=='job_started' and e.get('monotonic_seconds',0)>=auth['monotonic_start']:starts[e['job_id']]=e
 if e.get('event_type')=='job_completed' and e.get('job_id') in starts:
  a=starts[e['job_id']];jobs.append({'job_id':e['job_id'],'kind':a.get('job_kind'),'phase':a['phase'],'outcome':e.get('outcome'),'seconds':e['monotonic_seconds']-a['monotonic_seconds'],'clock_id':a['clock_id']})
operating={'activity_envelope_monotonic_seconds':time.monotonic()-auth['monotonic_start'],'pure_active_engineering_seconds':None,'note':'Activity envelope includes overlapping local jobs and supervision; pure active thinking is not independently measured. Native process sums are not wall time. Historical UTC discontinuity prevents whole-Stage-A exact net timing.','native_process_seconds':sum(j['seconds'] for j in jobs if j['kind']=='native'),'jobs':jobs,'director_review_seconds':None,'subscription_tokens':None};(out/'operating-summary.json').write_text(json.dumps(operating,indent=2)+'\n')
cost=json.loads((out/'costs.json').read_text());hero=render_summary['hero']['mean_seconds_per_frame'];scene=json.loads((out/'current-scene.json').read_text());activity=operating['activity_envelope_monotonic_seconds']/60;native=operating['native_process_seconds']/60
report=f'''# Six-second full-pace gallop — Stage A review packet

**Development preview ready for Director playback review; Stage A remains YELLOW.** This is an integrated horse/rider/tail/dust result, not a completed four-shot film or a formal GREEN motion qualification.

[Open synchronized playback](../../../../runs/demonstrator-01/sustained-preview/review.html) · [Hero MP4](../../../../runs/demonstrator-01/sustained-preview/hero.mp4) · [Dust-free MP4](../../../../runs/demonstrator-01/sustained-preview/contact.mp4)

## Delivered version

Both videos contain exactly 144 frames at 24 fps: **6.000 seconds**, with no duplicate endpoint. Hero is 960×540; the inspection view is 640×360. The motion is frozen at 12 m/s (43.2 km/h), 2.2 cycles/s and approximately 5.45 m stride. The complete physical timeline travels 72 m from frame 0 to the unrendered frame-144 endpoint. Source-authored gallop channels were retimed as coordinated leg families; rolling material pivots and a wider airborne capture blend preserve contact without the earlier abrupt touchdown capture. Source torso/rider motion remains the seed.

Tail has 896 tapered strands grouped into coherent clumps, fuller tips and travelling shape-key motion. Dust combines low contact plumes, a diffuse trailing volume and ballistic grit, seeded from hoof contact events with pre-roll. These are deterministic authored effects, including an ambient emission approximation in Eevee, not physical fluid/hair simulation. The ground is a review backdrop; scenery, sound and cinematic finishing remain for the film.

Final native scene: [scene.blend](../../../../runs/demonstrator-01/smooth-fx/scene.blend), SHA-256 `{scene['sha256']}`.

## Evidence and its limits

- Final saved-scene scan: 1,153 samples at 1/8-frame spacing, plus all integer-frame horse vertices checked for finite coordinates. Fixed-material ground-band travel: **{compact['max_material_point_ground_band_travel_m']*1000:.2f} mm**; sampled hoof penetration: **0**; maximum rein gap: **{compact['max_rein_gap_m']*1000:.2f} mm**.
- Independent off-grid control: positive **{compact['native_control']['positive']['max_material_ground_band_travel_m']*1000:.2f} mm** versus **{compact['native_control']['path_speed_125pct']['max_material_ground_band_travel_m']*1000:.1f} mm** in an actual +25% path-speed animation variant. The 20 mm material-contact screen rejects the corruption. This uses evaluated mesh points, not altered measured JSON.
- The historical 50 mm near-floor centroid screen still fails: **{compact['max_near_floor_travel_m']*1000:.1f} mm**. Its result remains in the records. Rolling changes the lowest-decile membership; fixed material points supply the independent contact evidence. The refinement is documented in the motion brief and is preview admission, not a retroactive campaign GREEN.
- The pre-touchdown speed diagnostic fell from 70.5 to **{compact['peak_hoof_centroid_speed']['mps']:.2f} m/s** after broadening the airborne correction. This centroid statistic is a temporal diagnostic, not a validated biological speed bound. Maximum integer-frame mesh RMS step is **{compact['max_integer_mesh_rms_step_local_m']:.4f} m**; no borrowed human-rig threshold is applied.
- Source closure at held-out poses reproduced the admitted evaluated source to sub-0.01 mm differences. That isolates state restoration; it does not certify all deformations in the modified gait. There is no new comprehensive anatomical strain qualification for this horse.
- **43 relevant offline tests passed.** Complete rendered-cycle frames and full-duration/final-frame contact sheets were inspected. Neither those stills nor the advisory API critique establish temporal realism. Director full playback acceptance and review duration remain unrecorded.

The API critique was on an earlier selected-frame version and was advisory. It identified a wedge-like tail, diffuse dust contact, crowded framing, and a relatively upright rider. Tail tips, dust contact, framing and airborne capture were subsequently refined. The free horse remains angular/stylized in places, and the rider remains relatively upright. A credible visual judgment must come from playback; no photorealism claim is made.

[Validation summary](validation-summary.json) · [Full scan](../../../../runs/demonstrator-01/smooth-reopen/reopen.json) · [Full-duration contact sheet](full-duration-contact-sheet.jpg) · [Media checks](media-validation.json)

## Time, money and process

Current pass activity envelope: approximately **{activity:.1f} minutes**, including overlapping render/validation supervision. Native process sum: **{native:.1f} minutes**; do not add it to the activity envelope as elapsed time. Pure active engineering and subscription token use are not independently known. Both authorized four-hour ceilings remain respected using the conservative activity envelope for engineering. Historical Stage A UTC discontinuities remain disclosed.

New paid model API cost: **${cost['this_pass_calculated_usd']:.6f}**; cumulative demonstrator cost **${cost['known_cost_usd']:.6f}**, with no unresolved reservations. These include reasoning and all calls/retries and are conservative calculated estimates, not provider-invoice reconciliation. The effective cap is **$50 cumulative**, within the approved additional $47.45 and preserving the original $50 buffer. No purchases, paid media or cloud rendering occurred.

The pass included discarded gait/contact variants, an impractical CPU Cycles volume frame, a timed-out scan, and two cancelled pairs of partial renders. All remain preserved and count toward the totals. [Process review](PROCESS_REVIEW.md) records why and how to avoid the rework. No historical evidence was deleted, no closed campaign was reopened, and nothing was pushed or uploaded.

## Stage A gate and recommended next step

First review the six-second hero at normal speed, then the dust-free view. Judge matched stride/travel, weight and rider coupling, hoof contact, tail flow and dust continuity. Please give one consolidated readiness verdict and review duration; identify any dominant remaining defect. This is not an A/B preference campaign.

**If this motion/look is worth using, the next step is one complete 24-second, four-shot rough cut with provisional local sound**, following The Courier charter. Reuse this scene and existing assets; add the mountain-road/watchtower staging, signal and rider response through coordinated pose/framing/editing. No new rig project or harness rewrite.

Proposed scope freeze: 24 fps, 960×540 Eevee rough cut, approximately 6+7+5+6 seconds, one lighting treatment and dust. Proposed next-stage ceiling: **3 active engineering hours and 2 local render hours**, still within the existing paid API cap, with at most **$5 additional API exposure allocated to the rough cut**. No purchases/cloud/media charges. These are forecasts requiring Stage A agreement, not new authorization inferred from this preview.

The measured hero render averaged **{hero:.2f} seconds/frame** in this two-view local run. A 576-frame cut at that rate is **{576*hero/60:.1f} render minutes** before scenery overhead or changes. Budgeting approximately 60–120 minutes permits added scenery and affected-shot retries; benchmark one populated frame before committing. 720p/1080p finishing is not frozen or promised from the 540p measurement. Full production has not started.

## Durability

[Reproduction guide](REPRODUCIBILITY.md) · [Source snapshot](source-snapshot.zip) · [Source binding](source-binding.json) · [Cost ledger summary](costs.json) · [Operating summary](operating-summary.json) · [Checksums](manifest.json)

Source binding is a retrospective dirty-worktree snapshot; the historical Git HEAD does not contain these repairs. The native scene is preserved locally. Existing asset license/redistribution restrictions remain; there is no off-machine durability claim. The manifest references preserved scenes and images instead of duplicating a large archive.
'''
(out/'REPORT.md').write_text(report)
print(json.dumps({'media':media,'render':render_summary,'activity_minutes':activity,'native_minutes':native},indent=2))
