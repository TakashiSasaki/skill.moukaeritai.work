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

def check_for_field_patches(target_branch):
    """
    Checks for field patches on the target branch.
    Returns: (has_field_patches, last_generated_commit, pending_commits_list, changed_files_list)
    """
    try:
        remote_exists = run_cmd(["git", "ls-remote", "--heads", "origin", target_branch], capture_output=True) != ""
        if not remote_exists:
            return False, None, [], []

        # Fetch the target branch
        run_cmd(["git", "fetch", "origin", target_branch], check=False, capture_output=True)

        # Get all commits on the branch
        commits_output = run_cmd(["git", "log", "--format=%H|%s", f"origin/{target_branch}"], check=False, capture_output=True)
        if not commits_output:
            return False, None, [], []

        # Find the last generated commit
        commits = commits_output.strip().split('\n')
        last_gen_commit_hash = None
        for line in commits:
            if not line: continue
            commit_hash = line.split('|')[0]
            msg_body = run_cmd(["git", "log", "-1", "--format=%b", commit_hash], check=False, capture_output=True)
            if "Generated-by: skill-bundle-publisher" in msg_body:
                last_gen_commit_hash = commit_hash
                break

        if not last_gen_commit_hash:
            # Branch exists but no generated commit marker found. Treat as suspicious/all field patches.
            return True, None, commits, [] # Can't reliably get changed files for all history easily without full clone

        # Get commits after the last generated commit
        pending_commits_output = run_cmd(["git", "log", "--format=%h %s", f"{last_gen_commit_hash}..origin/{target_branch}"], check=False, capture_output=True)
        pending_commits = [line for line in pending_commits_output.strip().split('\n') if line]

        if not pending_commits:
            return False, last_gen_commit_hash, [], []

        # Get files changed by pending commits
        changed_files_output = run_cmd(["git", "diff", "--name-only", f"{last_gen_commit_hash}..origin/{target_branch}"], check=False, capture_output=True)
        changed_files = [line for line in changed_files_output.strip().split('\n') if line]

        return True, last_gen_commit_hash, pending_commits, changed_files

    except Exception as e:
        print(f"Warning: Failed to check for field patches: {e}")
        return False, None, [], []


def publish_bundle(bundle_dir, push=False, allow_overwrite=False, overwrite_reason=None):
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

    print(f"\nBundle: {bundle_name}")
    print(f"Target branch: {target_branch}")

    # Check for field patches
    remote_exists = False
    try:
        remote_exists = run_cmd(["git", "ls-remote", "--heads", "origin", target_branch], capture_output=True) != ""
    except Exception:
        pass

    print(f"Branch exists: {'Yes' if remote_exists else 'No'}")

    has_field_patches, last_gen_commit, pending_commits, changed_files = check_for_field_patches(target_branch)

    if last_gen_commit:
        last_gen_msg = run_cmd(["git", "log", "-1", "--format=%s", last_gen_commit], check=False, capture_output=True)
        print(f"Last generated commit: {last_gen_commit[:7]} {last_gen_msg}")
    elif remote_exists:
         print("Last generated commit: None found")

    if has_field_patches:
        if pending_commits:
            print(f"Pending field patches: {len(pending_commits)}")
            print("\nField patch commits:")
            for commit in pending_commits:
                print(f"  {commit}")
            print("\nChanged files:")
            for f in changed_files:
                print(f"  {f}")
        else:
             print("Pending field patches: Branch exists but no generated commit marker found. Entire history is treated as suspicious.")

        if not allow_overwrite:
            print("\nNormal publish would abort to avoid overwriting field patches." if not push else "\nERROR: Normal publication is aborted to avoid overwriting field patches.")
            return
        else:
            print(f"\nWARNING: Overwriting field patches because --allow-overwrite-field-patches was specified.")
            print(f"Reason: {overwrite_reason}")
    else:
        if remote_exists:
            print("Pending field patches: 0")
        print("\nNormal publish would proceed." if not push else "")


    worktree_dir = f".worktree-{bundle_name}"

    try:
        if os.path.exists(worktree_dir):
            shutil.rmtree(worktree_dir)

        if remote_exists:
            print(f"Branch {target_branch} exists. Checking out.")
            run_cmd(["git", "worktree", "add", worktree_dir, target_branch])
        else:
            print(f"Branch {target_branch} does not exist. Creating as orphan.")
            # Remove worktree references if it was previously failed
            run_cmd(["git", "worktree", "prune"], check=False)
            run_cmd(["git", "branch", "-D", target_branch], check=False)
            run_cmd(["git", "worktree", "add", "--detach", worktree_dir])
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

Generated-by: skill-bundle-publisher
Bundle: {bundle_name}
Output-branch: {target_branch}
Source-branch: main
Source-commit: {source_commit}
Bundle-definition: {source_bundle_def}"""

            if allow_overwrite and has_field_patches:
                commit_msg += f"\nOverwrite-field-patches: yes\nOverwrite-reason: {overwrite_reason}"

            if push:
                run_cmd(["git", "commit", "-m", commit_msg], cwd=worktree_dir)
                print(f"Pushing {target_branch}...")
                run_cmd(["git", "push", "--force", "origin", target_branch] if allow_overwrite else ["git", "push", "origin", target_branch], cwd=worktree_dir)
                print(f"Successfully published {bundle_name} to {target_branch}.")
            else:
                print(f"Dry run: Would commit and push {bundle_name} to {target_branch}.")
                print(f"Commit message would be:\n{commit_msg}")

    finally:
        # Cleanup worktree
        if os.path.exists(worktree_dir):
            try:
                run_cmd(["git", "worktree", "remove", "--force", worktree_dir], check=False)
            except:
                pass
            try:
                shutil.rmtree(worktree_dir)
            except:
                pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Publish bundle branches")
    parser.add_argument("--bundles-out", required=True, help="Directory containing generated bundles")
    parser.add_argument("--push", action="store_true", help="Actually push changes to remote")
    parser.add_argument("--allow-overwrite-field-patches", action="store_true", help="Allow overwriting pending field patches")
    parser.add_argument("--overwrite-reason", type=str, help="Reason for overwriting field patches")

    args = parser.parse_args()

    bundles_out = args.bundles_out
    push = args.push
    allow_overwrite = args.allow_overwrite_field_patches
    overwrite_reason = args.overwrite_reason

    if allow_overwrite:
        if not push:
            print("Error: --allow-overwrite-field-patches requires --push")
            sys.exit(1)
        if not overwrite_reason:
            print("Error: --allow-overwrite-field-patches requires --overwrite-reason")
            sys.exit(1)

    if not push:
        print("Running in DRY RUN mode. Use --push to actualize changes.")

    if not os.path.exists(bundles_out):
        print(f"Error: Directory {bundles_out} does not exist.")
        sys.exit(1)

    for item in os.listdir(bundles_out):
        bundle_dir = os.path.join(bundles_out, item)
        if os.path.isdir(bundle_dir):
            publish_bundle(bundle_dir, push, allow_overwrite, overwrite_reason)

if __name__ == "__main__":
    main()
