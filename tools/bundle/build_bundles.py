#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess

import hashlib

def parse_simple_yaml(filepath):
    # A very simple YAML parser sufficient for our bundle definition template
    # Replaces PyYAML to avoid dependencies in the minimal template
    data = {"bundle": {}, "include": [], "generate": {}}
    in_include = False
    current_include = {}

    with open(filepath) as f:
        for line in f:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("bundle:"):
                in_include = False
                continue
            elif line.startswith("include:"):
                in_include = True
                continue
            elif line.startswith("generate:"):
                in_include = False
                continue

            if in_include:
                if line.startswith("  - from:"):
                    if current_include:
                        data["include"].append(current_include)
                    current_include = {"from": line.split("from:")[1].strip()}
                elif line.startswith("    to:"):
                    current_include["to"] = line.split("to:")[1].strip()
                elif line.startswith("    mode:"):
                    current_include["mode"] = line.split("mode:")[1].strip()
            else:
                if line.startswith("  name:"):
                    data["bundle"]["name"] = line.split("name:")[1].strip()
                elif line.startswith("  kind:"):
                    data["bundle"]["kind"] = line.split("kind:")[1].strip()
                elif line.startswith("  outputBranch:"):
                    data["bundle"]["outputBranch"] = line.split("outputBranch:")[1].strip()
                elif line.startswith("  lockFile:"):
                    data["generate"]["lockFile"] = line.split("lockFile:")[1].strip()
                elif line.startswith("  readme:"):
                    data["generate"]["readme"] = line.split("readme:")[1].strip()

    if current_include:
        data["include"].append(current_include)

    return data

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def build_bundle(yaml_path, out_dir):
    print(f"Building bundle from {yaml_path}...")
    bundle_data = parse_simple_yaml(yaml_path)

    bundle_name = bundle_data["bundle"].get("name", "unknown")
    target_dir = os.path.join(out_dir, bundle_name)

    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)

    included_files = []

    def copy_file(src_path, dst_path, rel_src, rel_dst):
        if os.path.islink(src_path):
            print(f"Error: Symlinks are not allowed: {src_path}")
            sys.exit(1)

        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)

        # normalize path for json
        rel_dst_norm = os.path.relpath(dst_path, target_dir)
        included_files.append({
            "from": rel_src,
            "to": rel_dst_norm,
            "sha256": get_file_hash(dst_path)
        })

    for inc in bundle_data.get("include", []):
        src = inc.get("from")
        dst = inc.get("to")

        if not src or not dst:
            continue

        if os.path.isabs(src) or ".." in src or os.path.isabs(dst) or ".." in dst:
            print(f"Error: Invalid path in include directive: {src} -> {dst}")
            sys.exit(1)

        target_path = os.path.normpath(os.path.join(target_dir, dst))

        # Verify target path does not escape target_dir
        if not os.path.abspath(target_path).startswith(os.path.abspath(target_dir)):
            print(f"Error: Target path escapes bundle root: {target_path}")
            sys.exit(1)

        if os.path.isdir(src):
            for root, dirs, files in os.walk(src):
                # Ensure deterministic order
                dirs.sort()
                files.sort()
                for file in files:
                    file_src = os.path.join(root, file)
                    rel_path = os.path.relpath(file_src, src)
                    file_dst = os.path.join(target_path, rel_path) if dst != "./" else os.path.join(target_dir, rel_path)
                    if os.path.normpath(dst) == ".":
                        file_dst = os.path.join(target_dir, rel_path)
                    copy_file(file_src, file_dst, file_src, os.path.relpath(file_dst, target_dir))
        elif os.path.isfile(src):
            copy_file(src, target_path, src, dst)

    try:
        repo_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode("utf-8").strip()
    except Exception:
        repo_url = "https://github.com/TakashiSasaki/skill.moukaeritai.work.git"

    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
    except Exception:
        commit = "unknown"

    # Generate lock file
    lock_file = bundle_data.get("generate", {}).get("lockFile")
    if lock_file:
        lock_path = os.path.normpath(os.path.join(target_dir, lock_file))
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)

        lock_data = {
            "schemaVersion": 1,
            "bundle": {
                "name": bundle_name,
                "kind": bundle_data["bundle"].get("kind", "unknown"),
                "outputBranch": bundle_data["bundle"].get("outputBranch", "unknown")
            },
            "source": {
                "repository": repo_url,
                "branch": "main",
                "commit": commit,
                "bundleDefinition": yaml_path
            },
            "generated": {
                "mode": "orphan-distribution-branch",
                "historyPolicy": "append-only"
            },
            "included": included_files
        }

        with open(lock_path, "w") as f:
            import json
            json.dump(lock_data, f, indent=2)

    # Generate README
    readme_file = bundle_data.get("generate", {}).get("readme")
    if readme_file:
        readme_path = os.path.normpath(os.path.join(target_dir, readme_file))
        os.makedirs(os.path.dirname(readme_path), exist_ok=True)

        output_branch = bundle_data["bundle"].get("outputBranch", "unknown")

        readme_content = f"""# {bundle_name}

> [!WARNING]
> This is a generated distribution branch.
> This branch is generated from `main` and is not the canonical source.
>
> Small-team field patches may be committed directly to this branch for debugging or minor improvements. Such changes are temporary and must be backported to `main` or explicitly discarded. The bundle publisher detects commits after the last generated commit and aborts normal publication to avoid silently overwriting field patches.
>
> Optional commit message trailer:
>
> Backport-to-main: required
>
> This trailer is helpful but not required. Field patches are detected even without it.

## Provenance

- **Source bundle definition:** `{yaml_path}`
- **Source commit:** `{commit}`

## Usage

You can add this bundle as a submodule to your project:

```bash
git submodule add -b {output_branch} \\
  {repo_url} \\
  .agents/skills/{bundle_name}
```

To update the submodule later:

```bash
git submodule update --remote .agents/skills/{bundle_name}
```
"""
        with open(readme_path, "w") as f:
            f.write(readme_content)

def main():
    if "--all" not in sys.argv or "--out" not in sys.argv:
        print("Usage: build_bundles.py --all --out <dir>")
        sys.exit(1)

    out_idx = sys.argv.index("--out") + 1
    out_dir = sys.argv[out_idx]

    bundles_dir = "bundles"
    for root, _, files in os.walk(bundles_dir):
        for f in files:
            if f.endswith(".yaml") or f.endswith(".yml"):
                yaml_path = os.path.join(root, f)
                build_bundle(yaml_path, out_dir)

if __name__ == "__main__":
    main()
