from module.alas import AzurLaneAutoScript
from module.logger import logger


class FuXiaoCopilot(AzurLaneAutoScript):
    def restart(self):
        from tasks.login.login import Login
        Login(self.config, device=self.device).app_restart()

    def start(self):
        from tasks.login.login import Login
        Login(self.config, device=self.device).app_start()

    def stop(self):
        from tasks.login.login import Login
        Login(self.config, device=self.device).app_stop()

    def goto_main(self):
        from tasks.login.login import Login
        from tasks.base.ui import UI
        if self.device.app_is_running():
            logger.info('App is already running, goto main page')
            UI(self.config, device=self.device).ui_goto_main()
        else:
            logger.info('App is not running, start app and goto main page')
            Login(self.config, device=self.device).app_start()
            UI(self.config, device=self.device).ui_goto_main()

    def error_postprocess(self):
        # Exit cloud game to reduce extra fee
        if self.config.is_cloud_game:
            from tasks.login.login import Login
            Login(self.config, device=self.device).app_stop()





    def benchmark(self):
        from module.daemon.benchmark import run_benchmark
        run_benchmark(config=self.config)

    def reward(self):
        from tasks.reward.reward import Reward
        Reward(config=self.config, device=self.device, task="Reward").run()

    def rescheduler(self):
        from tasks.rescheduler.rescheduler import Rescheduler
        Rescheduler(config=self.config, device=self.device, task="Rescheduler").run()

    def exercise(self):
        from tasks.exercise.exercise import Exercise
        Exercise(self.config,self.device, task="Exercise").run()

    def quiz_center(self):
        from tasks.quiz_center.quiz_center import QuizCenter
        QuizCenter(self.config, self.device, task="QuizCenter").run()

    def competition(self):
        from tasks.competition.competition import Competition
        Competition(self.config, self.device, task="Competition").run()

    def daily_routine(self):
        from tasks.daily_routine.daily_routine import DailyRoutine
        DailyRoutine(self.config, self.device, task="DailyRoutine").run()

    def expedition(self):
        from tasks.expedition.expedition import Expedition
        Expedition(self.config, self.device, task="Expedition").run()

    def beach(self):
        from tasks.beach.beach import Beach
        Beach(self.config, self.device, task="Beach").run()

    def time_odyssey(self):
        from tasks.time_odyssey.time_odyssey import TimeOdyssey
        TimeOdyssey(self.config, self.device, task="TimeOdyssey").run()

    def tactical_academy(self):
        from tasks.tactical_academy.tactical_academy import TacticalAcademy
        TacticalAcademy(self.config, self.device, task="TacticalAcademy").run()

    def mainline(self):
        from tasks.mainline.mainline import Mainline
        Mainline(self.config, self.device, task="Mainline").run()

    def mail(self):
        from tasks.mail.mail import Mail
        Mail(self.config, self.device, task="Mail").run()

    def weekly_shop(self):
        from tasks.weekly_shop.weekly_shop import WeeklyShop
        WeeklyShop(self.config, self.device, task="WeeklyShop").run()

    def daily_shop(self):
        from tasks.daily_shop.daily_shop import DailyShop
        DailyShop(self.config, self.device, task="DailyShop").run()


if __name__ == '__main__':
    src = FuXiaoCopilot('fxc')
    src.loop()
