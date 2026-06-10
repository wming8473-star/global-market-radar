from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from urllib.request import Request, urlopen
from xml.etree import ElementTree

try:
    import feedparser
except ImportError:  # pragma: no cover
    feedparser = None

from .utils import DATA_DIR, parse_datetime, save_json


LOGGER = logging.getLogger(__name__)

RSS_SOURCES = [
    {"name": "Reuters Markets", "url": "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best", "raw_category": "markets"},
    {"name": "CNBC World", "url": "https://www.cnbc.com/id/100727362/device/rss/rss.html", "raw_category": "world"},
    {"name": "CNBC Technology", "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html", "raw_category": "technology"},
    {"name": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories/", "raw_category": "markets"},
    {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex", "raw_category": "finance"},
    {"name": "Nvidia Blog", "url": "https://blogs.nvidia.com/feed/", "raw_category": "company"},
    {"name": "AMD News", "url": "https://www.amd.com/en/newsroom/rss.xml", "raw_category": "company"},
    {"name": "TSMC News", "url": "https://pr.tsmc.com/english/rss.xml", "raw_category": "company"},
    {"name": "ASML Press", "url": "https://www.asml.com/en/news/rss.xml", "raw_category": "company"},
]


def _entry_to_item(entry: Any, source: dict[str, str]) -> dict[str, str]:
    published = getattr(entry, "published", "") or getattr(entry, "updated", "") or parse_datetime(getattr(entry, "published_parsed", "")) or parse_datetime(getattr(entry, "updated_parsed", ""))
    return {"title": getattr(entry, "title", "").strip(), "summary": getattr(entry, "summary", "").strip(), "url": getattr(entry, "link", "").strip(), "source": source["name"], "published_at": parse_datetime(published), "raw_category": source.get("raw_category", "")}


def _text(node: ElementTree.Element | None, name: str) -> str:
    if node is None:
        return ""
    child = node.find(name) or node.find(f"{{*}}{name}")
    return "".join(child.itertext()).strip() if child is not None else ""


def _fetch_with_stdlib(source: dict[str, str], limit_per_source: int) -> list[dict[str, str]]:
    request = Request(source["url"], headers={"User-Agent": "global-market-radar/0.1"})
    with urlopen(request, timeout=20) as response:
        root = ElementTree.fromstring(response.read())
    entries = root.findall(".//item") or root.findall(".//{*}entry")
    items: list[dict[str, str]] = []
    for entry in entries[:limit_per_source]:
        title = _text(entry, "title")
        link = _text(entry, "link")
        if not link:
            link_node = entry.find("{*}link")
            link = link_node.attrib.get("href", "") if link_node is not None else ""
        summary = _text(entry, "description") or _text(entry, "summary")
        published = _text(entry, "pubDate") or _text(entry, "published") or _text(entry, "updated")
        if title and link:
            items.append({"title": title, "summary": summary, "url": link, "source": source["name"], "published_at": parse_datetime(published), "raw_category": source.get("raw_category", "")})
    return items


def fetch_rss_news(sources: list[dict[str, str]] | None = None, limit_per_source: int = 25) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for source in sources or RSS_SOURCES:
        try:
            if feedparser is not None:
                feed = feedparser.parse(source["url"])
                if getattr(feed, "bozo", 0):
                    LOGGER.warning("RSS parse warning for %s: %s", source["name"], getattr(feed, "bozo_exception", "unknown"))
                for entry in feed.entries[:limit_per_source]:
                    item = _entry_to_item(entry, source)
                    if item["title"] and item["url"]:
                        items.append(item)
            else:
                items.extend(_fetch_with_stdlib(source, limit_per_source))
        except Exception as exc:
            LOGGER.exception("Failed to fetch %s: %s", source.get("name", source.get("url", "")), exc)
            continue
    output = DATA_DIR / "raw" / f"{datetime.now().strftime('%Y-%m-%d')}_rss_news.json"
    save_json(output, items)
    LOGGER.info("Fetched %s RSS items", len(items))
    return items
