"""Prepared isolated continuous proof; dispatch waits for actual appearance review."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'results/sikh362'
template=json.loads((r/'results/sikh361/CONTINUOUS_RENDER_TEMPLATE.json').read_text())
cfg=dict(parent='.runtime/factory-native/sikh362-appearance-c99-save/scene.blend',template='results/sikh353/motion-strategizing-c16.json',cause='Earlier351..361 motion components and99 supporting look require one integrated continuous proof. Static key poses and collision-certified reins cannot establish fluidity or seam stability through transitions.',method='Freeze the current dressed leader/horse and all source performance, camera, crowd and sound. Use admitted save/reopen and actual production-camera frames252..376 at24fps with one-second handles around276..352. Preserve reference phase clocks and current supported reins/seams; inspect complete chronological frames plus reference phase controls, encode a silent review clip and queue full-speed judgment honestly for Director313. No new pose or cloth authoring, timing change or crowd construction.',proof='All125 exact frames and one-second handles complete; canonical283 source/reopen matches, clean diagnostics, no known frame-visible anatomical, garment, tack, groom or contact failures. Chronological original-reference comparison and transition interiors remain required. Full-speed fluidity/timing and all audio stay AWAITING_DIRECTOR_AV/EXCLUDED, never inferred from keys or stills.',scope='Isolated leader/horse performance and integrated appearance only. Existing crowd/principal in handles remain explicitly deferred/unqualified. No sound, full sequence, Pashtun render, provider/spend or external operations.',methods={},sources=['results/sikh362/STRATEGY.md','results/sikh362/REQUEST.md','results/sikh362/appearance-c99.json','results/sikh362/texture-control.json','src/movie_factory/adapters/blender/nihang_finish362.py','src/movie_factory/adapters/blender/nihang_control.py','.runtime/factory-native/sikh361-motion-c24-save/rein361.json'],steps=template['steps'])
for step in cfg['steps']:
    # Same profile as99 production stills, not an unqualified lower-quality
    # substitution. A full1080p release render remains a later separate gate.
    step['recipe'].update(width=432,height=768,samples=16)
    if step['id']=='save':step['requirements']=['preservation']
cfg['sources'].append('results/sikh362/STATIC_REVIEW99.md')
text=json.dumps(cfg,indent=2)+'\n';dest=p/'motion-c25.json'
if dest.exists():assert dest.read_text()==text
else:dest.write_text(text)
