import win32gui
import win32api
import win32con
import time


def move_click(hwnd, x, y, isLeft=True):
    # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    # win32gui.SetForegroundWindow(hwnd)
    screen_x, screen_y = win32gui.ClientToScreen(hwnd, (x, y))
    win32api.SetCursorPos((screen_x, screen_y))
    if isLeft:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
        time.sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)
    else:
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, screen_x, screen_y, 0, 0)
        time.sleep(0.02)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, screen_x, screen_y, 0, 0)


def press_key(key):
    win32api.keybd_event(key, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
