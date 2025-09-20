
from tasks.base.ui import UI
from tasks.base.remain_time_mixin import RemainTimeMixin
from tasks.base.page import page_reward, page_beach,page_temp
from module.ocr.ocr import QuickClaimTimeOcr,ItemOcr
from module.logger.logger import logger
from module.base.button import ItemWrapper
from tasks.base.assets.assets_base_page import BEACH_TIME_DATA,BEACH_CONTINUE_TRAINING,GET_ITEMS,BEACH_START_TRAINING,BEACH_FOOD_COCONUT,BEACH_FOOD_CHICKEN,BEACH_PAGE
from module.base.timer import Timer
import datetime

class Beach(UI, RemainTimeMixin):
    def find_food(self, food: ItemWrapper) -> int:
        ocr = ItemOcr(food)
        timer = Timer(5).start()
        for image in self.loop():
            if self.appear(food):
                cnt = int(ocr.ocr_single_line(image))
                if cnt > 0:
                    return cnt
                else:
                    continue
            if timer.reached():
                return 0
        return 0
    def add_food(self, foods: list[tuple[ItemWrapper,int]]):
        target_search_area = (144,507,826,619)
        idx = 0
        for image in self.loop():
            (food, cnt) = foods[idx]
            added_food = food.temp_multi_match(image, target_search_area)
            if len(added_food) == cnt:
                idx = idx + 1
                if idx == len(foods):
                    break
                else:
                    continue
            if self.appear_then_click(food, interval=1):
                continue
    def process_pick_food(self):
        foods = [BEACH_FOOD_COCONUT,BEACH_FOOD_CHICKEN]
        total = 6
        pick_food: list[tuple[ItemWrapper, int]] = []
        for food in foods:
            cnt = self.find_food(food)
            if cnt >= total:
                pick_food.append((food, total))
                break
            else:
                pick_food.append((food, cnt))
                total = total - cnt
        self.add_food(pick_food)
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
                self.device.sleep(60)
                
    def check_if_finished(self):
        self.ui_ensure(page_reward)
        ocr = QuickClaimTimeOcr(BEACH_TIME_DATA)
        for image in self.loop():
            (has_finished, deltas) = ocr.ocr_single_line(image)
            if has_finished or len(deltas) != 0:
                break
        return (has_finished, deltas)

    def run(self):
        # self.ui_ensure(page_temp)
        # self.process_pick_food()
        (has_finished, deltas) = self.check_if_finished()
        if has_finished:
            self.ui_ensure(page_beach)
            self.process_continue_training()
            (_, deltas) = self.check_if_finished()
        target = [datetime.datetime.now() + d for d in deltas]
        self.config.task_delay(target=target)

if __name__ == '__main__':
    task = Beach('src', task='Beach')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test2.png")
    task.image_file=image_path
    print(BEACH_FOOD_COCONUT.button_offset)
    b = task.appear(BEACH_FOOD_COCONUT)
    print(f"{b}")
    print(BEACH_FOOD_COCONUT.button_offset)
    ocr = ItemOcr(BEACH_FOOD_COCONUT)
    num = ocr.ocr_single_line(task.device.image)
    print(num)
