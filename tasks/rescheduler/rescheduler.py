
from tasks.base.ui import UI
from module.logger import logger
from tasks.base.page import page_reward,page_refinery,page_refinery_schedule,page_convenience_store,page_convenience_store_schedule
from tasks.base.assets.assets_base_page import SCHEDULE_EDIT_BUTTON,SCHEDULE_START_BUTTON
from module.exception import RequestHumanTakeover, ScriptError
from tasks.base.assets.assets_base_popup import POPUP_CONFIRM
class Rescheduler(UI):
    def reschedule(self):
        edited = False
        started = False
        #因为涉及到popup出现时编辑按钮和开始排班按钮并不会被覆盖所以检查逻辑如下：
        #假设一开始是编辑按钮那么点击编辑按钮时按钮瞬间被切换至开始排班，这个时候点击开始排班是无效的。所以开始排班需要可以被点击多次这就是为什么第一个if不要加not started
        #todo change similary to escape popup
        for _ in self.loop(False):
            if self.appear(SCHEDULE_START_BUTTON):
                self.appear_then_click(SCHEDULE_START_BUTTON,interval=0.5)
                started = True
                continue
            if self.handle_popup_confirm():
                if started:
                    break
                else:
                    continue
            if self.appear(SCHEDULE_EDIT_BUTTON) and (not edited):
                self.appear_then_click(SCHEDULE_EDIT_BUTTON)
                edited = True
                continue

    def reschedule_refinery(self):
        self.ui_ensure(page_refinery)
        self.device.sleep(0.5)
        self.ui_ensure(page_refinery_schedule)
        self.reschedule()
        self.device.sleep(0.5)
        # check edit or begin
    def reschedule_convenience_store(self):
        self.ui_ensure(page_convenience_store)
        self.device.sleep(0.5)
        self.ui_ensure(page_convenience_store_schedule)
        self.reschedule()
        self.device.sleep(0.5)
    def run(self):
        self.ui_ensure(page_reward)
        self.reschedule_refinery()
        self.reschedule_convenience_store()
        self.config.task_delay(minute=8.4)

if __name__ == '__main__':
    rescheduler = Rescheduler('src', task='Reward')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"test.png")
    rescheduler.image_file=image_path
    b = rescheduler.appear(POPUP_CONFIRM)
    print(b)