"""Compose the profile README from templates, metrics, and live data."""

from __future__ import annotations

import sys

from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.generate_cards import build_cards
from automation.utils import CONFIG_DIR, ROOT, build_widget_url, load_json, read_text, render_markdown_table, short_text


def build_hero(settings: dict) -> str:
    profile = settings.get("profile", {})
    display_name = profile.get("display_name", "Md. Taher Bin Omar Hijbullah")
    role = profile.get("role", "AI Research Engineer")
    tagline = profile.get("tagline", "Computer Vision • Autonomous Systems • Backend Engineering")
    mission = "Building production AI systems with research depth and startup-grade execution."
    return (
        "<div align=\"center\">\n\n"
        "<img src=\"assets/hero.svg\" width=\"100%\" alt=\"HIJBULLAH AI LAB hero\" />\n\n"
        f"# {display_name}\n\n"
        f"**{role}**\n\n"
        f"{tagline}\n\n"
        f"{short_text(mission, 120)}\n\n"
        "</div>"
    )


def build_mission_line() -> str:
    return (
        "## Mission\n\n"
        "<div align=\"center\">\n"
        "<img src=\"assets/mission-bar.svg\" width=\"100%\" alt=\"Animated mission status bar\" />\n"
        "</div>"
    )


def build_current_focus(settings: dict) -> str:
    focus = settings.get("profile", {}).get("vision", [])[:4] or [
        "Attention-Guided YOLOv11",
        "DeepScope Research",
        "Medical AI",
        "Intelligent Transportation",
    ]
    return (
        "## Current Focus\n\n"
        "<div align=\"center\">\n"
        "<img src=\"assets/current-focus.svg\" width=\"100%\" alt=\"Animated current focus panel\" />\n"
        "</div>"
    )


def build_technology_stack(settings: dict, statistics: dict) -> str:
    top_languages = statistics.get("top_languages", [])[:4]
    return (
        "## Technology Stack\n\n"
        "<div align=\"center\">\n"
        "<img src=\"assets/tech-stack.svg\" width=\"100%\" alt=\"Animated technology stack\" />\n"
        "</div>"
    )


def build_github_analytics(settings: dict) -> str:
    owner = settings.get("profile", {}).get("owner", "hijbullahx")
    streak = f"https://streak-stats.demolab.com?user={owner}&theme=transparent&border_radius=12&date_format=M%20j%5B%2C%20Y%5D"
    return (
        "## GitHub Analytics\n\n"
        f"<div align=\"center\">\n  <img src=\"{streak}\" height=\"170\" alt=\"GitHub streak\" />\n</div>\n\n"
        f"<div align=\"center\">\n  <img src=\"https://github-readme-activity-graph.vercel.app/graph?username={owner}&theme=github-compact&hide_border=true&bg_color=050816&color=F8FAFC&line=00F5FF&point=8B5CF6\" alt=\"Contribution graph\" />\n</div>\n\n"
        ""
    )


def build_research_journey() -> str:
    return (
        "## Research Journey\n\n"
        "<div align=\"center\">\n"
        "<img src=\"assets/research-journey.svg\" width=\"100%\" alt=\"Animated research journey timeline\" />\n"
        "</div>"
    )


def build_lets_build_together(settings: dict) -> str:
    profile = settings.get("profile", {})
    github_url = profile.get("contact", {}).get("github", "https://github.com/hijbullahx")
    portfolio_url = profile.get("contact", {}).get("website", "https://www.hijbullah.me") or "https://www.hijbullah.me"
    linkedin_url = profile.get("contact", {}).get("linkedin", "")
    email_value = profile.get("contact", {}).get("email", "")
    buttons = [
        f'<a href="{portfolio_url}"><img src="https://img.shields.io/badge/Portfolio-050816?style=for-the-badge&logo=vercel&logoColor=00F5FF" alt="Portfolio" /></a>',
        f'<a href="{github_url}"><img src="https://img.shields.io/badge/GitHub-050816?style=for-the-badge&logo=github&logoColor=00F5FF" alt="GitHub" /></a>',
    ]
    if linkedin_url:
        buttons.append(f'<a href="{linkedin_url}"><img src="https://img.shields.io/badge/LinkedIn-050816?style=for-the-badge&logo=linkedin&logoColor=00F5FF" alt="LinkedIn" /></a>')
    if email_value:
        buttons.append(f'<a href="mailto:{email_value}"><img src="https://img.shields.io/badge/Email-050816?style=for-the-badge&logo=gmail&logoColor=00F5FF" alt="Email" /></a>')
    return (
        "## Connect With Me\n\n"
        "<div align=\"center\">\n"
        + "\n".join(buttons)
        + "\n</div>"
    )


def build_footer() -> str:
    return (
        "## Animated Footer\n\n"
        "<div align=\"center\">\n"
        "<img src=\"assets/footer.svg\" width=\"100%\" alt=\"Animated footer\" />\n"
        "</div>"
    )


def build_live_widgets(settings: dict) -> str:
    widget_order = ["graph", "snake", "trophy", "waka", "spotify", "leetcode"]
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
    readme_template = read_text(ROOT / "templates" / "readme_template.md", default="")

    sections = [
        build_hero(settings),
        build_mission_line(),
        build_current_focus(settings),
        build_technology_stack(settings, statistics),
        build_github_analytics(settings),
        build_research_journey(),
        build_lets_build_together(settings),
        build_footer(),
    ]
    body = "\n\n".join(section for section in sections if section)

    if readme_template.strip():
        return readme_template.replace("{{BODY}}", body).replace("{{WIDGETS}}", build_live_widgets(settings))

    return f"# HIJBULLAH AI LAB\n\n{body}".strip() + "\n"


def main() -> None:
    output = build_readme()
    output_path = ROOT / "README.md"
    output_path.write_text(output, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
