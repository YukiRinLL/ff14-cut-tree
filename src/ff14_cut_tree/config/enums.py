from enum import Enum


class CutTreeGameStatus(Enum):
    # 游戏未开始
    STOP = 0
    # 是否在指针移动阶段
    ARROW_MOVING = 1
    # 是否在判断树木生命值阶段
    CHECK_TREE = 2
    # 是否在判断是否尝试双倍积分阶段
    JUDGE_DOUBLE = 3
