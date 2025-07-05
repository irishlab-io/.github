from .github_api import get_repos, get_commits, get_commit_stats


def collect_repo_stats(org, since, until):
    repos = get_repos(org)
    results = []
    for repo in repos:
        commits = get_commits(org, repo, since, until)
        commit_count = 0
        additions = 0
        deletions = 0
        contributors = set()
        for commit in commits:
            sha = commit["sha"]
            author = commit.get("author")
            if author and author.get("login"):
                contributors.add(author["login"])
            stats = get_commit_stats(org, repo, sha)
            additions += stats.get("additions", 0)
            deletions += stats.get("deletions", 0)
            commit_count += 1
        results.append(
            {
                "repo": repo,
                "commits": commit_count,
                "additions": additions,
                "deletions": deletions,
                "contributors": len(contributors),
            }
        )
    return results
