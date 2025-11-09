from tasks.base.free_gift import FreeGift
from .assets.assets_daily_shop import *


class DailyShop(FreeGift):
    @property
    def shop_gift_button(self):
        return SHOP_DAILY_GIFT
    
    @property
    def shop_gift_selected(self):
        return SHOP_DAILY_GIFT_SELECTED  # 使用更明确的别名
    
    @property
    def free_gift_button(self):
        return SHOP_FREE_DAILY_GIFT
    
    @property
    def free_gift_confirm(self):
        return SHOP_FREE_DAILY_GIFT_CONFIRM
    
    @property
    def first_nonfree_gift(self):
        return SHOP_FIRST_NONFREE_DAILY_GIFT
    
    def finish_task(self):
        self.config.task_delay(server_update=True)