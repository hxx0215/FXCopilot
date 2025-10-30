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
    def cn2int(self, cn_num: str) -> int:
        pass
    def validate_stage_setting(self) -> bool:
        stage_setting = self.config.MainlineSetting_Stage
        if not stage_setting or '-' not in stage_setting:
            return False
        parts = stage_setting.split('-')
        if len(parts) != 2:
            return False
        try:
            a = int(parts[0])
            b = int(parts[1])
        except ValueError:
            return False
        if not (1 <= a <= 19):
            return False
        if a < 19:
            if not (1 <= b <= 10):
                return False
        elif a == 19:
            if not (1 <= b <= 5):
                return False
        return True
    def run(self):
        if self.validate_stage_setting():
            self.ui_ensure(page_main_line)
            self.make_sure_normal()
            logger.info('current in normal mode')
        else:
            logger.warning('the stage setting is not right please make sure it is x-x')
        self.device.sleep(60)
        self.config.task_delay(minute=1)