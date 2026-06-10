from __future__ import annotations


DEFAULT_TIME_LAG = {
    "sentiment_period": "T+0至T+3",
    "price_period": "1-2周",
    "business_period": "1-3个月",
    "earnings_period": "1个季度以上",
}

EVENT_TIME_LAGS = {
    "raw_material_price_up": {
        "sentiment_period": "T+0至T+3，资源与成本敏感板块先反应",
        "price_period": "1-2周，现货报价、长协谈判和库存重估开始体现",
        "business_period": "1-3个月，毛利率和订单价格逐步传导",
        "earnings_period": "1个季度以上，需要财报验证成本或利润弹性",
    },
    "tech_product_cycle": {
        "sentiment_period": "T+0至T+2，主题情绪和供应链预期先升温",
        "price_period": "2-4周，订单、排产、招标和渠道数据决定持续性",
        "business_period": "1-2个季度，供应链收入确认逐步落地",
        "earnings_period": "2个季度以上，需观察量产节奏和利润率",
    },
    "geopolitical_conflict": {
        "sentiment_period": "T+0至T+3，避险和风险偏好快速切换",
        "price_period": "数日至2周，能源、黄金、航运和汇率价格波动放大",
        "business_period": "1-3个月，物流、订单和成本扰动显现",
        "earnings_period": "1个季度以上，需确认冲突持续时间和制裁影响",
    },
    "interest_rate_change": {
        "sentiment_period": "T+0至T+2，权益估值和成长风格先定价",
        "price_period": "1-4周，美元、美债、黄金和全球资金流重新平衡",
        "business_period": "1-2个季度，融资成本和需求侧逐步反馈",
        "earnings_period": "2个季度以上，企业利润影响滞后确认",
    },
    "fx_move": {
        "sentiment_period": "T+0至T+2，出口、航空、造纸等方向先反应",
        "price_period": "1-2周，套保、进口成本和结算价格开始调整",
        "business_period": "1-3个月，订单利润率和费用端体现",
        "earnings_period": "1个季度以上，汇兑损益需财报验证",
    },
}


def infer_event_type(item: dict, category: str, matched_topics: list[str]) -> str:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    commodity_topics = {"crude_oil", "copper", "aluminum", "lithium", "gold", "natural_gas", "shipping"}
    if set(matched_topics) & commodity_topics or category in {"能源", "金属", "原材料"}:
        return "raw_material_price_up"
    if category in {"AI算力", "半导体", "存储"}:
        return "tech_product_cycle"
    if category == "地缘":
        return "geopolitical_conflict"
    if "rate" in text or "fed" in text or "yield" in text or category == "宏观":
        return "interest_rate_change"
    if category == "汇率" or "dollar" in text or "currency" in text:
        return "fx_move"
    return "general_news"


def get_time_lag(event_type: str) -> dict[str, str]:
    return EVENT_TIME_LAGS.get(event_type, DEFAULT_TIME_LAG)
