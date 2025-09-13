from tasks.base.ui import UI
from tasks.base.page import page_competition
from tasks.base.assets.assets_base_page import *
from tasks.base.assets.assets_base_popup import *
from module.logger import logger
from module.ocr.ocr import Ocr,OcrResultButton
import random
import operator
class CompetitorOcr(Ocr):
    pass
class Competition(UI):
    def go_normal_arena(self):
        for _ in self.loop():
            if self.appear_then_click(ARENA_BUTTON):
                continue
            if self.handle_popup_confirm():
                return False
            if self.appear(ARENA_REFRESH):
                return True
    def find_competitor(self):
        ocrs = [CompetitorOcr(ARENA_COMPETITOR_1_DATA),CompetitorOcr(ARENA_COMPETITOR_2_DATA), CompetitorOcr(ARENA_COMPETITOR_3_DATA)]
        btns: list[OcrResultButton] = []
        for ocr in ocrs:
            c = ocr.detect_and_ocr(self.device.image)
            if (len(c) > 0):
                name = c[0].ocr_text
                if '代号' in name:
                    return OcrResultButton(c[0], None)
                else:
                    btns.append(OcrResultButton(c[0], None))
        if len(btns) > 0:
            return random.choice(btns)
        else:
            return None
    def check_scout(self, scout_tuple: tuple[int, int, int, int]) -> tuple[int,int,int,int] | None:
        if self.appear(ARENA_CROSSING_T,similarity=0.96):
            (a,b,c,d)= tuple(map(operator.add, scout_tuple, (1,0,0,0)))
            return (a,b,c,d)
        elif self.appear(ARENA_T_CROSSED,similarity=0.96):
            (a,b,c,d)= tuple(map(operator.add, scout_tuple, (0,0,0,1)))
            return (a,b,c,d)
        elif self.appear(ARENA_PARALLEL_COURSE,similarity=0.96):
            (a,b,c,d)= tuple(map(operator.add, scout_tuple, (0,1,0,0)))
            return (a,b,c,d)
        elif self.appear(ARENA_OPPOSITE_COURSE,similarity=0.96):
            (a,b,c,d)= tuple(map(operator.add,scout_tuple, (0,0,1,0)))
            return(a,b,c,d)
        else:
            return None

    def calc_current_competition(self):
        scout_result = (0,0,0,0)
        params: list[tuple[ButtonWrapper,bool, ButtonWrapper|None]] = [(ARENA_SMALL_CLASS_SELECTED, False, ARENA_MIDDLE_CLASS), (ARENA_MIDDLE_CLASS_SELECTED, False, ARENA_LARGE_CLASS), (ARENA_LARGE_CLASS_SELECTED, False, None)]
        finish = False
        for _ in self.loop():
            for i in range(len(params)):
                (current, flag, next_button) = params[i]
                if self.appear(current, similarity=0.9):
                    if not flag:
                        new_scout_result = self.check_scout(scout_result)
                        logger.info(f"button: {current} result:{new_scout_result}")
                        if new_scout_result:
                            scout_result = new_scout_result
                        else:
                            break
                        params[i] = (current, True, next_button)
                    if next_button:
                        if self.appear_then_click(next_button):
                            break
                    else:
                        finish = True
                        break
            if finish:
                break
        (t_crossing,parallel,opposite,t_crossed) = scout_result
        # score = t_crossing * 0.9 + parallel * 0.7 + opposite * 0.4 + t_crossed * 0.1 
        logger.info(f"TA:{t_crossing},PA:{parallel},OP:{opposite},TD:{t_crossed}")
        return scout_result

    def go_to_prepare(self) -> str:
        if self.handle_popup_cancel():
            return 'Cancel'
        if self.appear(ARENA_SMALL_CLASS_SELECTED):
            return 'Ready'
        btn = self.find_competitor()
        if btn:
            self.ui_ocr_button_click(btn)
            self.device.sleep(3)
        logger.info(f"cancel show {self.appear(POPUP_CANCEL)}")
        return 'Unknown'

    def wait_competition_finish(self):
        for _ in self.loop():
            if self.appear_then_click(ARENA_SET_SAIL):
                continue
            if self.appear_then_click(CLICK_TO_CONTINUE):
                continue
            if self.appear(ARENA_REFRESH):
                return


    def start_competition(self):
        cnt = 0
        while 1:
            for _ in self.loop():
                prepare = self.go_to_prepare()
                logger.info(f"prepare is {prepare}")
                if prepare == 'Unknown':
                    continue
                elif prepare == 'Cancel':
                    return
                elif prepare == 'Ready':
                    break
            self.device.sleep(2)
            (t_crossing,_,_,_) = self.calc_current_competition()
            if t_crossing >= 2:
                self.wait_competition_finish()
                cnt = 0
                continue
            else:
                if cnt < 10:
                    for _ in self.loop():
                        if self.appear_then_click(ARENA_REFRESH, interval=7):
                            cnt+=1
                            break
                else:
                    self.wait_competition_finish()
                    cnt = 0
                    continue


    def run(self):
        self.ui_ensure(page_competition)
        can_go_into_arena = self.go_normal_arena()
        if not can_go_into_arena:
            self.config.task_delay(server_update=True)
            return
        else:
            logger.info("begin to find opposite")
            self.start_competition()
        self.config.task_delay(server_update=True)


if __name__ == '__main__':
    task = Competition('src', task='Exercise')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test","test4.png")
    task.image_file=image_path
    b = task.appear(ARENA_SMALL_CLASS_SELECTED)
    print(b)