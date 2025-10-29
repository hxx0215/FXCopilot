import re

from module.base.button import ButtonWrapper
from module.exception import GameStuckError, RequestHumanTakeover
from tasks.base.ui import UI
from module.logger import logger
from tasks.base.page import page_main_line, page_exercise,page_season_pass
from tasks.base.assets.assets_base_page import EXERCISE_PAGE,CONTINUOUS_CHALLENGE_BUTTON,CONTINUOUS_CHALLENGE_ON_BUTTON,EXERCISE_ALL_BUTTON,EXERCISE_ALL_CHECKBOX,EXERCISE_START_HOSTING,EXERCISE_REMAIN_COUNT_DATA,CHANGE_OPPONENT,CLICK_TO_CONTINUE, SEASON_PASS_DAILY1,SEASON_PASS_DAILY2,SEASON_PASS_DAILY3,SEASON_PASS_REMAIN,SEASON_PASS_DAILY_TASK,SEASON_PASS_SWITCH_TASK
from module.ocr.ocr import Ocr,DigitCounter
from module.base.timer import Timer

class Exercise(UI):
    def _get_remain_count(self):
        # timeout = Timer(2, count=6).start()
        ocr = DigitCounter(EXERCISE_REMAIN_COUNT_DATA)
        # c = -1
        for image in self.loop():
            (current,remain,total) = ocr.ocr_single_line(image)
            if (current, remain, total) != (0,0,0):
                return current
            # remain_count = ocr.detect_and_ocr(self.device.image)
            # if len(remain_count) > 0:
            #     c = [int(re.sub(r'\s','',d.ocr_text)) for d in remain_count][0]
            #     if c >= 0:
            #         break
            # logger.warning(f'Invalid remain_count: {remain_count}')
            # if timeout.reached():
            #     logger.warning('Get remain_count timeout')
            #     break
        # logger.info(f"current remain refresh count is: {c}")
        # return c
        return 0
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

    def check_should_refresh(self, btn: ButtonWrapper):
        ocr = Ocr(btn)
        for image in self.loop():
            r = ocr.ocr_single_line(image)
            if r!= '':
                return '演习' in r and r != '于演习出战'

    def check_season_pass(self) -> int:
        self.ui_ensure(page_season_pass)
        self.ui_click(SEASON_PASS_SWITCH_TASK,SEASON_PASS_DAILY_TASK)
        ls = [SEASON_PASS_DAILY1,SEASON_PASS_DAILY2,SEASON_PASS_DAILY3]
        refresh = [self.check_should_refresh(item) for item in ls]
        if any(refresh):
            logger.info('季票有任务需要手动刷新')
            raise RequestHumanTakeover
        ocr = Ocr(SEASON_PASS_REMAIN)
        for image in self.loop():
            remain = ocr.ocr_single_line(image)
            if remain != '':
                if '小时' in remain:
                    return 1
                else:
                    return 0
        return 0

    def run(self):
        logger.info("begin daily exercise")
        keep_time = self.check_season_pass()
        self.ui_ensure(page_main_line)
        self.device.sleep(0.5)
        self.ui_ensure(page_exercise)
        #确保当前确实没有进入连续挑战（连续挑战直接退出ui会残留)
        for _ in self.loop():
            if self.appear(CONTINUOUS_CHALLENGE_BUTTON):
                break
        #至少测一次是否还能进行演习
        remain_count = self._get_remain_count()
        while remain_count > keep_time:
            self.ui_click(CONTINUOUS_CHALLENGE_BUTTON, CONTINUOUS_CHALLENGE_ON_BUTTON)
            self.ui_click(EXERCISE_ALL_BUTTON, EXERCISE_ALL_CHECKBOX)
            self.start_hosting()
            remain_count = self._get_remain_count()
            if remain_count > keep_time:
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
