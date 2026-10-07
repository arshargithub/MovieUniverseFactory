"""Small allowlisted CC0 asset acquisition, no credentials or uploads."""
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / '.runtime/assets/entrance-astra'
MODELS = ('rock_face_01', 'namaqualand_boulder_03', 'pine_sapling_small', 'shrub_02')
TEXTURES = ('rocky_terrain', 'rocks_ground_05')
LIMIT = 180_000_000


def get(url):
    if not url.startswith(('https://api.polyhaven.com/', 'https://dl.polyhaven.org/')):
        raise ValueError('Unapproved asset host')
    request = urllib.request.Request(url, headers={'User-Agent': 'MovieUniverseFactory-private-art-proof/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError('Oversized download')
    return data


def main():
    ROOT.mkdir(exist_ok=True, parents=True)
    records = []
    total = 0
    for asset in MODELS + TEXTURES:
        folder = ROOT / asset
        folder.mkdir(exist_ok=True)
        meta_path = folder / 'files.json'
        meta_bytes = meta_path.read_bytes() if meta_path.exists() else get('https://api.polyhaven.com/files/' + asset)
        meta = json.loads(meta_bytes)
        if not meta_path.exists():
            meta_path.write_bytes(meta_bytes)
        if asset in MODELS:
            mainfile = meta['gltf']['1k']['gltf']
            selected = {asset + '.gltf': mainfile, **mainfile.get('include', {})}
        else:
            selected = {key + '.jpg': meta[key]['1k']['jpg'] for key in ('Diffuse', 'nor_gl')}
        for rel, row in selected.items():
            path = folder / rel
            if not path.resolve().is_relative_to(folder.resolve()) or path.is_symlink():
                raise ValueError('Unsafe asset path')
            total += row['size']
            if total > LIMIT:
                raise ValueError('Selected asset budget exceeds180MB')
            data = path.read_bytes() if path.exists() else get(row['url'])
            if len(data) != row['size'] or hashlib.md5(data).hexdigest() != row['md5']:
                raise ValueError('Asset checksum mismatch: ' + rel)
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            records.append({'asset': asset, 'path': str(path.relative_to(ROOT)), 'bytes': len(data),
                            'sha256': hashlib.sha256(data).hexdigest(), 'url': row['url'],
                            'license': 'CC0-1.0', 'source': 'https://polyhaven.com/a/' + asset})
        print(asset, 'verified', flush=True)
    (ROOT / 'manifest.json').write_text(json.dumps({'credit': 'Assets from Poly Haven',
        'license_source': 'https://polyhaven.com/license', 'files': records, 'bytes': total}, indent=2) + '\n')
    print('Total verified bytes:', total)


if __name__ == '__main__':
    main()
