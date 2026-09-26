#!/usr/bin/env python3
"""Append-only knowledge expansion before the existing Medium assembly CLI.

The immutable boot and source snapshots plus ordered patch files are the state.
No model calls, publication, or semantic-truth oracle. Single cooperative writer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import medium_compiler as mc


class Refusal(ValueError):
    pass


class LearningPending(Refusal):
    def __init__(self, projection: dict):
        self.projection = projection
        super().__init__("learning handoff prerequisites are incomplete")


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def read_json(path: Path) -> dict:
    value = json.loads(read_file(path))
    if not isinstance(value, dict):
        raise Refusal(f"expected an object: {path.name}")
    return value


def read_file(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise Refusal(f"missing or symlinked input: {path}")
    return path.read_bytes()


def string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Refusal(f"{name} must be a nonempty string")
    return value


def plain_article(data: bytes) -> str:
    text = data.decode("utf-8")
    if not text.strip() or text != text.rstrip() + "\n":
        raise Refusal("article must be nonempty UTF-8 with one terminal newline")
    blocks = mc._extract_fences(text)
    prose = text
    for block in blocks:
        prose = prose.replace(block, "", 1)
    if re.search(r"(?mi)^\s*\|.*\|\s*$|<table\b", prose):
        raise Refusal("Medium prose must not contain a table")
    if any(marker in text for marker in mc.MACHINE_MARKERS):
        raise Refusal("machine sidecar in reader prose")
    return text


def learning_gate(plan: dict, sources: dict[str, bytes]) -> dict | None:
    """Read an externally supplied learning handoff; never grade or write progress.

    Digests/anchors bind a caller-selected snapshot, not the identity or honesty of its
    author. The learning owner must supply ACCEPTED; the writer must not manufacture it.
    """
    purpose = plan.get("purpose", "source-explanation")
    if purpose not in {"source-explanation", "learning-episode"}:
        raise Refusal("unknown writing purpose")
    if purpose == "source-explanation":
        if "learning" in plan:
            raise Refusal("learning metadata requires purpose=learning-episode")
        return None
    target = plan.get("learning")
    if target is None:
        return {"status": "BLOCKED", "next": {"owner": "learning-owner",
                "operation": "supply-learning-prerequisite", "missing_input": "learning_handoff"},
                "missing": [{"input": "learning_handoff", "owner": "learning-owner"}],
                "article_mutation_allowed": False, "progress_write": "NEVER_BY_MEDIUM_COMPILER",
                "human_learning_outcome": "NOT_MEASURED"}
    if not isinstance(target, dict) or set(target) != {"episode_id", "lesson_ref", "handoff_source"}:
        raise Refusal("learning needs episode_id, lesson_ref and handoff_source")
    for key, value in target.items():
        string(value, f"learning.{key}")
    if target["handoff_source"] not in sources:
        raise Refusal("missing learning handoff source")
    record = json.loads(sources[target["handoff_source"]])
    required = {"schema_version", "episode_id", "lesson_ref", "case", "status",
                "experiment_decision", "promotion_decision", "product_need",
                "evidence_refs", "human_checkpoint", "learning_record"}
    if not isinstance(record, dict) or set(record) != required:
        raise Refusal("invalid learning handoff fields")
    if record["schema_version"] != "medium-learning-handoff@2":
        raise Refusal("unsupported learning handoff version")
    if any(record[k] != target[k] for k in ("episode_id", "lesson_ref")):
        raise Refusal("learning episode or lesson mismatch")
    if plan.get("case") is None or record["case"] != plan["case"]:
        raise Refusal("learning handoff case revision mismatch")
    if record["status"] not in {"PENDING", "ACCEPTED"}:
        raise Refusal("learning handoff status must be PENDING or ACCEPTED")
    if record["experiment_decision"] not in {"PENDING", "EXPERIMENT", "NO_CHANGE"}:
        raise Refusal("unknown experiment decision")
    if record["promotion_decision"] not in {"NOT_EVALUATED", "PENDING", "PROMOTE", "DO_NOT_PROMOTE"}:
        raise Refusal("unknown promotion decision")
    if record["product_need"] not in {"UNKNOWN", "PRESENT", "ABSENT"}:
        raise Refusal("unknown product need")
    if record["experiment_decision"] == "NO_CHANGE" and record["promotion_decision"] != "NOT_EVALUATED":
        raise Refusal("NO_CHANGE cannot carry a product-promotion decision")
    if record["promotion_decision"] in {"PENDING", "PROMOTE", "DO_NOT_PROMOTE"} and record["experiment_decision"] != "EXPERIMENT":
        raise Refusal("product promotion is evaluated only after an experiment")
    if record["promotion_decision"] == "PROMOTE" and record["product_need"] != "PRESENT":
        raise Refusal("PROMOTE requires a declared real product need")
    evidence = record["evidence_refs"]
    if not isinstance(evidence, list):
        raise Refusal("learning evidence_refs must be a list")
    def check_ref(ref: dict) -> None:
        if not isinstance(ref, dict) or set(ref) != {"source_id", "anchor"}:
            raise Refusal("handoff reference needs source_id and anchor")
        sid = string(ref["source_id"], "handoff source_id")
        if sid == target["handoff_source"] or sid not in sources:
            raise Refusal("handoff reference must name a separate pinned source")
        if string(ref["anchor"], "handoff anchor") not in sources[sid].decode("utf-8"):
            raise Refusal("handoff evidence anchor absent")
    for ref in evidence:
        check_ref(ref)
    for key in ("human_checkpoint", "learning_record"):
        if record[key] is not None:
            check_ref(record[key])
    missing = []
    if record["experiment_decision"] == "PENDING":
        missing.append({"input": "experiment_decision", "owner": "experiment-owner"})
    if not evidence:
        missing.append({"input": "evidence_refs", "owner": "evidence-owner"})
    if record["human_checkpoint"] is None:
        missing.append({"input": "human_checkpoint", "owner": "learner"})
    if record["status"] != "ACCEPTED" or record["learning_record"] is None:
        missing.append({"input": "accepted_learning_record", "owner": "learning-owner"})
    return {
        "status": "BLOCKED" if missing else "READY",
        "next": {"owner": missing[0]["owner"], "operation": "supply-learning-prerequisite",
                 "missing_input": missing[0]["input"]} if missing else
                {"owner": "medium-compiler", "operation": "boot"},
        "episode_id": target["episode_id"], "lesson_ref": target["lesson_ref"],
        "handoff_sha256": digest(sources[target["handoff_source"]]),
        "experiment_decision": record["experiment_decision"],
        "promotion_decision": record["promotion_decision"],
        "product_need": record["product_need"],
        "promotion_prerequisites_declared": bool(
            record["promotion_decision"] == "PROMOTE"
            and record["experiment_decision"] == "EXPERIMENT"
            and record["product_need"] == "PRESENT"
            and evidence
        ),
        "authorizes_product_write": False,
        "missing": missing,
        "article_mutation_allowed": not missing,
        "progress_write": "NEVER_BY_MEDIUM_COMPILER",
        "human_learning_outcome": "NOT_MEASURED",
        "trust_boundary": "caller-selected owner declaration; hashes do not authenticate humans or authorize product writes",
    }


def validate_plan(plan: dict, boot_text: str, sources: dict[str, bytes]) -> None:
    string(plan.get("topic"), "topic")
    case = plan.get("case")
    if case is not None:
        if not isinstance(case, dict) or set(case) != {"id", "repo", "revision"}:
            raise Refusal("case needs stable id, repo and revision")
        string(case["id"], "case.id")
        string(case["repo"], "case.repo")
        if not re.fullmatch(r"[0-9a-f]{40}", string(case["revision"], "case.revision")):
            raise Refusal("case revision must be a full commit SHA")
    units = plan.get("units")
    if not isinstance(units, list) or not units:
        raise Refusal("boot requires explicit pending knowledge units")
    ids = []
    for unit in units:
        if not isinstance(unit, dict):
            raise Refusal("unit must be an object")
        uid = string(unit.get("id"), "unit.id")
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", uid):
            raise Refusal("unit IDs must be stable slugs")
        ids.append(uid)
        string(unit.get("question"), "unit.question")
        anchor = string(unit.get("insert_before"), "unit.insert_before")
        if not anchor.startswith("## ") or "\n" in anchor or boot_text.count(anchor) != 1:
            raise Refusal("destination must be one exact existing H2 heading")
        sid = unit.get("source_id")
        quote = string(unit.get("source_anchor"), "unit.source_anchor")
        if sid not in sources or quote not in sources[sid].decode("utf-8"):
            raise Refusal("source anchor missing from the pinned source")
        terms = unit.get("terms", [])
        if not isinstance(terms, list) or any(not isinstance(t, str) or not t for t in terms):
            raise Refusal("unit terms must be nonempty strings")
        if case is not None:
            string(unit.get("learning_step"), "unit.learning_step")
            string(unit.get("decision_prompt"), "unit.decision_prompt")
            refs = unit.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                raise Refusal("unit needs code/test/eval evidence references")
            for ref in refs:
                if not isinstance(ref, dict) or set(ref) != {"source_id", "anchor", "role"}:
                    raise Refusal("evidence reference needs source_id, anchor and role")
                if ref["role"] not in {"code", "test", "test_result", "eval", "historical_eval"}:
                    raise Refusal("unknown evidence role")
                if ref["source_id"] not in sources or string(ref["anchor"], "evidence anchor") not in sources[ref["source_id"]].decode("utf-8"):
                    raise Refusal("evidence anchor missing from pinned source")
            case_sources = {unit["source_id"], *(ref["source_id"] for ref in refs)}
            provenance = {entry["id"]: entry["provenance"] for entry in plan["sources"]}
            if any(f'{case["repo"]}@{case["revision"]}:' not in provenance[sid]
                   for sid in case_sources):
                raise Refusal("product source provenance must name the case revision")
    if len(ids) != len(set(ids)):
        raise Refusal("duplicate knowledge unit")


def prepare_inputs(article: Path, plan_path: Path) -> tuple[bytes, dict, dict[str, bytes]]:
    before = read_file(article)
    text = plain_article(before)
    plan = read_json(plan_path)
    source_entries = plan.get("sources")
    if not isinstance(source_entries, list) or not source_entries:
        raise Refusal("plan requires pinned sources")
    sources = {}
    for entry in source_entries:
        sid = string(entry.get("id"), "source.id")
        if not re.fullmatch(r"[a-z0-9-]+", sid) or sid in sources:
            raise Refusal("invalid or duplicate source ID")
        rel = Path(string(entry.get("path"), "source.path"))
        if rel.is_absolute() or ".." in rel.parts:
            raise Refusal("source path must stay beside the plan")
        path = plan_path.parent / rel
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise Refusal("symlinked source path")
        data = read_file(path)
        if digest(data) != entry.get("sha256"):
            raise Refusal("source digest mismatch")
        string(entry.get("provenance"), "source.provenance")
        sources[sid] = data
    validate_plan(plan, text, sources)
    return before, plan, sources


def preflight(article: Path, plan_path: Path) -> dict:
    before, plan, sources = prepare_inputs(article, plan_path)
    gate = learning_gate(plan, sources)
    return {"article_sha256": digest(before), "plan_sha256": digest(encoded(plan)),
            **(gate or {"status": "READY", "next": {"owner": "medium-compiler", "operation": "boot"},
                        "purpose": "source-explanation", "human_learning_outcome": "NOT_MEASURED"})}


def boot(article: Path, plan_path: Path, run: Path) -> dict:
    if run.exists() or run.is_symlink():
        raise Refusal("boot output must be a new directory; use next for an existing run")
    before, plan, sources = prepare_inputs(article, plan_path)
    gate = learning_gate(plan, sources)
    if gate and gate["status"] == "BLOCKED":
        raise LearningPending(gate)
    if any(run.resolve().is_relative_to(p.resolve()) for p in (article, plan_path)):
        raise Refusal("output overlaps inputs")
    run.mkdir(parents=True)
    try:
        (run / "sources").mkdir()
        (run / "patches").mkdir()
        (run / "boot.md").write_bytes(before)
        (run / "plan.json").write_bytes(encoded(plan))
        for sid, data in sources.items():
            (run / "sources" / f"{sid}.txt").write_bytes(data)
        (run / "bindings.json").write_bytes(encoded({
            "boot_sha256": digest(before), "plan_sha256": digest(encoded(plan)),
            "sources": {sid: digest(data) for sid, data in sources.items()},
        }))
    except Exception:
        shutil.rmtree(run)
        raise
    return inspect(run)


def replay(run: Path) -> tuple[dict, bytes, list[dict]]:
    if run.is_symlink() or any((run / p).is_symlink() for p in ("patches", "sources")):
        raise Refusal("symlinked batch directory")
    binding = read_json(run / "bindings.json")
    before = read_file(run / "boot.md")
    raw_plan = read_file(run / "plan.json")
    if digest(before) != binding.get("boot_sha256") or digest(raw_plan) != binding.get("plan_sha256"):
        raise Refusal("boot or plan drift")
    plan = json.loads(raw_plan)
    sources = {}
    for sid, sha in binding.get("sources", {}).items():
        if not re.fullmatch(r"[a-z0-9-]+", sid):
            raise Refusal("invalid source ID")
        data = read_file(run / "sources" / f"{sid}.txt")
        if digest(data) != sha:
            raise Refusal("source snapshot drift")
        sources[sid] = data
    validate_plan(plan, plain_article(before), sources)
    gate = learning_gate(plan, sources)
    if gate and gate["status"] == "BLOCKED":
        raise LearningPending(gate)
    text = before.decode("utf-8")
    applied = []
    found = sorted((run / "patches").glob("*.json"))
    for index, path in enumerate(found):
        if index >= len(plan["units"]) or path.name != f"{index:04d}-{digest(read_file(path))[7:]}.json":
            raise Refusal("missing or out-of-order patch")
        patch = read_json(path)
        unit = plan["units"][index]
        if set(patch) != {"unit_id", "base_sha256", "text"}:
            raise Refusal("patch accepts only unit_id, base_sha256 and text")
        if patch["unit_id"] != unit["id"] or patch["base_sha256"] != digest(text.encode()):
            raise Refusal("wrong unit or stale patch base")
        delta = string(patch["text"], "patch.text")
        if delta != delta.rstrip() + "\n\n":
            raise Refusal("delta must end with two newlines")
        if any(term not in delta for term in unit.get("terms", [])):
            raise Refusal("delta lacks a declared canonical term")
        mc._extract_fences(delta)  # A batch must not borrow a closing fence from later prose.
        anchor = unit["insert_before"]
        if anchor in delta or text.count(anchor) != 1:
            raise Refusal("ambiguous patch destination")
        # The only allowed edit is insertion. Existing bytes cannot be replaced.
        text = text.replace(anchor, delta + anchor, 1)
        plain_article(text.encode())
        applied.append({"unit_id": unit["id"], "patch_sha256": digest(read_file(path))})
    return plan, text.encode(), applied


def inspect(run: Path) -> dict:
    plan, article, applied = replay(run)
    remaining = plan["units"][len(applied):]
    sources = {entry["id"]: read_file(run / "sources" / f"{entry['id']}.txt")
               for entry in plan["sources"]}
    handoff = learning_gate(plan, sources)
    if handoff is not None:
        handoff = {key: value for key, value in handoff.items() if key != "next"}
    final = run / "final"
    if final.exists():
        if remaining:
            raise Refusal("final output exists while work remains")
        proof = read_json(final / "batch-proof.json")
        review = read_json(final / "review.json")
        validate_review(review, plan, article)
        expected = {"boot_sha256": digest(read_file(run / "boot.md")),
                    "article_sha256": digest(article), "patches": applied,
                    "review_sha256": digest(read_file(final / "review.json")),
                    "bindings_sha256": digest(read_file(run / "bindings.json")),
                    "batch_helper_sha256": digest(Path(__file__).read_bytes())}
        if any(proof.get(k) != v for k, v in expected.items()):
            raise Refusal("final proof is stale")
        mc.check_receipt(final / "compiled")
        if read_file(final / "compiled/medium-canonical.md") != article:
            raise Refusal("canonical article does not match batch replay")
        return {"status": "DONE", "next": None, **expected,
                "learning_handoff": handoff, "case": plan.get("case"), "human_checkpoint": checkpoint_status(run, plan, article, len(applied)),
                "completion_scope": "declared source-bound work queue and recorded review",
                "semantic_review": "INDEPENDENT_DECLARED" if review["independent"] else "AUTHOR_REVIEW_ONLY",
                "human_learning_outcome": "NOT_MEASURED"}
    return {"status": "CONTINUE", "next": "drill-down" if remaining else "review-and-finish",
            "source_cursor": remaining[0]["id"] if remaining else None,
            "question": remaining[0]["question"] if remaining else None,
            "learning_handoff": handoff, "case": plan.get("case"),
            "learning_step": remaining[0].get("learning_step") if remaining else None,
            "decision_prompt": remaining[0].get("decision_prompt") if remaining else None,
            "evidence_refs": remaining[0].get("evidence_refs") if remaining else None,
            "human_checkpoint": checkpoint_status(run, plan, article, len(applied)),
            "remaining_work": [u["id"] for u in remaining], "applied": applied,
            "article_sha256": digest(article), "semantic_correctness": "NOT_ASSESSED"}


def checkpoint_status(run: Path, plan: dict, article: bytes, applied_count: int) -> dict | None:
    if "case" not in plan:
        return None
    files = list(run.glob("human-checkpoint-*.json"))
    if applied_count < len(plan["units"]):
        if files:
            raise Refusal("human checkpoint exists before all patches")
        return {"status": "DEFERRED"}
    prompts = [{"unit_id": u["id"], "prompt": u["decision_prompt"]} for u in plan["units"]]
    if not files:
        return {"status": "PENDING", "prompts": prompts}
    if len(files) != 1:
        raise Refusal("conflicting human checkpoints")
    path = files[0]
    if path.name != f"human-checkpoint-{digest(read_file(path))[7:]}.json":
        raise Refusal("human checkpoint receipt is stale")
    response = read_json(path)
    if set(response) != {"case", "article_sha256", "answers"}:
        raise Refusal("human checkpoint needs case, article_sha256 and answers")
    if response.get("case") != plan["case"] or response.get("article_sha256") != digest(article):
        raise Refusal("human checkpoint is stale for case revision or article")
    answers = response.get("answers")
    if not isinstance(answers, list) or len(answers) != len(prompts):
        raise Refusal("human checkpoint must answer each stable unit in order")
    for unit, answer in zip(plan["units"], answers):
        if not isinstance(answer, dict) or set(answer) != {"unit_id", "answer"} or answer["unit_id"] != unit["id"]:
            raise Refusal("human checkpoint must answer each stable unit in order")
        string(answer.get("answer"), "checkpoint answer")
    return {"status": "RECORDED_UNGRADED", "receipt_sha256": digest(read_file(path)), "prompts": prompts}


def record_checkpoint(run: Path, response_path: Path) -> dict:
    plan, article, applied = replay(run)
    if "case" not in plan or len(applied) != len(plan["units"]):
        raise Refusal("checkpoint requires a completed case work queue")
    response = read_json(response_path)
    existing = list(run.glob("human-checkpoint-*.json"))
    if existing:
        if len(existing) != 1 or read_json(existing[0]) != response:
            raise Refusal("conflicting human checkpoint")
        return {"operation": "NOOP", **inspect(run)}
    dest = run / f"human-checkpoint-{digest(encoded(response))[7:]}.json"
    with tempfile.TemporaryDirectory(prefix="medium-checkpoint-") as tmp:
        trial = Path(tmp) / "run"
        shutil.copytree(run, trial)
        (trial / dest.name).write_bytes(encoded(response))
        checkpoint_status(trial, plan, article, len(applied))
    with dest.open("xb") as stream:
        stream.write(encoded(response))
    return {"operation": "RECORDED", **inspect(run)}


def apply_patch(run: Path, patch_path: Path) -> dict:
    plan, article, applied = replay(run)
    patch = read_json(patch_path)
    # Identical retries are explicit no-ops, even when the original base is older.
    for index, item in enumerate(applied):
        if item["unit_id"] == patch.get("unit_id"):
            if read_json(sorted((run / "patches").glob("*.json"))[index]) != patch:
                raise Refusal("conflicting replay for an existing unit")
            return {"operation": "NOOP", **inspect(run)}
    if (run / "final").exists() or len(applied) == len(plan["units"]):
        raise Refusal("no pending unit; inspect current continuation")
    index = len(applied)
    filename = f"{index:04d}-{digest(encoded(patch))[7:]}.json"
    # Validate in a scratch clone; refusals cannot advance the live journal.
    with tempfile.TemporaryDirectory(prefix="medium-patch-") as tmp:
        trial = Path(tmp) / "run"
        shutil.copytree(run, trial)
        (trial / "patches" / filename).write_bytes(encoded(patch))
        replay(trial)
    dest = run / "patches" / filename
    # Exclusive creation is the commit; callers must not concurrently write one run.
    with dest.open("xb") as stream:
        stream.write(encoded(patch))
    return {"operation": "APPLIED", "delta": str(dest), **inspect(run)}


def validate_review(review: dict, plan: dict, article: bytes) -> None:
    if review.get("article_sha256") != digest(article):
        raise Refusal("review does not name current article bytes")
    if review.get("unit_ids") != [u["id"] for u in plan["units"]]:
        raise Refusal("review must cover every declared unit")
    if review.get("verdict") != "PASS" or review.get("unresolved_gaps") != []:
        raise Refusal("review has failures or unresolved gaps")
    if type(review.get("independent")) is not bool:
        raise Refusal("review must identify whether it is independent")
    string(review.get("reviewer"), "reviewer")
    for key in ("source_fidelity", "causal_continuity", "limits"):
        string(review.get(key), key)


def finish(run: Path, review_path: Path) -> dict:
    plan, article, applied = replay(run)
    if len(applied) != len(plan["units"]):
        raise Refusal("pending work: finish is not legal")
    if (run / "final").exists():
        return inspect(run)
    review = read_json(review_path)
    validate_review(review, plan, article)
    temp = Path(tempfile.mkdtemp(prefix=".finish-", dir=run))
    logs = []
    try:
        (temp / "draft.md").write_bytes(article)
        (temp / "spec.json").write_bytes(encoded({"topic": plan["topic"], "claims": [], "terms": []}))
        (temp / "coverage.json").write_bytes(encoded({"elements": ["copyedit"], "claims": [], "terms": []}))
        cmds = [
            ["init", "--spec", str(temp / "spec.json"), "--draft", str(temp / "draft.md"), "--run-dir", str(temp / "compiled")],
            ["submit", "--run-dir", str(temp / "compiled"), "--stage", "6", "--input", str(temp / "draft.md"), "--coverage", str(temp / "coverage.json")],
            ["assemble", "--run-dir", str(temp / "compiled")],
            ["verify", "--run-dir", str(temp / "compiled")],
            ["check-receipt", "--run-dir", str(temp / "compiled")],
        ]
        for args in cmds:
            argv = [sys.executable, str(ROOT / "medium_compiler.py"), *args]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            logs.append({"argv": argv, "exit": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
            if result.returncode:
                raise Refusal("existing compiler rejected finalization")
        if read_file(temp / "compiled/medium-canonical.md") != article:
            raise Refusal("assembly changed batch article bytes")
        (temp / "review.json").write_bytes(encoded(review))
        (temp / "batch-proof.json").write_bytes(encoded({
            "boot_sha256": digest(read_file(run / "boot.md")), "article_sha256": digest(article),
            "patches": applied, "review_sha256": digest(encoded(review)),
            "bindings_sha256": digest(read_file(run / "bindings.json")),
            "batch_helper_sha256": digest(Path(__file__).read_bytes()),
            "semantics": "recorded review, not proven by hashes", "publication": "NOT_PERFORMED"}))
        (temp / "commands.json").write_bytes(encoded({"commands": logs}))
        temp.rename(run / "final")
    except Exception:
        (temp / "commands.json").write_bytes(encoded({"commands": logs}))
        raise Refusal(f"finalization failed; diagnostic evidence retained at {temp}")
    return inspect(run)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight", help="Read-only source/learning prerequisites; no progress writes")
    p.add_argument("--article", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p = sub.add_parser("boot")
    p.add_argument("--article", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--run-dir", type=Path, required=True)
    for cmd in ("next", "drill-down", "finish", "render", "checkpoint"):
        p = sub.add_parser(cmd)
        p.add_argument("--run-dir", type=Path, required=True)
        if cmd == "drill-down": p.add_argument("--patch", type=Path, required=True)
        if cmd == "finish": p.add_argument("--review", type=Path, required=True)
        if cmd == "render": p.add_argument("--output", type=Path, required=True)
        if cmd == "checkpoint": p.add_argument("--response", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.cmd == "preflight": result = preflight(args.article, args.plan)
        elif args.cmd == "boot": result = boot(args.article, args.plan, args.run_dir)
        elif args.cmd == "drill-down": result = apply_patch(args.run_dir, args.patch)
        elif args.cmd == "finish": result = finish(args.run_dir, args.review)
        elif args.cmd == "checkpoint": result = record_checkpoint(args.run_dir, args.response)
        elif args.cmd == "render":
            _, data, _ = replay(args.run_dir)
            if args.output.exists() or args.output.resolve().is_relative_to(args.run_dir.resolve()):
                raise Refusal("render output must be new and outside the run")
            args.output.write_bytes(data)
            result = {"status": "RENDERED", "article_sha256": digest(data)}
        else: result = inspect(args.run_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 3 if result.get("status") == "BLOCKED" else 0
    except LearningPending as exc:
        print(json.dumps(exc.projection, ensure_ascii=False, indent=2))
        return 3
    except (Refusal, mc.CompilerError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
