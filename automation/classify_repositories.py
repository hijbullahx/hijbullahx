"""Classify repositories into research-friendly portfolio categories."""

from __future__ import annotations

import argparse
from collections import defaultdict
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.utils import CONFIG_DIR, ROOT, load_json, repository_score, save_json


def load_repositories(path: Path) -> list[dict]:
    payload = load_json(path, default={})
    return payload.get("repositories", []) if isinstance(payload, dict) else []


def classify_repositories(repositories: list[dict], rules: dict) -> dict:
    enriched: list[dict] = []
    buckets: dict[str, list[dict]] = defaultdict(list)
    for repository in repositories:
        score, matched = repository_score(repository, rules)
        item = {**repository, "score": score, "categories": matched or ["Utilities"]}
        enriched.append(item)
        for category in item["categories"]:
            buckets[category].append(item)
    for category in buckets:
        buckets[category].sort(key=lambda item: (-item.get("score", 0), -item.get("stars", 0), item.get("name", "").lower()))
    enriched.sort(key=lambda item: (-item.get("score", 0), -item.get("stars", 0), item.get("name", "").lower()))
    return {"repositories": enriched, "categories": dict(sorted(buckets.items()))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(ROOT / ".cache" / "profile" / "repositories.json"), help="Input repository cache.")
    parser.add_argument("--output", default=str(ROOT / ".cache" / "profile" / "classified_repositories.json"), help="Output classification cache.")
    args = parser.parse_args()

    repositories = load_repositories(Path(args.input))
    rules = load_json(CONFIG_DIR / "categories.json", default={})
    classification = classify_repositories(repositories, rules)
    save_json(Path(args.output), classification)
    print(f"Classified {len(classification['repositories'])} repositories into {len(classification['categories'])} categories")


if __name__ == "__main__":
    main()
