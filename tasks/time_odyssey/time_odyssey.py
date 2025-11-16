from tasks.base.resource_check import ResourceCheck
from tasks.base.page import page_time_odyssey_map,page_decommissioning_batch
from tasks.base.assets.assets_base_page import (TIME_ODYSSEY_PAGE,TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_TIMES_DATA,TIME_ODYSSEY_TIMES_SELECT,STAGE_HOSTING,STAGE_HOSTING_FINISH_DECOMMISIONING,
                                                STAGE_HOSTING_CLOSE,DECOMMISSIONING_PAGE,TIME_ODYSSEY_CONTINUE_HOSTING,STAGE_HOSTING_FINISH_FUEL,STAGE_SET_SAIL,STAGE_TO_PORT,STAGE_HOSTING_FINISH_SINK,
                                                TIME_ODYSSEY_SAIL_HOSTING_BUTTON,TIME_ODYSSEY_HOSTING_START,TIME_ODYSSEY_REMAIN_TIME,TIME_ODYSSEY_SAIL_SET_SAIL,TIME_ODYSSEY_STAGE_SET_SAIL,TIME_ODYSSEY_STAGE_POSITION,
                                                DECOMMISSIONING_BATCH_CONFIRM,DECOMMISSIONING_SELECTED_DATA,DECOMMISSIONING_CONFIRM,GET_ITEMS,STOP_HOSTING,BATTLE_PAGE,STAGE_HOSTING_FINISH_REACH_TIMES,
                                                TIME_ODYSSEY_STAGE_TO_PORT,TIME_ODYSSEY_STAGE_SUCCESS,TIME_ODYSSEY_STAGE_FAIL,TIME_ODYSSEY_S_WIN,TIME_ODYSSEY_FLEET,TIME_ODYSSEY_FLEET_SWITCH,
                                                TIME_ODYSSEY_FLEET_AMMUNITION,GET_SHIP,TIME_ODYSSEY_CONTINUE_MANUAL
                                                )
from module.logger.logger import logger
from module.ocr.ocr import Ocr,OcrResultButton,DigitCounter,DataDigit
from module.base.timer import Timer
from module.exception import RequestHumanTakeover
import random
import re

class PositionOcr(Ocr):
    def format_result(self, result):
        result = result.replace('0', 'O').replace('1', 'I')
        match = re.match(r'^([A-Za-z])\s*点\s*$', result.strip())
        if match:
            letter = match.group(1)  # 提取字母部分
            logger.info(f'current position = {letter}')  
            return letter
        return None

