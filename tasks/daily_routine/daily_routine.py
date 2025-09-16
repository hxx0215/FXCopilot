from tasks.base.ui import UI
from tasks.base.page import page_daily_routine
from tasks.base.assets.assets_base_page import *
from module.logger import logger
from module.config.utils import get_server_weekday
from module.exception import RequestHumanTakeover
from dataclasses import dataclass
from module.ocr.keyword import Keyword
from typing import ClassVar
STAGE_SELECTOR_AREA=(231,157,1280,426)
STAGE_CLASS_SELECTOR_AREA=(283,558,1224,671)
@dataclass(repr=False)
class BattleFieldKeyword(Keyword):
    instances: ClassVar = {}
    @classmethod
    def init(cls,id: int, name: str):
        return cls(id,name,cn = name,en = name,jp = name, cht = '',es = '')
class DailyRoutine(UI):
    ARM_TRANSPORT_KV = [("a-ng1", DAILY_ARM_TRANSPORT_NG1),("a-ng2", DAILY_ARM_TRANSPORT_NG2),
                        ("a-tp1", DAILY_ARM_TRANSPORT_TP1),("a-tp2", DAILY_ARM_TRANSPORT_TP2),
                        ("a-ac1", DAILY_ARM_TRANSPORT_AC1),("a-ac2", DAILY_ARM_TRANSPORT_AC2),
                        ("a-aa1", DAILY_ARM_TRANSPORT_AA1),("a-aa2", DAILY_ARM_TRANSPORT_AA2),
                        ("a-eq1", DAILY_ARM_TRANSPORT_EQ1),("a-eq2", DAILY_ARM_TRANSPORT_EQ2)]
    BATTLE_FIELD_KV= [("nv-1")]
    def arm_transport_stage(self):
        self.start_stage(DAILY_ARM_TRANSPORT_BUTTON, DAILY_ARM_TRANSPORT_ACTIVE, DAILY_ARM_TRANSPORT_START, None)
        target_idx = next((index for index, (k,_) in enumerate(self.ARM_TRANSPORT_KV) if k == self.config.DungeonSetting_ArmTransport), None)
        idx = 0
        if not target_idx:
            raise RequestHumanTakeover
        for _ in self.loop():
            if self.handle_popup_confirm():
                logger.info("次数用完")
                return
            (_ , button) = self.ARM_TRANSPORT_KV[idx]
            if idx < target_idx:
                if self.appear(button) and self.appear_then_click(NEXT_STAGE_BUTTON,1):
                    idx = idx + 1
            else:
                if self.appear(button):
                    break
        self.max_stage_and_process()

    def convoy_escort_stage(self):
        self.start_stage(DAILY_CONVOY_ESCORT_BUTTON, DAILY_CONVOY_ESCORT_ACTIVE, DAILY_CONVOY_ESCORT_START, DAILY_CONVOY_ESCORT_START2)
        if self.find_last_stage():
            self.max_stage_and_process()

    def military_technology_stage(self):
        self.start_stage(DAILY_MILITARY_TECHNOLOGY_BUTTON,DAILY_MILITARY_TECHNOLOGY_ACTIVE, DAILY_MILITARY_TECHNOLOGY_START, DAILY_MILITARY_TECHNOLOGY_START2)
        if self.find_last_stage():
            self.max_stage_and_process()
    def tactical_traning_stage(self):
        self.start_stage(DAILY_TACTICAL_TRAINING_BUTTON,DAILY_TACTICAL_TRAINING_ACTIVE,DAILY_TACTICAL_TRAINING_START, DAILY_TACTICAL_TRAINING_START2)
        if self.find_last_stage():
            self.max_stage_and_process()

    def start_stage(self, find_button: ButtonWrapper, active_button: ButtonWrapper, start_button: ButtonWrapper, start_button2: ButtonWrapper | None):
        for _ in self.loop():
            if (not self.appear(find_button) and not self.appear(active_button)):
                self.device.swipe_vector((500,0), box=STAGE_CLASS_SELECTOR_AREA)
                self.device.sleep((1,2))
            else:
                break
        self.ui_click(find_button, active_button)
        self.device.sleep((3,3.5))
        b2 = start_button2 if start_button2 else start_button
        for _ in self.loop():
            if not self.appear(start_button) and not self.appear(b2):
                self.device.swipe_vector((1200,0),box=STAGE_SELECTOR_AREA)
                self.device.sleep((2,3))
            else:
                self.appear_then_click(start_button)
                if start_button2:
                    self.appear_then_click(start_button2)
                self.device.sleep((0.5,1))
                break
    def find_last_stage(self):
        cnt = 0
        for _ in self.loop():
            if self.handle_popup_confirm():
                logger.info("次数用完")
                return False
            if self.appear_then_click(NEXT_STAGE_BUTTON,1.0):
                cnt = 0
                continue
            if not self.appear(NEXT_STAGE_BUTTON):
                if cnt > 5:
                    break
                else:
                    cnt = cnt + 1
        return True
        
    def max_stage_and_process(self):
        for _ in self.loop():
            if self.appear_then_click(STAGE_TIMES_SELECT_BUTTON):
                continue
            if self.appear_then_click(STAGE_MAX_TIMES_BUTTON):
                break
        for _ in self.loop():
            if self.appear_then_click(STAGE_SWEEP_BUTTON):
                continue
            if self.handle_popup_confirm():
                break
        clicked = False
        for _ in self.loop():
            if self.appear_then_click(GET_REWARD):
                clicked = True
                continue
            if clicked and (not self.appear(GET_REWARD)):
                break
        for _ in self.loop():
            if self.appear_then_click(STAGE_CLOSE_BUTTON):
                break
    def run(self):
        self.ui_ensure(page_daily_routine)
        self.device.sleep(5)
        weekday = get_server_weekday()
        if weekday != 6 and weekday % 2 == 0:
            #1,3,5
            self.convoy_escort_stage()
            self.arm_transport_stage()
        elif weekday % 2 == 1:
            #2,4,6
            self.convoy_escort_stage()
            self.military_technology_stage()
            self.tactical_traning_stage()
        else:
            self.arm_transport_stage()
            self.convoy_escort_stage()
        self.config.task_delay(server_update=True)

if __name__ == '__main__':
    task = DailyRoutine('src', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test7.png")
    task.image_file=image_path
    b = task.appear(GET_REWARD)
    print(b)
    