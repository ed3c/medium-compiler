#!/usr/bin/env python3
"""Install commit-pinned, complete upstream design skills into this checkout only.

No shell execution, global installation, dependency install, or symlink traversal.
Run from a trusted checkout after reviewing upstream sources and licenses.
"""
import argparse
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import tempfile
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
MAX_COMPRESSED_BYTES = 50 * 1024 * 1024
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def read_archive(source):
    owner, repo = source["repo"].split("/")
    url = "https://github.com/" + owner + "/" + repo + "/archive/" + source["sha"] + ".tar.gz"
    with urlopen(url, timeout=30) as response:
        raw = response.read(MAX_COMPRESSED_BYTES + 1)
    if len(raw) > MAX_COMPRESSED_BYTES:
        raise ValueError("Upstream archive exceeds size limit: " + source["id"])
    return raw


def extracted_files(raw, source):
    if len(raw) > MAX_COMPRESSED_BYTES:
        raise ValueError("Upstream archive exceeds size limit")
    found = {}
    total = 0
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not name.parts:
                raise ValueError("Unsafe archive member path")
            if not member.isfile() and not member.isdir():
                raise ValueError("Archive symlink, device or hardlink is forbidden: " + str(name))
            if not member.isfile():
                continue
            if len(name.parts) < 2:
                continue
            relative = PurePosixPath(*name.parts[1:])
            if relative in found:
                raise ValueError("Duplicate archive member")
            if member.size > MAX_FILE_BYTES:
                raise ValueError("Upstream file exceeds size limit: " + str(relative))
            total += member.size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("Upstream content exceeds size limit")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError("Unreadable upstream member")
            data = stream.read(MAX_FILE_BYTES + 1)
            if len(data) != member.size:
                raise ValueError("Truncated upstream member")
            found[relative] = data
    if not found:
        raise ValueError("Empty archive: " + source["id"])
    return found


def selected_skills(source, files):
    base = PurePosixPath(source["source"])
    chosen = {}
    if source["id"] == "emil":
        for original, data in files.items():
            if original.parts[:1] == ("skills",) and len(original.parts) >= 3:
                target = PurePosixPath(original.parts[1]) / PurePosixPath(*original.parts[2:])
                chosen[target] = data
    elif source["id"] == "anatomy":
        chosen = {PurePosixPath("anatomy") / p: data for p, data in files.items()}
    else:
        prefix = base.parts
        target_root = PurePosixPath(source["targets"][0])
        for original, data in files.items():
            if original.parts[:len(prefix)] == prefix and len(original.parts) > len(prefix):
                target = target_root / PurePosixPath(*original.parts[len(prefix):])
                chosen[target] = data
    # Supply the upstream license text with each installed package as provenance.
    license_bytes = next((files[p] for p in [PurePosixPath("LICENSE"), PurePosixPath("LICENSE.md")] if p in files), None)
    groups = {}
    for path, data in chosen.items():
        groups.setdefault(path.parts[0], {})[PurePosixPath(*path.parts[1:])] = data
    for target, contents in groups.items():
        if PurePosixPath("SKILL.md") not in contents:
            raise ValueError("Incomplete skill missing SKILL.md: " + target)
        if license_bytes is not None:
            contents[PurePosixPath("UPSTREAM-LICENSE")] = license_bytes
        contents[PurePosixPath(".upstream-provenance.json")] = (
            json.dumps({"repo":source["repo"],"sha":source["sha"],
                        "license":source["license"]}, sort_keys=True) + "\n"
        ).encode("utf-8")
    return groups


def install(root, lock, dry_run=False):
    skills = root / ".agents" / "skills"
    if skills.is_symlink():
        raise ValueError("Skill directory cannot be a symlink")
    planned = {}
    for source in lock["sources"]:
        members = extracted_files(read_archive(source), source)
        groups = selected_skills(source, members)
        for name, files in groups.items():
            if name in planned:
                raise ValueError("Collision between upstream packages: " + name)
            planned[name] = files
    for name, members in planned.items():
        destination = skills / name
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink() or not destination.is_dir():
                raise ValueError("Existing skill path is not an ordinary directory: " + name)
            existing = {
                PurePosixPath(*p.relative_to(destination).parts): p.read_bytes()
                for p in destination.rglob("*") if p.is_file()
            }
            if any(p.is_symlink() for p in destination.rglob("*")) or existing != members:
                raise ValueError("Existing skill differs; refuse overwrite: " + name)
    if dry_run:
        return {"status":"DRY_RUN","skills":sorted(planned)}
    skills.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".loop-skills-", dir=skills) as scratch:
        staged = Path(scratch)
        for name, members in planned.items():
            for path, data in members.items():
                output = staged / name / Path(*path.parts)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
        for name in sorted(planned):
            dest = skills / name
            if not dest.exists():
                (staged / name).rename(dest)
    return {"status":"INSTALLED_OR_VERIFIED","skills":sorted(planned)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    lock = json.loads((ROOT / "design/visual-skills.lock.json").read_text("utf-8"))
    if lock.get("schema_version") != 1:
        raise ValueError("Unsupported visualization skill lock")
    print(json.dumps(install(ROOT, lock, args.dry_run), ensure_ascii=False))


if __name__ == "__main__":
    main()
