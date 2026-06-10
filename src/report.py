from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .utils import DATA_DIR, today_yyyymmdd


REPORT_TITLE = "国际消息产业链传导日报"


def _line_item(item: dict) -> str:
    mapping_keys = "、".join(item.get("a_share_mapping", {}).keys()) or "暂无明确映射"
    return (
        f"### {item.get('title')}\n"
        f"- 来源：{item.get('source')} | 时间：{item.get('published_at')} | 分类：{item.get('category')} | 影响级别：{item.get('impact_level')}\n"
        f"- 链接：{item.get('url')}\n"
        f"- 摘要：{item.get('summary_cn')}\n"
        f"- 产业链推演：{item.get('chain_analysis')}\n"
        f"- 正向方向：{'、'.join(item.get('positive_sectors', [])) or '无'}\n"
        f"- 负向方向：{'、'.join(item.get('negative_sectors', [])) or '无'}\n"
        f"- 影响周期：情绪 {item.get('time_lag', {}).get('sentiment_period')}；价格 {item.get('time_lag', {}).get('price_period')}；经营 {item.get('time_lag', {}).get('business_period')}；业绩 {item.get('time_lag', {}).get('earnings_period')}\n"
        f"- A股观察映射：{mapping_keys}\n"
        f"- 交易观察：{item.get('trading_note')}\n"
        f"- 风险提示：{item.get('risk_note')}\n"
    )


def _section(title: str, items: list[dict]) -> str:
    if not items:
        return f"## {title}\n暂无高相关消息。\n"
    return f"## {title}\n" + "\n".join(_line_item(item) for item in items)


def generate_markdown_report(items: list[dict], report_date: str | None = None) -> Path:
    date = report_date or today_yyyymmdd()
    report_path = DATA_DIR / "reports" / f"{date}_global_market_radar.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    by_category: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        by_category[item.get("category", "其他")].append(item)
    high_impact = [item for item in items if item.get("impact_level") == "高"][:10]
    macro_fx = by_category.get("宏观", []) + by_category.get("汇率", []) + by_category.get("海外股市", [])
    ai_semis = by_category.get("AI算力", []) + by_category.get("半导体", []) + by_category.get("存储", [])
    commodities = by_category.get("能源", []) + by_category.get("金属", []) + by_category.get("原材料", [])
    geopolitical = by_category.get("地缘", [])
    affected: list[str] = []
    seen = set()
    for item in items:
        for sector in item.get("positive_sectors", []) + item.get("negative_sectors", []) + item.get("neutral_sectors", []):
            if sector not in seen:
                seen.add(sector)
                affected.append(sector)
    tomorrow_watch = [
        "验证国际期货价格、美元指数、美债收益率与A股相关板块是否同向确认。",
        "关注被映射方向是否出现成交额放大、产业数据跟进或公司公告印证。",
        "对资源品和原材料主题，重点看现货价格、库存、加工费与下游接受度。",
        "对AI算力和半导体主题，重点看订单、排产、CapEx、供应链交付周期。",
    ]
    content = [
        f"# {REPORT_TITLE}",
        f"报告日期：{date}",
        "> 本报告基于公开 RSS 信息和本地规则生成，只做产业链观察和风险提示，不构成投资建议。",
        _section("一、高影响事件", high_impact),
        _section("二、宏观与汇率", macro_fx[:8]),
        _section("三、AI算力与半导体", ai_semis[:8]),
        _section("四、能源与大宗商品", commodities[:8]),
        _section("五、地缘风险", geopolitical[:8]),
        "## 六、A股可能受影响方向\n" + ("、".join(affected) if affected else "暂无明确方向。"),
        "## 七、明日观察重点\n" + "\n".join(f"- {line}" for line in tomorrow_watch),
    ]
    report_path.write_text("\n\n".join(content), encoding="utf-8")
    return report_path
