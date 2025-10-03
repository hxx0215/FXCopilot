import re

from module.exception import GameStuckError
from tasks.base.ui import UI
from module.logger import logger
from tasks.base.page import page_main_line, page_exercise
from tasks.base.assets.assets_base_page import EXERCISE_PAGE,CONTINUOUS_CHALLENGE_BUTTON,CONTINUOUS_CHALLENGE_ON_BUTTON,EXERCISE_ALL_BUTTON,EXERCISE_ALL_CHECKBOX,EXERCISE_START_HOSTING,EXERCISE_REMAIN_COUNT_DATA,CHANGE_OPPONENT,CLICK_TO_CONTINUE
from module.ocr.ocr import Digit
from module.base.timer import Timer

class DataDigit(Digit):
    def after_process(self, result):
        result = re.sub(r'[l|]', '1', result)
        result = re.sub(r'[oO]', '0', result)
        return super().after_process(result)
class Exercise(UI):
    def _get_remain_count(self):
        timeout = Timer(2, count=6).start()
        ocr = DataDigit(EXERCISE_REMAIN_COUNT_DATA)
        c = -1
        for _ in self.loop():
            remain_count = ocr.detect_and_ocr(self.device.image)
            if len(remain_count) > 0:
                c = [int(re.sub(r'\s','',d.ocr_text)) for d in remain_count][0]
                if c >= 0:
                    break
            logger.warning(f'Invalid remain_count: {remain_count}')
            if timeout.reached():
                logger.warning('Get remain_count timeout')
                break
        logger.info(f"current remain refresh count is: {c}")
        return c
    def start_hosting(self):
        hosting = False
        # 一场战斗最多120s
        max_wait = Timer(120).start()
        for _ in self.loop():
            if (not hosting) and self.appear_then_click(EXERCISE_START_HOSTING):
                hosting = True
                continue
            if self.handle_popup_confirm():
                hosting = False
                break
            if self.appear_then_click(CLICK_TO_CONTINUE):
                max_wait.reset()
                continue
            if max_wait.reached():
                raise GameStuckError
            else:
                self.device.stuck_record_clear()
        logger.info("host 1 turn over")
    def refresh(self):
        logger.info("begining refresh opponent")
        refreshing = False
        for _ in self.loop():
            if self.appear_then_click(CHANGE_OPPONENT) and (not refreshing):
                refreshing = True
                continue
            if self.handle_popup_confirm():
                refreshing = False
                break
        logger.info("refreshed opponents")
    def run(self):
        logger.info("begin daily exercise")
        self.ui_ensure(page_main_line)
        self.device.sleep(0.5)
        self.ui_ensure(page_exercise)
        #确保当前确实没有进入连续挑战（连续挑战直接退出ui会残留)
        for _ in self.loop():
            if self.appear(CONTINUOUS_CHALLENGE_BUTTON):
                break
        #至少测一次是否还能进行演习
        remain_count = 1
        while remain_count:
            self.ui_click(CONTINUOUS_CHALLENGE_BUTTON, CONTINUOUS_CHALLENGE_ON_BUTTON)
            self.ui_click(EXERCISE_ALL_BUTTON, EXERCISE_ALL_CHECKBOX)
            self.start_hosting()
            remain_count = self._get_remain_count()
            if remain_count:
                self.refresh()
            else:
                break;
        logger.info("execise finished")
        self.device.sleep(1)
        self.config.task_delay(server_update=True)

        
if __name__ == '__main__':
    task = Exercise('src', task='Exercise')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test2.png")
    task.image_file=image_path
    b = task.appear(CHANGE_OPPONENT)
    print(b)
