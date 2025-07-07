import requests
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# -------- CONFIGURATION --------
load_dotenv()  # Load environment variables from .env file

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Set your token in the .env file
ORG_NAME = os.getenv("ORG_NAME")  # Set your org name in the .env file

if not GITHUB_TOKEN or not ORG_NAME:
    raise ValueError("Please set GITHUB_TOKEN and ORG_NAME in your .env file.")

BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}
DAYS = 30
# --------------------------------


def github_api_get(url, params=None, max_retries=5):
    """Make a GET request and handle rate limits."""
    for attempt in range(max_retries):
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 403 and "rate limit" in response.text.lower():
            reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(0, reset - int(time.time()) + 1)
            print(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue
        elif response.status_code in (500, 502, 503, 504):
            print(f"Server error {response.status_code}. Retrying after 10 seconds...")
            time.sleep(10)
            continue
        response.raise_for_status()
        remaining = int(response.headers.get("X-RateLimit-Remaining", 1))
        if remaining == 0:
            reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_time = max(0, reset - int(time.time()) + 1)
            print(f"Rate limit exhausted. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
        return response
    raise Exception("Max retries exceeded for GitHub API requests.")


def get_repos(org):
    """Get the list of repositories in the organization."""
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/orgs/{org}/repos"
        params = {"per_page": 100, "page": page}
        r = github_api_get(url, params)
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return [repo["name"] for repo in repos]


def get_commits(org, repo, since_iso):
    """Get all commits for a repo since given ISO date."""
    url = f"{BASE_URL}/repos/{org}/{repo}/commits"
    params = {"since": since_iso, "per_page": 100, "page": 1}
    all_commits = []
    while True:
        r = github_api_get(url, params)
        commits = r.json()
        if not commits:
            break
        all_commits.extend(commits)
        if len(commits) < 100:
            break
        params["page"] += 1
    return all_commits


def get_commit_stats(org, repo, sha):
    """Fetch stats (additions, deletions) for a specific commit."""
    url = f"{BASE_URL}/repos/{org}/{repo}/commits/{sha}"
    r = github_api_get(url)
    data = r.json()
    stats = data.get("stats", {})
    return stats.get("additions", 0), stats.get("deletions", 0)


def get_branches(org, repo):
    """Get all branches in the repo."""
    branches = []
    page = 1
    while True:
        url = f"{BASE_URL}/repos/{org}/{repo}/branches"
        params = {"per_page": 100, "page": page}
        r = github_api_get(url, params)
        batch = r.json()
        if not batch:
            break
        branches.extend(batch)
        page += 1
    return branches


def get_pull_requests_opened_since(org, repo, since_iso):
    """Count all PRs opened since the given ISO date."""
    prs_opened = 0
    page = 1
    while True:
        url = f"{BASE_URL}/repos/{org}/{repo}/pulls"
        params = {
            "state": "all",
            "sort": "created",
            "direction": "desc",
            "per_page": 100,
            "page": page,
        }
        r = github_api_get(url, params)
        pulls = r.json()
        if not pulls:
            break
        for pr in pulls:
            created_at = pr.get("created_at")
            if created_at and created_at >= since_iso:
                prs_opened += 1
            else:
                # Since PRs are sorted by created_at descending, we can stop early
                return prs_opened
        page += 1
    return prs_opened


def main():
    since = datetime.now() - timedelta(days=DAYS)
    since_iso = since.isoformat() + "Z"
    print(
        f"Counting commits, LOC changes, unique contributors, and PRs opened since: {since_iso}\n"
    )
    repos = get_repos(ORG_NAME)
    for repo in repos:
        commits = get_commits(ORG_NAME, repo, since_iso)
        total_add = 0
        total_del = 0
        contributors = set()
        for commit in commits:
            sha = commit["sha"]
            author = commit.get("author")
            if author and author.get("login"):
                contributors.add(author["login"])
            elif commit.get("commit", {}).get("author", {}).get("email"):
                contributors.add(commit["commit"]["author"]["email"])
            additions, deletions = get_commit_stats(ORG_NAME, repo, sha)
            total_add += additions
            total_del += deletions
        prs_opened = get_pull_requests_opened_since(ORG_NAME, repo, since_iso)
        print(
            f"{repo}: {len(commits)} commits, +{total_add} additions, -{total_del} deletions, {len(contributors)} unique contributors, {prs_opened} PRs opened in last {DAYS} days"
        )


if __name__ == "__main__":
    main()
