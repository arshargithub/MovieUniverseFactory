"""Read-only media intake verification; writes a separate immutable inventory."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'artifacts/imports/suno-theme-01'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    if sys.argv[1:]:raise ValueError('Closed Suno239 intake')
    out=BASE/'source-details/media-inventory.json'
    if out.exists():raise ValueError('Preserve existing inventory')
    master=BASE/'original/Harmonic Release.wav'
    if not master.is_file():raise ValueError('Missing original WAV')
    paths=[master]+sorted(p for p in (BASE/'stems').rglob('*') if p.suffix.lower() in ('.wav','.mp3') and p.is_file())
    rows=[]
    for p in paths:
        if not p.resolve().is_relative_to(BASE.resolve()):raise ValueError('External symlink')
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
        audio=[s for s in probe['streams'] if s['codec_type']=='audio']
        if len(audio)!=1:raise ValueError('Unexpected stream count')
        a=audio[0]
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
        rows.append(dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p),codec=a['codec_name'],
            sample_rate=int(a['sample_rate']),channels=a['channels'],duration_seconds=float(a.get('duration',probe['format']['duration'])),
            duration_ts=a.get('duration_ts'),time_base=a.get('time_base'),bits_per_sample=a.get('bits_per_sample'),complete_decode=True))
    result=dict(source_selection_sha256=sha(BASE/'source-details/director-selection.json'),files=rows,
        wav_stems=sum(p.suffix.lower()=='.wav' for p in paths[1:]),mp3_stems=sum(p.suffix.lower()=='.mp3' for p in paths[1:]),
        master_preserved=True,agent_perceptual_listening='NOT_RUN',backup_verified=False,
        note='Equal durations alone do not prove sample alignment or source-sum parity; separated labels are not verified instrumentation.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(master=rows[0],wav_stems=result['wav_stems'],mp3_stems=result['mp3_stems'],inventory=str(out)),indent=2))
if __name__=='__main__':main()
