
from tasks.base.ui import UI

class Beach(UI):
    def run(self):
        self.device.sleep(60)
        self.config.task_delay(minute= 1)