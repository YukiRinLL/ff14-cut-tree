import logging
import win32con
from ff14_cut_tree.config.common import get_g_handle_hwnd, get_g_frame_capturing
from ff14_cut_tree.config.enums import CutTreeGameStatus
from ff14_cut_tree.ui.window import MainWindows
from ff14_cut_tree.utils.object import capture_window_frame, get_arrow, get_progress, get_news, get_sec, get_cut_btn, \
    get_game_model
from ff14_cut_tree.utils.operation import move_click, press_key
import time
import threading


def start_new_game(hwnd):
    logging.info("开始新游戏")
    move_click(hwnd, 1500, 540, False)
    time.sleep(1)
    move_click(hwnd, 900, 596)
    time.sleep(2)
    move_click(hwnd, 435, 930)
    time.sleep(2)


def cancel_game(hwnd):
    press_key(win32con.VK_ESCAPE)
    time.sleep(1)
    move_click(hwnd, 906, 563)
    time.sleep(1)


def cut_tree(hwnd):
    logging.info("正在砍树...")
    move_click(hwnd, 478, 913)
    time.sleep(2.05)


def try_to_double_game_score(hwnd):
    time.sleep(3.5)
    logging.info("尝试双倍积分")
    move_click(hwnd, 902, 624)
    time.sleep(0.25)


def give_up_double_game_score(hwnd):
    time.sleep(3.5)
    logging.info("放弃双倍积分")
    move_click(hwnd, 1012, 624)
    time.sleep(0.25)


