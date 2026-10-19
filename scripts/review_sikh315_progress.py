"""Build one complete chronological review page, never a partial page."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

def main():
    version,page=map(int,sys.argv[1:])
    assert 1<=version<=16 and 1<=page<=29
    base=Path(__file__).resolve().parents[1]/f'.runtime/art-direction/series01-sikh315/movie-{version:02d}'
    width,height=240,427
    sheet=Image.new('RGB',(width*6,(height+23)*4),(32,32,32));draw=ImageDraw.Draw(sheet)
    for j,f in enumerate(range((page-1)*24+1,page*24+1)):
        p=base/'frames'/f'frame-{f:04d}.png'
        with Image.open(p) as source:
            source.load();assert source.size==(720,1280)
            im=source.convert('RGB');im.thumbnail((width,height))
        x=(j%6)*width;y=(j//6)*(height+23)
        sheet.paste(im,(x,y));draw.text((x+4,y+height+3),p.stem,fill='white')
    out=base/'progress-sheets';out.mkdir(exist_ok=True)
    sheet.save(out/f'chronology-{page:02d}.jpg',quality=93)
    print(f'Complete page{page}: frames{(page-1)*24+1}–{page*24}')

if __name__=='__main__':main()
