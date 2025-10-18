from module.base.button import ButtonWrapper
from tasks.base.quick_claim_check import QuickClaimCheck
from tasks.base.assets.assets_base_page import (TACTICAL_ACADEMY_TIME_DATA,TACTICAL_ACADEMY_CONTINUE_TRAINING,TACTICAL_ACADEMY_GET_EXP,TACTICAL_ACADEMY_START_TRAINING,
                                                TACTICAL_ACADEMY_CURRENT_LEVEL,TACTICAL_ACADEMY_CURRENT_EXP,
                                                TACTICAL_ACADEMY_BASIC_GUNNERY,TACTICAL_ACADEMY_INTERMEDIATE_GUNNERY,TACTICAL_ACADEMY_ADVANCED_GUNNERY,
                                                TACTICAL_ACADEMY_BASIC_TORPEDO,TACTICAL_ACADEMY_INTERMEDIATE_TORPEDO,TACTICAL_ACADEMY_ADVANCED_TORPEDO,
                                                TACTICAL_ACADEMY_BASIC_AUXILIARY,TACTICAL_ACADEMY_INTERMEDIATE_AUXILIARY,TACTICAL_ACADEMY_ADVANCED_AUXILIARY,
                                                TACTICAL_ACADEMY_BASIC_AVIATION,TACTICAL_ACADEMY_INTERMEDIATE_AVIATION,TACTICAL_ACADEMY_ADVANCED_AVIATION,
                                                TACTICAL_ACADEMY_BASIC_SUPPORT,TACTICAL_ACADEMY_INTERMEDIATE_SUPPORT,TACTICAL_ACADEMY_ADVANCED_SUPPORT,
                                                TACTICAL_ACADEMY_BASIC_COMMAND,TACTICAL_ACADEMY_INTERMEDIATE_COMMAND,TACTICAL_ACADEMY_ADVANCED_COMMAND,
                                                TACTICAL_ACADEMY_CLASS_COMMAND,TACTICAL_ACADEMY_CLASS_PRIMARY,TACTICAL_ACADEMY_CLASS_ULTIMATE,TACTICAL_ACADEMY_CLASS_SUPPORT,
                                                TACTICAL_ACADEMY_BOOK_TYPE_DATA,TACTICAL_ACADEMY_PAGE
                                                )
from tasks.base.page import page_tactical_academy,page_temp
from module.base.timer import Timer
from module.ocr.ocr import DataDigit,DigitCounter,Ocr
from module.logger.logger import logger
import datetime
from typing import cast

