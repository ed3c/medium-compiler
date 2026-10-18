#!/usr/bin/env python3
"""Compile source-bound, inert ViewEnv Design Artifacts.

No prompts, model calls, executable nexts or runtime metadata invented here.
Session chooses one design intent; this program pins its source and maps a
known intent to one primary pinned Skill.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
MODES = {
    "public_story": "taste-skill",
    "operations": "impeccable",
    "mechanism": "anatomy",
    "motion_audit": "emil-design-eng",
    "annotation": "build-review-interface",
}
SECONDARY = {"motion_review":"review-animations",
             "animation_performance":"animation-performance",
             "accessibility":"impeccable"}


def compile_design(request, root=ROOT):
    if type(request) is not dict or set(request) != {
            "mode", "source", "goal", "reviews"}:
        raise ValueError("invalid_viewenv_design_request")
    if request["mode"] not in MODES or type(request["goal"]) is not str or not request["goal"].strip():
        raise ValueError("invalid_design_goal_or_mode")
    if type(request["source"]) is not str or not request["source"].strip():
        raise ValueError("invalid_source")
    if type(request["reviews"]) is not list or len(set(map(str, request["reviews"]))) != len(request["reviews"]):
        raise ValueError("invalid_reviews")
    if any(type(x) is not str or x not in SECONDARY for x in request["reviews"]):
        raise ValueError("unsupported_secondary_review")
    relative = Path(request["source"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("source_outside_checkout")
    source = root / relative
    if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(root.resolve()):
        raise ValueError("source_not_regular_or_outside_checkout")
    raw = source.read_bytes()
    if not raw:
        raise ValueError("empty_source")
    primary = MODES[request["mode"]]
    secondary = sorted({SECONDARY[x] for x in request["reviews"]} - {primary})
    manifest = json.loads((root / "design/visual-skills.lock.json").read_text("utf-8"))
    pins = {x["id"]: x["sha"] for x in manifest["sources"]}
    # build-review-interface is already local, no external SHA fabricated
    primary_pin = {
        "taste-skill":pins["taste"], "impeccable":pins["impeccable"],
        "anatomy":pins["anatomy"], "emil-design-eng":pins["emil"]
    }.get(primary)
    return {
        "kind":"viewenv/design/v1", "status":"planned",
        "goal":request["goal"],"source":{"path":relative.as_posix(),
                                            "sha256":hashlib.sha256(raw).hexdigest()},
        "mode":request["mode"],"primary_skill":primary,
        "primary_upstream_commit":primary_pin,
        "secondary_skills":secondary,
        "execution_authority":False, "training_authority":False,
        "publish_authority":False, "skill_invoked":False,
        "browser_verified":False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.request.is_symlink() or not args.request.is_file():
            raise ValueError("invalid_request_file")
        result = compile_design(json.loads(args.request.read_text("utf-8")))
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (ValueError, OSError, TypeError) as error:
        print(json.dumps({"status":"REFUSED","condition":str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
