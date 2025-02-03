#!/usr/bin/env python3
"""
GitHub Commits Fetcher Script with Interactive Login

This script logs into the GitHub API using your credentials and retrieves all commits
(including commit messages/bodies) from a specified repository on a particular date.

-----------------------------------------------------------
How to Run This Script:
-----------------------------------------------------------
1. Ensure you have Python 3 installed.
2. Install the required packages if you haven't already:
     pip install requests
3. Save this script as "github_commits.py" (or another name you prefer).
4. Open your terminal/command prompt and navigate to the directory where this script is located.
5. Run the script using a command similar to the following:
   
   python github_commits.py --repo owner/repo --date YYYY-MM-DD

   Example:
   python github_commits.py --repo octocat/Hello-World --date 2023-09-15

6. If you do not supply your GitHub username or token as command-line arguments,
   the script will prompt you to enter them interactively. The token is requested securely,
   so its input will not be displayed on the screen.

-----------------------------------------------------------
Notes:
- The repository should be provided in the format "owner/repo".
- Your GitHub personal access token must have permissions to access the repository.
- The date must be provided in the format YYYY-MM-DD.
"""

import requests      # To perform HTTP requests to the GitHub API.
import argparse      # To parse command-line arguments.
import datetime      # To work with dates.
import sys           # To exit in case of errors.
import getpass       # To securely prompt the user for the GitHub token.

def fetch_commits(username, token, owner, repo, date_str):
    """
    Fetch commits from the specified GitHub repository that occurred on the given date.

    Parameters:
        username (str): GitHub username.
        token (str): GitHub personal access token.
        owner (str): Owner of the repository.
        repo (str): Repository name.
        date_str (str): Date in YYYY-MM-DD format.

    Returns:
        A list of commit objects retrieved from the GitHub API.
    """
    # Convert the provided date string into a datetime object.
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        sys.exit("Invalid date format. Please use YYYY-MM-DD.")

    # Define the time window for fetching commits:
    # - 'since' marks the start of the day (in UTC) in ISO 8601 format.
    # - 'until' marks the start of the next day (covering the entire day).
    since = date_obj.isoformat() + "Z"  # Start of the day (UTC)
    until_date = date_obj + datetime.timedelta(days=1)
    until = until_date.isoformat() + "Z"  # Start of the next day (UTC)

    # Build the GitHub API URL for listing commits.
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    # Set query parameters: filter commits between 'since' and 'until' (up to 100 per page).
    params = {
        "since": since,
        "until": until,
        "per_page": 100  # Maximum commits per page.
    }
    
    # Use basic authentication with your GitHub username and personal access token.
    auth = (username, token)
    
    all_commits = []  # List to accumulate all fetched commits.
    page = 1  # Start with the first page.
    
    while True:
        # Update the page number in the parameters for each request.
        params["page"] = page
        response = requests.get(url, params=params, auth=auth)
        
        # Check if the API request was successful.
        if response.status_code != 200:
            sys.exit(f"Failed to fetch commits: {response.status_code} - {response.text}")
        
        commits = response.json()
        if not commits:
            # No further commits found; exit the pagination loop.
            break
        
        # Append commits from the current page.
        all_commits.extend(commits)
        page += 1  # Move on to the next page.
    
    return all_commits

def main():
    # Set up command-line argument parsing.
    parser = argparse.ArgumentParser(
        description="Fetch GitHub commits (with messages) for a specific date."
    )
    # Optional username; if not provided, the script will prompt for it.
    parser.add_argument("--username", help="Your GitHub username. If omitted, you'll be prompted.")
    # Optional token; if not provided, the script will prompt for it securely.
    parser.add_argument("--token", help="Your GitHub personal access token. If omitted, you'll be prompted.")
    # Required repository in the format "owner/repo".
    parser.add_argument("--repo", required=True, help="Repository in the format 'owner/repo'.")
    # Required date in the format "YYYY-MM-DD".
    parser.add_argument("--date", required=True, help="Date (YYYY-MM-DD) to fetch commits for.")
    
    args = parser.parse_args()

    # Prompt for the username if not provided via command-line.
    if not args.username:
        args.username = input("Enter your GitHub username: ")

    # Prompt for the token if not provided via command-line.
    if not args.token:
        args.token = getpass.getpass("Enter your GitHub token: ")

    # Validate and parse the repository argument into owner and repo name.
    if '/' not in args.repo:
        sys.exit("Invalid repository format. Please use 'owner/repo' format.")
    owner, repo = args.repo.split('/', 1)

    # Retrieve commits from the GitHub API using the supplied parameters.
    commits = fetch_commits(args.username, args.token, owner, repo, args.date)
    
    # Inform the user if no commits were found for the given date.
    if not commits:
        print(f"No commits found for {args.date} in {owner}/{repo}.")
        return
    
    # Loop over each commit and display its details.
    for commit in commits:
        # Extract commit details from the response.
        commit_info = commit.get("commit", {})
        author_info = commit_info.get("author", {})
        commit_message = commit_info.get("message", "")
        commit_author = author_info.get("name", "Unknown")
        commit_date = author_info.get("date", "Unknown")
        
        # Display the commit details.
        print(f"Author: {commit_author}")
        print(f"Date:   {commit_date}")
        print("Message:")
        print(commit_message)
        print("-" * 60)

# Run the main() function when the script is executed.
if __name__ == "__main__":
    main()
