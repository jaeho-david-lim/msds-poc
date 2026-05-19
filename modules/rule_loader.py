from __future__ import annotations

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = [
    "filename_keyword",
    "product_code",
    "viewer_input_folder",
    "viewer_apply_text",
    "enabled",
    "product_click_x",
    "product_click_y",
    "product_image",
]


def load_rules(rules_path: Path) -> list[dict]:
    df = pd.read_excel(rules_path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"rules.xlsx 필수 컬럼 누락: {missing}")
    df = df.fillna("")
    enabled_df = df[df["enabled"].astype(str).str.lower().isin(["1", "true", "y", "yes"]) | (df["enabled"] == 1)]
    return enabled_df.to_dict(orient="records")


def detect_product(file_name: str, rules: list[dict]) -> dict:
    name = file_name.lower()
    matched = [r for r in rules if str(r["filename_keyword"]).lower() in name]
    if len(matched) == 1:
        return matched[0]
    if len(matched) == 0:
        raise ValueError("제품 keyword 미인식")
    raise ValueError("제품 keyword 중복 매칭")
