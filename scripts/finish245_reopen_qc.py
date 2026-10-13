"""Compare fixed fresh-process controls to the delivered native sequence."""
import json
from PIL import Image, ImageDraw
from finish245_qc import OUT, differences
from finish242_audition import sha

def main():
    dest = OUT / 'reopen-verification.json'
    if dest.exists():
        raise ValueError('Preserve prior verification')
    rows = []
    canvas = Image.new('RGB', (1080, 816), (235, 230, 215))
    draw = ImageDraw.Draw(canvas)
    for kind, source in [('opening', 'opening-resume-final'), ('route', 'route-final')]:
        folder = OUT / (kind + '-reopen')
        result = json.loads((folder / 'result.json').read_text())
        original = json.loads((OUT / source / 'result.json').read_text())
        assert result['complete'] and result['source_sha256'] == original['source_sha256']
        assert result['profile'] == original['profile']
        for frame in result['frames']:
            p = folder / frame['file']
            q = OUT / source / frame['file']
            assert sha(p) == frame['sha256']
            d = differences(q, p)
            d.update(index=frame['index'], source_sha256=sha(q), replay_sha256=sha(p))
            d['prospective_alarm_pass'] = d['mean'] <= .05 and d['fraction_over4'] <= .001 and d['maximum'] <= 12
            j = len(rows)
            im = Image.open(p).convert('RGB'); im.thumbnail((216, 384))
            x, y = j % 5 * 216, j // 5 * 408
            canvas.paste(im, (x, y)); draw.text((x+4, y+387), str(frame['index']), fill=(20,20,20))
            rows.append(d)
    assert len(rows) == 10
    image = OUT / 'reopen-contact-sheet.jpg'
    canvas.save(image, quality=94)
    report = {'controls': rows, 'all_strict_one_level': all(r['strict_one_level'] for r in rows),
              'all_prospective_alarms_pass': all(r['prospective_alarm_pass'] for r in rows),
              'scope': 'Ten fixed 1080p/16-sample Metal fresh-process controls; does not erase historical210 failure or qualify other hardware/profiles.',
              'contact_sheet_sha256': sha(image)}
    dest.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
