from __future__ import annotations

from .utils import CONFIG_DIR, load_yaml, normalize_text


def load_chain_rules() -> dict:
    return load_yaml(CONFIG_DIR / "industry_chain_rules.yml", default={})


def match_topics(item: dict, rules: dict | None = None) -> list[str]:
    chain_rules = rules or load_chain_rules()
    text = normalize_text(f"{item.get('title', '')} {item.get('summary', '')} {item.get('category', '')}")
    matched: list[str] = []
    for topic, rule in chain_rules.items():
        aliases = rule.get("aliases", []) + [topic, rule.get("name", "")]
        if any(normalize_text(alias) in text for alias in aliases):
            matched.append(topic)
    return matched


def map_industry_chain(item: dict, rules: dict | None = None) -> dict:
    chain_rules = rules or load_chain_rules()
    topics = match_topics(item, chain_rules)
    if not topics:
        return {
            "matched_topics": [],
            "upstream_impact": [],
            "midstream_impact": [],
            "downstream_impact": [],
            "positive_sectors": [],
            "negative_sectors": [],
            "neutral_sectors": [],
            "chain_analysis": "暂未命中明确产业链规则，需结合后续价格、订单或政策数据继续观察。",
        }
    upstream: list[str] = []
    midstream: list[str] = []
    downstream: list[str] = []
    positive: list[str] = []
    negative: list[str] = []
    neutral: list[str] = []
    analyses: list[str] = []
    for topic in topics:
        rule = chain_rules[topic]
        upstream += rule.get("upstream_impact", [])
        midstream += rule.get("midstream_impact", [])
        downstream += rule.get("downstream_impact", [])
        positive += rule.get("positive_sectors", [])
        negative += rule.get("negative_sectors", [])
        neutral += rule.get("neutral_sectors", [])
        analyses.append(f"{rule.get('name', topic)}：{rule.get('chain_analysis', '')}")
    dedupe = lambda values: list(dict.fromkeys(values))
    return {
        "matched_topics": topics,
        "upstream_impact": dedupe(upstream),
        "midstream_impact": dedupe(midstream),
        "downstream_impact": dedupe(downstream),
        "positive_sectors": dedupe(positive),
        "negative_sectors": dedupe(negative),
        "neutral_sectors": dedupe(neutral),
        "chain_analysis": "\n\n".join(analyses),
    }
