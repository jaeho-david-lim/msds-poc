from __future__ import annotations

from pathlib import Path
import subprocess
import time

import pyautogui
from pywinauto import Application


class ViewerController:
    def __init__(self, viewer_path: str, user_id: str, password: str, wait_loading_sec: int = 20, wait_after_apply_sec: int = 2):
        self.viewer_path = viewer_path
        self.user_id = user_id
        self.password = password
        self.wait_loading_sec = wait_loading_sec
        self.wait_after_apply_sec = wait_after_apply_sec
        self.app = None

    def ensure_running(self):
        try:
            self.app = Application(backend="uia").connect(path=self.viewer_path)
        except Exception:
            subprocess.Popen([self.viewer_path])
            time.sleep(self.wait_loading_sec)
            self.app = Application(backend="uia").connect(path=self.viewer_path)

    def _window(self):
        return self.app.top_window()

    def try_login_if_needed(self):
        w = self._window()
        if w.child_window(title_re=".*User ID.*|.*Login.*", control_type="Edit").exists(timeout=2):
            edits = w.descendants(control_type="Edit")
            if len(edits) >= 2:
                edits[0].set_edit_text(self.user_id)
                edits[1].set_edit_text(self.password)
                w.type_keys("{ENTER}")
                time.sleep(3)

    def open_xlsx(self, xlsx_path: Path):
        w = self._window()
        w.set_focus()
        w.type_keys("%FO")
        time.sleep(1)
        w.type_keys(str(xlsx_path), with_spaces=True)
        w.type_keys("{ENTER}")
        time.sleep(2)

    def select_product(self, rule: dict):
        w = self._window()
        text = str(rule.get("viewer_apply_text", "")).strip()
        if text:
            el = w.child_window(title=text)
            if el.exists(timeout=2):
                el.click_input()
                return
        img = str(rule.get("product_image", "")).strip()
        if img and Path(img).exists():
            loc = pyautogui.locateCenterOnScreen(img, confidence=0.8)
            if loc:
                pyautogui.click(loc.x, loc.y)
                return
        x, y = rule.get("product_click_x"), rule.get("product_click_y")
        if str(x) and str(y):
            pyautogui.click(int(float(x)), int(float(y)))
            return
        raise RuntimeError("Product Selection 실패")

    def apply_and_check_sample(self, checkbox_x: int, checkbox_y: int):
        w = self._window()
        apply_btn = w.child_window(title_re="Apply|적용")
        if apply_btn.exists(timeout=2):
            apply_btn.click_input()
        else:
            raise RuntimeError("Apply 버튼 탐색 실패")
        time.sleep(self.wait_after_apply_sec)
        pyautogui.click(checkbox_x, checkbox_y)

    def export_to(self, output_file: Path):
        w = self._window()
        w.set_focus()
        w.type_keys("%FE")
        time.sleep(1)
        w.type_keys(str(output_file), with_spaces=True)
        w.type_keys("{ENTER}")
        time.sleep(2)
