from __future__ import annotations

from difflib import SequenceMatcher

from .utils import normalize_text, stable_id


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def deduplicate_news(items: list[dict], title_threshold: float = 0.88) -> list[dict]:
    seen_keys: set[str] = set()
    kept: list[dict] = []
    kept_titles: list[str] = []
    for item in items:
        key = stable_id(item.get("title", ""), item.get("url", ""))
        url_key = normalize_text(item.get("url", ""))
        if key in seen_keys or url_key in seen_keys:
            continue
        title = item.get("title", "")
        if any(_similar(title, existing) >= title_threshold for existing in kept_titles):
            continue
        seen_keys.add(key)
        seen_keys.add(url_key)
        kept_titles.append(title)
        kept.append(item)
    return kept
