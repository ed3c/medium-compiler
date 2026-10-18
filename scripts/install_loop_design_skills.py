#!/usr/bin/env python3
"""Install pinned, project-local upstream design skills. Never execute upstream code.

Network/git access is required for --install. Default --plan is side-effect-free.
Run on the intended Codex/Noodle host, not in CI or on a public deployment.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "docs/loop-design-skill-lock.json"

def load_plan():
    data = json.loads(LOCK.read_text(encoding="utf-8"))
    if data["schema_version"] != 1:
        raise ValueError("Unsupported lock version")
    for row in data["sources"]:
        sha = row["commit"]
        if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("Source pin must be a full commit hash")
        repo = row["repository"]
        if not repo or "/" not in repo or not all(x.replace("-", "").replace("_", "").isalnum() for x in repo.split("/")):
            raise ValueError("Invalid repository")
        dest = Path(row["destination"])
        if dest.is_absolute() or ".." in dest.parts or not str(dest).startswith(".agents/skills/"):
            raise ValueError("Install outside project skill root")
    return data

def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

def copy_safe(source, destination):
    if source.is_symlink() or not source.exists():
        raise ValueError(f"Missing or symlinked source: {source}")
    for part in source.rglob("*"):
        if part.is_symlink():
            raise ValueError(f"Symlink refused: {part}")
    shutil.copytree(source, destination)

def stage_source(row, scratch):
    checkout = scratch / ("source-" + row["id"])
    url = "https://github.com/" + row["repository"] + ".git"
    # Pinned checkout; no installer, dependency hook, or upstream script is run.
    run("git", "clone", "--quiet", "--no-checkout", "--filter=blob:none", url, str(checkout))
    run("git", "-C", str(checkout), "fetch", "--quiet", "--depth=1", "origin", row["commit"])
    if row["subtree"] != ".":
        run("git", "-C", str(checkout), "sparse-checkout", "init", "--cone")
        run("git", "-C", str(checkout), "sparse-checkout", "set", row["subtree"])
    run("git", "-C", str(checkout), "checkout", "--quiet", "--detach", row["commit"])
    actual = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if actual != row["commit"]:
        raise ValueError("Pinned SHA mismatch: " + row["id"])
    output = scratch / "stage" / row["id"]
    output.mkdir(parents=True)
    src = checkout / row["subtree"]
    if row["id"] == "emil":
        for skill in sorted(src.iterdir()):
            if skill.is_dir() and (skill / "SKILL.md").is_file():
                copy_safe(skill, output / skill.name)
    elif row["id"] == "anatomy":
        # The Anatomy kit, scripts and examples are a single skill.
        for entry in src.iterdir():
            if entry.name in (".git", ".github") or entry.name.startswith("."):
                continue
            if entry.is_dir():
                copy_safe(entry, output / entry.name)
            elif entry.is_file() and not entry.is_symlink():
                shutil.copy2(entry, output / entry.name)
            else:
                raise ValueError("Unexpected Anatomy entry")
    else:
        copy_safe(src, output / row["id"])
    if row["id"] == "emil":
        return [(child, ROOT / row["destination"] / child.name) for child in output.iterdir()]
    final = ROOT / row["destination"]
    if row["id"] == "anatomy":
        # Contents of the staged root become the install directory.
        return [(output, final)]
    return [(output / row["id"], final)]

def install(plan):
    destinations = [ROOT / r["destination"] for r in plan["sources"] if r["id"] != "emil"]
    if any(p.exists() or p.is_symlink() for p in destinations):
        raise ValueError("Skill already present; refuse implicit replacement")
    with tempfile.TemporaryDirectory(prefix="loop-skills-") as temp:
        scratch = Path(temp)
        entries = []
        for source in plan["sources"]:
            entries.extend(stage_source(source, scratch))
        paths = [dest for _, dest in entries]
        if len(set(paths)) != len(paths) or any(d.exists() or d.is_symlink() for d in paths):
            raise ValueError("Conflicting skill names; no files installed")
        for _, dest in entries:
            dest.parent.mkdir(parents=True, exist_ok=True)
        completed = []
        try:
            for staged, dest in entries:
                os.replace(staged, dest)
                completed.append(dest)
        except Exception:
            for path in reversed(completed):
                shutil.rmtree(path)
            raise
        return [str(path.relative_to(ROOT)) for path in completed]

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--plan", action="store_true", help="Print pins; default, no writes")
    actions.add_argument("--install", action="store_true", help="Install pinned skills locally")
    args = parser.parse_args(argv)
    try:
        plan = load_plan()
        if not args.install:
            print(json.dumps({"status":"PLAN_ONLY","sources":plan["sources"]}, indent=2))
            return 0
        paths = install(plan)
        print(json.dumps({"status":"FILES_INSTALLED","paths":paths,
                          "native_skill_consumption":"NOT_RUN",
                          "browser_acceptance":"NOT_RUN"}, indent=2))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({"status":"REFUSED","reason":str(exc)}), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
