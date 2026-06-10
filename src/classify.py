from __future__ import annotations

from .utils import CONFIG_DIR, load_yaml, normalize_text


DEFAULT_CATEGORY = "其他"


def load_keywords() -> dict[str, list[str]]:
    return load_yaml(CONFIG_DIR / "keywords.yml", default={})


def classify_item(item: dict, keywords: dict[str, list[str]] | None = None) -> str:
    rules = keywords or load_keywords()
    text = normalize_text(f"{item.get('title', '')} {item.get('summary', '')} {item.get('raw_category', '')}")
    best_category = DEFAULT_CATEGORY
    best_score = 0
    for category, words in rules.items():
        score = sum(1 for word in words if normalize_text(word) in text)
        if score > best_score:
            best_category = category
            best_score = score
    return best_category


def classify_news(items: list[dict], keywords: dict[str, list[str]] | None = None) -> list[dict]:
    rules = keywords or load_keywords()
    for item in items:
        item["category"] = classify_item(item, rules)
    return items
