from __future__ import annotations

from pathlib import Path
import subprocess
import time

from pywinauto import Application


class CFXController:
    def __init__(self, cfx_path: str, wait_export_sec: int = 20):
        self.cfx_path = cfx_path
        self.wait_export_sec = wait_export_sec
        self.app = None

    def ensure_running(self):
        try:
            self.app = Application(backend="uia").connect(path=self.cfx_path)
        except Exception:
            subprocess.Popen([self.cfx_path])
            time.sleep(5)
            self.app = Application(backend="uia").connect(path=self.cfx_path)

    def _main_window(self):
        return self.app.top_window()

    def open_pcrd(self, pcrd_path: Path):
        w = self._main_window()
        w.set_focus()
        w.type_keys("%FOD")
        time.sleep(1)
        w.type_keys(str(pcrd_path), with_spaces=True)
        w.type_keys("{ENTER}")
        time.sleep(5)

    def set_no_baseline(self):
        w = self._main_window()
        w.set_focus()
        w.type_keys("%S{DOWN}{RIGHT}{ENTER}")
        time.sleep(1)

    def seegene_export(self):
        w = self._main_window()
        w.set_focus()
        w.type_keys("%E{DOWN 3}{ENTER}{ENTER}")
        time.sleep(self.wait_export_sec)
        w.type_keys("{ENTER}")

    def close_current_analysis(self):
        w = self._main_window()
        w.set_focus()
        w.type_keys("^w")
        time.sleep(1)
