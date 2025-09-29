from tasks.base.resource_check import ResourceCheck
from tasks.base.page import page_time_odyssey_map,page_decommissioning_batch
from tasks.base.assets.assets_base_page import (TIME_ODYSSEY_PAGE,TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_TIMES_DATA,TIME_ODYSSEY_TIMES_SELECT,STAGE_HOSTING,STAGE_HOSTING_FINISH_DECOMMISIONING,
                                                STAGE_HOSTING_CLOSE,DECOMMISSIONING_PAGE,TIME_ODYSSEY_CONTINUE_HOSTING,STAGE_HOSTING_FINISH_FUEL,STAGE_SET_SAIL,
                                                TIME_ODYSSEY_SAIL_HOSTING_BUTTON,TIME_ODYSSEY_HOSTING_START,TIME_ODYSSEY_REMAIN_TIME,
                                                DECOMMISSIONING_BATCH_CONFIRM,DECOMMISSIONING_SELECTED_DATA,DECOMMISSIONING_CONFIRM,GET_ITEMS,STOP_HOSTING,BATTLE_PAGE,STAGE_HOSTING_FINISH_REACH_TIMES
                                                )
from module.logger.logger import logger
from module.ocr.ocr import Ocr,OcrResultButton,DigitCounter
from module.base.timer import Timer

class TimeOdyssey(ResourceCheck):
    def setup_mode(self):
        mode = self.config.TimeOdysseySetting_Mode
        logger.info(f"start time oddysey mode: {mode}")
        if mode == 'default':
            return

    def time_odyssey_map(self):
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

    def hosting_prepare(self):
        times = self.config.TimeOdysseySetting_Times
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
    def start_hosting(self):
        timer=Timer(3).start()
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
            if self.appear_then_click(STAGE_HOSTING_FINISH_REACH_TIMES):
                finish_reason = 'reach_times'
                break
            ocr_result = self.get_current_resources()
            if ocr_result:
                fuel, _, _ = ocr_result
                if fuel < self.config.TimeOdysseySetting_MinimalFuel:
                    finish_reason = 'less_than_minimal_fuel'
                    break
        return finish_reason
    def post_hosting(self, finish_reason):
        self.device.screenshot_interval_set()
        decommission_times = 0
        if finish_reason == 'depot_full':
            self.ui_click(STAGE_HOSTING_CLOSE, DECOMMISSIONING_PAGE)
            if self.config.TimeOdysseySetting_AutoDecommissioning:
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
                    decommission_times+=1
                    self.ui_click(DECOMMISSIONING_CONFIRM, GET_ITEMS)
                    timer=Timer(3).start()
                    for _ in self.loop():
                        if self.appear_then_click(GET_ITEMS):
                            continue
                        if (not self.appear(GET_ITEMS)) and timer.reached():
                            break
                self.ui_goto_main()
            if decommission_times != 0 and self.config.TimeOdysseySetting_EnableContinuous:
                #等5分钟让调度器自己启动, TODO: 如何设定下次启动时间
                self.config.task_delay(minute=5)
            else:
                #如果一次批量退役也没有表示仓库里没有格子放白色和绿色的舰灵了只能停下来了
                self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        elif finish_reason == 'insufficient_fuel':
            self.ui_click(STAGE_HOSTING_CLOSE, STAGE_SET_SAIL)
            self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        elif finish_reason == 'less_than_minimal_fuel':
            self.ui_click(STAGE_HOSTING,STOP_HOSTING)
            self.ui_click(STOP_HOSTING, BATTLE_PAGE)
            self.ui_goto_main(extra_default=False)
            self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        elif finish_reason == 'reach_times':
            self.ui_click(STAGE_HOSTING_CLOSE,TIME_ODYSSEY_REMAIN_TIME)
            if self.config.TimeOdysseySetting_EnableContinuous:
                self.config.task_delay(minute=5)
            else:
                self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        else:
            self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        self.ui_goto_main()
    
    def hosting(self):
        #确认当前石油
        self.time_odyssey_map()
        self.hosting_prepare()
        finish_reason = self.start_hosting()
        self.post_hosting(finish_reason=finish_reason)

    def run(self):
        self.ui_ensure(page_time_odyssey_map)
        self.hosting()

if __name__ == '__main__':
    task = TimeOdyssey('fxc', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test7.png")
    task.image_file=image_path
    b = task.appear(DECOMMISSIONING_BATCH_CONFIRM)
    print(b)
    print(DECOMMISSIONING_BATCH_CONFIRM.button)
    print(DECOMMISSIONING_BATCH_CONFIRM.button_offset)