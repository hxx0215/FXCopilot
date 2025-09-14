from tasks.base.ui import UI
from tasks.base.page import page_daily_routine
from tasks.base.assets.assets_base_page import DAILY_CONVOY_ESCORT_ACTIVE,DAILY_CONVOY_ESCORT_BUTTON,DAILY_ARM_TRANSPORT_BUTTON,DAILY_ARM_TRANSPORT_ACTIVE
from module.logger import logger
from module.config.utils import get_server_weekday
STAGE_SELECTOR_AREA=(231,157,1280,426)
class DailyRoutine(UI):

    def arm_transport_stage(self):
        self.ui_click(DAILY_ARM_TRANSPORT_BUTTON,DAILY_ARM_TRANSPORT_ACTIVE)
        self.device.swipe_vector((1200,0),box=STAGE_SELECTOR_AREA)
        logger.info("current in arms transport")
        pass

    def run(self):
        self.ui_ensure(page_daily_routine)
        self.device.sleep(5)
        weekday = get_server_weekday()
        if weekday != 6 and weekday % 2 == 0:
            #1,3,5
            self.arm_transport_stage()
        elif weekday % 2 == 1:
            #2,4,6
            pass
        else:
            self.arm_transport_stage()
        self.arm_transport_stage()
        self.device.sleep(60)
        self.config.task_delay(minute=60)