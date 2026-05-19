from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import traceback

from .utils import load_json, save_json
from main import run_batch_job


class App:
    def __init__(self, root: tk.Tk, config_path: Path):
        self.root = root
        self.config_path = config_path
        self.cfg = load_json(config_path)
        self.status = tk.StringVar(value="대기 중")
        self.vars: dict[str, tk.Variable] = {}
        self._setup_window()
        self._setup_styles()
        self._build()

    def _setup_window(self):
        self.root.title(f"{self.cfg.get('app_name','PAT')} - Process Automation Tool")
        self.root.geometry("1180x780")
        self.root.minsize(1080, 720)
        self.root.configure(bg="#F3F6FB")

        icon_path = Path(str(self.cfg.get("icon_path", "assets/pat_icon.ppm")))
        if icon_path.exists():
            try:
                self._icon_img = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, self._icon_img)
            except Exception:
                pass

    def _setup_styles(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("App.TFrame", background="#F3F6FB")
        style.configure("Card.TFrame", background="#FFFFFF", relief="flat")
        style.configure("Title.TLabel", background="#1E2A3A", foreground="#FFFFFF", font=("Segoe UI", 18, "bold"))
        style.configure("SubTitle.TLabel", background="#1E2A3A", foreground="#CED8E5", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe", background="#FFFFFF", foreground="#1E2A3A", font=("Segoe UI", 10, "bold"))
        style.configure("Section.TLabelframe.Label", background="#FFFFFF", foreground="#1E2A3A")
        style.configure("Field.TLabel", background="#FFFFFF", foreground="#263446", font=("Segoe UI", 9))
        style.configure("Status.TLabel", background="#EAF2FF", foreground="#0A3E8A", font=("Segoe UI", 10, "bold"))
        style.configure("Run.TButton", font=("Segoe UI", 10, "bold"))

    def _browse_path(self, key: str):
        current = self.vars[key].get()
        is_file = key.endswith("_path") or key == "rules_excel_path"
        if is_file:
            selected = filedialog.askopenfilename(initialdir=current if current else None)
        else:
            selected = filedialog.askdirectory(initialdir=current if current else None)
        if selected:
            self.vars[key].set(selected)

    def _add_field(self, parent, row: int, key: str, label: str, width: int = 54, password: bool = False):
        ttk.Label(parent, text=label, style="Field.TLabel").grid(row=row, column=0, padx=(8, 8), pady=5, sticky="w")
        var = tk.StringVar(value=str(self.cfg.get(key, "")))
        ttk.Entry(parent, textvariable=var, width=width, show="*" if password else "").grid(
            row=row, column=1, padx=(0, 8), pady=5, sticky="we"
        )
        self.vars[key] = var

    def _add_path_field(self, parent, row: int, key: str, label: str):
        self._add_field(parent, row, key, label)
        ttk.Button(parent, text="찾아보기", command=lambda k=key: self._browse_path(k)).grid(
            row=row, column=2, padx=(0, 8), pady=5, sticky="e"
        )

    def _build(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=14)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="Card.TFrame")
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, bg="#1E2A3A", height=4).pack(fill="x")
        ttk.Label(header, text="PAT (Process Automation Tool)", style="Title.TLabel").place(x=16, y=12)
        ttk.Label(header, text="PCRD → CFX → Seegene Viewer 자동화 · 단계 검증 · 로그/스크린샷 자동 기록", style="SubTitle.TLabel").place(x=18, y=46)

        content = ttk.Frame(outer, style="App.TFrame")
        content.pack(fill="both", expand=True)

        left = ttk.LabelFrame(content, text="기본 작업 정보", style="Section.TLabelframe", padding=10)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        left.columnconfigure(1, weight=1)

        self._add_field(left, 0, "job_name", "작업명")
        self._add_field(left, 1, "base_time", "기준 시각 (YYYY-MM-DD HH:MM)")
        self._add_field(left, 2, "expected_count", "예상 pcrd 파일 개수")
        self._add_field(left, 3, "user_id", "Viewer User ID")
        self._add_field(left, 4, "password", "Viewer Password", password=True)

        self.vars["copy_or_move_pcrd"] = tk.StringVar(value=str(self.cfg.get("copy_or_move_pcrd", "copy")))
        ttk.Label(left, text="원본 pcrd 처리 방식", style="Field.TLabel").grid(row=5, column=0, padx=(8, 8), pady=5, sticky="w")
        ttk.Combobox(left, values=["copy", "move"], textvariable=self.vars["copy_or_move_pcrd"], state="readonly", width=20).grid(
            row=5, column=1, padx=(0, 8), pady=5, sticky="w"
        )

        self.vars["continue_on_error"] = tk.BooleanVar(value=bool(self.cfg.get("continue_on_error", True)))
        ttk.Checkbutton(left, text="오류 발생 시 다음 파일 계속 진행", variable=self.vars["continue_on_error"]).grid(
            row=6, column=1, padx=(0, 8), pady=5, sticky="w"
        )

        right = ttk.LabelFrame(content, text="경로 및 실행 설정", style="Section.TLabelframe", padding=10)
        right.pack(side="left", fill="both", expand=True)
        right.columnconfigure(1, weight=1)

        path_rows = [
            ("pcrd_watch_folder", "PCRD 인식 폴더"),
            ("quantstep4_folder", "QuantStep4 폴더"),
            ("result_root_folder", "결과 root 폴더"),
            ("viewer_export_folder", "Viewer export 저장 폴더(옵션)"),
            ("cfx_manager_path", "CFX Manager DX 실행 파일"),
            ("seegene_viewer_path", "Seegene Viewer 실행 파일"),
            ("rules_excel_path", "rules.xlsx 경로"),
        ]
        for idx, (key, label) in enumerate(path_rows):
            self._add_path_field(right, idx, key, label)

        footer = ttk.Frame(outer, style="App.TFrame")
        footer.pack(fill="x", pady=(10, 0))

        ttk.Button(footer, text="실행", style="Run.TButton", command=self.run).pack(side="left", padx=(0, 8))
        ttk.Button(footer, text="설정 저장", command=self.save_cfg).pack(side="left", padx=(0, 8))
        ttk.Button(footer, text="종료", command=self.root.quit).pack(side="left")
        ttk.Label(footer, textvariable=self.status, style="Status.TLabel", anchor="w").pack(side="right", fill="x", expand=True)

    def _collect_cfg(self):
        data = self.cfg.copy()
        for k, v in self.vars.items():
            data[k] = v.get()
        return data

    def save_cfg(self):
        self.cfg = self._collect_cfg()
        save_json(self.config_path, self.cfg)
        self.status.set("설정을 저장했습니다.")
        messagebox.showinfo("저장", "설정을 저장했습니다.")

    def run(self):
        try:
            self.cfg = self._collect_cfg()
            save_json(self.config_path, self.cfg)
            self.status.set("작업 실행 중...")
            self.root.update_idletasks()
            run_batch_job(self.cfg, self.status)
            self.status.set("작업 완료")
            messagebox.showinfo("완료", "작업이 완료되었습니다.")
        except Exception:
            self.status.set("오류 발생")
            messagebox.showerror("오류", traceback.format_exc())


def launch_gui(config_path: Path):
    root = tk.Tk()
    App(root, config_path)
    root.mainloop()
