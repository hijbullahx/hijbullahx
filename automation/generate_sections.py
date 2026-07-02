"""Compose the profile README from templates, metrics, and live data."""

from __future__ import annotations

import sys

from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.generate_cards import build_cards
from automation.utils import CONFIG_DIR, ROOT, build_widget_url, load_json, read_text, render_markdown_table


def build_who_am_i(settings: dict) -> str:
    profile = settings.get("profile", {})
    display_name = profile.get("display_name", "Md. Taher Bin Omar Hijbullah")
    brand = profile.get("brand", "HIJBULLAH AI LAB")
    role = profile.get("role", "AI Research Engineer")
    tagline = profile.get("tagline", "Computer vision, autonomous systems, backend engineering, and applied research.")
    position = profile.get("current_position", "Final-year Computer Science & Engineering student focused on production AI systems.")
    return (
        "## Who I Am\n\n"
        f"{display_name} builds under {brand} as a {role}. {tagline} {position} "
        "The profile is intentionally positioned around engineering output: research systems, reproducible experiments, and production software that can stand in front of labs, recruiters, and collaborators with equal confidence."
    )


def build_current_research(settings: dict) -> str:
    vision = settings.get("profile", {}).get("vision", [])
    research_items = vision or [
        "Computer Vision",
        "Autonomous Systems",
        "Intelligent Transportation",
        "Medical AI",
        "Robotics",
        "Open Source AI",
    ]
    bullets = "\n".join(f"- {item}" for item in research_items)
    return (
        "## Current Research\n\n"
        f"{bullets}\n\n"
        "The live portfolio surface is tuned to these areas so the profile reads like a research lab rather than a student snapshot."
    )


def build_live_mission_status(statistics: dict) -> str:
    summary = statistics.get("summary", [])
    rows = [["Area", "Focus", "Status"]]
    if summary:
        rows.extend(
            [
                ["Vision Systems", "Detection, tracking, and scene understanding", "Active"],
                ["Research Engineering", "Automation, analysis, and reproducibility", "Active"],
                ["Backend Platforms", "APIs, data models, and operational tooling", "Active"],
                ["IoT Systems", "Embedded sensing and automation", "Ongoing"],
                ["Open Source", "Public tools, reusable components, and workflows", "Active"],
            ]
        )
    return "## Live Mission Status\n\n" + render_markdown_table(rows)


def build_auto_repository_gallery(statistics: dict) -> str:
    top_languages = statistics.get("top_languages", [])
    top_topics = statistics.get("top_topics", [])
    language_line = ", ".join(top_languages[:6]) if top_languages else "Auto-detected from live repository metadata"
    topic_line = ", ".join(top_topics[:6]) if top_topics else "Repo topics, README text, stars, and recent activity"
    return (
        "## Auto Repository Gallery\n\n"
        "The gallery is driven by repository metadata, topics, stars, recent activity, README content, and language signals. Categories are assigned automatically so the profile stays current as the portfolio evolves.\n\n"
        f"- Dominant languages: {language_line}\n"
        f"- Dominant signals: {topic_line}"
    )


def build_technology_universe(settings: dict, statistics: dict) -> str:
    profile = settings.get("profile", {})
    categories = profile.get("vision", [])
    category_line = ", ".join(categories) if categories else "Programming languages, frameworks, data stores, AI tooling, cloud, DevOps, and research tools"
    return (
        "## Technology Universe\n\n"
        "![Technology matrix](assets/grid.svg)\n\n"
        f"The stack is organized by function, not by badge clutter. Core focus areas: {category_line}.\n\n"
        "This layout keeps the profile readable on desktop and mobile while still signaling breadth across languages, frameworks, databases, AI, cloud, DevOps, operating systems, and research tooling."
    )


def build_github_analytics(settings: dict) -> str:
    owner = settings.get("profile", {}).get("owner", "hijbullahx")
    return (
        "## GitHub Analytics\n\n"
        f"<div align=\"center\">\n  <img src=\"https://github-readme-stats.vercel.app/api?username={owner}&show_icons=true&theme=transparent&title_color=00E5FF&text_color=E5EEF7&icon_color=4DA3FF&hide_border=true&count_private=true\" height=\"180\" alt=\"GitHub stats\" />\n  <img src=\"https://github-readme-stats.vercel.app/api/top-langs/?username={owner}&layout=compact&theme=transparent&title_color=00E5FF&text_color=E5EEF7&hide_border=true\" height=\"180\" alt=\"Top languages\" />\n</div>\n\n"
        f"<div align=\"center\">\n  <img src=\"https://github-readme-activity-graph.vercel.app/graph?username={owner}&theme=github-compact&hide_border=true&bg_color=0B1020&color=E5EEF7&line=00E5FF&point=7C3AED\" alt=\"Contribution graph\" />\n</div>"
    )


