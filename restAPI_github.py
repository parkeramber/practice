import argparse
import requests

def fetch_commits(repo, owner, author=None, token=None):
    """Fetch all commits from a GitHub repository. Optionally filter by author."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"} if token else {}

    params = {"per_page": 100, "page": 1}
    if author:
        params["author"] = author  # Filter commits by author

    commits = []
    
    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch commits (Status Code {response.status_code})")
            print(response.json())
            break

        batch = response.json()
        if not batch:
            break  # No more commits to fetch

        commits.extend(batch)
        params["page"] += 1  # Move to the next page

    # Print commit details
    if not commits:
        print(f"No commits found for {'all contributors' if not author else author}.")
        return

    for commit in commits:
        sha = commit['sha']
        message = commit['commit']['message']
        commit_author = commit['commit']['author']['name'] if commit['commit']['author'] else "Unknown Author"
        date = commit['commit']['author']['date']
        print(f"Commit: {sha}\nAuthor: {commit_author}\nDate: {date}\nMessage: {message}\n{'-'*40}")

def fetch_merged_issues(repo, owner, token=None):
    """Fetch all merged issues (PRs that were merged) and display their body."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {"Authorization": f"token {token}"} if token else {}
    
    params = {"state": "closed", "per_page": 100, "page": 1}

    merged_issues = []

    while True:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch issues (Status Code {response.status_code})")
            print(response.json())
            break

        issues = response.json()
        if not issues:
            break  # No more issues to fetch

        for issue in issues:
            if "pull_request" in issue:  # Check if it's a PR (merged or closed)
                pr_url = issue["pull_request"]["url"]
                
                # Fetch the PR details
                pr_response = requests.get(pr_url, headers=headers)
                if pr_response.status_code == 200:
                    pr_data = pr_response.json()
                    
                    if pr_data.get("merged_at"):  # Check if PR was merged
                        merged_issues.append({
                            "title": issue["title"],
                            "body": issue["body"] or "No description provided.",
                            "author": issue["user"]["login"],
                            "merged_at": pr_data["merged_at"]
                        })

        params["page"] += 1  # Move to the next page

    # Print merged issues with body
    if not merged_issues:
        print("No merged issues found.")
        return

    for issue in merged_issues:
        print(f"Title: {issue['title']}")
        print(f"Author: {issue['author']}")
        print(f"Merged At: {issue['merged_at']}")
        print(f"Description: {issue['body']}\n{'-'*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch commits and merged issues from a GitHub repository.")
    parser.add_argument("owner", help="GitHub username or organization name")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("--author", help="Filter commits by author (GitHub username)", default=None)
    parser.add_argument("--token", help="GitHub personal access token (optional for private repos)", default=None)
    parser.add_argument("--merged-issues", action="store_true", help="Fetch merged issues instead of commits")

    args = parser.parse_args()

    if args.merged_issues:
        fetch_merged_issues(args.repo, args.owner, args.token)
    else:
        fetch_commits(args.repo, args.owner, args.author, args.token)
