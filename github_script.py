import argparse
import subprocess
import json

def fetch_commits(repo, owner, author=None):
    """Fetch all commits from a GitHub repository using `gh` CLI."""
    cmd = ["gh", "api", f"/repos/{owner}/{repo}/commits"]
    
    if author:
        cmd.append(f"--jq=[.[] | select(.commit.author.name==\"{author}\")]")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = json.loads(result.stdout)
        
        if not commits:
            print(f"No commits found for {'all contributors' if not author else author}.")
            return
        
        for commit in commits:
            sha = commit['sha']
            message = commit['commit']['message']
            commit_author = commit['commit']['author']['name']
            date = commit['commit']['author']['date']
            print(f"Commit: {sha}\nAuthor: {commit_author}\nDate: {date}\nMessage: {message}\n{'-'*40}")

    except subprocess.CalledProcessError as e:
        print(f"Error fetching commits: {e.stderr}")

def fetch_merged_issues(repo, owner):
    """Fetch all merged pull requests from a GitHub repository using `gh` CLI."""
    cmd = ["gh", "api", f"/repos/{owner}/{repo}/pulls?state=closed"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        prs = json.loads(result.stdout)

        merged_prs = [pr for pr in prs if pr.get("merged_at")]

        if not merged_prs:
            print("No merged issues found.")
            return
        
        for pr in merged_prs:
            title = pr["title"]
            author = pr["user"]["login"]
            merged_at = pr["merged_at"]
            body = pr["body"] or "No description provided."
            print(f"Title: {title}\nAuthor: {author}\nMerged At: {merged_at}\nDescription: {body}\n{'-'*60}")

    except subprocess.CalledProcessError as e:
        print(f"Error fetching merged issues: {e.stderr}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch commits and merged issues from a GitHub repository using `gh` CLI.")
    parser.add_argument("owner", help="GitHub username or organization name")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("--author", help="Filter commits by author (GitHub username)", default=None)
    parser.add_argument("--merged-issues", action="store_true", help="Fetch merged issues instead of commits")

    args = parser.parse_args()

    if args.merged_issues:
        fetch_merged_issues(args.repo, args.owner)
    else:
        fetch_commits(args.repo, args.owner, args.author)
