"""Publish only the Director-authorized finish248 MP4 to private S3 review storage.

No bucket mutation, public ACL, credentials in receipts, project upload or deletion.
The presigned bearer URL is kept in ignored runtime output, not Git.
"""
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_active_backup import bucket_controls, stream_sha256

PROFILE = 'adi-sso'
REGION = 'ca-central-1'
BUCKET = 'movie-factory-archive'
CLIP = ROOT / '.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
OUT = ROOT / '.runtime/art-direction/series01-finish248/phone-review252'


def aws(*args):
    result = subprocess.run(
        ['/usr/local/bin/aws', *args, '--profile', PROFILE, '--region', REGION],
        capture_output=True, text=True, check=True)
    return result.stdout.strip()


def main():
    OUT.mkdir(exist_ok=False)
    digest = hashlib.sha256(CLIP.read_bytes()).hexdigest()
    manifest = json.loads((CLIP.parent / 'manifest.json').read_text())
    source = next(r for r in manifest['deliveries'] if r['file'] == CLIP.name)
    if source['sha256'] != digest or not source['full_decode']:
        raise ValueError('Clip differs from verified delivery')
    if manifest['duration'] != 20 or len(manifest['frames']) != 480:
        raise ValueError('Wrong requested cut')
    if aws('sts', 'get-caller-identity', '--query', 'Account', '--output', 'text') != '281482331395':
        raise ValueError('Unexpected AWS account')
    controls = bucket_controls(PROFILE, REGION, BUCKET)
    key = f'movie-factory/reviews/pashtun/finish248/{digest}/pashtun-20s.mp4'
    uri = f's3://{BUCKET}/{key}'
    # Unique content-addressed path; upload no other file or metadata payload.
    aws('s3', 'cp', str(CLIP), uri, '--only-show-errors', '--sse', 'AES256',
        '--content-type', 'video/mp4', '--content-disposition', 'inline; filename="The-Martials-Pashtun-20s.mp4"',
        '--cache-control', 'private, max-age=0', '--metadata', f'sha256={digest}')
    head = json.loads(aws('s3api', 'head-object', '--bucket', BUCKET, '--key', key, '--output', 'json'))
    size, restored_hash = stream_sha256(uri, PROFILE, REGION)
    if size != CLIP.stat().st_size or restored_hash != digest or head['ContentType'] != 'video/mp4':
        raise ValueError('Uploaded clip failed streamed integrity verification')
    url = aws('s3', 'presign', uri, '--expires-in', '86400')
    # Verify signed access and range delivery without retaining credential-bearing URL in a report.
    req = urllib.request.Request(url, headers={'Range': 'bytes=0-1023'})
    with urllib.request.urlopen(req, timeout=30) as response:
        status = response.status
        sample = response.read(1024)
        content_range = response.headers.get('Content-Range')
    with CLIP.open('rb') as source_file:
        if status != 206 or sample != source_file.read(1024):
            raise ValueError('Signed ranged playback access failed')
    link = OUT / 'private-link.txt'
    fd = os.open(link, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(url + '\n')
    receipt = dict(
        authorized_exchange=252, observed_utc=datetime.now(timezone.utc).isoformat(),
        bucket=BUCKET, key=key, version_id=head.get('VersionId'), bytes=size,
        local_sha256=digest, streamed_remote_sha256=restored_hash,
        private_bucket_controls=controls, http_range_status=status, content_range=content_range,
        requested_link_lifetime_seconds=86400,
        expiry_caveat='Underlying temporary AWS credentials may expire earlier; link grants access to this clip only.',
        uploaded_files=1, public_acl_change=False, project_backup=False,
        director_phone_review='PENDING', link_file=str(link.relative_to(ROOT)))
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