LEVEL_ACCUMULATE_EXP=[0,100,300,700,1500,3100,5500,9100]
BOOK_DICT= {
    "【炮击】":[TACTICAL_ACADEMY_BASIC_GUNNERY,TACTICAL_ACADEMY_INTERMEDIATE_GUNNERY,TACTICAL_ACADEMY_ADVANCED_GUNNERY],
    "【雷击】":[TACTICAL_ACADEMY_BASIC_TORPEDO,TACTICAL_ACADEMY_INTERMEDIATE_TORPEDO,TACTICAL_ACADEMY_ADVANCED_TORPEDO],
    "【辅助】":[TACTICAL_ACADEMY_BASIC_AUXILIARY,TACTICAL_ACADEMY_INTERMEDIATE_AUXILIARY,TACTICAL_ACADEMY_ADVANCED_AUXILIARY],
    "【航空】":[TACTICAL_ACADEMY_BASIC_AVIATION,TACTICAL_ACADEMY_INTERMEDIATE_AVIATION,TACTICAL_ACADEMY_ADVANCED_AVIATION],
    'support': [TACTICAL_ACADEMY_BASIC_SUPPORT,TACTICAL_ACADEMY_INTERMEDIATE_SUPPORT,TACTICAL_ACADEMY_ADVANCED_SUPPORT],
    'command': [TACTICAL_ACADEMY_BASIC_COMMAND,TACTICAL_ACADEMY_INTERMEDIATE_COMMAND,TACTICAL_ACADEMY_ADVANCED_COMMAND]
}
class TacticalAcademy(QuickClaimCheck):
    def __init__(self, config, device=None, task=None):
        super().__init__(config, TACTICAL_ACADEMY_TIME_DATA, device, task)

    def process_pick_book(self):
        current_level = 0
        level_ocr = DataDigit(TACTICAL_ACADEMY_CURRENT_LEVEL)
        for image in self.loop():
            level = level_ocr.ocr_single_line(image)
            if level != 0:
                current_level = level
                break
        if current_level == 9:
            #close and return
            self.device.adb_shell(['input', 'keyevent', '4'])
            return
        exp_ocr = DigitCounter(TACTICAL_ACADEMY_CURRENT_EXP)
        current_exp = -1
        for image in self.loop():
            (current,remain,total) = exp_ocr.ocr_single_line(image)
            if not (current == 0  and remain == 0 and total == 0):
                current_exp = current
                break
        logger.info(f'current level{current_level}')
        current_acc_exp = LEVEL_ACCUMULATE_EXP[current_level - 1] + current_exp
        tactical_class = ''
        for image in self.loop():
            if self.appear(TACTICAL_ACADEMY_CLASS_SUPPORT):
                tactical_class = 'support'
                break
            if self.appear(TACTICAL_ACADEMY_CLASS_PRIMARY):
                tactical_class = 'primary'
                break
            if self.appear(TACTICAL_ACADEMY_CLASS_COMMAND):
                tactical_class = 'command'
                break
            if self.appear(TACTICAL_ACADEMY_CLASS_ULTIMATE):
                tactical_class = 'ultimate'
                break
        if tactical_class == 'primary' or tactical_class == 'ultimate':
            self.pick_front_skill_book(current_acc_exp // 150)
        if tactical_class == 'support' or tactical_class == 'command':
            self.pick_front_skill_book(current_acc_exp // 100, book_type= tactical_class, combat=False)
    def pick_front_skill_book(self, exp: int, book_type: str = '', combat: bool = True):
        ocr = Ocr(TACTICAL_ACADEMY_BOOK_TYPE_DATA)
        if book_type == '':
            for image in self.loop():
                book_type = ocr.ocr_single_line(image)
                if book_type in BOOK_DICT:
                    break
        btns = BOOK_DICT[book_type]
        max_count: tuple[int,int,int] = (0,0,0)
        for (idx,btn) in enumerate(btns):
            cnt = self.find_item(btn)
            ls = list(max_count)
            ls[idx] = cnt
            max_count = cast(tuple[int,int,int],tuple(ls))
        logger.info(f'book count:{max_count}')
        if max_count == (0,0,0):
            self.device.adb_shell(['input', 'keyevent', '4'])
            return
        if combat:
            pick_count = self.pick_book_count(exp, (1,2,8), 93, max_count)
        else:
            pick_count = self.pick_book_count(exp, (1,2,8), 139, max_count)
        (base,inter,adv) = pick_count
        logger.info(f'pick book tuple:{pick_count}')
        target = [(btns[0],base),(btns[1], inter), (btns[2], adv)]
        self.add_item(target,(144,507,826,619))
        logger.info('pick finished')
        self.ui_click(TACTICAL_ACADEMY_START_TRAINING, TACTICAL_ACADEMY_PAGE)
            
        

    def pick_book_count(self, current: int, book_exp: tuple[int,int,int], total: int, max_book: tuple[int,int,int]) -> tuple[int,int,int]:
        remain = total - current
        (a,b,c) = book_exp
        (ma,mb,mc) = max_book
        result = (0,0,0)
        max_exp = -1
        for nc in range(min(mc, 6) + 1):
            for nb in range(min(mb, 6-nc)+ 1):
                for na in range(min(ma, 6-nc-nb)+ 1):
                    current_exp = na * a + nb * b + nc * c
                    if current_exp <= remain:
                        if current_exp > max_exp:
                            max_exp = current_exp
                            result = (na,nb,nc)
        return result


    def process_continue_training(self):
        while True:
            timer = Timer(5).start()
            for image in self.loop():
                btns = TACTICAL_ACADEMY_CONTINUE_TRAINING.match_multi_template(image=image)
                if len(btns) > 0:
                    break
                if timer.reached():
                    return
            for btn in btns:
                for _ in self.loop():
                    if not self.appear(TACTICAL_ACADEMY_GET_EXP):
                        self.ui_button_click(btn)
                        continue
                    if self.appear(TACTICAL_ACADEMY_GET_EXP):
                        break
                self.ui_click(TACTICAL_ACADEMY_GET_EXP, TACTICAL_ACADEMY_START_TRAINING)
                self.process_pick_book()


    def run(self):
        (has_finished, deltas,_) = self.check_if_finished()
        if has_finished:
            # continue learning
            self.ui_ensure(page_tactical_academy)
            self.process_continue_training()
            (_, deltas,_) = self.check_if_finished()
        target = [datetime.datetime.now() + d for d in deltas]
        logger.info(f'delay: {target}')
        if len(target) > 0:
            self.config.task_delay(target=target)
        else:
            #beach没有舰灵2小时后再来检测
            self.config.task_delay(minute=120)

        # self.ui_ensure(page_tactical_academy)
        # self.process_continue_training()

        # self.ui_ensure(page_temp)
        # self.process_pick_book()
        # self.device.sleep(60)
if __name__ == '__main__':
    task = TacticalAcademy('fxc', task='Beach')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test5.png")
    task.image_file=image_path
    b = task.appear(TACTICAL_ACADEMY_ADVANCED_GUNNERY)
    print(b)
