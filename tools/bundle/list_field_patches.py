#!/usr/bin/env python3
"""
Script to list pending field patches on distribution branches.

Usage:
  python tools/bundle/list_field_patches.py --branch <branch-name>
  python tools/bundle/list_field_patches.py --all-dist-branches
"""
import sys
import subprocess
import json
import argparse

def run_cmd(cmd, check=True, capture_output=False):
    if capture_output:
        result = subprocess.run(cmd, check=check, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    subprocess.run(cmd, check=check)

def get_bundle_lock(branch):
    """Attempt to retrieve references/bundle-lock.json from the branch."""
    try:
        content = run_cmd(["git", "show", f"origin/{branch}:references/bundle-lock.json"], check=False, capture_output=True)
        if content:
            return json.loads(content)
    except Exception:
        pass
    return None

def check_branch(branch):
    print(f"\nBranch: {branch}")
    try:
        # Fetch branch
        run_cmd(["git", "fetch", "origin", branch], check=False, capture_output=True)

        commits_output = run_cmd(["git", "log", "--format=%H|%s", f"origin/{branch}"], check=False, capture_output=True)
        if not commits_output:
            print("  No commits found or branch does not exist on remote.")
            return

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
             print("  ERROR: Branch exists but no generated commit marker found. Entire history is treated as suspicious.")
             return

        last_gen_msg = run_cmd(["git", "log", "-1", "--format=%s", last_gen_commit_hash], check=False, capture_output=True)
        print(f"Last generated commit: {last_gen_commit_hash[:7]} {last_gen_msg}")

        # Try to parse source commit from message
        source_commit = "unknown"
        msg_body = run_cmd(["git", "log", "-1", "--format=%b", last_gen_commit_hash], check=False, capture_output=True)
        for line in msg_body.split('\n'):
             if line.startswith("Source-commit: "):
                 source_commit = line.split("Source-commit: ")[1].strip()
                 break
        print(f"Source commit: {source_commit[:7] if source_commit != 'unknown' else 'unknown'}")

        # Get pending commits
        pending_commits_output = run_cmd(["git", "log", "--format=%h|%an|%ad|%s", "--date=short", f"{last_gen_commit_hash}..origin/{branch}"], check=False, capture_output=True)
        pending_commits = [line for line in pending_commits_output.strip().split('\n') if line]

        if not pending_commits:
            print("\nNo pending field patches.")
            return

        print(f"\nPending field patch commits: {len(pending_commits)}")

        lock_data = get_bundle_lock(branch)
        mappings = lock_data.get("included", []) if lock_data else []
        file_map = {m["to"]: m["from"] for m in mappings if "to" in m and "from" in m}

        for commit_line in pending_commits:
            parts = commit_line.split('|', 3)
            if len(parts) != 4: continue
            chash, author, date, subj = parts
            print(f"\n  {chash} {subj} ({author}, {date})")

            changed_files_output = run_cmd(["git", "show", "--name-only", "--format=", chash], check=False, capture_output=True)
            changed_files = [f for f in changed_files_output.strip().split('\n') if f]

            if changed_files:
                print("    Files:")
                for f in changed_files:
                    print(f"      {f}")

                print("    Backport candidates:")
                for f in changed_files:
                    # Match mapping
                    target = file_map.get(f)
                    if target:
                         print(f"      {f} -> {target}")
                    else:
                         print(f"      {f} -> (no mapping found)")

    except Exception as e:
         print(f"  Error processing branch: {e}")

def main():
    parser = argparse.ArgumentParser(description="List pending field patches on distribution branches.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--branch", type=str, help="Specific dist/* branch to check")
    group.add_argument("--all-dist-branches", action="store_true", help="Check all dist/* branches")

    args = parser.parse_args()

    if args.branch:
        if not args.branch.startswith("dist/"):
             print(f"Warning: {args.branch} does not start with 'dist/'. Proceeding anyway.")
        check_branch(args.branch)
    elif args.all_dist_branches:
        print("Fetching remote branches...")
        run_cmd(["git", "fetch", "origin"], check=False, capture_output=True)
        branches_output = run_cmd(["git", "ls-remote", "--heads", "origin", "refs/heads/dist/*"], check=False, capture_output=True)

        branches = []
        for line in branches_output.strip().split('\n'):
             if line:
                 parts = line.split('\t')
                 if len(parts) == 2:
                      ref = parts[1]
                      if ref.startswith("refs/heads/"):
                          branches.append(ref[len("refs/heads/"):])

        if not branches:
             print("No dist/* branches found on remote origin.")
             return

        for b in branches:
             check_branch(b)

if __name__ == "__main__":
    main()