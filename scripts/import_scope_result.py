#!/usr/bin/env python3
"""Recompute a NeoWeaver result at explicit upstream roots before immutable import."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from scope_site import PUBLIC_PATH, checked_result, read_regular


ROOT = Path(__file__).resolve().parents[1]


def compare_result(actual, expected, path='$'):
    if type(actual) is not type(expected):
        raise ValueError('source_result_type_mismatch:' + path)
    if isinstance(expected, dict):
        if actual.keys() != expected.keys():
            raise ValueError('source_result_fields_mismatch:' + path)
        for key in expected:
            compare_result(actual[key], expected[key], path + '.' + key)
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError('source_result_length_mismatch:' + path)
        for index, item in enumerate(expected):
            compare_result(actual[index], item, path + '[' + str(index) + ']')
    elif actual != expected:
        raise ValueError('source_result_value_mismatch:' + path)


def recompute(bundle_raw, factoryweaver_root, neoweaver_root):
    factoryweaver_root = factoryweaver_root.resolve(strict=True)
    neoweaver_root = neoweaver_root.resolve(strict=True)
    for path in (neoweaver_root / 'scripts/import_factory_scope.py',
                 factoryweaver_root / 'scripts/soodles_handoff.py',
                 factoryweaver_root / 'scripts/factoryweaver.py'):
        read_regular(path)
        if not path.resolve().is_relative_to(path.parent.parent):
            raise ValueError('upstream_script_escapes_checkout')
    with tempfile.TemporaryDirectory(prefix='scope-recompute-') as name:
        folder = Path(name)
        bundle = folder / 'bundle.json'
        output = folder / 'selected-scope.json'
        bundle.write_bytes(bundle_raw)
        command = [sys.executable, '-I', '-B',
                   str(neoweaver_root / 'scripts/import_factory_scope.py'), str(bundle),
                   '--factoryweaver-root', str(factoryweaver_root), '--output', str(output)]
        result = subprocess.run(command, cwd=neoweaver_root, capture_output=True,
                                timeout=30, check=False)
        if result.returncode != 0:
            raise ValueError('neoweaver_recompute_refused:exit=' + str(result.returncode))
        return checked_result(read_regular(output))


def import_result(result_path, bundle_path, factoryweaver_root, neoweaver_root, root=ROOT):
    raw = read_regular(result_path)
    value = checked_result(raw)
    bundle_raw = read_regular(bundle_path)
    if value['bundle_sha256'] != hashlib.sha256(bundle_raw).hexdigest():
        raise ValueError('source_bundle_digest_mismatch')
    expected = recompute(bundle_raw, factoryweaver_root, neoweaver_root)
    compare_result(value, expected)

    root = root.resolve(strict=True)
    destination = root / PUBLIC_PATH
    if destination.is_symlink() or not destination.parent.resolve().is_relative_to(root):
        raise ValueError('scope_public_path_escapes_repository_or_is_symlink')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o444)
            try:
                os.link(temporary, destination)
                status = 'IMPORTED'
            except FileExistsError:
                if read_regular(destination) != raw:
                    raise ValueError('scope_output_conflict_requires_original_readback')
                status = 'NOOP'
        finally:
            temporary.unlink(missing_ok=True)
    return {'status': status, 'path': PUBLIC_PATH.as_posix(),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'bundle_sha256': value['bundle_sha256'],
            'proof_ceiling': value['proof_ceiling'],
            'effects': [], 'authorizes_landing': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', required=True, type=Path)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--factoryweaver-root', required=True, type=Path)
    parser.add_argument('--neoweaver-root', required=True, type=Path)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = import_result(args.result, args.bundle, args.factoryweaver_root,
                               args.neoweaver_root, args.root)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'REFUSED', 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
