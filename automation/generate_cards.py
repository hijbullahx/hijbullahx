"""Render premium portfolio cards in GitHub-flavored Markdown."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from automation.utils import ROOT, iso_to_date, load_json, markdown_escape, relative_age, save_json, short_text


def build_card(repository: dict, docs_base: str = "") -> str:
    name = markdown_escape(repository.get("name", "Repository"))
    description_source = repository.get("description") or repository.get("readme_snippet") or repository.get("name") or ""
    description = markdown_escape(short_text(description_source, 140)) or "No description provided."
    language = markdown_escape(repository.get("language") or "Unknown")
    topics = ", ".join(markdown_escape(topic) for topic in (repository.get("topics", []) or [])[:6]) or "None"
    repo_url = repository.get("html_url", "#")
    homepage = repository.get("homepage") or ""
    paper_url = repository.get("paper_url") or ""
    live_url = homepage or repository.get("demo_url") or ""

    links = [f"[Repository]({repo_url})"]
    if live_url:
        links.append(f"[Live Demo]({live_url})")
    if paper_url:
        links.append(f"[Paper]({paper_url})")

    return f"""<td valign=\"top\" width=\"50%\">\n\n**{name}**  \n{description}\n\n- Language: {language}\n- Stars: {repository.get('stars', 0)} | Forks: {repository.get('forks', 0)}\n- Updated: {relative_age(repository.get('updated_at'))}\n\n{" · ".join(links)}\n\n</td>"""


def build_cards(repositories: list[dict], columns: int = 2) -> str:
    rows: list[str] = []
    for index in range(0, len(repositories), columns):
        slice_repos = repositories[index : index + columns]
        while len(slice_repos) < columns:
            slice_repos.append({"name": "", "description": "", "topics": [], "languages": {}, "language": "", "stars": 0, "forks": 0, "updated_at": "", "html_url": "#", "default_branch": "main"})
        cells = "\n".join(build_card(repo) for repo in slice_repos)
        rows.append(f"<tr>\n{cells}\n</tr>")
    if not rows:
        return "_No public repositories matched the current filters._"
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def main() -> None:
    payload = load_json(ROOT / ".cache" / "profile" / "classified_repositories.json", default={})
    repositories = payload.get("repositories", []) if isinstance(payload, dict) else []
    output = build_cards(repositories[:12])
    output_path = ROOT / ".cache" / "profile" / "cards.md"
    save_json(output_path.with_suffix(".json"), {"count": len(repositories)})
    output_path.write_text(output, encoding="utf-8")
    print(f"Rendered {min(len(repositories), 12)} project cards")


if __name__ == "__main__":
    main()
