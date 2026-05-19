from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import pyautogui

DEFAULT_CONFIG = {
    "pcrd_watch_folder": "",
    "quantstep4_folder": "",
    "result_root_folder": "",
    "viewer_export_folder": "",
    "cfx_manager_path": "",
    "seegene_viewer_path": "",
    "rules_excel_path": "",
    "user_id": "",
    "password": "",
    "default_wait_viewer_loading_sec": 20,
    "default_wait_cfx_export_sec": 20,
    "default_wait_after_apply_sec": 2,
    "sample_no_checkbox_x": 0,
    "sample_no_checkbox_y": 0,
    "continue_on_error": True,
    "copy_or_move_pcrd": "copy",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return DEFAULT_CONFIG.copy()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged


def save_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def take_screenshot(folder: Path, prefix: str) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    file = folder / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pyautogui.screenshot(str(file))
    return file
