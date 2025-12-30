from tasks.base.ui import UI
from tasks.base.page import page_shop_gift_shop
from tasks.base.assets.assets_base_page import GET_ITEMS
from module.config.utils import get_server_next_weekday_update
from module.logger.logger import logger
from module.base.timer import Timer
from abc import ABC, abstractmethod


class FreeGift(UI, ABC):
    """
    公共基类 - 处理免费礼物的领取
    
    子类需要定义的属性：
    - shop_gift_button: 商店礼品按钮
    - shop_gift_selected: 商店礼品选中状态
    - free_gift_button: 免费礼品按钮
    - free_gift_confirm: 免费礼品确认按钮
    - first_nonfree_gift: 第一个非免费礼品
    """
    
    # 抽象属性 - 子类必须定义这些
    @property
    @abstractmethod
    def shop_gift_button(self):
        pass
    
    @property
    @abstractmethod
    def shop_gift_selected(self):
        pass
    
    @property
    @abstractmethod
    def free_gift_button(self):
        pass
    
    @property
    @abstractmethod
    def free_gift_confirm(self):
        pass
    
    @property
    @abstractmethod
    def first_nonfree_gift(self):
        pass
    
    def finish_task(self):
        """
        完成任务 - 子类应该重写此方法来定义自己的延迟策略
        """
        raise NotImplementedError("子类必须实现 finish_task 方法")
    
    def run(self):
        self.ui_ensure(page_shop_gift_shop)
        self.ui_click(self.shop_gift_button, self.shop_gift_selected)
        
        timer = Timer(7).start()
        for _ in self.loop():
            if self.appear_then_click(self.free_gift_button):
                continue
            if self.appear(self.free_gift_confirm):
                break
            if self.appear(self.first_nonfree_gift):
                logger.info('no free gift')
                self.finish_task()
                return
            if timer.reached():
                logger.info('not found free gift')
                self.finish_task()
                return
        
        for _ in self.loop():
            if self.appear_then_click(self.free_gift_confirm):
                continue
            if self.appear_then_click(GET_ITEMS):
                continue
            if self.appear(self.first_nonfree_gift):
                break
        
        self.finish_task()