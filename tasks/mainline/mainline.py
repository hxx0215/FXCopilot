from tasks.base.ui import UI
from tasks.base.page import page_main_line,page_decommissioning_batch
from .assets import *
from tasks.base.assets.assets_base_page import (NEXT_STAGE_BUTTON,PREVIOUS_STAGE_BUTTON,STAGE_HOSTING,STOP_HOSTING,BATTLE_PAGE,STAGE_HOSTING_FINISH_DECOMMISIONING,STAGE_HOSTING_CLOSE,STAGE_HOSTING_FINISH_REACH_TIMES,
                                                DECOMMISSIONING_PAGE,DECOMMISSIONING_BATCH_CONFIRM,DECOMMISSIONING_SELECTED_DATA,DECOMMISSIONING_CONFIRM,GET_ITEMS,
                                                STAGE_HOSTING_GET_SSR, STAGE_INFO_PAGE,STAGE_CLOSE_BUTTON,MAIN_LINE_PAGE,STAGE_FAILED_PAGE,GET_SHIP)
from tasks.base.assets.assets_base_popup import POPUP_CANCEL,POPUP_CONFIRM
from module.logger.logger import logger
from module.ocr.ocr import Ocr,DigitCounter
from module.base.timer import Timer
import cn2an
import re
import random

