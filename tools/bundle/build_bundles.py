#!/usr/bin/env python3
import sys
import os
import shutil
import subprocess

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

    if current_include:
        data["include"].append(current_include)

    return data

def build_bundle(yaml_path, out_dir):
    print(f"Building bundle from {yaml_path}...")
    bundle_data = parse_simple_yaml(yaml_path)

    bundle_name = bundle_data["bundle"].get("name", "unknown")
    target_dir = os.path.join(out_dir, bundle_name)

    os.makedirs(target_dir, exist_ok=True)

    for inc in bundle_data.get("include", []):
        src = inc.get("from")
        dst = inc.get("to")

        if not src or not dst:
            continue

        if os.path.isabs(src) or ".." in src or os.path.isabs(dst) or ".." in dst:
            print(f"Error: Invalid path in include directive: {src} -> {dst}")
            sys.exit(1)

        target_path = os.path.normpath(os.path.join(target_dir, dst))

        if os.path.isdir(src):
            if target_path != target_dir: # don't copy dir to itself recursively
                shutil.copytree(src, target_path, dirs_exist_ok=True)
            else:
                # copy contents of dir
                for item in os.listdir(src):
                    s = os.path.join(src, item)
                    d = os.path.join(target_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True)
                    else:
                        shutil.copy2(s, d)
        elif os.path.isfile(src):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(src, target_path)

    # Generate lock file
    lock_file = bundle_data.get("generate", {}).get("lockFile")
    if lock_file:
        lock_path = os.path.normpath(os.path.join(target_dir, lock_file))
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)

        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        except Exception:
            commit = "unknown"

        lock_data = {
            "bundleName": bundle_name,
            "sourceCommit": commit
        }

        with open(lock_path, "w") as f:
            import json
            json.dump(lock_data, f, indent=2)

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
