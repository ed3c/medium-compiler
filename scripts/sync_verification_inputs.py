#!/usr/bin/env python3
"""Install pinned, reviewed skill/data snapshots into this repository only.

No network, model calls, global configuration, or execution of upstream code.
Input archives must match the recorded SHA-256 bytes. Existing different files
are refused so updates require an explicit source/version review.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "evals-skills": ("80d5f7b0127c7572ed9e9339937adbfd7240ffeb", "55cf2aa0856ba162ba06377b0db88f7bae87435ecec0497620ccf6c7c9b0717c"),
    "pstack": ("68836ddaf5697224520f1847d90cdb90ca8babaa", "fd95a601d883d271ebc00bcb54cb69278c65ab67d97e16594704c1ca2c6b986d"),
    "ops": ("24a56d18661630b0dba97dcb0b057dce07b0ab32", "a30177f91ef113b94c9b928ee97f79481cf7807fe2c9bb1a4cc1513b5212c12a"),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs",type=Path,required=True)
    args=parser.parse_args()
    pending={};records=[]
    for key,(revision,sha) in PINS.items():
        path=args.inputs/f"{key}.tar.gz"
        if hashlib.sha256(path.read_bytes()).hexdigest()!=sha:
            raise ValueError(f"archive mismatch: {key}")
        with tarfile.open(path) as archive:
            for member in archive.getmembers():
                if not member.isfile(): continue
                rel=PurePosixPath(*PurePosixPath(member.name).parts[1:])
                if ".." in rel.parts: raise ValueError("unsafe archive path")
                name=str(rel);dest=None
                if key=="evals-skills":
                    if name.startswith("skills/"):
                        dest=ROOT/".agents"/name
                    elif name=="LICENSE":dest=ROOT/"references/upstream/evals-skills.LICENSE"
                elif key=="pstack" and name in [
                    "pstack/skills/create-verification-skill/SKILL.md",
                    "pstack/skills/maintain-verification-skill/SKILL.md",
                    "pstack/skills/create-verification-skill/references/feature-map-example/README.md",
                ]:
                    short=("create" if "/create-" in name else "maintain")+"-verification.md"
                    if "feature-map-example" in name: short="feature-map-example.md"
                    dest=ROOT/".agents/skills/verify-medium/references"/short
                elif key=="ops" and name=="app/main.py":dest=ROOT/"evidence/issue-8/inputs/ops-main.py"
                if dest is None: continue
                data=archive.extractfile(member).read()
                if dest.is_symlink() or (dest.exists() and dest.read_bytes()!=data):
                    raise ValueError(f"existing different bytes: {dest.relative_to(ROOT)}")
                pending[dest]=data
                records.append({"source":key,"revision":revision,"source_path":name,
                    "path":str(dest.relative_to(ROOT)),"sha256":hashlib.sha256(data).hexdigest(),
                    "git_blob":hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()})
    # No writes happen before every existing file and every archive is checked.
    for dest,data in pending.items():
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    target=ROOT/"references/upstream/skills-lock.json"
    target.write_text(json.dumps({"pins":PINS,"files":records},indent=2)+"\n")
    print(json.dumps({"installed_files":len(records),"global_changes":False,"network":False}))


if __name__=="__main__":main()