def capture_frame_loop(hwnd):
    logging.info("开始帧画面分析循环")
    if hwnd is None:
        logging.error("未指定捕捉窗口")
        return

    # 当前游戏阶段
    game_stage = CutTreeGameStatus.STOP
    # 指针期望位置
    next_site = 108
    # 指针期望区间
    next_site_iv = 36
    # 最大健康值
    tree_max_health = 0
    # 上次健康值
    tree_last_health = 0
    # 同帧重复次数（防止在读取进度的时候，刚好卡帧）
    same_frame_count = 0
    # 上次箭头位置（防止在读取进度的时候，刚好卡帧）
    last_arrow_site = -1
    # 上次砍树位置
    last_cut_site = -1
    # 是否曾命中核心位置
    have_cut_core = False
    # 待边缘猜测区间
    guess_core = []
    # 是否为边缘打击后的猜测值
    guess_value = False
    # 是否为首次打击
    first_cut = True
    # 检查当前模式（只玩仙人掌）
    check_game_model = False
    # 小局成功次数
    success_count = 0

    while get_g_frame_capturing():
        frame = capture_window_frame()
        if frame is None:
            logging.error("帧获取失败")
            time.sleep(2)
            continue

        logging.info(f"获取帧成功，当前帧大小{frame.shape[1]}x{frame.shape[0]} 当前状态 {game_stage}")
        if get_news(frame) > 0.9:
            logging.info("开始新一局游戏")
            start_new_game(hwnd)
            game_stage = CutTreeGameStatus.ARROW_MOVING
            # 数据重置
            next_site = 108
            next_site_iv = 36
            tree_max_health = 0
            tree_last_health = 0
            same_frame_count = 0
            last_arrow_site = -1
            last_cut_site = -1
            have_cut_core = False
            guess_core = []
            guess_value = False
            first_cut = True
            check_game_model = False
            success_count = 0
            continue

        match game_stage:
            case CutTreeGameStatus.ARROW_MOVING:
                current_arrow_site = get_arrow(frame)
                logging.info(f"当前箭头位置 {current_arrow_site} 上次箭头位置 {last_arrow_site} "
                             f" 重复帧次 {same_frame_count} 核心位置 {next_site} "
                             f" 需要命中范围 {next_site - next_site_iv} - {next_site + next_site_iv}")
                # 基础检查
                if current_arrow_site == -1:
                    logging.error("获取指针位置失败")
                    continue
                # 防止卡帧
                if current_arrow_site == last_arrow_site:
                    same_frame_count += 1
                    if same_frame_count > 600:
                        game_stage = CutTreeGameStatus.CHECK_TREE
                        continue
                else:
                    same_frame_count = 0
                # 判断指针是否在指定区间内
                if (next_site - next_site_iv) < current_arrow_site < (next_site + next_site_iv):
                    if get_cut_btn(frame) < 0.9:
                        logging.info("等待允许击打")
                    elif check_game_model is False and get_game_model(frame) < 0.9:
                        logging.info("非指定游戏模式")
                        check_game_model = True
                        cancel_game(hwnd)
                        game_stage = CutTreeGameStatus.STOP
                        continue
                    else:
                        cut_tree(hwnd)
                        if first_cut:
                            tree_max_health = get_progress(frame)
                            tree_last_health = tree_max_health
                            logging.info(f"设置最大进度条值 {tree_max_health}")
                            first_cut = False
                        last_cut_site = current_arrow_site
                        game_stage = CutTreeGameStatus.CHECK_TREE
                last_arrow_site = current_arrow_site

            case CutTreeGameStatus.CHECK_TREE:
                current_tree_health = get_progress(frame)
                logging.info(f"当前树生命值 {current_tree_health} 上次生命值  {tree_last_health}")
                if current_tree_health < 0.01:
                    logging.info("生命值为0，判断是否加倍")
                    game_stage = CutTreeGameStatus.JUDGE_DOUBLE
                elif abs(current_tree_health - tree_max_health) < 0.01:
                    logging.info("初始尝试定位失败，重新定位")
                    next_site = next_site + 72 if next_site + 72 < 360 else 36
                    game_stage = CutTreeGameStatus.ARROW_MOVING
                elif abs(tree_last_health - current_tree_health) > 0.01:
                    logging.info(f"生命值减少，记录当前位置 {last_cut_site}")
                    next_site_iv = 20
                    reduce = abs(tree_last_health - current_tree_health)
                    if reduce < 0.2:
                        if have_cut_core:
                            logging.info("挥斧小失误")
                        else:
                            logging.info("未命中核心位置，需要调整角度 oooooooooooooooooooooooooooooooooooooooooooooo")
                            if len(guess_core) == 0:
                                # 往后调整
                                guess_core.append(last_cut_site + 60 if last_cut_site + 60 < 340 else 340)
                                # 往前调整
                                guess_core.append(last_cut_site - 30 if last_cut_site - 30 > 20 else 20)
                                # 中间调整（当前情况）
                                guess_core.append(last_cut_site + 15 if last_cut_site + 15 < 340 else 340)
                                guess_value = True
                                logging.info(f"尝试值核心数组 {guess_core}")
                            if len(guess_core) == 1:
                                next_site = guess_core[0]
                                logging.info(f"下次尝试值范围核心 {next_site} ")
                            else:
                                next_site = guess_core.pop(0)
                                logging.info(f"下次尝试值范围核心 {next_site} ")
                    else:
                        logging.info("命中核心位置 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ")
                        if have_cut_core is False:
                            if guess_value:
                                next_site = last_cut_site
                            else:
                                next_site = last_cut_site + 15 if last_cut_site + 15 < 340 else 340
                        have_cut_core = True
                    tree_last_health = current_tree_health
                    game_stage = CutTreeGameStatus.ARROW_MOVING
                else:
                    if have_cut_core:
                        logging.info("挥斧大失误")
                    else:
                        logging.info("尝试边缘猜测失败，尝试另一侧区间")
                        if len(guess_core) == 1:
                            next_site = guess_core[0]
                            logging.info(f"下次尝试值范围核心 {next_site} ")
                        else:
                            next_site = guess_core.pop(0)
                            logging.info(f"下次尝试值范围核心 {next_site} ")
                    game_stage = CutTreeGameStatus.ARROW_MOVING
            case CutTreeGameStatus.JUDGE_DOUBLE:
                remain = get_sec(frame)
                logging.info(f"此前成功次数 {success_count} ")
                if (success_count > 2 and remain < 20) or remain < 15:
                    give_up_double_game_score(hwnd)
                else:
                    try_to_double_game_score(hwnd)
                game_stage = CutTreeGameStatus.ARROW_MOVING
                # 数据重置
                next_site = 108
                next_site_iv = 36
                tree_max_health = 0
                tree_last_health = 0
                same_frame_count = 0
                last_arrow_site = -1
                last_cut_site = -1
                have_cut_core = False
                guess_core = []
                guess_value = False
                first_cut = True
                check_game_model = True
                success_count += 1


def app_start_capture():
    hwnd = get_g_handle_hwnd()
    if hwnd is None:
        logging.error("未指定捕捉窗口")
        return False
    logging.info("开始捕捉窗口")

    # 启动子线程
    capture_thread = threading.Thread(target=capture_frame_loop, args=(hwnd,))
    capture_thread.daemon = True
    capture_thread.start()

    return True


def app_stop_capture():
    logging.info("停止捕捉窗口")
    return True


def main():
    # 初始化UI
    win = MainWindows(app_start_capture, app_stop_capture)
    win.run()


if __name__ == "__main__":
    main()
