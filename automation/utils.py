"""Shared helpers for the profile generation pipeline.

The scripts in this package use only the Python standard library so the GitHub
Action stays lightweight and easy to maintain.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"
TEMPLATE_DIR = ROOT / "templates"
CACHE_DIR = ROOT / ".cache" / "profile"
GITHUB_API = "https://api.github.com"


def load_json(path: Path | str, default: Any | None = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return {} if default is None else default
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path | str, payload: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def write_text(path: Path | str, text: str) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")


def read_text(path: Path | str, default: str = "") -> str:
    file_path = Path(path)
    if not file_path.exists():
        return default
    return file_path.read_text(encoding="utf-8")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "item"


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;")


def short_text(value: str, limit: int = 180) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1].rstrip() + "…"


def iso_to_date(value: str | None) -> str:
    if not value:
        return "Unknown"
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except ValueError:
        return value


def relative_age(value: str | None) -> str:
    if not value:
        return "Unknown"
    try:
        updated = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    delta = datetime.now(timezone.utc) - updated
    days = max(delta.days, 0)
    if days == 0:
        return "Today"
    if days == 1:
        return "1 day ago"
    if days < 30:
        return f"{days} days ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = months // 12
    return f"{years} year{'s' if years != 1 else ''} ago"


def split_words(value: str) -> set[str]:
    return {piece for piece in re.split(r"[^a-z0-9]+", value.lower()) if piece}


def cached_path(key: str, suffix: str = ".json") -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    return CACHE_DIR / f"{digest}{suffix}"


def github_request(path: str, params: Mapping[str, Any] | None = None, *, token: str | None = None, use_cache: bool = True, ttl_seconds: int = 21600) -> Any:
    query = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v is not None})
    url = f"{GITHUB_API}{path}"
    if query:
        url = f"{url}?{query}"

    cache_file = cached_path(url)
    if use_cache and cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age <= ttl_seconds:
            return load_json(cache_file)

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "hijbullahx-profile-automation",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if use_cache:
                save_json(cache_file, payload)
            return payload
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        if error.code == 403 and use_cache and cache_file.exists():
            return load_json(cache_file)
        raise


def github_paginate(path: str, params: Mapping[str, Any] | None = None, *, token: str | None = None, max_pages: int = 10) -> list[Any]:
    items: list[Any] = []
    page = 1
    base_params = dict(params or {})
    while page <= max_pages:
        page_params = {**base_params, "per_page": 100, "page": page}
        payload = github_request(path, page_params, token=token)
        if not payload:
            break
        if not isinstance(payload, list):
            return [payload]
        items.extend(payload)
        if len(payload) < 100:
            break
        page += 1
    return items


def github_readme_snippet(owner: str, repo: str, *, token: str | None = None, limit: int = 500) -> str:
    payload = github_request(f"/repos/{owner}/{repo}/readme", token=token)
    if not payload:
        return ""
    content = payload.get("content", "")
    encoding = payload.get("encoding")
    if encoding == "base64" and content:
        decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
        return short_text(decoded, limit=limit)
    if isinstance(content, str):
        return short_text(content, limit=limit)
    return ""


def github_languages(owner: str, repo: str, *, token: str | None = None) -> dict[str, int]:
    payload = github_request(f"/repos/{owner}/{repo}/languages", token=token)
    return payload if isinstance(payload, dict) else {}


def normalize_repository(repo: Mapping[str, Any], *, token: str | None = None, owner: str | None = None) -> dict[str, Any]:
    repository_owner = owner or repo.get("owner", {}).get("login", "")
    repository_name = repo.get("name", "")
    languages = github_languages(repository_owner, repository_name, token=token) if repository_owner and repository_name else {}
    readme_snippet = github_readme_snippet(repository_owner, repository_name, token=token) if repository_owner and repository_name else ""
    topics = repo.get("topics") or []
    if isinstance(topics, str):
        topics = [topics]
    return {
        "name": repository_name,
        "full_name": repo.get("full_name", repository_name),
        "html_url": repo.get("html_url", ""),
        "description": repo.get("description") or "",
        "homepage": repo.get("homepage") or "",
        "topics": topics,
        "language": repo.get("language") or next(iter(languages), ""),
        "languages": languages,
        "stars": int(repo.get("stargazers_count") or 0),
        "forks": int(repo.get("forks_count") or 0),
        "size": int(repo.get("size") or 0),
        "archived": bool(repo.get("archived")),
        "fork": bool(repo.get("fork")),
        "updated_at": repo.get("updated_at") or "",
        "pushed_at": repo.get("pushed_at") or "",
        "created_at": repo.get("created_at") or "",
        "default_branch": repo.get("default_branch") or "main",
        "license": (repo.get("license") or {}).get("spdx_id") if isinstance(repo.get("license"), dict) else None,
        "readme_snippet": readme_snippet,
        "visibility": repo.get("visibility") or "public",
    }


def repository_score(repository: Mapping[str, Any], rules: Mapping[str, Any]) -> tuple[int, list[str]]:
    name_blob = " ".join(
        str(part)
        for part in [
            repository.get("name", ""),
            repository.get("description", ""),
            " ".join(repository.get("topics", []) or []),
            repository.get("language", ""),
            repository.get("readme_snippet", ""),
        ]
    ).lower()
    words = split_words(name_blob)
    scores: dict[str, int] = {}
    matched: list[str] = []
    for category, rule in rules.items():
        score = 0
        for keyword in rule.get("keywords", []):
            keyword_l = keyword.lower()
            if keyword_l in name_blob:
                score += 3
            elif keyword_l in words:
                score += 2
        for topic in rule.get("topics", []):
            if topic.lower() in [value.lower() for value in repository.get("topics", []) or []]:
                score += 4
        for language in rule.get("languages", []):
            if language.lower() == str(repository.get("language", "")).lower():
                score += 3
        scores[category] = score
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    if ordered:
        top_score = ordered[0][1]
        if top_score > 0:
            matched = [category for category, score in ordered if score == top_score or score >= max(top_score - 2, 1)]
    return (ordered[0][1] if ordered else 0, matched)


def render_markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def clamp_list(values: Iterable[str], limit: int) -> list[str]:
    collected: list[str] = []
    for value in values:
        if value and value not in collected:
            collected.append(value)
        if len(collected) >= limit:
            break
    return collected


def build_widget_url(name: str, settings: Mapping[str, Any]) -> str:
    profile = settings.get("profile", {})
    widgets = settings.get("widgets", {})
    owner = profile.get("owner", "hijbullahx")
    if name == "graph":
        return "assets/contribution-graph.svg"
    if name == "snake":
        return f"https://raw.githubusercontent.com/{owner}/{owner}/output/github-contribution-grid-snake.svg"
    if name == "trophy":
        return f"https://github-profile-trophy.vercel.app/?username={owner}&theme=darkhub&no-frame=true&margin-w=8"
    if name == "waka" and widgets.get("wakatime_username"):
        return f"https://github-readme-stats.vercel.app/api/wakatime?username={widgets['wakatime_username']}"
    if name == "spotify" and widgets.get("spotify_user_id"):
        return f"https://spotify-github-profile.kittinanx.com/api/view?uid={widgets['spotify_user_id']}&cover_image=true&theme=default"
    if name == "leetcode" and widgets.get("leetcode_username"):
        return f"https://leetcard.jacoblin.cool/{widgets['leetcode_username']}?theme=dark"
    return ""
