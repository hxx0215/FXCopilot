from tasks.base.quick_claim_check import QuickClaimCheck
from tasks.base.page import page_expedition,page_reward
from tasks.base.assets.assets_base_page import EXPEDITION_FINISH_FLAG,EXPEDITION_WAITING,EXPEDITION_COLLECT_ALL,EXPEDITION_FINISH_REWARD,EXPEDITION_WAITING2,EXPEDITION_TIME_DATA,EXPEDITION_READY,EXPEDITION_CURRENT_TEAMS_DATA,EXPEDITION_TIME_SELECT_DATA,EXPEDITION_DEPLOY_ICON_BUTTON,EXPEDITION_AUTO_DEPLOY,EXPEDITION_SAIL,EXPEDITION_RECALL,EXPEDITION_LIMITED_TIME_SELECT_DATA
from module.logger import logger
from module.base.timer import Timer
from module.ocr.ocr import DigitCounter,Ocr,OcrResultButton,QuickClaimTimeOcr
from module.config.utils import server_time_offset, get_server_now,get_server_next_update
from module.base.button import ButtonWrapper
import re
import datetime
from dataclasses import dataclass
from typing import ClassVar
from module.ocr.keyword import Keyword

class TimeExpeditionOcr(Ocr):
    pass
@dataclass(repr=False)
class TimeExpeditionKeyword(Keyword):
    instances: ClassVar = {}
    @classmethod
    def init(cls,id: int, name: str):
        return cls(id,name,cn = name,en = name,jp = name, cht = '',es = '')
class Expedition(QuickClaimCheck):
    def __init__(self, config, device=None, task=None):
        super().__init__(config, device=device, task=task, ocr_data=EXPEDITION_TIME_DATA)
        self.ocr = DigitCounter(EXPEDITION_CURRENT_TEAMS_DATA)

    # def check_remain_time(self):
    #     self.ui_ensure(page_reward)
    #     ocr = QuickClaimTimeOcr(EXPEDITION_TIME_DATA)
    #     for image in self.loop():
    #         (has_item_finished, deltas) = ocr.ocr_single_line(image)
    #         if has_item_finished or len(deltas) != 0:
    #             break
    #     return (has_item_finished, deltas)
    def collect_reward(self):
        self.ui_ensure(page_expedition)
        for image in self.loop():
            if self.appear(EXPEDITION_FINISH_FLAG):
                break
            (current, remain, total) = self.ocr.ocr_single_line(image)
            if remain > 0:
                return
        self.ui_click(EXPEDITION_COLLECT_ALL,EXPEDITION_FINISH_REWARD)
        cnt = 0
        check = False
        for _ in self.loop():
            if self.appear_then_click(EXPEDITION_FINISH_REWARD):
                check = True
                continue
            if check and not self.appear(EXPEDITION_FINISH_REWARD):
                cnt += 1
                if cnt > 10:
                    break
                else:
                    continue
        timer = Timer(3, 10).start()
        for _ in self.loop():
            (current, remain, total) = self.ocr.ocr_single_line(image)
            if remain > 0:
                return
            if timer.reached():
                break
    def select_expedition_page(self, page_name: str, button: ButtonWrapper):
        keywords_str = ['2小时','4小时','8小时','12小时']
        keywords = [TimeExpeditionKeyword.init(idx,k) for (idx,k) in enumerate(keywords_str)]
        ocr = TimeExpeditionOcr(button)
        for image in self.loop():
            r = ocr.matched_ocr(image, keyword_classes=keywords)
            if len(r) > 0:
                btn: OcrResultButton | None = next((item for item in r if item.text == page_name), None)
                if btn:
                    self.ui_ocr_button_click(btn)
                    return
                
    def deploy_next_expedition(self):
        current_time = get_server_now()
        server_special_expedition_start_time = current_time.replace(hour=18)
        server_special_expedition_end_time = current_time.replace(hour=23,minute=59,second=59)
        if current_time < server_special_expedition_start_time:
            delta = server_special_expedition_start_time - current_time
            eight_hour = 8 * 60 * 60
            four_hour = 4 * 60 * 60
            ten_minute = 60 * 10
            if delta.total_seconds() < ten_minute:
                next_time = get_server_next_update('18:00')
                self.config.task_delay(target=next_time)
            if delta.total_seconds() > eight_hour:
                self.select_expedition_page('8小时',EXPEDITION_TIME_SELECT_DATA)
            elif delta.total_seconds() > four_hour:
                self.select_expedition_page('4小时',EXPEDITION_TIME_SELECT_DATA)
            else:
                self.select_expedition_page('2小时',EXPEDITION_TIME_SELECT_DATA)
        if current_time >= server_special_expedition_start_time and current_time < server_special_expedition_end_time:
            self.select_expedition_page('12小时',EXPEDITION_LIMITED_TIME_SELECT_DATA)
        while 1:
            for image in self.loop():
                (c, team_to_deploy, total) = self.ocr.ocr_single_line(image)
                if c == 0 and team_to_deploy == 0 and total == 0:
                    continue
                if team_to_deploy == 0:
                    return
                else:
                    break
            timer = Timer(5).start()
            item_clicked = False
            for _ in self.loop():
                if self.appear_then_click(EXPEDITION_DEPLOY_ICON_BUTTON,similarity=0.75):
                    continue
                if timer.reached():
                    logger.info("time reached")
                    break
                if self.appear(EXPEDITION_RECALL):
                    continue
                if self.appear(EXPEDITION_SAIL):
                    item_clicked = True
                    break
                if self.appear_then_click(EXPEDITION_AUTO_DEPLOY):
                    continue
                if self.handle_popup_cancel():
                    continue
            if item_clicked:
                for _ in self.loop():
                    if self.appear_then_click(EXPEDITION_SAIL):
                        continue
                    if self.appear(EXPEDITION_RECALL):
                        break
            else:
                vector = (0,-500)
                box = (746,169,1252,484)
                self.device.swipe_vector(vector,box=box)
        

    def run(self):
        (has_finished,times, has_time) = self.check_if_finished()
        target = [datetime.datetime.now() + d for d in times]
        logger.info(f"{(has_finished, times)}")
        if not has_finished and has_time:
            self.config.task_delay(target= target)
        else:
            self.collect_reward()
            self.deploy_next_expedition()
        (_, times,_) = self.check_if_finished()
        target = [datetime.datetime.now() + d for d in times]
        self.config.task_delay(target= target)

if __name__ == '__main__':
    task = Expedition('src', task='Exercise')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test4.png")
    task.image_file=image_path
    rs = EXPEDITION_DEPLOY_ICON_BUTTON.match_multi_template(task.device.image, similarity=0.8)
    print(f"result {rs}")
