
from tasks.base.quick_claim_check import QuickClaimCheck
from tasks.base.page import  page_beach
from module.ocr.ocr import ItemOcr
from module.logger.logger import logger
from module.base.button import ItemWrapper
from tasks.base.assets.assets_base_page import BEACH_TIME_DATA,BEACH_CONTINUE_TRAINING,GET_ITEMS,BEACH_START_TRAINING,BEACH_PAGE
from .assets.beach_assets import BEACH_FOOD_COCONUT,BEACH_FOOD_CHICKEN,BEACH_FOOD_SEAFOOD,BEACH_FOOD_SHRIMP,BEACH_FOOD_FUGU,BEACH_FOOD_CHIKEN_PLUS,BEACH_FOOD_COCONUT_PLUS,BEACH_FOOD_FUGU_PLUS,BEACH_FOOD_SEAFOOD_PLUS,BEACH_FOOD_SHRIMP_PLUS
from module.base.timer import Timer
import datetime

class Beach(QuickClaimCheck):
    def __init__(self, config, device=None, task=None):
        super().__init__(config, BEACH_TIME_DATA, device, task)
    def process_pick_food(self):
        foods = [BEACH_FOOD_COCONUT, BEACH_FOOD_COCONUT_PLUS,BEACH_FOOD_FUGU, BEACH_FOOD_FUGU_PLUS, BEACH_FOOD_CHICKEN, BEACH_FOOD_CHIKEN_PLUS, 
                  BEACH_FOOD_SEAFOOD, BEACH_FOOD_SEAFOOD_PLUS, BEACH_FOOD_SHRIMP, BEACH_FOOD_SHRIMP_PLUS]
        total = 6
        pick_food: list[tuple[ItemWrapper, int]] = []
        for food in foods:
            cnt = self.find_item(food)
            if cnt >= total:
                pick_food.append((food, total))
                break
            else:
                pick_food.append((food, cnt))
                total = total - cnt
        self.add_item(pick_food,(144,507,826,619))
        self.ui_click(BEACH_START_TRAINING, BEACH_PAGE)

    def process_continue_training(self):
        while True:
            timer = Timer(5).start()
            for image in self.loop():
                btns = BEACH_CONTINUE_TRAINING.match_multi_template(image)
                if len(btns) > 0:
                    break
                if timer.reached():
                    return
            for btn in btns:
                for _ in self.loop():
                    if not self.appear(GET_ITEMS):
                        self.ui_button_click(btn)
                        continue
                    if self.appear(GET_ITEMS):
                        break
                self.ui_click(GET_ITEMS, BEACH_START_TRAINING)
                self.process_pick_food()
                

    def run(self):
        (has_finished, deltas,_) = self.check_if_finished()
        if has_finished:
            self.ui_ensure(page_beach)
            self.process_continue_training()
            (_, deltas, _) = self.check_if_finished()
        target = [datetime.datetime.now() + d for d in deltas]
        if len(target) > 0:
            self.config.task_delay(target=target)
        else:
            #beach没有舰灵2小时后再来检测
            self.config.task_delay(minute=120)

if __name__ == '__main__':
    task = Beach('fxc', task='Beach')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test3.png")
    task.image_file=image_path
    b = task.appear(BEACH_PAGE)
    print(f"{b}")
