from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from modules.cfx_controller import CFXController
from modules.file_manager import (
    copy_or_move,
    create_job_folders,
    expected_cfx_export_file,
    find_pcrd_files,
    next_viewer_export_name,
)
from modules.logger_excel import ExcelJobLogger
from modules.rule_loader import detect_product, load_rules
from modules.utils import take_screenshot
from modules.viewer_controller import ViewerController

logger = logging.getLogger(__name__)


def run_batch_job(cfg: dict, status_var=None):
    def set_status(msg: str):
        logger.info(msg)
        if status_var is not None:
            status_var.set(msg)

    job_name = cfg["job_name"]
    base_time = datetime.strptime(cfg["base_time"], "%Y-%m-%d %H:%M")
    expected_count = int(cfg["expected_count"])

    folders = create_job_folders(Path(cfg["result_root_folder"]), job_name)
    if cfg.get("viewer_export_folder"):
        folders["viewer_export"] = Path(cfg["viewer_export_folder"])
        folders["viewer_export"].mkdir(parents=True, exist_ok=True)

    rules = load_rules(Path(cfg["rules_excel_path"]))
    pcrd_files = find_pcrd_files(Path(cfg["pcrd_watch_folder"]), base_time)
    if not pcrd_files:
        raise RuntimeError("기준 시각 이후 .pcrd 파일이 없습니다.")
    if len(pcrd_files) != expected_count:
        set_status(f"경고: 예상 {expected_count}개 / 실제 {len(pcrd_files)}개")

    log_path = folders["logs"] / f"{job_name}_log.xlsx"
    xlogger = ExcelJobLogger(log_path)

    cfx = CFXController(cfg["cfx_manager_path"], int(cfg["default_wait_cfx_export_sec"]))
    viewer = ViewerController(
        cfg["seegene_viewer_path"],
        cfg.get("user_id", ""),
        cfg.get("password", ""),
        int(cfg["default_wait_viewer_loading_sec"]),
        int(cfg["default_wait_after_apply_sec"]),
    )
    cfx.ensure_running()
    viewer.ensure_running()
    viewer.try_login_if_needed()

    for pcrd in pcrd_files:
        started = datetime.now()
        row = {
            "job_name": job_name,
            "started_at": started.isoformat(),
            "pcrd_file": pcrd.name,
            "pcrd_source_path": str(pcrd),
            "status": "FAILED",
        }
        try:
            rule = detect_product(pcrd.name, rules)
            row["product_keyword"] = str(rule["filename_keyword"])
            row["product_code"] = str(rule["product_code"])
            row["viewer_apply_text"] = str(rule["viewer_apply_text"])

            copied_pcrd = copy_or_move(pcrd, folders["pcrd_raw"] / pcrd.name, cfg.get("copy_or_move_pcrd", "copy"))
            row["pcrd_copied_path"] = str(copied_pcrd)

            cfx.open_pcrd(copied_pcrd)
            cfx.set_no_baseline()
            cfx.seegene_export()

            exp = expected_cfx_export_file(copied_pcrd, Path(cfg["quantstep4_folder"]))
            row["cfx_export_expected"] = str(exp)
            if not exp.exists():
                raise RuntimeError("CFX export 파일 미생성")
            row["cfx_export_found"] = str(exp)
            copied_xlsx = copy_or_move(exp, folders["cfx_export"] / exp.name, "copy")
            row["cfx_export_copied_path"] = str(copied_xlsx)

            viewer.open_xlsx(copied_xlsx)
            viewer.select_product(rule)
            viewer.apply_and_check_sample(int(cfg["sample_no_checkbox_x"]), int(cfg["sample_no_checkbox_y"]))
            out_name = next_viewer_export_name(folders["viewer_export"], str(rule["filename_keyword"]), datetime.now())
            out_path = folders["viewer_export"] / out_name
            viewer.export_to(out_path)
            if not out_path.exists():
                raise RuntimeError("Viewer export 파일 생성 확인 실패")
            row["viewer_export_file"] = out_name
            row["viewer_export_path"] = str(out_path)
            row["status"] = "SUCCESS"
        except Exception as e:
            row["step_failed"] = "runtime"
            row["error_message"] = str(e)
            ss = take_screenshot(folders["screenshots"], pcrd.stem)
            row["screenshot_path"] = str(ss)
            if not cfg.get("continue_on_error", True):
                xlogger.add_row(row)
                raise
        finally:
            row["ended_at"] = datetime.now().isoformat()
            row["duration_sec"] = (datetime.now() - started).total_seconds()
            xlogger.add_row(row)
            try:
                cfx.close_current_analysis()
            except Exception:
                pass

    xlogger.save()


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    from modules.gui import launch_gui

    config_path = Path(__file__).resolve().parent / "config.json"
    launch_gui(config_path)


if __name__ == "__main__":
    main()
