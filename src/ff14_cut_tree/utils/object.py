import logging

import cv2
import numpy as np
from PIL import Image
import win32gui
import win32ui
import win32con
from ff14_cut_tree.config.common import get_g_handle_hwnd
import cv2
import pytesseract

from ff14_cut_tree import GAME_OBJ_SITE_PROGRESS, GAME_OBJ_SITE_SEC, GAME_OBJ_SITE_ARROW, GAME_OBJ_SITE_NEWS, \
    GAME_OBJ_SITE_CUT_BTN, GAME_OBJ_SITE_MODEL


def is_mostly_color(image, target_color, threshold=60):
    """判断颜色相似"""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    pixels = np.array(pil_image)
    # 计算每个像素与目标颜色的欧几里得距离
    diff = np.linalg.norm(pixels - np.array(target_color), axis=-1)
    # 判断有多少像素的颜色接近目标颜色
    match_pixels = np.sum(diff <= threshold)
    total_pixels = pixels.shape[0] * pixels.shape[1]
    # 比较匹配比例是否大于设定的比例
    match_ratio = match_pixels / total_pixels
    return match_ratio


def get_game_model(frame):
    """获取砍树按钮"""
    try:
        x, y, w, h = GAME_OBJ_SITE_MODEL
        cropped = frame[y:y + h, x:x + w]
        # cv2.imwrite("./game_model.jpg", cropped)
        return is_mostly_color(cropped, (86, 118, 44))
    except:
        return -1


def get_cut_btn(frame):
    """获取砍树按钮"""
    try:
        x, y, w, h = GAME_OBJ_SITE_CUT_BTN
        cropped = frame[y:y + h, x:x + w]
        # cv2.imwrite("./cut_btn.jpg", cropped)
        return is_mostly_color(cropped, (255, 192, 193))
    except:
        return -1


def get_progress(frame):
    """获取当前进度条"""
    try:
        x, y, w, h = GAME_OBJ_SITE_PROGRESS
        cropped = frame[y:y + h, x:x + w]
        # cv2.imwrite("./progress.jpg", cropped)
        return is_mostly_color(cropped, (95, 211, 191))
    except:
        return -1


def get_sec(frame):
    """获取当前剩余秒"""
    num = 0
    try:
        x, y, w, h = GAME_OBJ_SITE_SEC
        cropped = frame[y:y + h, x:x + w]
        # cv2.imwrite("./sec.jpg", cropped)
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        # 二值化 + 反色（亮字黑底）
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # 放大图像提高识别率
        resized = cv2.resize(binary, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
        # OCR 识别，仅限数字和冒号
        config = r'--psm 6 -c tessedit_char_whitelist=0123456789:'
        text = pytesseract.image_to_string(resized, config=config)
        logging.info(f"获取剩余时间文字 {text.strip()}")
        num = int(text.strip().replace(":", ""))
    except Exception as e:
        logging.error(f"捕捉帧时出错: {e}")
    logging.info(f"获取剩余时间文字值 = {num}")
    return num


def get_arrow(frame):
    """获取当前指针位置"""
    x, y, w, h = GAME_OBJ_SITE_ARROW
    cropped = frame[y:y + h, x:x + w]
    # cv2.imwrite("./arrow.jpg", cropped)
    # 转换为灰度图
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    # 阈值处理，提取白色区域
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 找到最大的白色区域（假设箭头是最显眼的白色物体）
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        # 过滤太小的区域
        if w * h > 200:
            return y + (h / 2)
    return -1


def get_news(frame):
    """获取右上角资讯中心，判断是否在游戏中"""
    try:
        x, y, w, h = GAME_OBJ_SITE_NEWS
        cropped = frame[y:y + h, x:x + w]
        # cv2.imwrite("./news.jpg", cropped)
        return is_mostly_color(cropped, (48, 48, 48))
    except:
        return -1


def capture_window_frame():
    """捕捉当前窗口的帧"""
    try:
        hwnd = get_g_handle_hwnd()
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        width = right - left
        height = bottom - top

        # 获取客户区左上角在屏幕的位置
        screen_left, screen_top = win32gui.ClientToScreen(hwnd, (0, 0))

        # 获取设备上下文
        hwin = win32gui.GetDesktopWindow()
        hwindc = win32gui.GetWindowDC(hwin)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()

        # 创建位图对象
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)

        # 从屏幕复制客户区的图像
        memdc.BitBlt((0, 0), (width, height), srcdc,
                     (screen_left, screen_top), win32con.SRCCOPY)

        # 将图像转换为 numpy array
        bmpinfo = bmp.GetInfo()
        bmpstr = bmp.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight'])
                               , bmpstr, 'raw', 'BGRX', 0, 1)
        mat = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # 释放资源
        win32gui.DeleteObject(bmp.GetHandle())
        memdc.DeleteDC()
        srcdc.DeleteDC()
        win32gui.ReleaseDC(hwin, hwindc)

        # cv2.imwrite("./frame.jpg", mat)
        return mat

    except Exception as e:
        logging.error(f"捕捉帧时出错: {e}")
        return None
