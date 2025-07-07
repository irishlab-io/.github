import pytest
import sys
from unittest.mock import patch

# Import the script as a module
import importlib.util

SCRIPT_PATH = "get_org_repo_commits_and_loc_changes_last_90_days.py"

spec = importlib.util.spec_from_file_location("org_stats", SCRIPT_PATH)
org_stats = importlib.util.module_from_spec(spec)
sys.modules["org_stats"] = org_stats
spec.loader.exec_module(org_stats)


@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "dummy")
    monkeypatch.setenv("ORG_NAME", "dummyorg")


def test_get_repos():
    mock_repos = [
        {"name": "repo1"},
        {"name": "repo2"},
    ]
    with patch.object(org_stats, "github_api_get") as mock_get:
        mock_get.return_value.json.side_effect = [mock_repos, []]
        repos = org_stats.get_repos("dummyorg")
        assert repos == ["repo1", "repo2"]


def test_get_commits():
    mock_commits_page1 = [
        {
            "sha": "a1",
            "author": {"login": "alice"},
            "commit": {"author": {"email": "alice@example.com"}},
        },
        {
            "sha": "b2",
            "author": {"login": "bob"},
            "commit": {"author": {"email": "bob@example.com"}},
        },
    ]
    with patch.object(org_stats, "github_api_get") as mock_get:
        mock_get.return_value.json.side_effect = [mock_commits_page1, []]
        commits = org_stats.get_commits("dummyorg", "repo1", "2024-01-01T00:00:00Z")
        assert commits == mock_commits_page1


def test_get_commit_stats():
    mock_commit = {"stats": {"additions": 42, "deletions": 13}}
    with patch.object(org_stats, "github_api_get") as mock_get:
        mock_get.return_value.json.return_value = mock_commit
        adds, dels = org_stats.get_commit_stats("dummyorg", "repo1", "a1")
        assert adds == 42
        assert dels == 13


def test_get_pull_requests_opened_since():
    # PR 1 - within range, PR 2 - within range, PR 3 - out of range
    mock_prs_page1 = [
        {"created_at": "2025-06-20T12:00:00Z"},
        {"created_at": "2025-05-15T10:00:00Z"},
        {"created_at": "2024-01-01T00:00:00Z"},  # out of range
    ]
    with patch.object(org_stats, "github_api_get") as mock_get:
        mock_get.return_value.json.side_effect = [mock_prs_page1, []]
        prs_opened = org_stats.get_pull_requests_opened_since(
            "dummyorg", "repo1", "2025-05-01T00:00:00Z"
        )
        assert prs_opened == 2


def test_full_flow(monkeypatch):
    # Compose mock returns for the sequence of function calls in main
    mock_repos = [{"name": "repo1"}]
    mock_commits = [
        {
            "sha": "a1",
            "author": {"login": "alice"},
            "commit": {"author": {"email": "alice@example.com"}},
        },
        {
            "sha": "b2",
            "author": {"login": "bob"},
            "commit": {"author": {"email": "bob@example.com"}},
        },
    ]
    mock_commit_stats = [
        {"stats": {"additions": 10, "deletions": 2}},
        {"stats": {"additions": 5, "deletions": 1}},
    ]
    mock_prs = [
        {"created_at": "2025-07-03T12:00:00Z"},
        {"created_at": "2025-06-10T08:00:00Z"},
    ]

    with (
        patch.object(org_stats, "get_repos", return_value=["repo1"]),
        patch.object(org_stats, "get_commits", return_value=mock_commits),
        patch.object(org_stats, "get_commit_stats", side_effect=[(10, 2), (5, 1)]),
        patch.object(org_stats, "get_pull_requests_opened_since", return_value=2),
        patch("builtins.print") as mock_print,
    ):
        org_stats.main()
        mock_print.assert_any_call(
            "repo1: 2 commits, +15 additions, -3 deletions, 2 unique contributors, 2 PRs opened in last 90 days"
        )
