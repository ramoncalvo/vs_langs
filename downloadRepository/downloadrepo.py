#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

def parse_repos(file_path):
    """Parse the repository information from a file."""
    repos = {}
    current_repo = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("-"):
                try:
                    # Use maxsplit=1 to ensure only the first colon is split
                    repo_name, repo_url = line.split(":", 1)
                    repo_name = repo_name.strip(" -")
                    repos[repo_name] = {"url": repo_url.strip(), "branch": None}
                    current_repo = repo_name
                except ValueError:
                    print(f"[ERROR] Invalid line format: {line}")
                    continue
            elif current_repo and line.startswith("- branch:"):
                branch = line.split(":", 1)[1].strip()
                repos[current_repo]["branch"] = branch
    return repos

def clone_repo(repo_name, repo_info, local_dir):
    """Clone a single repository."""
    repo_url = repo_info["url"]
    branch = repo_info["branch"]
    clone_dir = os.path.join(local_dir, repo_name)

    print(f"\nCloning {repo_name} from {repo_url} to {clone_dir}...")
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists. Skipping...")
        return

    cmd = ["git", "clone", repo_url, clone_dir]
    if branch:
        cmd.extend(["-b", branch])

    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully cloned {repo_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone {repo_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Clone repositories from a specified file.")
    parser.add_argument("--file", type=str, required=True, help="Path to the file containing repository information.")
    parser.add_argument("--all", type=bool, default=False, help="Whether to clone all repositories (default: False).")
    parser.add_argument("--one", type=str, help="Name of a single repository to clone.")
    parser.add_argument("--localdir", type=str, required=True, help="Local directory to clone repositories into.")
    args = parser.parse_args()

    # Parse the repository file
    if not os.path.exists(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    repos = parse_repos(args.file)
    if not repos:
        print(f"[ERROR] No repositories found in file: {args.file}")
        sys.exit(1)

    os.makedirs(args.localdir, exist_ok=True)

    if args.all:
        # Clone all repositories
        for repo_name, repo_info in repos.items():
            clone_repo(repo_name, repo_info, args.localdir)
    elif args.one:
        # Clone a single repository
        if args.one in repos:
            clone_repo(args.one, repos[args.one], args.localdir)
        else:
            print(f"[ERROR] Repository '{args.one}' not found in file: {args.file}")
    else:
        print("[ERROR] Specify either --all=true or --one=<repo_name>.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    