from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    from dateutil import parser
except ImportError:  # pragma: no cover
    parser = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"


def ensure_dirs() -> None:
    for path in [DATA_DIR / "raw", DATA_DIR / "processed", DATA_DIR / "reports", CONFIG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [part.strip().strip("\"'") for part in inner.split(",")]
    return value.strip("\"'")


def _simple_yaml_load(text: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_top: str | None = None
    current_field: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if indent == 0 and line.endswith(":"):
            current_top = line[:-1]
            result[current_top] = {}
            current_field = None
            continue
        if indent == 2 and current_top:
            if line.startswith("- "):
                if not isinstance(result[current_top], list):
                    result[current_top] = []
                result[current_top].append(_parse_scalar(line[2:]))
                continue
            key, _, value = line.partition(":")
            current_field = key.strip()
            result[current_top][current_field] = _parse_scalar(value) if value.strip() else []
            continue
        if indent == 4 and current_top and current_field and line.startswith("- "):
            result[current_top][current_field].append(_parse_scalar(line[2:]))
    return result


def load_yaml(path: str | Path, default: Any = None) -> Any:
    target = Path(path)
    if not target.exists():
        return default
    text = target.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text) or default
    return _simple_yaml_load(text) or default


def save_json(path: str | Path, data: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_text(text: str | None) -> str:
    text = text or ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def parse_datetime(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        try:
            if parser is not None:
                return parser.parse(value).isoformat()
            return parsedate_to_datetime(value).isoformat()
        except Exception:
            return value
    try:
        return datetime(*value[:6]).isoformat()
    except Exception:
        return ""


def stable_id(*parts: str) -> str:
    raw = "|".join(normalize_text(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def today_yyyymmdd() -> str:
    return datetime.now().strftime("%Y-%m-%d")
