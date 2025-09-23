from tasks.base.ui import UI
from module.logger import logger
from tasks.base.assets.assets_base_page import REWARD_CLAIM_FUEL, REWARD_CLAIM_MONEY,GET_REWARD
from tasks.base.page import page_reward
from module.base.timer import Timer
class Reward(UI):
    def run(self):
        self.ui_ensure(page_reward)
        btns = [REWARD_CLAIM_FUEL, REWARD_CLAIM_MONEY]
        for btn in btns:
            claimed = False
            for _ in self.loop():
                if not claimed and self.appear_then_click(btn):
                    continue
                if self.appear_then_click(GET_REWARD):
                    claimed = True
                    continue
                if claimed and not self.appear(GET_REWARD):
                    break
                if self.handle_popup_confirm():
                    break
        self.config.task_delay(minute=30)


if __name__ == '__main__':
    reward = Reward('src', task='Reward')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test2.png")
    reward.image_file=image_path
    from tasks.base.assets.assets_base_page import REWARD_CHECK_OPEN
    b = reward.appear(REWARD_CHECK_OPEN)
    print(b)
