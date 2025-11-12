
from tasks.base.ui import UI
from module.logger import logger
from tasks.base.page import page_reward,page_refinery,page_refinery_schedule,page_convenience_store,page_convenience_store_schedule
from .assets.assets_rescheduler import *
from module.exception import RequestHumanTakeover, ScriptError
from tasks.base.assets.assets_base_popup import POPUP_CONFIRM
class Rescheduler(UI):
    def reschedule(self):
        #因为涉及到popup出现时编辑按钮和开始排班按钮并不会被覆盖所以检查逻辑如下：
        #假设一开始是编辑按钮那么点击编辑按钮时按钮瞬间被切换至开始排班，这个时候点击开始排班是无效的。所以开始排班需要可以被点击多次这就是为什么第一个if不要加not started
        #todo change similary to escape popup
        state = ''
        for _ in self.loop():
            if self.appear(SCHEDULE_EDIT_BUTTON):
                state='edit'
                break
            if self.appear(SCHEDULE_START_BUTTON):
                state='start'
                break
        if state == 'edit':
            self.edit(SCHEDULE_EDIT_BUTTON)
            self.make_sure_popup_dismiss(SCHEDULER_POP_DISMISS)
        self.edit(SCHEDULE_START_BUTTON)
        self.make_sure_popup_dismiss(SCHEDULE_UPGRADE)
        logger.info('finish reschedule')

    def edit(self,btn: ButtonWrapper):
        for _ in self.loop():
            if self.appear_then_click(btn):
                continue
            if self.appear(POPUP_CONFIRM):
                break
    def make_sure_popup_dismiss(self, flag: ButtonWrapper):
        for _ in self.loop():
            if self.handle_popup_confirm():
                continue
            if self.appear(flag):
                break


    def reschedule_refinery(self):
        self.ui_ensure(page_refinery_schedule)
        self.reschedule()
        self.device.sleep(1)
        self.device.screenshot()
        # check edit or begin
    def reschedule_convenience_store(self):
        self.ui_ensure(page_convenience_store_schedule)
        self.reschedule()
        self.device.sleep(1)
        self.device.screenshot()
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