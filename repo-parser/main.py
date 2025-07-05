import datetime
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("ORG_NAME")


def get_repos(org):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        resp = requests.get(url, headers=headers)
        data = resp.json()
        if not data or resp.status_code != 200:
            break
        repos.extend([repo["name"] for repo in data])
        page += 1
    return repos


def get_commit_stats(org, repo, since, until):
    url = f"https://api.github.com/repos/{org}/{repo}/commits"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    params = {"since": since, "until": until, "per_page": 100}
    commit_count = 0
    additions = 0
    deletions = 0
    contributors = set()
    page = 1
    while True:
        params["page"] = page
        resp = requests.get(url, headers=headers, params=params)
        commits = resp.json()
        if not commits or resp.status_code != 200:
            break
        for commit in commits:
            sha = commit["sha"]
            author = commit.get("author")
            if author and author.get("login"):
                contributors.add(author["login"])
            commit_url = f"https://api.github.com/repos/{org}/{repo}/commits/{sha}"
            commit_resp = requests.get(commit_url, headers=headers)
            if commit_resp.status_code != 200:
                continue
            stats = commit_resp.json().get("stats", {})
            additions += stats.get("additions", 0)
            deletions += stats.get("deletions", 0)
            commit_count += 1
        if len(commits) < 100:
            break
        page += 1
    return commit_count, additions, deletions, len(contributors)


if __name__ == "__main__":
    today = datetime.datetime.now().replace(day=1)
    last_month_end = today - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    since = last_month_start.isoformat() + "Z"
    until = last_month_end.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    repos = get_repos(ORG_NAME)
    for repo in repos:
        commit_count, additions, deletions, unique_contributors = get_commit_stats(
            ORG_NAME, repo, since, until
        )
        print(
            f"{repo}: {commit_count} commits, {additions} additions, {deletions} deletions, {unique_contributors} unique contributors"
        )
