from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import traceback

from .cfx_controller import CFXController
from .file_manager import copy_or_move, create_job_folders, expected_cfx_export_file, find_pcrd_files, next_viewer_export_name
from .logger_excel import ExcelJobLogger
from .rule_loader import detect_product, load_rules
from .utils import load_json, save_json, take_screenshot
from ..main import run_batch_job


class App:
    def __init__(self, root: tk.Tk, config_path: Path):
        self.root = root
        self.config_path = config_path
        self.cfg = load_json(config_path)
        self.status = tk.StringVar(value="Ready")
        self._build()

    def _add_path_row(self, parent, row, key, label):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w")
        var = tk.StringVar(value=self.cfg.get(key, ""))
        ttk.Entry(parent, textvariable=var, width=70).grid(row=row, column=1, sticky="we")
        ttk.Button(parent, text="Browse", command=lambda: var.set(filedialog.askopenfilename() if key.endswith("_path") or key=="rules_excel_path" else filedialog.askdirectory())).grid(row=row, column=2)
        self.vars[key] = var

    def _build(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)
        self.vars = {}
        basic = [
            ("job_name", "작업명"),
            ("base_time", "기준 시각(YYYY-MM-DD HH:MM)"),
            ("expected_count", "예상 pcrd 파일 개수"),
            ("user_id", "Viewer User ID"),
            ("password", "Viewer Password"),
        ]
        for i, (k, l) in enumerate(basic):
            ttk.Label(frm, text=l).grid(row=i, column=0, sticky="w")
            var = tk.StringVar(value=self.cfg.get(k, ""))
            ttk.Entry(frm, textvariable=var, width=70, show="*" if k == "password" else "").grid(row=i, column=1, sticky="we", columnspan=2)
            self.vars[k] = var
        start = len(basic)
        self._add_path_row(frm, start + 0, "pcrd_watch_folder", "PCRD 인식 폴더")
        self._add_path_row(frm, start + 1, "quantstep4_folder", "QuantStep4 폴더")
        self._add_path_row(frm, start + 2, "result_root_folder", "결과 root 폴더")
        self._add_path_row(frm, start + 3, "viewer_export_folder", "Viewer export 저장 폴더(옵션)")
        self._add_path_row(frm, start + 4, "cfx_manager_path", "CFX Manager DX 실행 파일")
        self._add_path_row(frm, start + 5, "seegene_viewer_path", "Seegene Viewer 실행 파일")
        self._add_path_row(frm, start + 6, "rules_excel_path", "rules.xlsx 경로")

        self.vars["copy_or_move_pcrd"] = tk.StringVar(value=self.cfg.get("copy_or_move_pcrd", "copy"))
        ttk.Combobox(frm, values=["copy", "move"], textvariable=self.vars["copy_or_move_pcrd"]).grid(row=start+7, column=1, sticky="w")
        self.vars["continue_on_error"] = tk.BooleanVar(value=bool(self.cfg.get("continue_on_error", True)))
        ttk.Checkbutton(frm, text="오류 발생 시 다음 파일 계속", variable=self.vars["continue_on_error"]).grid(row=start+8, column=1, sticky="w")

        ttk.Button(frm, text="실행", command=self.run).grid(row=start+9, column=0)
        ttk.Button(frm, text="중지", command=self.root.quit).grid(row=start+9, column=1)
        ttk.Button(frm, text="설정 저장", command=self.save_cfg).grid(row=start+9, column=2)
        ttk.Label(frm, textvariable=self.status).grid(row=start+10, column=0, columnspan=3, sticky="w")

    def save_cfg(self):
        for k, v in self.vars.items():
            self.cfg[k] = v.get()
        save_json(self.config_path, self.cfg)
        messagebox.showinfo("저장", "설정을 저장했습니다.")

    def run(self):
        try:
            self.save_cfg()
            run_batch_job(self.cfg, self.status)
            messagebox.showinfo("완료", "작업이 완료되었습니다.")
        except Exception as e:
            self.status.set(f"오류: {e}")
            messagebox.showerror("오류", traceback.format_exc())


def launch_gui(config_path: Path):
    root = tk.Tk()
    root.title("PCRD-CFX-Seegene Viewer 자동화")
    App(root, config_path)
    root.mainloop()
