#!/usr/bin/env python3
"""Restore only the recorded small camera assets, never into this public repository."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

SCRIPTS = {'ps4_stream.py', 'ps4_depth.py', 'ps4_depth_test.py',
           'ps4_depth_stream.py', 'ps4_calib_capture.py', 'ps4_calibrate.py'}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-root', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--dest', required=True, type=Path)
    parser.add_argument('--check-only', action='store_true', help='Verify selection/hashes without copying')
    args = parser.parse_args()
    private = args.private_root.resolve()
    dest = args.dest.resolve()
    repo = Path(__file__).resolve().parents[1]
    if dest == repo or repo in dest.parents or dest.exists():
        parser.error('Destination must be new and outside this repository')
    if dest == private or private in dest.parents:
        parser.error('Destination must be separate from the private originals')
    selected = {}
    for record in json.loads(args.manifest.read_text()):
        original = Path(record['path'])
        parts = original.parts
        relative = None
        if len(parts) == 4 and parts[1] == 'home' and parts[-1] in SCRIPTS:
            relative = Path(parts[-1])
        elif original.name in {'stereo_calibration.npz', 'rectified_preview.jpg'} and original.parent.name == 'ps4_calib':
            relative = Path('ps4_calib') / original.name
        elif len(parts) >= 3 and parts[-3:-1] == ('ps4_calib', 'pairs') and re.fullmatch(r'cam[AB]_[0-9]+\.png', original.name):
            relative = Path('ps4_calib/pairs') / original.name
        if relative is None:
            continue
        if relative in selected:
            parser.error('Duplicate camera asset in manifest: ' + str(relative))
        source = (private / record['saved_as']).resolve()
        if private not in source.parents or not source.is_file():
            parser.error('Missing asset or path escaping private root: ' + str(relative))
        if source.stat().st_size != record['bytes'] or digest(source) != record['sha256']:
            parser.error('Asset hash/size mismatch: ' + str(relative))
        selected[relative] = (source, record)
    required = {Path(name) for name in SCRIPTS} | {Path('ps4_calib/stereo_calibration.npz')}
    if not required.issubset(selected):
        parser.error('Required scripts or calibration NPZ are missing')
    a = {x.name[5:] for x in selected if x.parent == Path('ps4_calib/pairs') and x.name.startswith('camA_')}
    b = {x.name[5:] for x in selected if x.parent == Path('ps4_calib/pairs') and x.name.startswith('camB_')}
    if a != b or len(a) != 25:
        parser.error('Expected 25 matching stereo pairs')
    if args.check_only:
        print('Verified {} assets and 25 matching pairs; no files copied.'.format(len(selected)))
        return
    dest.mkdir(parents=True, mode=0o700, exist_ok=False)
    report = []
    for relative, (source, record) in sorted(selected.items()):
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        shutil.copyfile(str(source), str(target))
        if digest(target) != record['sha256']:
            raise RuntimeError('Copy verification failed: ' + str(relative))
        report.append({'path': str(relative), 'sha256': record['sha256'], 'bytes': record['bytes']})
    (dest / 'restored-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('Restored {} original assets into a new private work directory.'.format(len(report)))
    print('No patches applied; no camera, firmware, or calibration code executed.')


if __name__ == '__main__':
    main()
