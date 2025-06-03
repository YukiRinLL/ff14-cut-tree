g_handle_hwnd = None
g_capture_thread = None
g_frame_capturing = None


def update_g_handle_hwnd(handle_hwnd):
    global g_handle_hwnd
    g_handle_hwnd = handle_hwnd


def get_g_handle_hwnd():
    global g_handle_hwnd
    return g_handle_hwnd


def update_g_frame_capturing(frame_capturing):
    global g_frame_capturing
    g_frame_capturing = frame_capturing


def get_g_frame_capturing():
    global g_frame_capturing
    return g_frame_capturing
