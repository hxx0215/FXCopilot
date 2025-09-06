from tasks.base.ui import UI
from module.logger import logger
from tasks.base.page import page_reward,page_refinery
class Reward(UI):
    def run(self):
        # self.ui_ensure(page_reward)
        logger.info("get reward")
        self.config.task_delay(minute=2)


if __name__ == '__main__':
    reward = Reward('src', task='Reward')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test2.png")
    reward.image_file=image_path
    from tasks.base.assets.assets_base_page import REWARD_CHECK_OPEN
    b = reward.appear(REWARD_CHECK_OPEN)
    print(b)
