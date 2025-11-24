from tasks.base.ui import UI
from tasks.base.page import page_task_daily,page_task_event,page_lucky_draw
from .assets.daily_task_assets import *
from tasks.base.assets.assets_base_page import GET_ITEMS
from module.logger.logger import logger
from module.ocr.ocr import DataDigit
from module.base.timer import Timer

class DailyTask(UI):
    def _claim_rewards(self, page):
        self.ui_ensure(page)
        for _ in self.loop():
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.match_color(TASK_COLLECT_ALL) and self.appear(TASK_COLLECT_ALL):
                self.appear_then_click(TASK_COLLECT_ALL)
                continue
            if self.match_color(TASK_COLLECT_ALL_DISABLED) and self.appear(TASK_COLLECT_ALL_DISABLED):
                break

    def claim_daily(self):
        self._claim_rewards(page_task_daily)
        for _ in self.loop():
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.appear_then_click(TASK_DAILY_FINAL):
                continue
            if self.appear(TASK_DAILY_FINAL_GO):
                break
            if self.appear(TASK_DAILY_FINAL_FINISHED):
                break

    def claim_event(self):
        self._claim_rewards(page_task_event)

    def lucky_draw(self):
        self.ui_ensure(page_lucky_draw)
        timer = Timer(3).start()
        ocr = DataDigit(LUCKY_DRAW_POINT)
        point = -1
        can_draw = False
        for image in self.loop():
            if self.appear(LUCKY_DRAW_REMAIN):
                can_draw = True
                timer.reset()
            if self.handle_popup_confirm():
                continue
            if can_draw and self.appear_then_click(LUCKY_DRAW, interval= 3):
                continue
            if self.appear_then_click(GET_ITEMS, interval= 1.5):
                continue
            if timer.reached():
                point = ocr.ocr_single_line(image)
                if point == 0:
                    break
                else:
                    timer.reset()
        # ocr = DataDigit(LUCKY_DRAW_POINT)
        # count = 0
        # for image in self.loop():
        #     if count == 0:
        #         point = ocr.ocr_single_line(image)
        #     if point == 0:
        #         break
        #     else:
        #         count = point
        #     if self.appear_then_click(LUCKY_DRAW, interval= 3):
        #         continue
        #     if self.appear_then_click(GET_ITEMS, interval= 1.5):
        #         count = count - 100
        #         continue


    def run(self):
        self.claim_daily()
        self.claim_event()
        if self.config.LuckyDraw_Enable:
            self.lucky_draw()
        self.config.task_delay(server_update=True,minute=60)


if __name__ == '__main__':
    task = DailyTask('fxc', task='DailyTask')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    task.image_file=image_path
    b = TASK_COLLECT_ALL_DISABLED.match_color(task.device.image)
    print(b)