#!/usr/bin/env python3
"""Project a frozen writer comparison onto the native ChatGPT cloud-subagent carrier.

This helper does not launch a model, install Codex, inspect credentials, or create host
approval. The current cloud supervisor owns capability discovery and the actual native
spawn calls. Repository code only binds the experiment inputs and launch requests.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Invalid(ValueError): pass

def sha(data: bytes)->str:
    return "sha256:"+hashlib.sha256(data).hexdigest()

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def hex40(value):
    return isinstance(value,str) and re.fullmatch(r"[0-9a-f]{40}",value) is not None

def validate(spec_path: Path, native_path: Path) -> dict:
    spec=load(spec_path); cloud=load(native_path)
    if spec.get("schema_version")!="writer-pair-experiment@1":
        raise Invalid("unsupported writer experiment")
    if cloud.get("schema_version")!="native-writer-cloud@1":
        raise Invalid("unsupported native cloud contract")
    if cloud.get("experiment_id")!=spec.get("experiment_id"):
        raise Invalid("native contract selects another experiment")
    if cloud.get("carrier")!="native collaboration.spawn_agent":
        raise Invalid("cloud carrier must be native collaboration.spawn_agent")
    if cloud.get("fork_turns")!="none":
        raise Invalid("native consumers must not inherit conversation")
    if cloud.get("model_override", "sentinel") is not None:
        raise Invalid("native comparison must not invent a model override")
    if cloud.get("order")!=spec.get("order"):
        raise Invalid("native run order differs from frozen experiment")
    if cloud.get("baseline_ref")!=spec["arms"]["baseline"]["revision"]:
        raise Invalid("baseline ref drift")
    if cloud.get("treatment_ref")!=spec["arms"]["treatment"]["revision"]:
        raise Invalid("treatment ref drift")
    if not hex40(cloud.get("common_ref")):
        raise Invalid("common ref must be a pinned 40-hex Git revision")
    probe=cloud.get("pilot_probe")
    if (not isinstance(probe,dict) or not hex40(probe.get("ref"))
            or probe.get("path")!=spec["task"]["path"]
            or probe.get("sha256")!=spec["task"]["sha256"]):
        raise Invalid("pilot probe must bind the exact task path and bytes")
    forbidden=cloud.get("consumer_forbidden_inputs")
    required={"expected answers","observer criteria","other arm output","experiment reports"}
    if not isinstance(forbidden,list) or not required.issubset(set(forbidden)):
        raise Invalid("consumer forbidden-input boundary incomplete")
    if cloud.get("observer_owner")!="external supervisor":
        raise Invalid("observer must remain outside consumer context")
    if cloud.get("effects")!=["read-pinned-github-inputs","write-assigned-evidence-only"]:
        raise Invalid("native consumer effects drift")
    return {"experiment":spec,"cloud":cloud}

def project(spec_path: Path, native_path: Path) -> dict:
    v=validate(spec_path,native_path);spec=v["experiment"];cloud=v["cloud"]
    common_ref=cloud["common_ref"]
    selected={
      "baseline": spec["arms"]["baseline"]["revision"],
      "treatment": spec["arms"]["treatment"]["revision"],
    }
    task={"ref":common_ref,"path":spec["task"]["path"],
          "sha256":spec["task"]["sha256"]}
    common=[{"ref":common_ref,**x} for x in spec["common_files"]]
    arms={a:[{"ref":selected[a],**x} for x in spec["arms"][a]["files"]]
          for a in selected}
    def source_lines(items):
        return "; ".join(f"{x['path']} -> {x['target']} ({x['sha256']})" for x in items)
    launches=[]
    for i,arm in enumerate(cloud["order"],1):
        ref=selected[arm]
        message=(
          "Execute the pinned writer task once in an isolated scratch work directory. "
          f"Experiment {spec['experiment_id']}; run run-{i:02d}; arm {arm}. "
          "Start from no inherited conversation. Read the task at "
          f"ed3c/medium-compiler@{common_ref}:{task['path']} ({task['sha256']}); "
          "treat its exact bytes as the writer instruction. Copy only these common GitHub "
          f"inputs from that ref into their target paths: {source_lines(common)}. "
          f"Copy only this arm's GitHub inputs from ed3c/medium-compiler@{ref}: "
          f"{source_lines(arms[arm])}. Verify every SHA-256 before executing the task. "
          "Use the supplied Python CLI in the isolated work directory and retain actual "
          "tool attempts, exits, final response and work/ file effects. "
          "Do not read expected answers, observer criteria, experiment reports, prior/other-arm "
          "results, later article explanations, or repository history. Do not modify source, Ops, "
          "LEARNING.md, provider state, or publish anything. Decide the currently permitted next "
          "step for the supplied learning-episode state. Report the exact GitHub sources actually "
          "read, the next owner/action or precise missing prerequisite, any attempted effect, and "
          "unknown telemetry. Write only the assigned evidence result when the native carrier "
          "supports an evidence destination. No delegation."
        )
        launches.append({
          "run_id":f"run-{i:02d}","arm":arm,"task_name":f"medium_writer_{i:02d}_{arm}",
          "tool":"collaboration.spawn_agent","fork_turns":"none","model_override":None,
          "message":message,"source_ref":ref,"common_ref":common_ref,
          "task":task,"common_inputs":common,"arm_inputs":arms[arm]
        })
    pilot={
      "task_name":"medium_writer_native_pilot","tool":"collaboration.spawn_agent",
      "fork_turns":"none","model_override":None,
      "counts_as_comparison":False,
      "message":(
        "Unscored native carrier pilot. Read only "
        f"ed3c/medium-compiler@{cloud['pilot_probe']['ref']}:"
        f"{cloud['pilot_probe']['path']} ({cloud['pilot_probe']['sha256']}) "
        "and report its blob identity and whether content was "
        "retrievable. Do not infer expected writer behavior, modify files, or delegate."
      ),"probe":cloud["pilot_probe"]
    }
    return {
      "schema_version":"native-writer-launch-plan@1",
      "status":"READY_FOR_NATIVE_SUPERVISOR",
      "experiment_id":spec["experiment_id"],
      "comparison_kind":spec["comparison_kind"],
      "carrier":cloud["carrier"],"fork_turns":"none","model_override":None,
      "pilot":pilot,"launches":launches,
      "observer_owner":"external supervisor",
      "shared_storage_is_security_isolation":False,
      "consumer_inputs_exclude":cloud["consumer_forbidden_inputs"],
      "model_calls":0,"fresh_writer_ab":"NOT_RUN","behavior":None,
      "authorizes_native_launch":False,"authorizes_landing":False,
      "next":{"owner":"current cloud Session supervisor",
              "operation":"discover-and-use-native-subagent-if-exposed",
              "missing_input":"actual native spawn/capture capability in this Session"},
      "contract_sha256":sha(native_path.read_bytes()),
      "experiment_sha256":sha(spec_path.read_bytes())
    }

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--spec",type=Path,default=ROOT/"evals/writing/ops-evidence-handoff/experiment.json")
    p.add_argument("--native",type=Path,default=ROOT/"evals/writing/ops-evidence-handoff/native-cloud.json")
    a=p.parse_args()
    try: result=project(a.spec,a.native)
    except (Invalid,KeyError,TypeError,ValueError,json.JSONDecodeError) as exc:
        result={"status":"BLOCKED","error":str(exc),"model_calls":0,
                "fresh_writer_ab":"NOT_RUN","behavior":None,
                "authorizes_native_launch":False,"authorizes_landing":False}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["status"]=="READY_FOR_NATIVE_SUPERVISOR" else 3

if __name__=="__main__": raise SystemExit(main())
