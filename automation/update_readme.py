"""End-to-end update entry point for the profile README."""

from __future__ import annotations

import argparse
import os
import sys

from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.classify_repositories import classify_repositories
from automation.fetch_repositories import fetch_repositories, load_settings
from automation.generate_sections import build_readme
from automation.generate_statistics import build_statistics
from automation.utils import CONFIG_DIR, ROOT, load_json, save_json


def orchestrate(owner: str | None = None, token: str | None = None) -> str:
    settings = load_settings()
    profile = settings.get("profile", {})
    github = settings.get("github", {})
    repository_owner = owner or profile.get("owner") or os.environ.get("GITHUB_OWNER") or "hijbullahx"
    api_token = token or os.environ.get("GITHUB_TOKEN") or profile.get("token")

    repositories = fetch_repositories(
        repository_owner,
        token=api_token,
        include_archived=bool(github.get("include_archived", False)),
        include_forks=bool(github.get("include_forks", False)),
    )
    rules = load_json(CONFIG_DIR / "categories.json", default={})
    classification = classify_repositories(repositories, rules)
    save_json(ROOT / ".cache" / "profile" / "repositories.json", {"owner": repository_owner, "repositories": repositories})
    save_json(ROOT / ".cache" / "profile" / "classified_repositories.json", classification)
    save_json(ROOT / ".cache" / "profile" / "statistics.json", build_statistics(classification, settings))
    save_json(ROOT / ".cache" / "profile" / "cards.json", {"count": len(classification.get("repositories", []))})
    readme = build_readme()
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    return readme


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", default=None, help="GitHub owner or organization to scan.")
    parser.add_argument("--token", default=None, help="GitHub API token for higher rate limits.")
    args = parser.parse_args()
    readme = orchestrate(owner=args.owner, token=args.token)
    print(f"Generated README with {len(readme.splitlines())} lines")


if __name__ == "__main__":
    main()
