from tasks.base.ui import UI
from tasks.base.page import page_shop_gift_shop
from tasks.base.assets.assets_base_page import GET_ITEMS
from .assets.assets_weekly_shop import *
from module.config.utils import get_server_next_weekday_update,get_server_next_update
from module.logger.logger import logger

class WeeklyShop(UI):
    def finish_task(self):
        diff = get_server_next_weekday_update('04:00', 6)
        self.config.task_delay(target=diff)
    def run(self):
        self.ui_ensure(page_shop_gift_shop)
        self.ui_click(SHOP_WEEKLY_GIFT, SHOP_WEEKLY_GIFT_SELECTED)
        for _ in self.loop():
            if self.appear_then_click(SHOP_FREE_WEEKLY_GIFT):
                continue
            if self.appear(SHOP_FREE_WEEKLY_GIFT_CONFIRTM):
                break
            if self.appear(SHOP_FIRST_NONFREE_WEEKLY_GIFT):
                logger.info('no free gift')
                self.finish_task()
                return
        for _ in self.loop():
            if self.appear_then_click(SHOP_FREE_WEEKLY_GIFT_CONFIRTM):
                continue
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.appear(SHOP_FIRST_NONFREE_WEEKLY_GIFT):
                break
        self.finish_task()

if __name__ == '__main__':
    task = WeeklyShop('fxc', task='WeeklyShop')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    task.image_file=image_path
    b = task.appear(SHOP_FIRST_NONFREE_WEEKLY_GIFT)
    print(b)