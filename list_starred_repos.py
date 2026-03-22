"""
list_starred_repos.py

Fetches and lists all GitHub repositories starred by the authenticated user.
Equivalent to: gh api user/starred --paginate --jq '.[].full_name'

Usage:
    python list_starred_repos.py [--token TOKEN] [--output OUTPUT]

    TOKEN  : GitHub personal access token (or set GITHUB_TOKEN env var)
    OUTPUT : Optional output file path (default: prints to stdout)
"""

import argparse
import os
import sys

import requests


def get_starred_repos(token):
    """Fetch all starred repositories for the authenticated GitHub user."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    repos = []
    page = 1

    while True:
        url = "https://api.github.com/user/starred"
        params = {"per_page": 100, "page": page}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        page_data = response.json()
        if not page_data:
            break

        for repo in page_data:
            repos.append(repo["full_name"])

        # Check for next page via Link header
        link_header = response.headers.get("Link", "")
        if 'rel="next"' not in link_header:
            break

        page += 1

    return repos


def main():
    parser = argparse.ArgumentParser(
        description="List all GitHub repositories starred by the authenticated user."
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (overrides GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token:
        print(
            "Error: GitHub token required. Use --token or set GITHUB_TOKEN env var.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        repos = get_starred_repos(token)
    except requests.RequestException as exc:
        print(f"Error fetching starred repositories: {exc}", file=sys.stderr)
        sys.exit(1)

    output = "\n".join(repos)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output + "\n")
        print(f"Starred repositories written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
