from tasks.base.free_gift import FreeGift
from .assets.assets_weekly_shop import *


class WeeklyShop(FreeGift):
    @property
    def shop_gift_button(self):
        return SHOP_WEEKLY_GIFT
    
    @property
    def shop_gift_selected(self):
        return SHOP_WEEKLY_GIFT_SELECTED
    
    @property
    def free_gift_button(self):
        return SHOP_FREE_WEEKLY_GIFT
    
    @property
    def free_gift_confirm(self):
        return SHOP_FREE_WEEKLY_GIFT_CONFIRM
    
    @property
    def first_nonfree_gift(self):
        return SHOP_FIRST_NONFREE_WEEKLY_GIFT
    
    def finish_task(self):
        from module.config.utils import get_server_next_weekday_update
        diff = get_server_next_weekday_update('04:00', 6)
        self.config.task_delay(target=diff)


if __name__ == '__main__':
    from tasks.base.free_gift import FreeGift
    task = WeeklyShop('fxc', task='WeeklyShop')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    task.image_file=image_path
    b = task.appear(SHOP_FIRST_NONFREE_WEEKLY_GIFT)
    print(b)