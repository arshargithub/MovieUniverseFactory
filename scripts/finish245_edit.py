"""Complete native-frame assembly and editable manuscript/caption deliveries."""
import json,subprocess
from pathlib import Path
import numpy as np
from finish242_audition import ROOT,sha
OUT=ROOT/'.runtime/art-direction/series01-finish245'

def manuscript():
    header=r'''[Script Info]
ScriptType: v4.00+
PlayResX: 432
PlayResY: 768
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Paper,Baskerville,20,&H00332D26,&H00332D26,&H004A4134,&H60000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Ink,Apple Chancery,26,&H002E2924,&H002E2924,&H002E2924,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    def line(layer,style,text):return f'Dialogue: {layer},0:00:03.80,0:00:08.50,{style},,0,0,0,,{{\\fad(220,250)}}{text}\n'
    body=line(0,'Paper',r'{\pos(0,0)\blur4\c&HB4C9D8&\alpha&H10&\p1}m 14 12 l 418 16 423 132 389 140 345 144 294 143 246 150 198 143 155 149 104 142 55 141 11 132 14 12{\p0}')
    body+=line(1,'Paper',r'{\pos(0,0)\blur9\c&HBCCEDB&\alpha&H65&\p1}m 10 119 l 423 119 424 147 367 150 314 159 262 152 212 162 152 152 100 158 48 148 9 145 10 119{\p0}')
    rng=np.random.default_rng(245)
    # Low-contrast fiber flecks inside the original graphic; not fake prose.
    for i in range(55):
        x=float(rng.uniform(20,412));y=float(rng.uniform(18,137));w=float(rng.uniform(.7,2.3))
        body+=line(1,'Paper',f'{{\\pos(0,0)\\blur1\\c&H78939F&\\alpha&HCA&\\p1}}m {x:.1f} {y:.1f} l {x+w:.1f} {y+.3:.1f} {x+w:.1f} {y+.7:.1f} {x:.1f} {y+.4:.1f}{{\\p0}}')
    for txt,y,size in [('The Pathans:',22,23),('“a hardy and',49,29),('martial people”',80,29),('— Sir Winston Churchill',119,18)]:
        font=r'\fnBaskerville' if 'Churchill' in txt else ''
        body+=line(2,'Ink',f'{{\\pos(216,{y})\\fs{size}{font}}}{txt}')
    return header+body

SRT='''1
00:00:01,500 --> 00:00:03,650
We call them martial races.

2
00:00:04,050 --> 00:00:05,480
Their credentials are …

3
00:00:05,920 --> 00:00:06,690
impeccable.
'''

def prepare_graphics():
    folder=OUT/'graphics01'
    if folder.exists():raise ValueError('Preserve graphics')
    folder.mkdir(parents=True);(folder/'manuscript.ass').write_text(manuscript());(folder/'narration.srt').write_text(SRT)
    return folder

def sources():
    rows=[]
    for kind,start,count in [('opening',0,234),('route',234,306)]:
        folder=OUT/('opening-resume-final' if kind=='opening' else 'route-final');r=json.loads((folder/'result.json').read_text())
        if not r['complete'] or [x['index'] for x in r['frames']]!=list(range(start,start+count)):raise ValueError('Incomplete native frames')
        for row in r['frames']:
            p=folder/row['file']
            if sha(p)!=row['sha256']:raise ValueError('Changed frame')
            rows.append({'path':str(p),'sha256':row['sha256'],'index':row['index']})
    return rows

def main():
    folder=OUT/'delivery01'
    if folder.exists():raise ValueError('Preserve delivery')
    rows=sources();folder.mkdir();graphic=OUT/'graphics01/manuscript.ass';sound=OUT/'audio02/mix.wav'
    (folder/'narration.srt').write_text(SRT)
    (folder/'narration.vtt').write_text('WEBVTT\n\n'+SRT.replace(',','.'))
    concat=folder/'frames.ffconcat';concat.write_text('ffconcat version 1.0\n'+''.join("file '"+r['path']+"'\noption framerate 24\nduration 0.0416666666667\n" for r in rows))
    clean=folder/'pashtun-entrance-complete.mp4'
    color=['-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-color_range','tv']
    subprocess.run(['ffmpeg','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(sound),'-map','0:v:0','-map','1:a:0','-vf','ass='+str(graphic)+',scale=out_color_matrix=bt709:out_range=tv','-r','24','-frames:v','540','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p',*color,'-c:a','aac','-b:a','256k','-ar','48000','-t','22.5','-movflags','+faststart',str(clean)],check=True)
    captioned=folder/'pashtun-entrance-captioned.mp4'
    style='FontName=Baskerville,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00222222,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=100'
    subprocess.run(['ffmpeg','-v','error','-i',str(clean),'-vf',f"subtitles={OUT/'graphics01/narration.srt'}:force_style='{style}'",'-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p',*color,'-c:a','copy','-movflags','+faststart',str(captioned)],check=True)
    for p in [clean,captioned]:subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    (folder/'manifest.json').write_text(json.dumps({'frames':rows,'unique_native_frames':540,'duration':22.5,'resolution':[1080,1920],'audio':sha(sound),'manuscript':sha(graphic),'deliveries':{p.name:sha(p) for p in [clean,captioned,folder/'narration.srt',folder/'narration.vtt']},'publication_authorized':False},indent=2)+'\n')
if __name__=='__main__':main()
