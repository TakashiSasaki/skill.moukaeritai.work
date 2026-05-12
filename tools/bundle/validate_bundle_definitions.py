#!/usr/bin/env python3
import sys
import os

def check_bundle(yaml_path):
    # Minimal check based on simple parsing
    errors = 0
    with open(yaml_path) as f:
        content = f.read()

    if "schemaVersion:" not in content:
        print(f"FAIL: {yaml_path} missing schemaVersion")
        errors += 1

    if "bundle:" not in content:
        print(f"FAIL: {yaml_path} missing bundle block")
        errors += 1
    else:
        if "  name:" not in content:
            print(f"FAIL: {yaml_path} missing bundle.name")
            errors += 1
        if "  kind:" not in content:
            print(f"FAIL: {yaml_path} missing bundle.kind")
            errors += 1
        if "  source:" not in content:
            print(f"FAIL: {yaml_path} missing bundle.source")
            errors += 1
        if "  outputBranch:" not in content:
            print(f"FAIL: {yaml_path} missing bundle.outputBranch")
            errors += 1
        elif "outputBranch: dist/" not in content:
            print(f"FAIL: {yaml_path} outputBranch must start with dist/")
            errors += 1

    if "include:" not in content:
        print(f"FAIL: {yaml_path} missing include block")
        errors += 1

    # Check paths
    for line in content.splitlines():
        if line.strip().startswith("- from:"):
            path = line.split("from:")[1].strip()
            if os.path.isabs(path) or ".." in path:
                print(f"FAIL: {yaml_path} includes unsafe source path: {path}")
                errors += 1
            elif not os.path.exists(path):
                print(f"FAIL: {yaml_path} includes non-existent path: {path}")
                errors += 1
        if line.strip().startswith("to:"):
            path = line.split("to:")[1].strip()
            if os.path.isabs(path) or ".." in path:
                print(f"FAIL: {yaml_path} includes unsafe target path: {path}")
                errors += 1
        if line.strip().startswith("mode:"):
            mode = line.split("mode:")[1].strip()
            if mode != "copy":
                print(f"FAIL: {yaml_path} unsupported mode: {mode}")
                errors += 1

    if "generate:" in content:
        has_lockfile = False
        for line in content.splitlines():
            if line.strip().startswith("lockFile:"):
                lock_file = line.split("lockFile:")[1].strip()
                has_lockfile = True
                if not lock_file.endswith("bundle-lock.json"):
                    print(f"FAIL: {yaml_path} generate.lockFile must end with bundle-lock.json")
                    errors += 1
        if not has_lockfile:
            print(f"FAIL: {yaml_path} missing generate.lockFile")
            errors += 1
    else:
        print(f"FAIL: {yaml_path} missing generate block")
        errors += 1

    if errors == 0:
        print(f"PASS: {yaml_path} is valid")

    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: validate_bundle_definitions.py <bundles_dir>")
        sys.exit(1)

    bundles_dir = sys.argv[1]
    total_errors = 0

    for root, _, files in os.walk(bundles_dir):
        for f in files:
            if f.endswith(".yaml") or f.endswith(".yml"):
                yaml_path = os.path.join(root, f)
                total_errors += check_bundle(yaml_path)

    if total_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
