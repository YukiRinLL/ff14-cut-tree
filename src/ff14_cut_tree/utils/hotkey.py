import keyboard


def register_hotkeys(start_capture, stop_capture):
    """注册全局热键"""
    keyboard.add_hotkey('ctrl+f1', start_capture)
    keyboard.add_hotkey('ctrl+f2', stop_capture)