STAGE_SELECTOR_AREA=(432,242,1098,361)
class Mainline(UI):
    def make_sure_normal(self):
        for _ in self.loop():
            if self.appear(MAINLINE_NORMAL_ACTIVE):
                break
            if self.appear_then_click(MAINLINE_NORMAL_INACTIVE):
                continue
    def cn2int(self, cn_num: str) -> int:
        return int(cn2an.cn2an(cn_num))
    def validate_stage_setting(self) -> tuple[bool,int,int]:
        stage_setting = self.config.MainlineSetting_Stage
        if not stage_setting or '-' not in stage_setting:
            return (False,-1,-1)
        parts = stage_setting.split('-')
        if len(parts) != 2:
            return (False,-1,-1)
        try:
            a = int(parts[0])
            b = int(parts[1])
        except ValueError:
            return (False,-1,-1)
        if not (1 <= a <= 20):
            return (False,-1,-1)
        if a < 20:
            if not (1 <= b <= 10):
                return (False,-1,-1)
        elif a == 20:
            if not (1 <= b <= 10):
                return (False,-1,-1)
        return (True,a,b)
    def move(self,current, target, left, right):
        times = abs(current - target)
        timer = Timer(10).start()
        logger.info(f'move times: {times}')
        for _ in self.loop():
            if times > 0:
                if current < target:
                    if self.appear_then_click(right, interval=1):
                        times = times - 1
                elif current > target:
                    if self.appear_then_click(left, interval=1):
                        times = times - 1
            else:
                break
            if timer.reached():
                break

    def move_stage(self,chapter,stage):
        timer = Timer(3)
        for _ in self.loop():
            if self.appear(MAINLINE_STAGE_START):
                timer.start()
                if timer.reached():
                    break
                else:
                    continue
            timer.reset()
            self.device.swipe_vector((500,0),box=STAGE_SELECTOR_AREA)
        ocr_chapter = -1
        while ocr_chapter != chapter:
            ocr = Ocr(MAINLINE_CHAPTER)
            self.device.screenshot()
            for image in self.loop():
                r: str = ocr.ocr_single_line(image)
                logger.info(f'r is {r}')
                if '第' in r and '章' in r:
                    r = r.replace('第','').replace('章','')
                    break
            ocr_chapter = self.cn2int(r)
            logger.info(f'current 第{ocr_chapter}章')
            times = abs(ocr_chapter - chapter)
            self.move(ocr_chapter,chapter,MAINLINE_PREV_CHAPTER,MAINLINE_NEXT_CHAPTER)
        logger.info('got target chapter')
        self.ui_click(MAINLINE_STAGE_START, MAINLINE_HOSTING)
        current_stage = -1
        self.device.sleep(1.0)
        self.device.screenshot()
        while stage != current_stage:
            ocr = Ocr(MAINLINE_STAGE_NAME)
            for image in self.loop(False):
                r = ocr.ocr_single_line(image)
                match = re.search(r'(\d+)-(\d+)', r)
                if match:
                    current_stage = int(match.group(2))
                    break
            if current_stage == stage:
                break
            self.move(current_stage, stage, PREVIOUS_STAGE_BUTTON,NEXT_STAGE_BUTTON)
            self.device.sleep(3.0)
        logger.info('find stage')
    def start_hosting(self):
        self.ui_click(MAINLINE_HOSTING,MAINLINE_START_HOSTING)
        timer = Timer(3).start()
        for _ in self.loop():
            if self.appear_then_click(MAINLINE_START_HOSTING):
                continue
            if timer.reached():
                break
        self.device.screenshot_interval_set(1.0)
        finish_reason = ''
        cnt = -1
        max_cnt = random.randrange(10, 20)
        for _ in self.loop():
            if self.appear(MAINLINE_STOP_HOSTING_FUEL):
                if self.handle_popup_cancel():
                    if cnt == -1:
                        finish_reason = 'not_begin_insufficient_fuel'
                    else:
                        finish_reason = 'insufficient_fuel'
                    break
            if self.appear(STAGE_HOSTING):
                cnt += 1
                if cnt > max_cnt and self.appear_then_click(BATTLE_PAGE, silent = True):
                    cnt = 0
                    max_cnt = random.randrange(10, 20)
                self.device.stuck_timer.reset()
            if self.appear_then_click(STAGE_HOSTING_FINISH_DECOMMISIONING):
                finish_reason = 'depot_full'
                break
            if self.appear_then_click(STAGE_HOSTING_FINISH_REACH_TIMES):
                finish_reason = 'reach_times'
                break
            priority_exist = self.check_if_priorty_exist()
            if priority_exist:
                finish_reason = 'task_interrupt'
                break
        return finish_reason
    def post_hosting(self, finish_reason):
        self.device.screenshot_interval_set()
        decommission_times = 0
        if finish_reason == 'depot_full':
            self.ui_click(STAGE_HOSTING_CLOSE, DECOMMISSIONING_PAGE)
            if self.config.MainlineSetting_AutoDecommissioning:
                current = -1
                while current != 0:
                    self.ui_goto(page_decommissioning_batch)
                    #make sure choose right rarity
                    self.ui_click(DECOMMISSIONING_BATCH_CONFIRM, DECOMMISSIONING_PAGE, similarity=0.9)
                    counter = DigitCounter(DECOMMISSIONING_SELECTED_DATA)
                    image = self.device.screenshot()
                    (current,remain,total) = counter.ocr_single_line(image)
                    if current == 0:
                        break
                    decommission_times+=1
                    self.ui_click(DECOMMISSIONING_CONFIRM, GET_ITEMS)
                    timer=Timer(3).start()
                    for _ in self.loop():
                        if self.appear_then_click(GET_ITEMS):
                            continue
                        if (not self.appear(GET_ITEMS)) and timer.reached():
                            break
                self.ui_goto_main()
            #FIXME: not TimeOdysseySetting_EnableContinuous
            if decommission_times != 0 and self.config.MainlineSetting_AutoDecommissioning:
                #等5分钟让调度器自己启动, TODO: 如何设定下次启动时间
                self.config.task_delay(minute=1)
            else:
                #如果一次批量退役也没有表示仓库里没有格子放白色和绿色的舰灵了只能停下来了
                self.config.cross_set('Mainline.Scheduler.Enable',False)
        elif finish_reason == 'insufficient_fuel':
            for _ in self.loop():
                if self.appear(MAINLINE_FINISH_HOSTING_FUEL_POPUP):
                    break
            self.ui_click(MAINLINE_FINISH_HOSTING_FUEL_POPUP, STAGE_HOSTING_GET_SSR)
            self.ui_click(STAGE_HOSTING_CLOSE, MAINLINE_STAGE_FINISH)
            self.ui_click(MAINLINE_STAGE_FINISH, GET_ITEMS)
            for _ in self.loop():
                if self.appear_then_click(GET_ITEMS):
                    continue
                if self.appear_then_click(GET_SHIP):
                    continue
                if self.appear(MAINLINE_STAGE_FINISH_EXIT):
                    break
            for _ in self.loop():
                if self.appear_then_click(MAINLINE_STAGE_FINISH_EXIT):
                    break
            self.config.cross_set('Mainline.Scheduler.Enable',False)
        elif finish_reason == 'not_begin_insufficient_fuel':
            for _ in self.loop():
                if self.appear(MAINLINE_FINISH_HOSTING_FUEL_POPUP):
                    break
            self.ui_click(MAINLINE_FINISH_HOSTING_FUEL_POPUP, STAGE_INFO_PAGE)
            self.ui_click(STAGE_CLOSE_BUTTON, MAIN_LINE_PAGE)
            self.ui_goto_main()
            self.config.cross_set('Mainline.Scheduler.Enable',False)
        elif finish_reason == 'reach_times':
            self.ui_click(STAGE_HOSTING_CLOSE,MAINLINE_STAGE_FINISH)
            for _ in self.loop():
                if self.appear_then_click(MAINLINE_STAGE_FINISH):
                    continue
                if self.appear_then_click(GET_ITEMS):
                    continue
                if self.appear(MAINLINE_STAGE_FINISH_EXIT):
                    break
            for _ in self.loop():
                if self.appear_then_click(MAINLINE_STAGE_FINISH_EXIT):
                    continue
                if self.appear(MAIN_LINE_PAGE):
                    break
                if self.appear(STAGE_FAILED_PAGE):
                    break
            self.config.cross_set('Mainline.Scheduler.Enable',False)
        elif finish_reason == 'task_interrupt':
            self.ui_click(STAGE_HOSTING,STOP_HOSTING)
            self.ui_click(STOP_HOSTING, BATTLE_PAGE)
            self.ui_goto_main(extra_default=False)
            self.config.task_delay(minute=5)

    def run(self):
        (validate,chapter,stage) = self.validate_stage_setting()
        if validate:
            self.ui_ensure(page_main_line)
            self.make_sure_normal()
            logger.info('current in normal mode')
            self.move_stage(chapter,stage)
            finish_reason = self.start_hosting()
            self.post_hosting(finish_reason)
        else:
            logger.warning('the stage setting is not right please make sure it is x-x')
if __name__ == '__main__':
    task = Mainline('fxc', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test5.png")
    task.image_file=image_path
    b = task.appear(DECOMMISSIONING_BATCH_CONFIRM)
    print(b)