from __future__ import annotations

from pathlib import Path
import pandas as pd

LOG_COLUMNS = [
    "job_name", "started_at", "ended_at", "status", "step_failed", "pcrd_file", "pcrd_source_path",
    "pcrd_copied_path", "product_keyword", "product_code", "viewer_apply_text", "cfx_export_expected",
    "cfx_export_found", "cfx_export_copied_path", "viewer_export_file", "viewer_export_path",
    "error_message", "screenshot_path", "duration_sec",
]


class ExcelJobLogger:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.rows: list[dict] = []

    def add_row(self, row: dict) -> None:
        base = {c: "" for c in LOG_COLUMNS}
        base.update(row)
        self.rows.append(base)

    def save(self) -> None:
        df = pd.DataFrame(self.rows, columns=LOG_COLUMNS)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(self.log_path, index=False)
