#!/usr/bin/env python3
"""Deterministic writing-state owner for staged Medium technical articles.

This tool intentionally does not judge technical truth. It owns only the mechanically
checkable writing contract: stage order, declared coverage, protected term/literal/code
integrity, deterministic assembly, and validation bound to final bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

STAGE_ELEMENTS: dict[int, tuple[str, ...]] = {
    0: ("toc", "decision_map", "runtime_map"),
    1: ("problem", "governing_property", "representation"),
    2: ("runtime_witness", "internals"),
    3: ("alternative", "decision_boundary", "complexity"),
    4: ("implementation", "correctness", "edge_cases"),
    5: ("interview", "master_map"),
    6: ("copyedit",),
}

STAGE_NAMES = {
    0: "toc-and-maps",
    1: "problem-property-representation",
    2: "runtime-and-internals",
    3: "alternative-and-cost",
    4: "implementation-correctness-edge-cases",
    5: "interview-and-master-map",
    6: "meaning-preserving-copyedit",
    7: "canonical-assembly",
}

FENCE = re.compile(r"(?ms)^\`\`\`[^\n]*\n.*?^\`\`\`\s*$")
MACHINE_MARKERS = (
    "<!-- MEDIUM_COMPILER",
    "<!-- RUN_STATE",
    "<!-- CLAIM_COVERAGE",
    "<!-- TERM_LEDGER",
)
STYLE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("staged-opener", re.compile(r"(?:本文將|接下來讓我們|以下將)")),
    ("curriculum-scaffold", re.compile(r"(?:這一階段的產物|前進條件|預計產物)")),
    ("generic-importance", re.compile(r"(?:值得注意的是|至關重要的是)")),
    ("stock-summary", re.compile(r"(?:總而言之|綜上所述)")),
)


class CompilerError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CompilerError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CompilerError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CompilerError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompilerError(f"{field} must be a non-empty string")
    return value


def _require_unique_ids(items: list[dict[str, Any]], kind: str) -> None:
    ids = [_require_string(item.get("id"), f"{kind}.id") for item in items]
    if len(ids) != len(set(ids)):
        raise CompilerError(f"duplicate {kind} id")


def validate_spec(spec: dict[str, Any]) -> None:
    _require_string(spec.get("topic"), "topic")

    claims = spec.get("claims", [])
    terms = spec.get("terms", [])
    if not isinstance(claims, list) or not all(isinstance(x, dict) for x in claims):
        raise CompilerError("claims must be a list of objects")
    if not isinstance(terms, list) or not all(isinstance(x, dict) for x in terms):
        raise CompilerError("terms must be a list of objects")

    _require_unique_ids(claims, "claim")
    _require_unique_ids(terms, "term")

    for claim in claims:
        stage = claim.get("stage")
        if not isinstance(stage, int) or stage not in range(1, 6):
            raise CompilerError(f"claim {claim['id']} stage must be 1..5")
        _require_string(claim.get("description"), f"claim {claim['id']}.description")
        literals = claim.get("protected_literals", [])
        if not isinstance(literals, list) or not all(
            isinstance(item, str) and item for item in literals
        ):
            raise CompilerError(
                f"claim {claim['id']}.protected_literals must be non-empty strings"
            )

    for term in terms:
        _require_string(term.get("canonical"), f"term {term['id']}.canonical")
        stage = term.get("first_stage")
        if not isinstance(stage, int) or stage not in range(1, 6):
            raise CompilerError(f"term {term['id']} first_stage must be 1..5")
        variants = term.get("forbidden_variants", [])
        if not isinstance(variants, list) or not all(
            isinstance(item, str) and item for item in variants
        ):
            raise CompilerError(
                f"term {term['id']}.forbidden_variants must be non-empty strings"
            )


def _run_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "spec": run_dir / "spec.json",
        "state": run_dir / "state.json",
        "parts": run_dir / "parts",
        "semantic": run_dir / "semantic-draft.md",
        "canonical": run_dir / "medium-canonical.md",
        "receipt": run_dir / "validation-receipt.json",
    }


def init_run(spec_path: Path, run_dir: Path) -> dict[str, Any]:
    if run_dir.exists() and any(run_dir.iterdir()):
        raise CompilerError(f"run directory is not empty: {run_dir}")
    spec = _read_json(spec_path)
    validate_spec(spec)

    run_dir.mkdir(parents=True, exist_ok=True)
    paths = _run_paths(run_dir)
    paths["parts"].mkdir(parents=True, exist_ok=True)
    shutil.copyfile(spec_path, paths["spec"])

    state = {
        "schema_version": "medium-compiler-state@1",
        "status": "CONTINUE",
        "next_stage": 0,
        "submitted_stages": [],
        "covered_claims": [],
        "defined_terms": [],
    }
    _write_json(paths["state"], state)
    return state


def _load_run(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    paths = _run_paths(run_dir)
    spec = _read_json(paths["spec"])
    validate_spec(spec)
    state = _read_json(paths["state"])
    return spec, state, paths


def _claim_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in spec.get("claims", [])}


def _term_map(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in spec.get("terms", [])}


def _due_claims(spec: dict[str, Any], stage: int) -> set[str]:
    return {item["id"] for item in spec.get("claims", []) if item["stage"] == stage}


def _due_terms(spec: dict[str, Any], stage: int) -> set[str]:
    return {item["id"] for item in spec.get("terms", []) if item["first_stage"] == stage}


def _protected_literals(spec: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for claim in spec.get("claims", []):
        result.extend(claim.get("protected_literals", []))
    return result


def _check_forbidden_variants(spec: dict[str, Any], text: str) -> None:
    failures: list[str] = []
    for term in spec.get("terms", []):
        for variant in term.get("forbidden_variants", []):
            if variant in text:
                failures.append(f"{term['id']}: forbidden variant {variant!r}")
    if failures:
        raise CompilerError("technical term drift: " + "; ".join(failures))


def _validate_coverage(
    spec: dict[str, Any], stage: int, coverage: dict[str, Any], text: str
) -> tuple[set[str], set[str]]:
    expected_elements = set(STAGE_ELEMENTS[stage])
    elements = coverage.get("elements", [])
    claims = coverage.get("claims", [])
    terms = coverage.get("terms", [])
    if not all(isinstance(x, list) for x in (elements, claims, terms)):
        raise CompilerError("coverage elements/claims/terms must be lists")
    if not all(isinstance(x, str) for x in elements + claims + terms):
        raise CompilerError("coverage values must be strings")

    if set(elements) != expected_elements:
        raise CompilerError(
            f"stage {stage} elements must be {sorted(expected_elements)}, got {sorted(set(elements))}"
        )

    all_claims = _claim_map(spec)
    all_terms = _term_map(spec)
    unknown_claims = set(claims) - set(all_claims)
    unknown_terms = set(terms) - set(all_terms)
    if unknown_claims:
        raise CompilerError(f"unknown claim ids: {sorted(unknown_claims)}")
    if unknown_terms:
        raise CompilerError(f"unknown term ids: {sorted(unknown_terms)}")

    due_claims = _due_claims(spec, stage)
    due_terms = _due_terms(spec, stage)
    if set(claims) != due_claims:
        raise CompilerError(
            f"stage {stage} claim coverage must be {sorted(due_claims)}, got {sorted(set(claims))}"
        )
    if set(terms) != due_terms:
        raise CompilerError(
            f"stage {stage} term coverage must be {sorted(due_terms)}, got {sorted(set(terms))}"
        )

    for claim_id in due_claims:
        for literal in all_claims[claim_id].get("protected_literals", []):
            if literal not in text:
                raise CompilerError(
                    f"stage {stage} missing protected literal for {claim_id}: {literal!r}"
                )

    for term_id in due_terms:
        canonical = all_terms[term_id]["canonical"]
        if canonical not in text:
            raise CompilerError(
                f"stage {stage} missing canonical term for {term_id}: {canonical!r}"
            )

    return due_claims, due_terms


def _extract_fences(text: str) -> list[str]:
    return [match.group(0) for match in FENCE.finditer(text)]


def _part_path(parts: Path, stage: int) -> Path:
    return parts / f"stage-{stage:02d}.md"


def _coverage_path(parts: Path, stage: int) -> Path:
    return parts / f"stage-{stage:02d}.coverage.json"


def _build_semantic_draft(paths: dict[str, Path]) -> None:
    pieces = [
        _part_path(paths["parts"], stage).read_text(encoding="utf-8").strip()
        for stage in range(1, 6)
    ]
    paths["semantic"].write_text("\n\n".join(pieces).rstrip() + "\n", encoding="utf-8")


def submit_stage(
    run_dir: Path, stage: int, input_path: Path, coverage_path: Path
) -> dict[str, Any]:
    spec, state, paths = _load_run(run_dir)
    if state.get("status") != "CONTINUE":
        raise CompilerError(f"run is not accepting stages: {state.get('status')}")
    expected = state.get("next_stage")
    if stage not in STAGE_ELEMENTS:
        raise CompilerError("submit accepts only stages 0..6")
    if stage != expected:
        raise CompilerError(f"out-of-order stage: expected {expected}, got {stage}")

    try:
        text = input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise CompilerError(f"missing stage input: {input_path}") from exc
    if not text.strip():
        raise CompilerError("stage input is empty")
    coverage = _read_json(coverage_path)

    _check_forbidden_variants(spec, text)

    if stage <= 5:
        due_claims, due_terms = _validate_coverage(spec, stage, coverage, text)
    else:
        expected_elements = set(STAGE_ELEMENTS[6])
        if set(coverage.get("elements", [])) != expected_elements:
            raise CompilerError(
                f"stage 6 elements must be {sorted(expected_elements)}"
            )
        if coverage.get("claims", []) or coverage.get("terms", []):
            raise CompilerError("stage 6 must not re-declare claim or term coverage")

        if not paths["semantic"].is_file():
            raise CompilerError("semantic draft is missing before copyedit")
        before = paths["semantic"].read_text(encoding="utf-8")
        if _extract_fences(before) != _extract_fences(text):
            raise CompilerError("copyedit changed fenced code/text blocks")
        for literal in _protected_literals(spec):
            if literal not in text:
                raise CompilerError(
                    f"copyedit dropped protected literal: {literal!r}"
                )
        for term in spec.get("terms", []):
            canonical = term["canonical"]
            if canonical not in text:
                raise CompilerError(
                    f"copyedit dropped canonical technical term: {canonical!r}"
                )
        due_claims, due_terms = set(), set()

    part_dest = _part_path(paths["parts"], stage)
    coverage_dest = _coverage_path(paths["parts"], stage)
    part_dest.write_text(text.rstrip() + "\n", encoding="utf-8")
    _write_json(coverage_dest, coverage)

    state["submitted_stages"] = [*state.get("submitted_stages", []), stage]
    state["covered_claims"] = sorted(
        set(state.get("covered_claims", [])) | due_claims
    )
    state["defined_terms"] = sorted(
        set(state.get("defined_terms", [])) | due_terms
    )
    state["next_stage"] = stage + 1

    if stage == 5:
        expected_claims = set(_claim_map(spec))
        expected_terms = set(_term_map(spec))
        if set(state["covered_claims"]) != expected_claims:
            raise CompilerError("cannot freeze semantics: not all claims are covered")
        if set(state["defined_terms"]) != expected_terms:
            raise CompilerError("cannot freeze semantics: not all terms are defined")
        _build_semantic_draft(paths)

    _write_json(paths["state"], state)
    return state


def next_action(run_dir: Path) -> dict[str, Any]:
    spec, state, paths = _load_run(run_dir)
    next_stage = state.get("next_stage")
    if state.get("status") == "ASSEMBLED":
        return {
            "status": "ASSEMBLED",
            "next": "verify",
            "canonical": str(paths["canonical"]),
        }
    if not isinstance(next_stage, int):
        raise CompilerError("state has no valid next_stage")
    if next_stage == 7:
        return {
            "status": "CONTINUE",
            "next_stage": 7,
            "name": STAGE_NAMES[7],
            "required": ["assemble admitted Stage 6 bytes; author no new prose"],
        }
    return {
        "status": "CONTINUE",
        "next_stage": next_stage,
        "name": STAGE_NAMES[next_stage],
        "required_elements": list(STAGE_ELEMENTS[next_stage]),
        "claim_ids": sorted(_due_claims(spec, next_stage)),
        "term_ids": sorted(_due_terms(spec, next_stage)),
    }


def assemble(run_dir: Path) -> dict[str, Any]:
    spec, state, paths = _load_run(run_dir)
    if state.get("next_stage") != 7 or state.get("status") != "CONTINUE":
        raise CompilerError("canonical assembly is legal only after admitted Stage 6")
    stage6 = _part_path(paths["parts"], 6)
    if not stage6.is_file():
        raise CompilerError("Stage 6 article is missing")
    text = stage6.read_text(encoding="utf-8")
    markers = [marker for marker in MACHINE_MARKERS if marker in text]
    if markers:
        raise CompilerError(f"machine sidecar leaked into article: {markers}")
    _check_forbidden_variants(spec, text)

    # Stage 7 is intentionally incapable of adding prose.
    paths["canonical"].write_bytes(stage6.read_bytes())
    state["status"] = "ASSEMBLED"
    state["next_stage"] = None
    state["canonical_sha256"] = _sha256_path(paths["canonical"])
    _write_json(paths["state"], state)
    return {
        "status": "ASSEMBLED",
        "article_sha256": state["canonical_sha256"],
        "path": str(paths["canonical"]),
    }


def build_receipt(run_dir: Path) -> dict[str, Any]:
    spec, state, paths = _load_run(run_dir)
    if state.get("status") != "ASSEMBLED" or not paths["canonical"].is_file():
        raise CompilerError("verify requires an assembled canonical article")
    stage6 = _part_path(paths["parts"], 6)
    if paths["canonical"].read_bytes() != stage6.read_bytes():
        raise CompilerError("canonical article no longer matches admitted Stage 6 bytes")

    receipt = {
        "schema_version": "medium-compiler-validation@1",
        "topic": spec["topic"],
        "article_sha256": _sha256_path(paths["canonical"]),
        "spec_sha256": _sha256_path(paths["spec"]),
        "stage_sha256": {
            str(stage): _sha256_path(_part_path(paths["parts"], stage))
            for stage in range(0, 7)
        },
        "checks": {
            "stage_order": True,
            "declared_claim_coverage": True,
            "technical_term_identity": True,
            "protected_literals": True,
            "copyedit_fenced_blocks": True,
            "deterministic_assembly": True,
        },
        "semantic_correctness": "NOT_ASSESSED",
        "human_preference": "NOT_ASSESSED",
    }
    _write_json(paths["receipt"], receipt)
    return receipt


def check_receipt(run_dir: Path, receipt_path: Path | None = None) -> dict[str, Any]:
    spec, state, paths = _load_run(run_dir)
    receipt_file = receipt_path or paths["receipt"]
    receipt = _read_json(receipt_file)
    failures: list[str] = []

    if not paths["canonical"].is_file():
        failures.append("canonical article missing")
    elif receipt.get("article_sha256") != _sha256_path(paths["canonical"]):
        failures.append("canonical article bytes changed")

    if receipt.get("spec_sha256") != _sha256_path(paths["spec"]):
        failures.append("spec bytes changed")

    stage_digests = receipt.get("stage_sha256")
    if not isinstance(stage_digests, dict):
        failures.append("stage_sha256 missing")
    else:
        for stage in range(0, 7):
            path = _part_path(paths["parts"], stage)
            expected = stage_digests.get(str(stage))
            if not path.is_file() or expected != _sha256_path(path):
                failures.append(f"stage {stage} bytes changed")

    if failures:
        raise CompilerError("stale/invalid validation receipt: " + "; ".join(failures))
    return {
        "status": "VALID",
        "article_sha256": receipt["article_sha256"],
        "semantic_correctness": receipt.get("semantic_correctness", "NOT_ASSESSED"),
    }


def style_lint(input_path: Path) -> dict[str, Any]:
    text = input_path.read_text(encoding="utf-8")
    findings: list[dict[str, Any]] = []
    for name, pattern in STYLE_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            findings.append(
                {
                    "pattern": name,
                    "count": len(matches),
                    "examples": [match.group(0) for match in matches[:3]],
                }
            )
    return {
        "schema_version": "medium-style-lint@1",
        "finding_count": sum(item["count"] for item in findings),
        "findings": findings,
        "blocking": False,
    }


def _print(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--run-dir", type=Path, required=True)

    p = sub.add_parser("next")
    p.add_argument("--run-dir", type=Path, required=True)

    p = sub.add_parser("submit")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--stage", type=int, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--coverage", type=Path, required=True)

    p = sub.add_parser("assemble")
    p.add_argument("--run-dir", type=Path, required=True)

    p = sub.add_parser("verify")
    p.add_argument("--run-dir", type=Path, required=True)

    p = sub.add_parser("check-receipt")
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--receipt", type=Path)

    p = sub.add_parser("style-lint")
    p.add_argument("--input", type=Path, required=True)

    args = parser.parse_args()
    try:
        if args.command == "init":
            _print(init_run(args.spec, args.run_dir))
        elif args.command == "next":
            _print(next_action(args.run_dir))
        elif args.command == "submit":
            _print(submit_stage(args.run_dir, args.stage, args.input, args.coverage))
        elif args.command == "assemble":
            _print(assemble(args.run_dir))
        elif args.command == "verify":
            _print(build_receipt(args.run_dir))
        elif args.command == "check-receipt":
            _print(check_receipt(args.run_dir, args.receipt))
        elif args.command == "style-lint":
            _print(style_lint(args.input))
        return 0
    except CompilerError as exc:
        print(f"medium-compiler refused: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
