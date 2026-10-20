"""Import an already authored Part 7 into the existing compiler's legal revision route.

Does not fabricate Stage 0..5 authorship or independently assess technical truth.
The unchanged Stage 6 bytes must be assembled and revalidated by original CLI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT=Path(__file__).resolve().parents[1]
ARTICLE=ROOT/"articles/leetcode-49-group-anagrams.md"
CLI=ROOT/"medium_compiler.py"


def cli(*args: str) -> dict:
    command=[sys.executable,str(CLI),*args]
    proc=subprocess.run(command,capture_output=True,text=True,check=False,cwd=ROOT)
    if proc.returncode:
        raise RuntimeError(f"{' '.join(command)} exited {proc.returncode}: {proc.stderr}")
    return json.loads(proc.stdout)


def validate_import(out: Path) -> dict:
    with tempfile.TemporaryDirectory(prefix="part7-compiler-") as temp:
        root=Path(temp)
        spec=root/"spec.json"
        spec.write_text(json.dumps({"topic":"Group Anagrams, canonical Part 7",
                                    "claims":[],"terms":[]}))
        coverage=root/"coverage.json"
        coverage.write_text(json.dumps({"elements":["copyedit"],"claims":[],"terms":[]}))
        run=root/"run"
        init=cli("init","--spec",str(spec),"--draft",str(ARTICLE),"--run-dir",str(run))
        next_step=cli("next","--run-dir",str(run))
        if init.get("mode")!="revision" or next_step.get("next_stage")!=6:
            raise RuntimeError("Existing content import must use Stage 6 revision route")
        cli("submit","--run-dir",str(run),"--stage","6","--input",str(ARTICLE),
            "--coverage",str(coverage))
        cli("assemble","--run-dir",str(run))
        receipt=cli("verify","--run-dir",str(run))
        checked=cli("check-receipt","--run-dir",str(run))
        original=ARTICLE.read_bytes()
        admitted=(run/"medium-canonical.md").read_bytes()
        if original!=admitted:
            first=next((i for i,(a,b) in enumerate(zip(original,admitted)) if a!=b),min(len(original),len(admitted)))
            raise RuntimeError("Canonical article bytes differ after compiler assembly: "
                               f"original={len(original)} assembled={len(admitted)} "
                               f"first_diff={first} original_tail={original[-40:]!r} "
                               f"assembled_tail={admitted[-40:]!r}")
        report={"status":"PASS","import_mode":"revision_not_fictional_stages",
                "cli_status":checked.get("status"),"bytes_equal":True,
                "article_sha256":receipt["article_sha256"],
                "semantic_correctness":"NOT_ASSESSED_BY_CLI"}
        out.mkdir(parents=True,exist_ok=True)
        (out/"import-validation.json").write_text(json.dumps(report,indent=2)+"\n")
        return report


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    print(json.dumps(validate_import(args.out),indent=2))
