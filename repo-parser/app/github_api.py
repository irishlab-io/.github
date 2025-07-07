import requests
import time
from .config import GITHUB_TOKEN


def github_get(url, params=None):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    while True:
        resp = requests.get(url, headers=headers, params=params)
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 1))
        reset = int(resp.headers.get("X-RateLimit-Reset", 0))
        if remaining == 0:
            sleep_time = max(reset - int(time.time()), 1)
            print(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
            time.sleep(sleep_time)
            continue
        time.sleep(0.5)
        return resp


def get_repos(org):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
        resp = github_get(url)
        data = resp.json()
        if not data or resp.status_code != 200:
            break
        repos.extend([repo["name"] for repo in data])
        page += 1
    return repos


def get_commits(org, repo, since, until):
    commits = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{org}/{repo}/commits"
        params = {"since": since, "until": until, "per_page": 100, "page": page}
        resp = github_get(url, params)
        data = resp.json()
        if not data or resp.status_code != 200:
            break
        commits.extend(data)
        if len(data) < 100:
            break
        page += 1
    return commits


def get_commit_stats(org, repo, sha):
    url = f"https://api.github.com/repos/{org}/{repo}/commits/{sha}"
    resp = github_get(url)
    if resp.status_code != 200:
        return {}
    return resp.json().get("stats", {})
