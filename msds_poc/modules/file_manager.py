from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil


def create_job_folders(result_root: Path, job_name: str) -> dict[str, Path]:
    job_root = result_root / job_name
    folders = {
        "job_root": job_root,
        "pcrd_raw": job_root / "01_pcrd_raw",
        "cfx_export": job_root / "02_cfx_export",
        "viewer_export": job_root / "03_viewer_export",
        "logs": job_root / "04_logs",
        "screenshots": job_root / "05_screenshots",
    }
    for p in folders.values():
        p.mkdir(parents=True, exist_ok=True)
    return folders


def find_pcrd_files(folder: Path, since_dt: datetime) -> list[Path]:
    files = [f for f in folder.glob("*.pcrd") if datetime.fromtimestamp(f.stat().st_mtime) >= since_dt]
    return sorted(files, key=lambda p: p.stat().st_mtime)


def expected_cfx_export_file(pcrd_file: Path, quantstep4_folder: Path) -> Path:
    return quantstep4_folder / f"{pcrd_file.stem} - Quantitation Ct Results.xlsx"


def copy_or_move(src: Path, dst: Path, mode: str = "copy") -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if mode == "move":
        shutil.move(str(src), str(dst))
    else:
        shutil.copy2(src, dst)
    return dst


def next_viewer_export_name(viewer_folder: Path, keyword: str, now: datetime) -> str:
    prefix = now.strftime("%y-%m%d")
    patt = re.compile(rf"^{re.escape(prefix)}_{re.escape(keyword)}_(\d+)\.xlsx$", re.IGNORECASE)
    nums = []
    for f in viewer_folder.glob(f"{prefix}_{keyword}_*.xlsx"):
        m = patt.match(f.name)
        if m:
            nums.append(int(m.group(1)))
    next_n = max(nums) + 1 if nums else 1
    return f"{prefix}_{keyword}_{next_n}.xlsx"
