"""Music-only comparison: fixed common sound/picture, earlier source landmark."""
import json,sys,subprocess
import numpy as np
from finish242_audition import ROOT,MUSIC,load,sha
from finish245_audio import RATE,DURATION,music_gain,measure
from finish237_audio import wav

BASE=ROOT/'.runtime/art-direction/series01-finish245'
OUT=ROOT/'.runtime/art-direction/series01-finish246'
TURN=11.75
SOURCE_TURN=51.0
START=SOURCE_TURN-TURN

def replace_music(a_mix,a_music,b_music,master):
    if a_mix.shape!=a_music.shape or a_mix.shape!=b_music.shape:
        raise ValueError('Music/common stem duration mismatch')
    common=a_mix-master*a_music
    return common+master*b_music,common

def audio():
    out=OUT/'audio01'
    if out.exists():raise ValueError('Preserve comparison')
    manifest=json.loads((BASE/'audio02/manifest.json').read_text())
    if sha(MUSIC)!=manifest['music_source_sha256']:raise ValueError('Changed theme source')
    a=load(BASE/'audio02/mix.wav');am=load(BASE/'audio02/music.wav')
    t=np.arange(len(a))/RATE;source=load(MUSIC)
    b=source[round(START*RATE):round((START+DURATION)*RATE)]*music_gain(t)[:,None]
    if len(a)!=round(DURATION*RATE):raise ValueError('Changed master duration')
    master=manifest['master_gain'];mix,common=replace_music(a,am,b,master)
    if np.max(abs(mix))>=.95:raise ValueError('B requires explicit music-only headroom reassessment')
    out.mkdir(parents=True);wav(out/'music.wav',b);wav(out/'mix.wav',mix)
    encoded=load(out/'mix.wav');levels=measure(out/'mix.wav')
    if float(levels['input_tp'])>-.9:raise ValueError('True-peak headroom needs reassessment')
    residual=float(np.max(abs((encoded-master*b)-common)))
    if residual>3e-7:raise ValueError('Common sound changed beyond PCM quantization')
    windows=[('first_line',1.5,3.65),('races_approximate',2.7,3.65),('credentials',4.08,5.47),('impeccable',5.92,manifest['voice_end'])]
    voice=load(BASE/'audio02/voice.wav')*master;margins=[]
    for label,lo,hi in windows:
        i,j=round(lo*RATE),round(hi*RATE);v=voice[i:j];other=mix[i:j]-v
        margins.append({'window':label,'voice_over_competing_rms_db':float(20*np.log10((np.sqrt(np.mean(v*v))+1e-12)/(np.sqrt(np.mean(other*other))+1e-12)))})
    record={'source_sha256':sha(MUSIC),'a_interval':manifest['music_interval'],'b_interval':[START,START+DURATION],
      'source_turn':SOURCE_TURN,'turn_time':TURN,'following_harmonica_source_landmark':52,'following_landmark_edit_time':52-START,
      'duration':DURATION,'music_gain':'Identical finish245 ramp; no constant trim, tempo change or independent master normalization',
      'master_gain':master,'common_sound_residual_max':residual,'common_sound_definition':'Original A final PCM minus its stored music times original master; identical common component retained in B',
      'common_source_hashes':{p:sha(BASE/'audio02'/p) for p in ['mix.wav','music.wav','voice.wav','physical-effects.wav','wind.wav','manifest.json']},
      'b_hashes':{p:sha(out/p) for p in ['mix.wav','music.wav']},'loudness':levels,'masking_margins':margins,
      'listening':'NOT_RUN; Director-requested source landmarks, not agent auditory/taste approval','new_paid_calls':0}
    (out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))

def video_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def deliver():
    out=OUT/'delivery01';audio_dir=OUT/'audio01';a_dir=BASE/'delivery01'
    if out.exists():raise ValueError('Preserve delivery')
    record=json.loads((audio_dir/'manifest.json').read_text());am=json.loads((a_dir/'manifest.json').read_text())
    if sha(audio_dir/'mix.wav')!=record['b_hashes']['mix.wav']:raise ValueError('Changed B sound')
    out.mkdir(parents=True);rows=[]
    for a_name,b_name in [('pashtun-entrance-complete.mp4','pashtun-B-earlier-music.mp4'),('pashtun-entrance-captioned.mp4','pashtun-B-earlier-music-captioned.mp4')]:
        ap=a_dir/a_name;bp=out/b_name
        if sha(ap)!=am['deliveries'][a_name]:raise ValueError('Changed A delivery')
        subprocess.run(['ffmpeg','-v','error','-i',str(ap),'-i',str(audio_dir/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t','22.5','-movflags','+faststart',str(bp)],check=True)
        va,vb=video_hash(ap),video_hash(bp)
        if va!=vb:raise ValueError('Picture changed in music-only comparison')
        subprocess.run(['ffmpeg','-v','error','-i',str(bp),'-f','null','-'],check=True)
        rows.append({'a_path':str(ap.relative_to(ROOT)),'b_file':b_name,'a_sha256':sha(ap),'b_sha256':sha(bp),'identical_video_sha256':va,'encoded_loudness':measure(bp)})
    (out/'manifest.json').write_text(json.dumps({'variants':rows,'audio_manifest_sha256':sha(audio_dir/'manifest.json'),'publication':False,'auditory_acceptance':'PENDING_DIRECTOR'},indent=2)+'\n');print(json.dumps(rows))

if __name__=='__main__':
    if sys.argv[1:]==['audio']:audio()
    elif sys.argv[1:]==['deliver']:deliver()
    else:raise ValueError('Closed music comparison operation')
