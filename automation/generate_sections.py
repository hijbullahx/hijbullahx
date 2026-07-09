"""Compose the profile README from templates, metrics, and live data."""

from __future__ import annotations

from html.parser import HTMLParser
import sys
import urllib.error
import urllib.request

from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.generate_cards import build_cards
from automation.utils import CONFIG_DIR, ROOT, build_widget_url, load_json, read_text, render_markdown_table, short_text


CONTRIBUTION_GRAPH_PATH = ROOT / "assets" / "contribution-graph.svg"


class _ContributionCalendarParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[dict[str, str]]] = []
        self._in_tbody = False
        self._current_row: list[dict[str, str]] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "tbody":
            self._in_tbody = True
        elif tag == "tr" and self._in_tbody:
            self._current_row = []
        elif tag == "td" and self._in_tbody and self._current_row is not None:
            classes = attr_map.get("class", "")
            if "ContributionCalendar-day" in classes:
                self._current_row.append(attr_map)

    def handle_endtag(self, tag: str) -> None:
        if tag == "tbody":
            self._in_tbody = False
            self._current_row = None
        elif tag == "tr" and self._in_tbody and self._current_row is not None:
            if self._current_row:
                self.rows.append(self._current_row)
            self._current_row = None


def _fetch_contribution_rows(owner: str) -> list[list[dict[str, str]]]:
    url = f"https://github.com/users/{owner}/contributions"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return []

    parser = _ContributionCalendarParser()
    parser.feed(html)
    return parser.rows


def _contribution_level_color(level: str) -> str:
    palette = {
        "0": "#161B22",
        "1": "#0E4429",
        "2": "#006D32",
        "3": "#26A641",
        "4": "#39D353",
    }
    return palette.get(level, palette["0"])


def _build_contribution_graph_svg(owner: str) -> str:
    rows = _fetch_contribution_rows(owner)
    if not rows:
        rows = [[{"data-level": "0"} for _ in range(53)] for _ in range(7)]

    columns = max((len(row) for row in rows), default=0)
    cell_size = 11
    cell_gap = 4
    graph_x = 88
    graph_y = 98
    grid_width = columns * (cell_size + cell_gap) - cell_gap if columns else 0
    grid_height = len(rows) * (cell_size + cell_gap) - cell_gap if rows else 0
    width = max(graph_x + grid_width + 92, 1200)
    height = max(graph_y + grid_height + 104, 320)

    cells: list[str] = []
    for row_index, row in enumerate(rows):
        for column_index, cell in enumerate(row):
            level = cell.get("data-level", "0")
            date = cell.get("data-date", "")
            color = _contribution_level_color(level)
            x = graph_x + column_index * (cell_size + cell_gap)
            y = graph_y + row_index * (cell_size + cell_gap)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="3" fill="{color}" data-date="{date}" data-level="{level}">' 
                f'<animate attributeName="opacity" values="0.82;1;0.82" dur="6s" repeatCount="indefinite" />'
                f"</rect>"
            )

    beam_width = max(grid_width // 8, 72)
    beam_x_end = graph_x + grid_width + 40

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
        '<title id="title">Animated contribution graph</title>'
        '<desc id="desc">A cinematic animated contribution graph rebuilt from the live GitHub contribution calendar.</desc>'
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0%" stop-color="#050816" />'
        '<stop offset="55%" stop-color="#081326" />'
        '<stop offset="100%" stop-color="#120B24" />'
        '</linearGradient>'
        '<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#00F5FF" stop-opacity="0" />'
        '<stop offset="50%" stop-color="#00F5FF" stop-opacity="0.88" />'
        '<stop offset="100%" stop-color="#8B5CF6" stop-opacity="0" />'
        '</linearGradient>'
        '<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="14" /></filter>'
        '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" /></filter>'
        '</defs>'
        f'<rect width="{width}" height="{height}" rx="24" fill="url(#bg)" />'
        f'<circle cx="170" cy="78" r="120" fill="#00F5FF" opacity="0.08" filter="url(#blur)">'
        '<animate attributeName="cx" values="170;230;170" dur="9s" repeatCount="indefinite" />'
        '<animate attributeName="cy" values="78;100;78" dur="11s" repeatCount="indefinite" />'
        '</circle>'
        f'<circle cx="{width - 170}" cy="{height - 72}" r="140" fill="#8B5CF6" opacity="0.09" filter="url(#blur)">'
        f'<animate attributeName="cx" values="{width - 170};{width - 230};{width - 170}" dur="10s" repeatCount="indefinite" />'
        f'<animate attributeName="cy" values="{height - 72};{height - 100};{height - 72}" dur="8s" repeatCount="indefinite" />'
        '</circle>'
        '<g opacity="0.14" stroke="#22314A" stroke-width="1">'
        f'<path d="M70 46H{width - 70}M70 92H{width - 70}M70 138H{width - 70}M70 184H{width - 70}M70 230H{width - 70}M70 276H{width - 70}" />'
        '</g>'
        '<g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace">'
        '<text x="80" y="34" font-size="18" letter-spacing="4" fill="#00F5FF">CONTRIBUTION CHRONICLE</text>'
        f'<text x="80" y="60" font-size="13" fill="#94A3B8">{owner} contributions in the last year</text>'
        '</g>'
        f'<g transform="translate(92 82)">'
        f'<rect width="{grid_width + 34}" height="{grid_height + 36}" rx="20" fill="#0B1120" stroke="#1F2937" opacity="0.96" />'
        f'<rect width="{grid_width + 34}" height="{grid_height + 36}" rx="20" fill="url(#beam)" opacity="0.12">'
        '<animate attributeName="opacity" values="0.05;0.16;0.05" dur="7s" repeatCount="indefinite" />'
        '</rect>'
        '<g filter="url(#glow)">'
        + ''.join(cells)
        + '</g>'
        f'<rect x="-{beam_width}" y="-10" width="{beam_width}" height="{grid_height + 56}" fill="url(#beam)" opacity="0.16">'
        f'<animate attributeName="x" values="-{beam_width};{beam_x_end};-{beam_width}" dur="8s" repeatCount="indefinite" />'
        '</rect>'
        '</g>'
        '</svg>'
    )


