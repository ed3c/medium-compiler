#!/usr/bin/env python3
"""Import an owner-reviewed public Loop snapshot without deploying it.

The original owner must review disclosure before import. Validation does not
establish publication authorization or detect every secret in free text.
"""
import argparse
import fcntl
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


def import_snapshot(snapshot_path, snapshot_id, root=ROOT, supersede=None):
    root = root.resolve()
    folder = root / 'reports/loops'
    if not folder.resolve().is_relative_to(root) or folder.is_symlink():
        raise ValueError('Public Loop import directory escapes its root or is a symlink')
    # The directory identity survives atomic catalog replacement. Locking the
    # catalog inode would let another importer lock its replacement too early.
    descriptor = os.open(folder, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        return _import_snapshot_locked(snapshot_path, snapshot_id, root, supersede)
    finally:
        os.close(descriptor)


def _import_snapshot_locked(snapshot_path, snapshot_id, root, supersede):
    identifier(snapshot_id)
    if snapshot_id.lower() == 'catalog':
        raise ValueError('Snapshot ID is reserved for the public Loop catalog')
    if supersede is not None:
        identifier(supersede)
        if supersede.lower() == 'catalog' or supersede == snapshot_id:
            raise ValueError('Supersession requires distinct old and new snapshot IDs')
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
    listed = None
    replaced = None
    replaced_runs = set()
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
            if {key: entry[key] for key in ('path', 'sha256')} != expected:
                raise ValueError('Conflicting public Loop catalog entry for snapshot ID')
            listed = entry
        if supersede is not None and path == (folder / (supersede + '.json')).resolve():
            replaced = entry
            replaced_runs = {run['id'] for run in existing['runs']}

    exists = destination.exists()
    if exists and destination.read_bytes() != raw:
        raise ValueError('Snapshot ID already exists with different bytes')
    if supersede is not None:
        if listed is not None:
            previous = listed.get('supersedes')
            if (replaced is not None or not isinstance(previous, dict)
                    or previous.get('path') != 'reports/loops/' + supersede + '.json'):
                raise ValueError('Snapshot ID is not this recorded supersession')
        else:
            if replaced is None:
                raise ValueError('Superseded snapshot ID is not selected in the catalog')
            previous = replaced
        old = checked_snapshot(root, previous)
        new_runs = {run['id']: run for run in snapshot['runs']}
        for run in old['runs']:
            successor = new_runs.get(run['id'])
            if successor is None or any(successor[key] != run[key] for key in ('repository', 'mode')):
                raise ValueError('Supersession must preserve every old run ID, repository and mode')
        expected['supersedes'] = previous
    if not listed and (seen_runs - replaced_runs).intersection(run['id'] for run in snapshot['runs']):
        raise ValueError('Duplicate public Loop run across snapshots')

    status = 'NOOP'
    if not listed:
        if replaced is not None:
            catalog['snapshots'][catalog['snapshots'].index(replaced)] = expected
        else:
            catalog['snapshots'].append(expected)
        catalog_raw = (json.dumps(catalog, indent=2) + '\n').encode('utf-8')
        if not exists:
            atomic_write(destination, raw)
        atomic_write(catalog_path, catalog_raw, replace=True)
        status = 'RECOVERED' if exists else 'SUPERSEDED' if replaced is not None else 'IMPORTED'
    elif 'supersedes' in listed:
        expected['supersedes'] = listed['supersedes']
    return {'status': status, 'id': snapshot_id, **expected,
            'run_ids': [run['id'] for run in snapshot['runs']]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--id', required=True)
    parser.add_argument('--supersede', help='Replace this selected catalog entry while retaining its snapshot bytes')
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root (defaults to this repository)')
    args = parser.parse_args(argv)
    try:
        result = import_snapshot(args.snapshot, args.id, args.root, args.supersede)
    except (OSError, TypeError, ValueError) as error:
        print(json.dumps({'status': 'REFUSED', 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
