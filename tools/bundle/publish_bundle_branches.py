#!/usr/bin/env python3
"""
Script for publishing bundle branches.

Algorithm:
1. Read generated bundle metadata from each bundle output directory.
2. Determine the target output branch from `references/bundle-lock.json`.
3. Verify that the target branch starts with `dist/`.
4. Fetch the target branch from `origin` if it exists.
5. If the target branch does not exist, create it as an orphan branch.
6. If the target branch exists, check it out normally.
7. Replace the branch working tree with the generated bundle contents.
8. Commit only if there is a diff.
9. Push only when `--push` is explicitly provided.
10. Never force-push by default.

Usage: publish_bundle_branches.py --bundles-out <dir> [--push]
"""
import sys
import os
import json
import subprocess
import shutil

def run_cmd(cmd, cwd=None, check=True, capture_output=False):
    if capture_output:
        result = subprocess.run(cmd, cwd=cwd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    subprocess.run(cmd, cwd=cwd, check=check)

def get_bundle_info(bundle_dir):
    lockfile_path = os.path.join(bundle_dir, "references", "bundle-lock.json")
    if not os.path.exists(lockfile_path):
        return None
    with open(lockfile_path) as f:
        return json.load(f)

def publish_bundle(bundle_dir, push=False):
    info = get_bundle_info(bundle_dir)
    if not info:
        print(f"Skipping {bundle_dir}: No bundle-lock.json found")
        return

    bundle_name = info.get("bundle", {}).get("name", "unknown")
    target_branch = info.get("bundle", {}).get("outputBranch")
    source_commit = info.get("source", {}).get("commit", "unknown")
    source_bundle_def = info.get("source", {}).get("bundleDefinition", "unknown")

    if not target_branch or not target_branch.startswith("dist/"):
        print(f"Error: Invalid target branch '{target_branch}' for bundle {bundle_name}")
        return

    print(f"\nProcessing bundle: {bundle_name}")
    print(f"Target branch: {target_branch}")

    worktree_dir = f".worktree-{bundle_name}"

    try:
        if os.path.exists(worktree_dir):
            shutil.rmtree(worktree_dir)

        # Check if remote branch exists
        try:
            run_cmd(["git", "fetch", "origin", target_branch], check=False, capture_output=True)
            remote_exists = run_cmd(["git", "ls-remote", "--heads", "origin", target_branch], capture_output=True) != ""
        except Exception:
            remote_exists = False

        if remote_exists:
            print(f"Branch {target_branch} exists. Checking out.")
            run_cmd(["git", "worktree", "add", worktree_dir, target_branch])
        else:
            print(f"Branch {target_branch} does not exist. Creating as orphan.")
            os.makedirs(worktree_dir)
            run_cmd(["git", "clone", "--no-checkout", ".", worktree_dir])
            run_cmd(["git", "checkout", "--orphan", target_branch], cwd=worktree_dir)
            run_cmd(["git", "rm", "-rf", "."], cwd=worktree_dir, check=False)

        # Clear existing content (except .git)
        for item in os.listdir(worktree_dir):
            if item == ".git":
                continue
            item_path = os.path.join(worktree_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

        # Copy new content
        for item in os.listdir(bundle_dir):
            if item == ".git":
                continue
            src = os.path.join(bundle_dir, item)
            dst = os.path.join(worktree_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        # Commit and push
        run_cmd(["git", "add", "-A"], cwd=worktree_dir)

        status = run_cmd(["git", "status", "--porcelain"], cwd=worktree_dir, capture_output=True)
        if not status:
            print(f"No changes to publish for {bundle_name}.")
        else:
            commit_msg = f"""Publish {bundle_name} bundle

Source branch: main
Source commit: {source_commit}
Bundle definition: {source_bundle_def}"""

            if push:
                run_cmd(["git", "commit", "-m", commit_msg], cwd=worktree_dir)
                print(f"Pushing {target_branch}...")
                run_cmd(["git", "push", "origin", target_branch], cwd=worktree_dir)
                print(f"Successfully published {bundle_name} to {target_branch}.")
            else:
                print(f"Dry run: Would commit and push {bundle_name} to {target_branch}.")
                print(f"Commit message would be:\n{commit_msg}")

    finally:
        # Cleanup worktree
        if os.path.exists(worktree_dir):
            if os.path.exists(os.path.join(worktree_dir, ".git")):
                 try:
                     run_cmd(["git", "worktree", "remove", "--force", worktree_dir], check=False)
                 except:
                     pass
            try:
                shutil.rmtree(worktree_dir)
            except:
                pass


def main():
    if "--bundles-out" not in sys.argv:
        print("Usage: publish_bundle_branches.py --bundles-out <dir> [--push]")
        sys.exit(1)

    out_idx = sys.argv.index("--bundles-out") + 1
    if out_idx >= len(sys.argv):
        print("Error: Missing directory after --bundles-out")
        sys.exit(1)

    bundles_out = sys.argv[out_idx]
    push = "--push" in sys.argv

    if not push:
        print("Running in DRY RUN mode. Use --push to actualize changes.")

    if not os.path.exists(bundles_out):
        print(f"Error: Directory {bundles_out} does not exist.")
        sys.exit(1)

    for item in os.listdir(bundles_out):
        bundle_dir = os.path.join(bundles_out, item)
        if os.path.isdir(bundle_dir):
            publish_bundle(bundle_dir, push)

if __name__ == "__main__":
    main()
