#!/usr/bin/env python3
"""Import an owner-reviewed public Loop snapshot without deploying it.

The original owner must review disclosure before import. Validation does not
establish publication authorization or detect every secret in free text.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from loop_site import checked_snapshot, fields, identifier, items, validate_snapshot


ROOT = Path(__file__).resolve().parents[1]


def atomic_write(path, raw, replace=False):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        if replace:
            temporary.replace(path)
        else:
            os.link(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def import_snapshot(snapshot_path, snapshot_id, root=ROOT):
    identifier(snapshot_id)
    if snapshot_id.lower() == 'catalog':
        raise ValueError('Snapshot ID is reserved for the public Loop catalog')
    root = root.resolve()
    folder = root / 'reports/loops'
    catalog_path = folder / 'catalog.json'
    destination = folder / (snapshot_id + '.json')
    if (not folder.resolve().is_relative_to(root)
            or catalog_path.is_symlink() or destination.is_symlink()):
        raise ValueError('Public Loop import path escapes its directory or is a symlink')

    if snapshot_path.is_symlink() or not snapshot_path.is_file():
        raise ValueError('Public Loop source must be a regular file, not a symlink')
    if snapshot_path.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Public Loop snapshot exceeds size limit')
    raw = snapshot_path.read_bytes()
    snapshot = validate_snapshot(json.loads(raw))
    digest = hashlib.sha256(raw).hexdigest()
    expected = {'path': destination.relative_to(root).as_posix(), 'sha256': digest}
    catalog = json.loads(catalog_path.read_bytes())
    fields(catalog, ('schema_version', 'snapshots'))
    if type(catalog['schema_version']) is not int or catalog['schema_version'] != 1:
        raise ValueError('Unsupported public Loop catalog')
    seen_runs, seen_paths = set(), set()
    listed = False
    for entry in items(catalog['snapshots']):
        existing = checked_snapshot(root, entry)
        path = (root / entry['path']).resolve()
        if path in seen_paths:
            raise ValueError('Duplicate public Loop snapshot path in catalog')
        seen_paths.add(path)
        for run in existing['runs']:
            if run['id'] in seen_runs:
                raise ValueError('Duplicate public Loop run across snapshots')
            seen_runs.add(run['id'])
        if path == destination.resolve():
            if entry != expected:
                raise ValueError('Conflicting public Loop catalog entry for snapshot ID')
            listed = True

    exists = destination.exists()
    if exists and destination.read_bytes() != raw:
        raise ValueError('Snapshot ID already exists with different bytes')
    if not listed and seen_runs.intersection(run['id'] for run in snapshot['runs']):
        raise ValueError('Duplicate public Loop run across snapshots')

    status = 'NOOP'
    if not listed:
        catalog['snapshots'].append(expected)
        catalog_raw = (json.dumps(catalog, indent=2) + '\n').encode('utf-8')
        if not exists:
            atomic_write(destination, raw)
        atomic_write(catalog_path, catalog_raw, replace=True)
        status = 'RECOVERED' if exists else 'IMPORTED'
    return {'status': status, 'id': snapshot_id, **expected,
            'run_ids': [run['id'] for run in snapshot['runs']]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--id', required=True)
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root (defaults to this repository)')
    args = parser.parse_args(argv)
    try:
        result = import_snapshot(args.snapshot, args.id, args.root)
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({'status': 'REFUSED', 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
