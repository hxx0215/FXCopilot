from tasks.base.ui import UI

from tasks.base.page import page_mail
from module.logger import logger
from .assets import *
from module.ocr.ocr import Ocr,DataDigit
from tasks.base.assets.assets_base_page import GET_ITEMS
import re

class Mail(UI):
    def check_current_mail_remain_days(self):
        ocr = Ocr(MAIL_REMAIN_DAYS)
        days = 30
        for image in self.loop():
            content = ocr.ocr_single_line(image)
            match = re.search(r'\d+', content)
            if match:
                days = int(match.group(0))
                break
        return days

    def open_mail(self):
        remain_ocr = DataDigit(MAIL_REMAIN_COUNT)
        current_remain_mail = None
        for _ in self.loop():
            if self.appear_then_click(MAIL_OPEN):
                break
        reward_show = 0
        for _ in self.loop():
            if reward_show == 1 and (not self.appear(GET_ITEMS)):
                break
            if self.appear_then_click(GET_ITEMS):
                reward_show = 1
        for image in self.loop():
            remain_count = remain_ocr.ocr_single_line(image);
            if remain_count:
                current_remain_mail = remain_count
                break
        logger.info(f'current remain mail {current_remain_mail}')
        for image in self.loop():
            self.appear_then_click(MAIL_DELETE)
            remain_count = remain_ocr.ocr_single_line(image)
            if remain_count and remain_count < current_remain_mail:
                break
            self.device.sleep((0.5,0.8))

    def run(self):
        self.ui_ensure(page_mail)
        self.device.screenshot()
        self.ui_click(MAIL_WILL_EXPIRED_UNSELECTED, MAIL_WILL_EXPIRED_SELECTED, similarity=0.98)
        while 1:
            days = self.check_current_mail_remain_days()
            if days <= 1:
                self.open_mail()
            else:
                logger.info('open mail finished')
                break
        self.config.task_delay(server_update=True)
if __name__ == '__main__':
    task = Mail('fxc', task='Mail')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    task.image_file=image_path
    b = task.appear(MAIL_WILL_EXPIRED_UNSELECTED)
    print(b)
    print(MAIL_WILL_EXPIRED_UNSELECTED.button)