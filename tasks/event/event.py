from tasks.base.ui import UI

class Event(UI):
    def run(self):
        self.config.task_delay(minute=1)