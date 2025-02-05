#!/usr/bin/python3
"""
GitHub Repository Report Script (Hardcoded Repository)

This script uses a hardcoded repository URL (set in the code below) so that you do not
need to provide the repository as input. It prompts the user for an action (commits, issues,
or pulls) and a date range (start and end dates). It then calls the appropriate GitHub API
endpoint and displays the results.

Repository is hardcoded below:
    repo = "octocat/Hello-World"  (Change this to your desired repository)

How to run:
1. Ensure you have a GitHub Personal Access Token saved in a file at ~/.gitautomation.
2. Make the script executable (optional):
      chmod +x script.py
3. Run the script:
      ./script.py
   Then follow the prompts for:
      - Action (commits, issues, or pulls)
      - Start date (YYYY-MM-DD)
      - End date (YYYY-MM-DD)
"""

import requests
import datetime
import json
import sys
import re
import os

def get_token():
    # Reads the GitHub token from ~/.gitautomation
    token_file = os.path.expanduser('~/.gitautomation')
    with open(token_file, 'r') as f:
        return f.read().strip()

def fetch_commits(token, repo, start, end):
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://api.github.com/repos/{repo}/commits?since={start}&until={end}"
    response = requests.get(url, headers=headers)
    commits = response.json()
    if isinstance(commits, dict) and commits.get("message"):
        print("Error:", commits["message"])
        return
    for commit in commits:
        title = commit['commit']['message'].split('\n')[0]
        author = commit['commit']['author']['name']
        # Find issue numbers (if any) in the commit message using a regex (e.g., "#123")
        issue_numbers = re.findall(r'#(\d+)', commit['commit']['message'])
        issue_str = ", ".join(issue_numbers) if issue_numbers else "None"
        print(f"Commit Title: {title}")
        print(f"Author: {author}")
        print(f"Issue #: {issue_str}")
        print("--------------------------------------")

def fetch_issues(token, repo, start, end):
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://api.github.com/repos/{repo}/issues?state=all&since={start}"
    response = requests.get(url, headers=headers)
    issues = response.json()
    if isinstance(issues, dict) and issues.get("message"):
        print("Error:", issues["message"])
        return
    # Filter issues by creation date (the API returns ISO 8601 dates)
    for issue in issues:
        created = issue.get('created_at', '')
        if created >= start and created <= end:
            print(f"Issue Number: {issue['number']}")
            print(f"Title: {issue['title']}")
            print(f"Body: {issue['body']}")
            print("--------------------------------------")

def fetch_pulls(token, repo, start, end):
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://api.github.com/repos/{repo}/pulls?state=closed&sort=updated"
    response = requests.get(url, headers=headers)
    pulls = response.json()
    if isinstance(pulls, dict) and pulls.get("message"):
        print("Error:", pulls["message"])
        return
    for pr in pulls:
        merged_at = pr.get('merged_at')
        if merged_at and merged_at >= start and merged_at <= end:
            title = pr['title']
            author = pr['user']['login']
            date = pr['merged_at']
            body = pr.get('body') or ""
            print(f"PR Title: {title}")
            print(f"Author: {author}")
            print(f"Merged at: {date}")
            print(f"Body: {body}")
            parse_fix_list(body)
            print("--------------------------------------")

def parse_fix_list(body):
    # Look for the section starting with "##Fix List Visability"
    m = re.search(r"##Fix List Visability(.*?)($|\n##)", body, re.DOTALL)
    if m:
        section = m.group(1)
        # Now search for "####Select on:" within that section.
        m2 = re.search(r"####Select on:(.*)", section, re.DOTALL)
        if m2:
            fix_list_text = m2.group(1).strip()
            # Split items by newline or dash; adjust as needed.
            items = re.split(r'\n|-', fix_list_text)
            items = [item.strip() for item in items if item.strip()]
            print("Fix List Items:")
            for item in items:
                print(item)
        else:
            print("No fix list items found.")
    else:
        print("No fix list section found.")

# --- Main script begins here (repository is hardcoded) ---
# Hardcoded repository (change as needed)
repo = "octocat/Hello-World"

print("Select action: commits, issues, or pulls")
action = input("Enter action: ").strip().lower()
if action not in ["commits", "issues", "pulls"]:
    print("Invalid action. Please enter 'commits', 'issues', or 'pulls'.")
    sys.exit(1)

start_date = input("Enter start date (YYYY-MM-DD): ").strip()
end_date = input("Enter end date (YYYY-MM-DD): ").strip()
# Dates are converted to ISO 8601 timestamps by appending time info
start = start_date + "T00:00:00Z"
end = end_date + "T23:59:59Z"

token = get_token()

if action == "commits":
    fetch_commits(token, repo, start, end)
elif action == "issues":
    fetch_issues(token, repo, start, end)
elif action == "pulls":
    fetch_pulls(token, repo, start, end)
