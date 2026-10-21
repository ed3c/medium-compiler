#!/usr/bin/env python3
"""Bounded read-only local-learning query using real DuckDB CLI Agent Mode.

Reads only an explicitly exported .duckdb file; never accesses browser OPFS.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import subprocess
import sys

FIXED_SQL = """
SET enable_external_access = false;
SET max_execution_time = 2000;
SELECT problem_id, COUNT(*) AS local_attempts,
 COUNT(*) FILTER (WHERE status = 'passed') AS untrusted_browser_passes
FROM learning_attempts
GROUP BY problem_id
ORDER BY problem_id
LIMIT 100;
"""

def build_command(filename, executable='duckdb'):
    p = Path(filename).expanduser()
    if p.is_symlink():
        raise ValueError('REFUSE_SYMLINK_DB')
    resolved = p.resolve(strict=True)
    if not resolved.is_file() or resolved.suffix.lower() != '.duckdb':
        raise ValueError('REQUIRES_EXPORTED_DUCKDB_FILE')
    if not re.fullmatch(r'[a-zA-Z0-9_.+/-]+', executable):
        raise ValueError('INVALID_BINARY')
    return [executable, '-agent', '-readonly', str(resolved), '-c', FIXED_SQL]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database', required=True)
    p.add_argument('--binary', default='duckdb')
    a = p.parse_args()
    try:
        version = subprocess.run([a.binary, '-version'],
             capture_output=True, text=True, timeout=3, check=True)
        m = re.search(r'\bv(\d+)\.(\d+)', version.stdout)
        if not m or int(m.group(1)) < 2:
            raise ValueError('REQUIRES_INSTALLED_DUCKDB_CLI_V2_AGENT_MODE')
        result = subprocess.run(build_command(a.database, a.binary),
            capture_output=True, text=True, timeout=10, check=False)
    except (OSError, ValueError, subprocess.TimeoutExpired,
            subprocess.CalledProcessError) as exc:
        p.exit(2, 'NOT_RUN: ' + str(exc) + '\n')
    if result.returncode:
        p.exit(result.returncode, 'DuckDB agent readback refused: '+result.stderr[:1600]+'\n')
    print(result.stdout, end='')

if __name__ == '__main__':
    main()
