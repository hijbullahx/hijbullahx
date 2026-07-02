"""Fetch public repositories and persist a normalized cache."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.utils import CONFIG_DIR, ROOT, github_paginate, load_json, normalize_repository, save_json


def load_settings() -> dict:
    return load_json(CONFIG_DIR / "settings.json", default={})


def fetch_repositories(owner: str, *, token: str | None = None, include_archived: bool = False, include_forks: bool = False) -> list[dict]:
    payload = github_paginate(f"/users/{owner}/repos", {"type": "public", "sort": "updated", "direction": "desc"}, token=token)
    repositories: list[dict] = []
    for repo in payload:
        if not isinstance(repo, dict):
            continue
        if repo.get("private"):
            continue
        if repo.get("archived") and not include_archived:
            continue
        if repo.get("fork") and not include_forks:
            continue
        repositories.append(normalize_repository(repo, token=token, owner=owner))
    return repositories


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=None, help="GitHub owner or organization to scan.")
    parser.add_argument("--token", default=None, help="GitHub API token for higher rate limits.")
    parser.add_argument("--output", default=str(ROOT / ".cache" / "profile" / "repositories.json"), help="Path to the cached repository snapshot.")
    args = parser.parse_args()

    settings = load_settings()
    profile = settings.get("profile", {})
    github = settings.get("github", {})
    owner = args.owner or profile.get("owner") or "hijbullahx"
    token = args.token or (profile.get("token") or "") or os.environ.get("GITHUB_TOKEN")

    repositories = fetch_repositories(
        owner,
        token=token,
        include_archived=bool(github.get("include_archived", False)),
        include_forks=bool(github.get("include_forks", False)),
    )

    output_path = Path(args.output)
    save_json(output_path, {"owner": owner, "repositories": repositories})
    print(f"Fetched {len(repositories)} repositories for {owner} -> {output_path}")


if __name__ == "__main__":
    main()
