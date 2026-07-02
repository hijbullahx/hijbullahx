"""Derive high-signal metrics from the classified repository set."""

from __future__ import annotations

from collections import Counter
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.utils import CONFIG_DIR, ROOT, clamp_list, load_json, relative_age, render_markdown_table, save_json


def build_statistics(payload: dict, settings: dict) -> dict:
    repositories = payload.get("repositories", []) if isinstance(payload, dict) else []
    categories = payload.get("categories", {}) if isinstance(payload, dict) else {}

    language_counts = Counter(repo.get("language") or "Unknown" for repo in repositories)
    topic_counts = Counter(topic.lower() for repo in repositories for topic in repo.get("topics", []) or [])
    category_counts = Counter(category for category, values in categories.items() for _ in values)
    starred = sorted(repositories, key=lambda item: (-item.get("stars", 0), -item.get("forks", 0), item.get("name", "").lower()))
    recent = sorted(repositories, key=lambda item: item.get("updated_at", ""), reverse=True)

    research_categories = {"AI", "Machine Learning", "Computer Vision", "Medical AI", "Research", "Research Papers"}
    research_repositories = [repo for repo in repositories if research_categories.intersection(set(repo.get("categories", [])))]
    production_categories = {"Backend", "Production", "Automation", "Utilities", "IoT"}
    production_repositories = [repo for repo in repositories if production_categories.intersection(set(repo.get("categories", [])))]

    top_languages = clamp_list((name for name, _ in language_counts.most_common(8)), 8)
    top_topics = clamp_list((name for name, _ in topic_counts.most_common(10)), 10)

    summary_rows = [
        ["Metric", "Value", "Meaning"],
        ["Public repositories", str(len(repositories)), "Live GitHub portfolio surface"],
        ["Research repositories", str(len(research_repositories)), "Vision, medical AI, and research tooling"],
        ["Production repositories", str(len(production_repositories)), "Backend, automation, and deployable systems"],
        ["Top language", top_languages[0] if top_languages else "Unknown", "Primary implementation stack"],
        ["Most recent update", relative_age(recent[0].get("updated_at")) if recent else "Unknown", "Maintenance signal"],
    ]

    return {
        "summary": summary_rows,
        "language_counts": language_counts.most_common(12),
        "topic_counts": topic_counts.most_common(12),
        "category_counts": category_counts.most_common(12),
        "top_languages": top_languages,
        "top_topics": top_topics,
        "top_starred": starred[:8],
        "recent": recent[:8],
        "repository_count": len(repositories),
        "research_count": len(research_repositories),
        "production_count": len(production_repositories),
    }


def main() -> None:
    payload = load_json(ROOT / ".cache" / "profile" / "classified_repositories.json", default={})
    settings = load_json(CONFIG_DIR / "settings.json", default={})
    statistics = build_statistics(payload, settings)
    output_path = ROOT / ".cache" / "profile" / "statistics.json"
    save_json(output_path, statistics)
    print(f"Derived statistics for {statistics['repository_count']} repositories")
    print(render_markdown_table(statistics["summary"]))


if __name__ == "__main__":
    main()
