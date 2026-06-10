from __future__ import annotations

from .utils import CONFIG_DIR, load_yaml


def load_stock_mapping() -> dict:
    return load_yaml(CONFIG_DIR / "stock_mapping.yml", default={})


def map_to_a_share(sectors: list[str], mapping: dict | None = None) -> dict:
    stock_mapping = mapping or load_stock_mapping()
    result: dict[str, dict] = {}
    for sector in sectors:
        if sector in stock_mapping:
            result[sector] = stock_mapping[sector]
    return result