def build_research_metrics(statistics: dict) -> str:
    rows = statistics.get("summary", [])
    body_rows = rows[1:] if len(rows) > 1 else []
    table = render_markdown_table([["Metric", "Value", "Meaning"], *body_rows]) if body_rows else ""
    return (
        "## Research Metrics\n\n"
        "The automation pipeline converts portfolio data into high-signal metrics that matter to recruiters, research labs, and engineering teams: production-readiness, active maintenance, project diversity, research intensity, and documentation quality.\n\n"
        f"{table}"
    )


def build_roadmap() -> str:
    return (
        "## Roadmap\n\n"
        "- Expand the research surface with papers, benchmarks, and experimental notebooks.\n"
        "- Keep the repository intelligence pipeline deterministic and easy to audit.\n"
        "- Grow reusable modules for computer vision, backend APIs, and automation.\n"
        "- Add more public demonstrations that combine engineering quality with research depth."
    )


def build_lets_build_together() -> str:
    return (
        "## Let's Build Together\n\n"
        "This profile is designed for collaboration with open source maintainers, research labs, startup teams, and graduate programs that care about rigor. If you are looking for someone who can move between research, deployment, and product thinking, this profile is structured to make that clear."
    )


def build_documentation_appendix() -> str:
    return (
        "## Architecture Explanation\n\n"
        "The repository is split into four layers: live data ingestion, classification, presentation generation, and scheduled publication. GitHub API data is pulled into the automation scripts, categorized by topic and content signals, transformed into project cards and metrics, and then written back into the profile README by GitHub Actions.\n\n"
        "## Setup Guide\n\n"
        "1. Set the GitHub repository owner in `config/settings.json` if you are not using the default profile account.\n"
        "2. Add any optional widget usernames, RSS URLs, or social links to the configuration files.\n"
        "3. Run `python automation/update_readme.py` locally to generate a fresh README snapshot.\n"
        "4. Commit the result or let the scheduled workflow update it automatically.\n\n"
        "## Installation Guide\n\n"
        "The automation layer only depends on Python 3.10+ and the standard library. No external packages are required for the core generator, which keeps the workflow lightweight and fast.\n\n"
        "```bash\npython automation/update_readme.py\n```\n\n"
        "## Customization Guide\n\n"
        "Update `config/categories.json` to shift category weights, `config/featured.json` to change spotlight logic, and `config/theme.json` to retune color and spacing decisions. The SVG assets are intentionally modular, so they can be replaced one by one without breaking the rest of the profile.\n\n"
        "## Deployment Guide\n\n"
        "The GitHub Action in `.github/workflows/update-profile.yml` runs on a schedule and on demand. It fetches public repositories, classifies them, regenerates the README, and commits changes only when the generated output is different.\n\n"
        "## GitHub Actions Documentation\n\n"
        "The workflow is designed for reliability over complexity. It uses `contents: write`, scheduled triggers, manual dispatch, a cache directory for API responses, and a conditional commit step so empty runs do not create noise.\n\n"
        "## Maintenance Guide\n\n"
        "- Review the category rules when new project types are added.\n"
        "- Refresh optional widget usernames if external services change.\n"
        "- Keep the README copy aligned with the actual direction of the lab.\n"
        "- Let the workflow handle routine updates instead of editing the generated sections by hand.\n\n"
        "## Troubleshooting Guide\n\n"
        "- If the workflow cannot reach the GitHub API, check the token and rate limit behavior first.\n"
        "- If a repository is missing from the profile, verify it is public and not archived.\n"
        "- If a section looks empty, confirm the configuration file includes the relevant optional data.\n"
        "- If the SVGs do not render, make sure the files are committed and referenced with the correct relative path.\n\n"
        "## Scaling Suggestions\n\n"
        "- Split larger experiments into separate repositories and let the classifier surface them automatically.\n"
        "- Add more topic rules instead of manually curating project order.\n"
        "- Keep generated content deterministic so the profile remains trustable over time.\n"
        "- Use README sections as a living operating system for the lab instead of a static bio.\n\n"
        "## Future Improvements\n\n"
        "- Add paper citation parsing for research repositories.\n"
        "- Add release intelligence so recent versioned work becomes more visible.\n"
        "- Expand widget configuration for WakaTime, Spotify, LeetCode, Medium, Dev.to, and RSS modules.\n"
        "- Generate per-project spotlight SVGs when a repository crosses defined thresholds.\n\n"
        "## Folder Structure\n\n"
        "```text\nREADME.md\nassets/\n  hero.svg\n  footer.svg\n  wave.svg\n  divider.svg\n  particles.svg\n  grid.svg\n  matrix.svg\n  neural-network.svg\n  research.svg\n  timeline.svg\nautomation/\n  fetch_repositories.py\n  classify_repositories.py\n  generate_cards.py\n  generate_sections.py\n  generate_statistics.py\n  update_readme.py\n  utils.py\ntemplates/\n  hero.md\n  projects.md\n  stats.md\n  footer.md\n  timeline.md\n  readme_template.md\nconfig/\n  settings.json\n  featured.json\n  categories.json\n  theme.json\n.github/\n  workflows/\n    update-profile.yml\n```\n\n"
        "## Workflow Diagram\n\n"
        "```mermaid\nflowchart TD\n  A[Schedule or manual trigger] --> B[Fetch public repositories]\n  B --> C[Download metadata, topics, languages, README snippets]\n  C --> D[Classify repositories by signals]\n  D --> E[Compute metrics and cards]\n  E --> F[Render README sections]\n  F --> G[Write README.md]\n  G --> H[Git diff check]\n  H --> I[Commit and push if changed]\n```"
    )


