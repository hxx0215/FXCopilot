from tasks.base.ui import UI
from tasks.base.page import page_task_daily,page_task_event
from .assets.daily_task_assets import *
from tasks.base.assets.assets_base_page import GET_ITEMS
from module.logger.logger import logger

class DailyTask(UI):
    def claim_daily(self):
        self.ui_ensure(page_task_daily)
        for _ in self.loop():
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.match_color(TASK_COLLECT_ALL) and self.appear(TASK_COLLECT_ALL):
                self.appear_then_click(TASK_COLLECT_ALL)
                continue
            if self.match_color(TASK_COLLECT_ALL_DISABLED) and self.appear(TASK_COLLECT_ALL_DISABLED):
                break
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
        self.ui_ensure(page_task_event)
        for _ in self.loop():
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.match_color(TASK_COLLECT_ALL) and self.appear(TASK_COLLECT_ALL):
                self.appear_then_click(TASK_COLLECT_ALL)
                continue
            if self.match_color(TASK_COLLECT_ALL_DISABLED) and self.appear(TASK_COLLECT_ALL_DISABLED):
                break

    def run(self):
        self.claim_daily()
        self.claim_event()
        self.config.task_delay(server_update=True,minute=60)


if __name__ == '__main__':
    task = DailyTask('fxc', task='DailyTask')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    task.image_file=image_path
    b = TASK_COLLECT_ALL_DISABLED.match_color(task.device.image)
    print(b)