class TimeOdyssey(ResourceCheck):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ammunition_capacity: list[int] = [5, 5]

    def setup_mode(self):
        mode = self.config.TimeOdysseySetting_Mode
        logger.info(f"start time oddysey mode: {mode}")
        if mode == 'default':
            return

    def check_current_map_state(self) -> str:
        current_state = 'map'
        timer = Timer(3).start()
        for _ in self.loop():
            if self.appear(TIME_ODYSSEY_MAP_BUTTON):
                current_state = 'map'
                break
            if self.appear(TIME_ODYSSEY_CONTINUE_HOSTING):
                current_state = 'continue'
                break
            if self.appear(TIME_ODYSSEY_CONTINUE_MANUAL):
                current_state = 'continue_manual'
                break
            if timer.reached():
                break
        logger.info(f'current state is {current_state}')
        return current_state

    def time_odyssey_map(self) -> str:
        current_state = self.check_current_map_state()
        if current_state == 'map':
            self.ui_click(TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_SAIL_HOSTING_BUTTON)
            self.ui_click(TIME_ODYSSEY_SAIL_HOSTING_BUTTON,TIME_ODYSSEY_HOSTING_START)
        else:
            self.ui_click(TIME_ODYSSEY_CONTINUE_HOSTING,TIME_ODYSSEY_HOSTING_START)
        return current_state

    def hosting_prepare(self, current_state: str):
        times = self.config.TimeOdysseySetting_Times
        ocr = Ocr(TIME_ODYSSEY_TIMES_DATA)
        timer = Timer(3).start()
        if times != 'default' and current_state != 'continue':
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
        cnt = 0
        max_cnt = random.randrange(10, 20)
        for image in self.loop():
            if self.appear(STAGE_HOSTING):
                cnt += 1
                if cnt > max_cnt and self.appear_then_click(BATTLE_PAGE, silent = True):
                    cnt = 0
                    max_cnt = random.randrange(10, 20)
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
            if self.appear_then_click(STAGE_HOSTING_FINISH_SINK):
                finish_reason = 'sink'
                break
            ocr_result = self.get_current_resources()
            if ocr_result:
                fuel, _, _ = ocr_result
                if fuel < self.config.TimeOdysseySetting_MinimalFuel:
                    finish_reason = 'less_than_minimal_fuel'
                    break
            priority_exist = self.check_if_priorty_exist()
            if priority_exist:
                finish_reason = 'task_interrupt'
                break
        return finish_reason
    def decommission(self):
        decommission_times = 0
        if self.config.TimeOdysseySetting_AutoDecommissioning:
            current = -1
            while current != 0:
                self.ui_goto(page_decommissioning_batch)
                #make sure choose right rarity
                for image in self.loop():
                    if self.appear_then_click(DECOMMISSIONING_BATCH_CONFIRM):
                        continue
                    if self.appear(DECOMMISSIONING_PAGE):
                        break
                # self.ui_click(DECOMMISSIONING_BATCH_CONFIRM, DECOMMISSIONING_PAGE)
                logger.info('demission batch confirm')
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

    def post_hosting(self, finish_reason):
        self.device.screenshot_interval_set()
        if finish_reason == 'depot_full':
            self.ui_click(STAGE_HOSTING_CLOSE, DECOMMISSIONING_PAGE)
            self.decommission()
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
        elif finish_reason == 'sink':
            self.ui_click(STAGE_HOSTING_CLOSE, STAGE_TO_PORT)
            for image in self.loop():
                if self.appear_then_click(STAGE_TO_PORT):
                    continue
                if self.handle_popup_confirm():
                    break
            self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        elif finish_reason == 'task_interrupt':
            self.ui_click(STAGE_HOSTING,STOP_HOSTING)
            self.ui_click(STOP_HOSTING, BATTLE_PAGE)
            self.ui_goto_main(extra_default=False)
            self.config.task_delay(minute=5)
        else:
            self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
        self.ui_goto_main()

    def manual_hosting(self) -> str:
        current = self.check_current_map_state()
        order = self.validate_order()
        count = self.config.stored.BattleCount.value
        self.ammunition_capacity = [5,5]
        if current == 'map':
            count = 0
            self.config.update_battle_count(count=count)
            self.ui_click(TIME_ODYSSEY_MAP_BUTTON,TIME_ODYSSEY_SAIL_HOSTING_BUTTON)
            for _ in self.loop():
                if self.appear_then_click(TIME_ODYSSEY_SAIL_SET_SAIL):
                    continue
                if self.appear_then_click(STAGE_HOSTING_FINISH_DECOMMISIONING):
                    continue
                if self.appear(TIME_ODYSSEY_STAGE_SET_SAIL):
                    break
                if self.appear(DECOMMISSIONING_PAGE):
                    return 'depot_full'
        elif current == 'continue_manual':
            for _ in self.loop():
                if self.appear_then_click(TIME_ODYSSEY_CONTINUE_MANUAL):
                    continue
                if self.handle_popup_confirm():
                    continue
                if self.appear(TIME_ODYSSEY_STAGE_SET_SAIL):
                    break
                if self.appear_then_click(STAGE_HOSTING_FINISH_DECOMMISIONING):
                    continue
                if self.appear(DECOMMISSIONING_PAGE):
                    return 'depot_full'
        else:
            return '???'
        while 1:
            for _ in self.loop():
                if self.appear(TIME_ODYSSEY_STAGE_SET_SAIL):
                    break
            ocr = PositionOcr(TIME_ODYSSEY_STAGE_POSITION)
            fleet_ocr = DataDigit(TIME_ODYSSEY_FLEET)
            ammunition_ocr = DigitCounter(TIME_ODYSSEY_FLEET_AMMUNITION)
            for image in self.loop():
                fleet = fleet_ocr.ocr_single_line(image)
                if fleet is None:
                    continue
                result = ammunition_ocr.ocr_single_line(image)
                if result == (0,0,0):
                    continue
                (ammunition,_,_) = result
                self.ammunition_capacity[fleet - 1] = ammunition
                next_fleet = self.get_next_fleet(count,order,fleet)
                if fleet == next_fleet:
                    break
                else:
                    self.appear_then_click(TIME_ODYSSEY_FLEET_SWITCH)
            for image in self.loop():
                position = ocr.ocr_single_line(image)
                if position:
                    logger.info(f'current position = {position}')  
                    if position.lower() == self.config.TimeOdysseySetting_ReturnPoint.lower():
                        return 'arrive_position'
                    else:
                        break
            for _ in self.loop():
                if self.appear_then_click(TIME_ODYSSEY_STAGE_SET_SAIL):
                    continue
                if self.appear(BATTLE_PAGE):
                    break
                if self.appear_then_click(STAGE_HOSTING_FINISH_DECOMMISIONING):
                    return 'depot_full'
            # self.ui_click(TIME_ODYSSEY_STAGE_SET_SAIL, BATTLE_PAGE)
            stage_result = ''
            self.device.screenshot_interval_set(1.0)
            for _ in self.loop():
                if self.appear_then_click(BATTLE_PAGE, silent=True):
                    continue
                if self.appear(TIME_ODYSSEY_S_WIN):
                    stage_result = 's-win'
                    break
                if self.appear(TIME_ODYSSEY_STAGE_SUCCESS):
                    stage_result = 'win'
                    break
                if self.appear(TIME_ODYSSEY_STAGE_FAIL):
                    stage_result = 'lose'
                    break
            count = count + 1
            self.config.update_battle_count(count)
            self.device.screenshot_interval_set()
            if stage_result == 'lose':
                for _ in self.loop():
                    if self.appear_then_click(TIME_ODYSSEY_STAGE_FAIL):
                        continue
                    if self.appear(TIME_ODYSSEY_STAGE_TO_PORT):
                        return 'lose_in_stage'
            if stage_result == 'win':
                for _ in self.loop():
                    if self.appear_then_click(TIME_ODYSSEY_STAGE_SUCCESS):
                        continue
                    if self.appear_then_click(GET_ITEMS):
                        continue
                    if self.appear_then_click(GET_SHIP):
                        continue
                    if self.appear(TIME_ODYSSEY_STAGE_TO_PORT):
                        return 'not_s_win'
            if stage_result == 's-win':
                for _ in self.loop():
                    if self.appear_then_click(TIME_ODYSSEY_S_WIN):
                        continue
                    if self.appear_then_click(GET_ITEMS):
                        continue
                    if self.appear_then_click(GET_SHIP):
                        continue
                    if self.handle_popup_confirm():
                        continue
                    if self.appear(TIME_ODYSSEY_STAGE_SET_SAIL):
                        break
        return '???'
    def get_next_fleet(self, count: int, order: list[int], current: int):
        if count < len(order):
            designated_fleet = order[count]
            if self.ammunition_capacity[designated_fleet - 1] > 0:
                return designated_fleet
            else:
                return 3 - designated_fleet
        else:
            if self.ammunition_capacity[current - 1] > 0:
                return current
            else:
                return 3 - current
    def validate_order(self):
        order = self.config.TimeOdysseySetting_ManualOrder
        order_str = str(order)
        if not all(c in '12' for c in order_str):
            logger.info(f"invalid order: {order_str}, must be consist of 1 or 2")
            raise RequestHumanTakeover
        return [int(c) for c in order_str]
    def manual_hosting_back_port(self):
        for _ in self.loop():
            if self.appear_then_click(TIME_ODYSSEY_STAGE_TO_PORT):
                break
        confirm_clicked = False
        timer = Timer(3)
        for _ in self.loop():
            if self.handle_popup_confirm():
                confirm_clicked = True
                timer.start()
                continue
            if confirm_clicked and timer.reached():
                break
    
    def hosting(self):
        #确认当前石油
        finish_reason = ''
        if self.config.TimeOdysseySetting_HostingMode == 'foreground':
            current = self.time_odyssey_map()
            self.hosting_prepare(current)
            finish_reason = self.start_hosting()
            self.post_hosting(finish_reason=finish_reason)
        elif self.config.TimeOdysseySetting_HostingMode == 'manual':
            finish_reason = self.manual_hosting()
            #TODO abstract here
            if finish_reason == 'arrive_position':
                self.manual_hosting_back_port()
                self.ui_goto_main()
            if finish_reason == 'depot_full':
                self.decommission()
            if finish_reason == 'lose_in_stage' or finish_reason == 'not_s_win':
                self.config.cross_set('TimeOdyssey.Scheduler.Enable',False)
                self.ui_goto_main()


    def run(self):
        self.ui_ensure(page_time_odyssey_map)
        self.hosting()

if __name__ == '__main__':
    task = TimeOdyssey('fxc', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test9.png")
    task.image_file=image_path
    b = task.appear(GET_SHIP)
    print(b)