def build_live_widgets(settings: dict) -> str:
    widget_order = ["stats", "langs", "graph", "snake", "trophy", "waka", "spotify", "leetcode"]
    images = [build_widget_url(name, settings) for name in widget_order]
    images = [image for image in images if image]
    if not images:
        return "_No optional widgets configured yet._"
    return "\n".join(f'<img src="{url}" alt="Live widget" />' for url in images)


def build_timeline_section(settings: dict) -> str:
    template = read_text(ROOT / "templates" / "timeline.md", default="")
    return template.strip() or "## Research Timeline\n\nThe timeline will be populated by the automation pipeline."


def build_readme() -> str:
    settings = load_json(CONFIG_DIR / "settings.json", default={})
    payload = load_json(ROOT / ".cache" / "profile" / "classified_repositories.json", default={})
    statistics = load_json(ROOT / ".cache" / "profile" / "statistics.json", default={})
    repositories = payload.get("repositories", []) if isinstance(payload, dict) else []
    cards = build_cards(repositories[:12], columns=int(settings.get("layout", {}).get("gallery_columns", 2)))

    hero = read_text(ROOT / "templates" / "hero.md", default="")
    projects = read_text(ROOT / "templates" / "projects.md", default="")
    footer = read_text(ROOT / "templates" / "footer.md", default="")
    readme_template = read_text(ROOT / "templates" / "readme_template.md", default="")

    sections = [
        hero.strip(),
        build_who_am_i(settings),
        build_current_research(settings),
        build_live_mission_status(statistics),
        "## Featured Projects\n\n" + projects.strip() if projects.strip() else "## Featured Projects",
        cards,
        build_auto_repository_gallery(statistics),
        read_text(ROOT / "templates" / "timeline.md", default="").strip(),
        build_technology_universe(settings, statistics),
        build_github_analytics(settings),
        build_research_metrics(statistics),
        build_roadmap(),
        build_lets_build_together(),
        "## Live Widgets\n\n" + build_live_widgets(settings),
        footer.strip(),
        build_documentation_appendix(),
    ]
    body = "\n\n".join(section for section in sections if section)

    if readme_template.strip():
        return readme_template.replace("{{BODY}}", body).replace("{{WIDGETS}}", build_live_widgets(settings))

    statistics_summary = statistics.get("summary", [])
    summary_block = "\n".join(f"- {row[0]}: {row[1]} — {row[2]}" for row in statistics_summary[1:]) if statistics_summary else ""
    return f"# HIJBULLAH AI LAB\n\n{body}\n\n{summary_block}".strip() + "\n"


def main() -> None:
    output = build_readme()
    output_path = ROOT / "README.md"
    output_path.write_text(output, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
