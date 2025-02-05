#!/usr/bin/python3
import requests
import re
import os
import sys
import argparse
"""
./script.py commits --start 2023-01-01 --end 2023-01-31
./script.py issues --start 2023-01-01 --end 2023-01-31
./script.py pulls --start 2023-01-01 --end 2023-01-31

"""
# Hardcoded repository (update this value as needed)
repo = "octocat/Hello-World"

parser = argparse.ArgumentParser(description="GitHub Repository Report")
parser.add_argument("action", choices=["commits", "issues", "pulls"],
                    help="Select action: commits, issues, or pulls")
parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
args = parser.parse_args()

# Get the GitHub token from ~/.gitautomation
token_file = os.path.expanduser('~/.gitautomation')
with open(token_file, 'r') as f:
    token = f.read().strip()

# Convert dates to ISO 8601 format
start = args.start + "T00:00:00Z"
end = args.end + "T23:59:59Z"
headers = {'Authorization': f'Bearer {token}'}

if args.action == "commits":
    url = f"https://api.github.com/repos/{repo}/commits?since={start}&until={end}"
    response = requests.get(url, headers=headers)
    commits = response.json()
    if isinstance(commits, dict) and commits.get("message"):
        print("Error:", commits["message"])
        sys.exit(1)
    for commit in commits:
        title = commit['commit']['message'].split('\n')[0]
        author = commit['commit']['author']['name']
        issue_numbers = re.findall(r'#(\d+)', commit['commit']['message'])
        issues_str = ", ".join(issue_numbers) if issue_numbers else "None"
        print("Commit Title:", title)
        print("Author:", author)
        print("Issue #:", issues_str)
        print("--------------------------------------")

elif args.action == "issues":
    url = f"https://api.github.com/repos/{repo}/issues?state=all&since={start}"
    response = requests.get(url, headers=headers)
    issues = response.json()
    if isinstance(issues, dict) and issues.get("message"):
        print("Error:", issues["message"])
        sys.exit(1)
    for issue in issues:
        created = issue.get('created_at', '')
        if created >= start and created <= end:
            print("Issue Number:", issue['number'])
            print("Title:", issue['title'])
            print("Body:", issue['body'])
            print("--------------------------------------")

elif args.action == "pulls":
    url = f"https://api.github.com/repos/{repo}/pulls?state=closed&sort=updated"
    response = requests.get(url, headers=headers)
    pulls = response.json()
    if isinstance(pulls, dict) and pulls.get("message"):
        print("Error:", pulls["message"])
        sys.exit(1)
    for pr in pulls:
        merged_at = pr.get('merged_at')
        if merged_at and merged_at >= start and merged_at <= end:
            title = pr['title']
            author = pr['user']['login']
            date = pr['merged_at']
            body = pr.get('body') or ""
            print("PR Title:", title)
            print("Author:", author)
            print("Merged at:", date)
            print("Body:", body)
            m = re.search(r"##Fix List Visability(.*?)($|\n##)", body, re.DOTALL)
            if m:
                section = m.group(1)
                m2 = re.search(r"####Select on:(.*)", section, re.DOTALL)
                if m2:
                    fix_list_text = m2.group(1).strip()
                    items = re.split(r'\n|-', fix_list_text)
                    items = [item.strip() for item in items if item.strip()]
                    print("Fix List Items:")
                    for item in items:
                        print(item)
                else:
                    print("No fix list items found.")
            else:
                print("No fix list section found.")
            print("--------------------------------------")