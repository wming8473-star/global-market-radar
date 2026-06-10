from __future__ import annotations

from src.analyze import analyze_items
from src.classify import classify_news
from src.deduplicate import deduplicate_news
from src.fetch_news import fetch_rss_news
from src.report import generate_markdown_report
from src.utils import DATA_DIR, ensure_dirs, save_json, setup_logging, today_yyyymmdd


def main() -> None:
    ensure_dirs()
    setup_logging()

    raw_items = fetch_rss_news()
    unique_items = deduplicate_news(raw_items)
    classified_items = classify_news(unique_items)
    analyzed_items = analyze_items(classified_items)

    date = today_yyyymmdd()
    save_json(DATA_DIR / "processed" / f"{date}_analyzed_news.json", analyzed_items)
    report_path = generate_markdown_report(analyzed_items, date)
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
