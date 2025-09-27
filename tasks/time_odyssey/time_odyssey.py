from tasks.base.resource_check import ResourceCheck
from tasks.base.page import page_time_odyssey_map,page_decommissioning_batch
from tasks.base.assets.assets_base_page import (TIME_ODYSSEY_PAGE,TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_TIMES_DATA,TIME_ODYSSEY_TIMES_SELECT,STAGE_HOSTING,STAGE_HOSTING_FINISH_DECOMMISIONING,
                                                STAGE_HOSTING_CLOSE,DECOMMISSIONING_PAGE,TIME_ODYSSEY_CONTINUE_HOSTING,STAGE_HOSTING_FINISH_FUEL,STAGE_SET_SAIL,
                                                TIME_ODYSSEY_SAIL_HOSTING_BUTTON,TIME_ODYSSEY_HOSTING_START,
                                                DECOMMISSIONING_BATCH_CONFIRM,DECOMMISSIONING_SELECTED_DATA,DECOMMISSIONING_CONFIRM,GET_ITEMS
                                                )
from module.logger.logger import logger
from module.ocr.ocr import Ocr,OcrResultButton,DigitCounter
from module.base.timer import Timer

class TimeOdyssey(ResourceCheck):
    def setup_mode(self):
        mode = self.config.TimeOdysseyModeSetting_Mode
        logger.info(f"start time oddysey mode: {mode}")
        if mode == 'default':
            return
    
    def start_hosting(self):
        current_state = 'map'
        for _ in self.loop():
            if self.appear(TIME_ODYSSEY_MAP_BUTTON):
                current_state = 'map'
                break
            if self.appear(TIME_ODYSSEY_CONTINUE_HOSTING):
                current_state = 'continue'
                break
        logger.info(f'current state is {current_state}')
        if current_state == 'map':
            self.ui_click(TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_SAIL_HOSTING_BUTTON)
            self.ui_click(TIME_ODYSSEY_SAIL_HOSTING_BUTTON,TIME_ODYSSEY_HOSTING_START)
        else:
            self.ui_click(TIME_ODYSSEY_CONTINUE_HOSTING,TIME_ODYSSEY_HOSTING_START)
        times = self.config.TimeOdysseyModeSetting_Times
        ocr = Ocr(TIME_ODYSSEY_TIMES_DATA)
        timer = Timer(3).start()
        if times != 'default':
            times = '默认最高' if times == 'max' else str(times)
            self.ui_click(TIME_ODYSSEY_TIMES_SELECT, TIME_ODYSSEY_TIMES_DATA)
            timer.reset()
            for image in self.loop():
                result = ocr.detect_and_ocr(image)
                if len(result) > 0:
                    for r in result:
                        if r.ocr_text == times:
                            self.ui_ocr_button_click(OcrResultButton(r,None))
                if (not self.appear(TIME_ODYSSEY_TIMES_DATA)) and timer.reached():
                    break
        timer.reset()
        for image in self.loop():
            if self.appear_then_click(TIME_ODYSSEY_HOSTING_START):
                continue
            if timer.reached():
                break
        self.device.screenshot_interval_set(1.0)
        finish_reason = ''
        for image in self.loop():
            if self.appear(STAGE_HOSTING):
                self.device.stuck_timer.reset()
            if self.appear_then_click(STAGE_HOSTING_FINISH_DECOMMISIONING):
                finish_reason = 'depot_full'
                break
            if self.appear_then_click(STAGE_HOSTING_FINISH_FUEL):
                # fuel not enough
                finish_reason = 'insufficient_fuel'
                break
            ocr_result = self.get_current_resources()
            if ocr_result:
                fuel, money, diamond = ocr_result
        self.device.screenshot_interval_set()
        if finish_reason == 'depot_full':
            self.ui_click(STAGE_HOSTING_CLOSE, DECOMMISSIONING_PAGE)
            if self.config.TimeOdysseyModeSetting_AutoDecommissioning:
                current = -1
                while current != 0:
                    self.ui_goto(page_decommissioning_batch)
                    #make sure choose right rarity
                    self.ui_click(DECOMMISSIONING_BATCH_CONFIRM, DECOMMISSIONING_PAGE)
                    counter = DigitCounter(DECOMMISSIONING_SELECTED_DATA)
                    image = self.device.screenshot()
                    (current,remain,total) = counter.ocr_single_line(image)
                    if current == 0:
                        break
                    self.ui_click(DECOMMISSIONING_CONFIRM, GET_ITEMS)
                    timer=Timer(3).start()
                    for _ in self.loop():
                        if self.appear_then_click(GET_ITEMS):
                            continue
                        if (not self.appear(GET_ITEMS)) and timer.reached():
                            break
        elif finish_reason == 'insufficient_fuel':
            self.ui_click(STAGE_HOSTING_CLOSE, STAGE_SET_SAIL)
        self.ui_goto_main()
        self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)

    def run(self):
        self.ui_ensure(page_time_odyssey_map)
        self.start_hosting()

if __name__ == '__main__':
    task = TimeOdyssey('fxc', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test5.png")
    task.image_file=image_path
    b = task.appear(DECOMMISSIONING_PAGE)
    print(b)