from __future__ import annotations

import re

from .chain_mapper import load_chain_rules, map_industry_chain
from .classify import classify_item, load_keywords
from .impact_timer import get_time_lag, infer_event_type
from .sector_mapper import load_stock_mapping, map_to_a_share
from .utils import normalize_text


POSITIVE_WORDS = ["surge", "rise", "gain", "record", "beat", "approval", "launch", "growth", "shortage", "higher"]
NEGATIVE_WORDS = ["fall", "drop", "slump", "miss", "sanction", "war", "ban", "delay", "cut", "risk", "lower"]


def _summary_cn(item: dict) -> str:
    summary = re.sub(r"<[^>]+>", " ", item.get("summary", ""))
    summary = re.sub(r"\s+", " ", summary).strip()
    if not summary:
        summary = item.get("title", "")
    return f"原文要点：{summary[:260]}"


def _score_text(item: dict) -> int:
    text = normalize_text(f"{item.get('title', '')} {item.get('summary', '')}")
    score = sum(1 for word in POSITIVE_WORDS if word in text)
    score -= sum(1 for word in NEGATIVE_WORDS if word in text)
    return max(-5, min(5, score))


def _impact_level(category: str, chain_result: dict, fundamental_score: int) -> str:
    high_categories = {"宏观", "地缘", "AI算力", "半导体", "能源", "金属", "原材料", "汇率"}
    if chain_result.get("matched_topics") and category in high_categories:
        return "高"
    if abs(fundamental_score) >= 3 or category in high_categories:
        return "中"
    return "低"


def _trading_note(chain_result: dict, time_lag: dict) -> str:
    positives = "、".join(chain_result.get("positive_sectors", [])[:5]) or "相关方向"
    negatives = "、".join(chain_result.get("negative_sectors", [])[:5]) or "成本承压方向"
    return f"仅作观察映射：短线关注{time_lag.get('sentiment_period')}内{positives}的情绪强弱，同时跟踪{negatives}是否出现成本、订单或汇率压力。若后续价格与成交量不能配合，主题持续性需下修。"


def _risk_note(category: str, chain_result: dict) -> str:
    if not chain_result.get("matched_topics"):
        return "未命中明确规则，可能只是孤立消息；需等待权威数据、价格走势或公司公告确认。"
    if category in {"地缘", "宏观", "汇率"}:
        return "宏观变量反转较快，需警惕政策表态、美元利率和风险偏好变化导致映射失效。"
    return "产业链传导存在库存、长协价格、套保和订单确认滞后，不能直接等同于上市公司业绩变化。"


def analyze_items(items: list[dict]) -> list[dict]:
    keywords = load_keywords()
    chain_rules = load_chain_rules()
    stock_mapping = load_stock_mapping()
    analyzed: list[dict] = []
    for item in items:
        category = item.get("category") or classify_item(item, keywords)
        item["category"] = category
        chain_result = map_industry_chain(item, chain_rules)
        event_type = infer_event_type(item, category, chain_result.get("matched_topics", []))
        time_lag = get_time_lag(event_type)
        sentiment_score = _score_text(item)
        fundamental_score = min(5, len(chain_result.get("matched_topics", [])) * 2 + max(sentiment_score, 0))
        all_sectors = chain_result.get("positive_sectors", []) + chain_result.get("negative_sectors", []) + chain_result.get("neutral_sectors", [])
        analyzed.append({
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "published_at": item.get("published_at", ""),
            "url": item.get("url", ""),
            "category": category,
            "summary_cn": _summary_cn(item),
            "event_type": event_type,
            "sentiment_score": sentiment_score,
            "fundamental_score": fundamental_score,
            "impact_level": _impact_level(category, chain_result, fundamental_score),
            "positive_sectors": chain_result.get("positive_sectors", []),
            "negative_sectors": chain_result.get("negative_sectors", []),
            "neutral_sectors": chain_result.get("neutral_sectors", []),
            "chain_analysis": chain_result.get("chain_analysis", ""),
            "time_lag": time_lag,
            "a_share_mapping": map_to_a_share(list(dict.fromkeys(all_sectors)), stock_mapping),
            "trading_note": _trading_note(chain_result, time_lag),
            "risk_note": _risk_note(category, chain_result),
        })
    return analyzed
