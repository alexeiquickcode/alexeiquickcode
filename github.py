import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import requests

GH_USERNAME = "alexeiquickcode"
GH_TOKEN = os.getenv("GH_TOKEN")

TODAY = datetime.now(timezone.utc).date()
YESTERDAY = TODAY - timedelta(days=1)


def run_graphql_query(query, variables=None):
    headers = {"Authorization": f"bearer {GH_TOKEN}", "Content-Type": "application/json"}
    url = "https://api.github.com/graphql"
    json = {"query": query, "variables": variables or {}}
    response = requests.post(url, json=json, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GraphQL query failed: {response.text}")
    return response.json()


def get_repos():
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            name
            defaultBranchRef {
              name
            }
          }
        }
      }
    }
    """

    cursor = None
    repos = []

    while True:
        result = run_graphql_query(query, {"login": GH_USERNAME, "cursor": cursor})
        repo_nodes = result["data"]["user"]["repositories"]["nodes"]
        for node in repo_nodes:
            if node["defaultBranchRef"]:
                repos.append((node["name"], node["defaultBranchRef"]["name"]))

        page = result["data"]["user"]["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    return repos


def get_commit_stats(repo_name, branch):
    query = """
    query($owner: String!, $repo: String!, $branch: String!) {
      repository(owner: $owner, name: $repo) {
        ref(qualifiedName: $branch) {
          target {
            ... on Commit {
              history(first: 100) {
                totalCount
                nodes {
                  additions
                  deletions
                  author {
                    user {
                      login
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    result = run_graphql_query(
        query, {
            "owner": GH_USERNAME,
            "repo": repo_name,
            "branch": f"refs/heads/{branch}"
        }
    )

    nodes = (
        result.get("data", {}).get("repository", {}).get("ref", {}).get("target",
                                                                        {}).get("history", {})
    )

    commit_count = nodes.get("totalCount", 0)
    nodes = nodes.get("nodes", [])

    added = sum(
        n["additions"]
        for n in nodes
        if n.get("author", {}).get("user", {}).get("login") == GH_USERNAME
    )
    removed = sum(
        n["deletions"]
        for n in nodes
        if n.get("author", {}).get("user", {}).get("login") == GH_USERNAME
    )
    return added, removed, commit_count


def get_github_stats():
    total_added, total_removed, total_commits = 0, 0, 0
    repos = get_repos()
    for repo, branch in repos:
        try:
            added, removed, commits = get_commit_stats(repo, branch)
            total_added += added
            total_removed += removed
            total_commits += commits
        except Exception as e:
            print(f"Failed to fetch stats for {repo}: {e}")
    return {
        "github":
            {
                "added": total_added,
                "removed": total_removed,
                "commits": total_commits,
                "repos": len(repos)
            }
    }