def refresh_contribution_graph_asset(settings: dict) -> None:
    owner = settings.get("profile", {}).get("owner", "hijbullahx")
    CONTRIBUTION_GRAPH_PATH.write_text(_build_contribution_graph_svg(owner), encoding="utf-8")


def build_hero(settings: dict) -> str:
    profile = settings.get("profile", {})
    display_name = profile.get("display_name", "Md. Taher Bin Omar Hijbullah")
    role = profile.get("role", "AI Research Engineer")
    tagline = profile.get("tagline", "Computer Vision • Autonomous Systems • Backend Engineering")
    mission = "Building production AI systems with research depth and startup-grade execution."
    return (
        "<div align=\"center\">\n\n"
        "<img src=\"assets/hero-signature.svg\" width=\"100%\" alt=\"Animated profile signature\" />\n\n"
        "<img src=\"assets/hero.svg\" width=\"100%\" alt=\"HIJBULLAH AI LAB hero\" />\n\n"
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
        "Computer Vision",
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


def build_contribution_graph(settings: dict) -> str:
    graph = build_widget_url("graph", settings)
    return (
        "## Contribution Graph\n\n"
        f"<div align=\"center\">\n  <img src=\"{graph}\" alt=\"Contribution graph\" />\n</div>"
    )


def build_github_analytics(settings: dict) -> str:
    owner = settings.get("profile", {}).get("owner", "hijbullahx")
    streak = f"https://streak-stats.demolab.com?user={owner}&theme=transparent&border_radius=12&date_format=M%20j%5B%2C%20Y%5D"
    return (
        "## GitHub Analytics\n\n"
        f"<div align=\"center\">\n  <img src=\"{streak}\" height=\"170\" alt=\"GitHub streak\" />\n</div>\n\n"
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
    refresh_contribution_graph_asset(settings)
    payload = load_json(ROOT / ".cache" / "profile" / "classified_repositories.json", default={})
    statistics = load_json(ROOT / ".cache" / "profile" / "statistics.json", default={})
    repositories = payload.get("repositories", []) if isinstance(payload, dict) else []
    readme_template = read_text(ROOT / "templates" / "readme_template.md", default="")

    sections = [
        build_hero(settings),
        build_contribution_graph(settings),
        build_mission_line(),
        build_current_focus(settings),
        build_technology_stack(settings, statistics),
        build_github_analytics(settings),
        build_research_journey(),
        build_lets_build_together(settings),
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
