from module.base.timer import Timer
from module.exception import GameNotRunningError
from module.logger import logger
from tasks.base.page import page_main
from tasks.login.assets.assets_login import *
from tasks.base.assets.assets_base_page import GET_REWARD,GET_SHIP
from tasks.login.assets.assets_login_popup import ADVERTISE_Castorice
from module.ocr.ocr import Ocr
from tasks.base.ui import UI

class Login(UI):
    def _handle_app_login(self):
        """
        Pages:
            in: Any page
            out: page_main

        Raises:
            GameStuckError:
            GameTooManyClickError:
            GameNotRunningError:
        """
        logger.hr('App login')
        orientation_timer = Timer(5)
        startup_timer = Timer(5).start()
        app_timer = Timer(5).start()
        login_success = False
        self.device.stuck_record_clear()
        ocr = Ocr(LOGIN_SUCCESS_DATA)
        login_confirm_appeared = False

        while 1:
            # Watch if game alive
            if app_timer.reached():
                if not self.device.app_is_running():
                    logger.error('Game died during launch')
                    raise GameNotRunningError('Game not running')
                app_timer.reset()
            # Watch device rotation
            if not login_success and orientation_timer.reached():
                # Screen may rotate after starting an app
                self.device.get_orientation()
                orientation_timer.reset()

            self.device.screenshot()

            # End
            # Game client requires at least 5s to start
            # The first few frames might be captured before app_stop(), ignore them
            if startup_timer.reached():
                if self.ui_page_appear(page_main):
                    logger.info('Login to main confirm')
                    break

            if self.appear(SERVER_MAINTAIN):
                self.handle_popup_confirm()
                logger.info('server is in maintain wait 600s to check')
                self.device.stuck_record_clear()
                app_timer.reset()
                orientation_timer.reset()
                self.device.sleep(600)
                continue

            if self.appear_then_click(APP_UPDATE):
                logger.info('app should update')
                continue

            if self.appear_then_click(NETWORK_ERROR):
                logger.warning('network error retry')
                continue

            # Watch resource downloading and loading
            if self.appear(LOGIN_LOADING, interval=5):
                logger.info('Game resources downloading or loading')
                self.device.stuck_record_clear()
                app_timer.reset()
                orientation_timer.reset()
                continue

            if login_confirm_appeared and (not login_success):
                text = ocr.ocr_single_line(self.device.image)
                if '成功' in text:
                    login_success = True
            if self.appear_then_click(LOGIN_CONFIRM):
                login_confirm_appeared = True
                continue
            if self.handle_popup_confirm():
                continue
            if self.appear_then_click(LOGIN_REWARD):
                continue
            if self.appear_then_click(LOGIN_NOTIFICATION):
                continue
            if self.appear_then_click(GET_REWARD):
                continue
            if self.appear_then_click(GET_SHIP):
                continue
            continue
            # Additional
            if self.handle_popup_single():
                continue
            if self.ui_additional():
                continue
            if self.handle_login_popup():
                continue

        return True

    def handle_account_confirm(self):
        """
        ACCOUNT_CONFIRM is not a multi-server assets as text language is not detected before log in.
        It just detects all languages.

        ACCOUNT_CONFIRM doesn't appear in most times, sometimes game client won't auto login but requiring you to
        click login even if there is only one account.

        Returns:
            bool: If clicked
        """
        if self.appear_then_click(ACCOUNT_CONFIRM):
            return True
        return False

    def handle_login_popup(self):
        """
        Returns:
            bool: If clicked
        """
        # 3.2 Castorice popup that advertise you go gacha, but no, close it
        if self.handle_ui_close(ADVERTISE_Castorice, interval=2):
            return True
        return False

    def handle_app_login(self):
        logger.info('handle_app_login')
        self.device.screenshot_interval_set(1.0)
        self.device.stuck_timer = Timer(300, count=300).start()
        try:
            self._handle_app_login()
        finally:
            self.device.screenshot_interval_set()
            self.device.stuck_timer = Timer(60, count=60).start()

    def app_stop(self):
        logger.hr('App stop')
        self.device.app_stop()

    def app_start(self):
        logger.hr('App start')
        self.device.app_start()

        self.handle_app_login()

    def app_restart(self):
        logger.hr('App restart')
        self.device.app_stop()
        self.device.app_start()

        self.handle_app_login()

        self.config.task_delay(server_update=True)
