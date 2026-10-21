# Local-first Learning using DuckDB and DuckDB CLI Agent Mode

Decisions: VIS-12 A, VIS-13 A, VIS-14 A, with DuckDB substituted for
IndexedDB-primary storage. Preserve VIS-06 B, VIS-07 B, VIS-08 A,
VIS-09 A, VIS-10 A, VIS-11 A, VIZ-01–04 and ViewEnv Q1–Q36.

The DuckDB 2.0 CLI Agent Mode discussed on 2026-10-09 formats SQL output
for AI coding agents. It does not persist browser data or grade Python.
DuckDB-Wasm + OPFS owns local learning records; the native DuckDB CLI
Agent Mode is only an optional read-only consumer of a manually exported
DuckDB database. The browser cannot directly invoke the CLI and the CLI
cannot automatically read browser OPFS. Do not confuse these three facts.
Source: https://duckdb.org/2026/10/09/agent-mode

Original problem/content owners supply the tasks. Local study attempts
and grades are browser-untrusted and have no native Agent/evals authority.
No user account, remote sync, trusted leaderboard or payment endpoint.
Keep Python execution in a separate, network-restricted sandbox with
bounded packages, CPU and output. A Web Worker by itself is not security
isolation, so report that gate as NOT_ACCEPTED until tested. A submitted
Python solution must pass real runtime tests before recording a local
pass; never fabricate PASS from a rendered animation.

DuckDB-Wasm requires verified OPFS persistence with CHECKPOINT,
same-origin storage, one writer, reload and cross-browser testing.
OPFS data can be evicted or manually deleted: offer explicit export and
import. The first slice must not silently fall back to volatile memory
and claim saved progress. In native CLI, require DuckDB v2, force
agent mode, use read-only database access and fixed bounded SQL.

Acceptance layers: typed source/attempt contracts, real DuckDB-Wasm
OPFS write/reopen and recover, actual Python worker and network-denial
test, independent Browser tests, original Graph and ALG Four regression,
and separate cloud Provider readback. None of these prove a native Agent
task completed. PR #72 remains a Draft and Production untouched.
