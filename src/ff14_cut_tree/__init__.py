import logging

GAME_OBJ_SITE_PROGRESS = (332, 865, 320, 15)
GAME_OBJ_SITE_SEC = (466, 659, 47, 27)
GAME_OBJ_SITE_ARROW = (439, 514, 260, 360)
GAME_OBJ_SITE_NEWS = (120, 65, 130, 15)
GAME_OBJ_SITE_CUT_BTN = (465, 909, 10, 10)
GAME_OBJ_SITE_MODEL = (395, 639, 10, 10)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s %(levelname)s %(module)s %(funcName)s :%(lineno)d] %(message)s'
)

logging.info(f"Progress: {GAME_OBJ_SITE_PROGRESS}")
logging.info(f"Sec: {GAME_OBJ_SITE_SEC}")
logging.info(f"Arrow: {GAME_OBJ_SITE_ARROW}")
