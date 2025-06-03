import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
import win32gui

from ff14_cut_tree.config.common import update_g_handle_hwnd, update_g_frame_capturing, get_g_frame_capturing
from ff14_cut_tree.utils.hotkey import register_hotkeys


class MainWindows:
    def __init__(self, start_capture, stop_capture):
        # 数据定义
        self._start_capture = start_capture
        self._stop_capture = stop_capture
        # UI定义
        self.stop_btn = None
        self.start_btn = None
        self.window_combo = None
        self.window_var = None
        self.root = None
        # UI构建
        self.setup_gui()
        # 注册热键
        register_hotkeys(self.on_start_capture, self.on_stop_capture)

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("窗口帧捕捉分析器")
        self.root.geometry("420x200+50+50")

        # 窗口选择框
        frame1 = ttk.Frame(self.root)
        frame1.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(frame1, text="目标窗口:").pack(side=tk.LEFT)
        self.window_var = tk.StringVar()
        self.window_combo = ttk.Combobox(frame1, textvariable=self.window_var, width=50)
        self.window_combo.pack(side=tk.LEFT, padx=5)

        # 控制按钮区域，按钮居中
        frame2 = ttk.Frame(self.root)
        frame2.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        self.start_btn = ttk.Button(frame2, text="开始捕捉 (Ctrl+F1)", command=self.on_start_capture)
        self.start_btn.pack(padx=5, anchor='center')

        frame3 = ttk.Frame(self.root)
        frame3.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)

        self.stop_btn = ttk.Button(frame3, text="停止捕捉 (Ctrl+F2)", command=self.on_stop_capture, state=tk.DISABLED)
        self.stop_btn.pack(padx=5, anchor='center')

        # 状态显示按钮居中
        frame4 = ttk.Frame(self.root)
        frame4.pack(fill=tk.BOTH, padx=10, pady=5, expand=True)
        ttk.Button(frame4, text="刷新窗口列表", command=self.refresh_windows).pack(padx=5, anchor='center')

        self.refresh_windows()

    def on_start_capture(self):
        if get_g_frame_capturing():
            return
        update_g_frame_capturing(True)
        window_info = self.window_var.get()
        if not window_info:
            logging.error("未指定捕捉窗口")
            update_g_frame_capturing(False)
            return
        try:
            new_hwnd = int(window_info.split('(')[-1].split(')')[0])
            update_g_handle_hwnd(new_hwnd)
            logging.info(f"窗口句柄获取成功： {new_hwnd}")
        except:
            logging.error("窗口句柄获取失败")
            update_g_frame_capturing(False)
            return

        ret = self._start_capture()
        if ret:
            self.start_btn['state'] = tk.DISABLED
            self.stop_btn['state'] = tk.NORMAL
        else:
            update_g_frame_capturing(False)

    def on_stop_capture(self):
        if not get_g_frame_capturing():
            return
        update_g_frame_capturing(False)

        ret = self._stop_capture()
        if ret:
            self.start_btn['state'] = tk.NORMAL
            self.stop_btn['state'] = tk.DISABLED
        else:
            update_g_frame_capturing(True)

    def refresh_windows(self):
        windows = []

        def enum_windows_proc(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if window_text:
                    windows.append(f"{window_text} ({hwnd})")
            return True

        win32gui.EnumWindows(enum_windows_proc, 0)
        self.window_combo['values'] = windows

    def run(self):
        self.root.mainloop()
