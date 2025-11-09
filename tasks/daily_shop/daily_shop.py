
from tasks.base.ui import UI
from tasks.base.page import page_shop_gift_shop
from tasks.base.assets.assets_base_page import GET_ITEMS
from .assets.assets_daily_shop import *
from module.config.utils import get_server_next_weekday_update
from module.logger.logger import logger

class DailyShop(UI):
    def finish_task(self):
        self.config.task_delay(server_update=True)
    def run(self):
        self.ui_ensure(page_shop_gift_shop)
        self.ui_click(SHOP_DAILY_GIFT,SHOP_WEEKLY_GIFT_SELECTED)
        for _ in self.loop():
            if self.appear_then_click(SHOP_FREE_DAILY_GIFT):
                continue
            if self.appear(SHOP_FREE_DAILY_GIFT_CONFIRM):
                break
            if self.appear(SHOP_FIRST_NONFREE_DAILY_GIFT):
                logger.info('no free gift')
                self.finish_task()
                return
        for _ in self.loop():
            if self.appear_then_click(SHOP_FREE_DAILY_GIFT_CONFIRM):
                continue
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.appear(SHOP_FIRST_NONFREE_DAILY_GIFT):
                break
        self.finish_task()