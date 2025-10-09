from tasks.base.ui import UI
from tasks.base.page import page_main_line
from .assets import *
from module.logger.logger import logger

class Mainline(UI):
    def make_sure_normal(self):
        for _ in self.loop():
            if self.appear(MAINLINE_NORMAL_ACTIVE):
                break
            if self.appear_then_click(MAINLINE_NORMAL_INACTIVE):
                continue
    def run(self):
        self.ui_ensure(page_main_line)
        self.make_sure_normal()
        logger.info('current in normal mode')
        self.device.sleep(60)
        self.config.task_delay(minute=1)