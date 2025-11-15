from module.base.button import ButtonWrapper,ClickButton
from module.base.decorator import run_once
from module.base.timer import Timer
from module.exception import GameNotRunningError, GamePageUnknownError, HandledError
from module.logger import logger
from module.ocr.ocr import Ocr,OcrResultButton
from tasks.base.assets.assets_base_main_page import ROGUE_LEAVE_FOR_NOW, ROGUE_LEAVE_FOR_NOW_OE
from tasks.base.assets.assets_base_page import CLOSE, MAIN_GOTO_CHARACTER, MAP_EXIT, MAP_EXIT_OE, MAIN_PAGE,HOME_BUTTON
from tasks.base.assets.assets_base_popup import POPUP_STORY_LATER
from tasks.base.main_page import MainPage
from tasks.base.page import Page, page_gacha, page_main
from tasks.login.assets.assets_login import LOGIN_CONFIRM


class UI(MainPage):
    ui_current: Page
    ui_main_confirm_timer = Timer(0.2, count=0)

    def ui_page_appear(self, page, interval=0):
        """
        Args:
            page (Page):
            interval:
        """
        if page == page_main:
            return self.is_in_main(interval=interval)
        return self.appear(page.check_button, interval=interval)

    def ui_get_current_page(self, skip_first_screenshot=True):
        """
        Args:
            skip_first_screenshot:

        Returns:
            Page:

        Raises:
            GameNotRunningError:
            GamePageUnknownError:
        """
        logger.info("UI get current page")

        @run_once
        def app_check():
            if not self.device.app_is_running():
                raise GameNotRunningError("Game not running")

        @run_once
        def minicap_check():
            if self.config.Emulator_ControlMethod == "uiautomator2":
                self.device.uninstall_minicap()

        @run_once
        def rotation_check():
            self.device.get_orientation()

        timeout = Timer(10, count=20).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
                if not hasattr(self.device, "image") or self.device.image is None:
                    self.device.screenshot()
            else:
                self.device.screenshot()

            # End
            if timeout.reached():
                break

            # Known pages
            for page in Page.iter_pages():
                if page.check_button is None:
                    continue
                if self.ui_page_appear(page=page):
                    logger.attr("UI", page.name)
                    self.ui_current = page
                    return page

            # Unknown page but able to handle
            logger.info("Unknown ui page")
            if self.ui_additional():
                timeout.reset()
                continue
            if self.handle_popup_single():
                timeout.reset()
                continue
            if self.handle_popup_confirm():
                timeout.reset()
                continue
            if self.handle_login_confirm():
                continue
            # TODO: change it to fx map loading
            # if self.appear(MAP_LOADING, similarity=0.75, interval=2):
            #     logger.info('Map loading')
            #     timeout.reset()
            #     continue

            app_check()
            minicap_check()
            rotation_check()

        # Unknown page, need manual switching
        logger.warning("Unknown ui page")
        logger.attr("EMULATOR__SCREENSHOT_METHOD", self.config.Emulator_ScreenshotMethod)
        logger.attr("EMULATOR__CONTROL_METHOD", self.config.Emulator_ControlMethod)
        logger.attr("Lang", self.config.LANG)
        logger.warning("Starting from current page is not supported")
        logger.warning(f"Supported page: {[str(page) for page in Page.iter_pages()]}")
        logger.warning('Supported page: Any page with a "HOME" button on the upper-right')
        logger.critical("Please switch to a supported page before starting FXC")
        raise GamePageUnknownError

    def ui_goto(self, destination, skip_first_screenshot=True):
        """
        Args:
            destination (Page):
            skip_first_screenshot:
        """
        # Create connection
        Page.init_connection(destination)
        self.interval_clear(list(Page.iter_check_buttons()))

        logger.hr(f"UI goto {destination}")
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # Destination page
            if self.ui_page_appear(destination):
                logger.info(f'Page arrive: {destination}')
                if self.ui_page_confirm(destination):
                    logger.info(f'Page arrive confirm {destination}')
                break

            # Other pages
            clicked = False
            for page in Page.iter_pages():
                if page.parent is None or page.check_button is None:
                    continue
                if self.ui_page_appear(page, interval=5):
                    logger.info(f'Page switch: {page} -> {page.parent}')
                    if self.ui_page_confirm(page):
                        logger.info(f'Page arrive confirm {page}')
                    button = page.links[page.parent]
                    self.device.click(button)
                    self.ui_button_interval_reset(button)
                    clicked = True
                    break
            if clicked:
                continue

            # Additional
            if self.ui_additional():
                continue
            if self.handle_popup_single():
                continue
            if self.handle_popup_confirm():
                continue
            if self.handle_login_confirm():
                continue

        # Reset connection
        Page.clear_connection()

    def ui_ensure(self, destination: Page, acquire_lang_checked=True, skip_first_screenshot=True):
        """
        Args:
            destination (Page):
            acquire_lang_checked:
            skip_first_screenshot:

        Returns:
            bool: If UI switched.
        """
        logger.hr("UI ensure")
        self.ui_get_current_page(skip_first_screenshot=skip_first_screenshot)

        # no need exit any special
        # self.ui_leave_special()

        # fuxiao is always use cn so no need check lang
        # if acquire_lang_checked:
        #     if self.acquire_lang_checked():
        #         self.ui_get_current_page(skip_first_screenshot=skip_first_screenshot)

        if self.ui_current == destination:
            logger.info("Already at %s" % destination)
            return False
        else:
            logger.info("Goto %s" % destination)
            self.ui_goto(destination, skip_first_screenshot=True)
            return True

    def ui_ensure_index(
            self,
            index,
            letter,
            next_button,
            prev_button,
            skip_first_screenshot=False,
            fast=True,
            interval=(0.2, 0.3),
    ):
        """
        Args:
            index (int):
            letter (Ocr, callable): OCR button.
            next_button (Button):
            prev_button (Button):
            skip_first_screenshot (bool):
            fast (bool): Default true. False when index is not continuous.
            interval (tuple, int, float): Seconds between two click.
        """
        logger.hr("UI ensure index")
        retry = Timer(1, count=2)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if isinstance(letter, Ocr):
                current = letter.ocr_single_line(self.device.image)
            else:
                current = letter(self.device.image)

            logger.attr("Index", current)
            diff = index - current
            if diff == 0:
                break
            if current == 0:
                logger.warning(f'ui_ensure_index got an empty current value: {current}')
                continue

            if retry.reached():
                button = next_button if diff > 0 else prev_button
                if fast:
                    self.device.multi_click(button, n=abs(diff), interval=interval)
                else:
                    self.device.click(button)
                retry.reset()

    def ui_click(
            self,
            click_button,
            check_button,
            appear_button=None,
            additional=None,
            retry_wait: int | float=5,
            skip_first_screenshot=True,
            similarity = 0.85
    ):
        """
        Args:
            click_button (ButtonWrapper):
            check_button (ButtonWrapper, callable, list[ButtonWrapper], tuple[ButtonWrapper]):
            appear_button (ButtonWrapper, callable, list[ButtonWrapper], tuple[ButtonWrapper]):
            additional (callable):
            retry_wait (int, float):
            skip_first_screenshot (bool):
        """
        if appear_button is None:
            appear_button = click_button

        def process_appear(button):
            if isinstance(button, ButtonWrapper):
                return self.appear(button, similarity=similarity)
            elif callable(button):
                return button()
            elif isinstance(button, (list, tuple)):
                for b in button:
                    if self.appear(b, similarity=similarity):
                        return True
                return False
            else:
                return self.appear(button, similarity=similarity)

        # changed to fix count to be int
        click_timer = Timer(retry_wait, count=int(retry_wait // 0.5))
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if process_appear(check_button):
                break

            # Click
            if click_timer.reached():
                if process_appear(appear_button):
                    self.device.click(click_button)
                    click_timer.reset()
                    continue
            if additional is not None:
                if additional():
                    continue

    def is_in_main(self, interval=0):
        p_main = MAIN_PAGE
        self.device.stuck_record_add(p_main)
        if interval and not self.interval_is_reached(p_main, interval=interval):
            return False

        appear = False
        if p_main.match_template_luma(self.device.image):
            if self.image_color_count(p_main, color=(79, 164, 215), threshold=234, count=400):
            # if self.image_color_count(p_main, color=(235, 235, 235), threshold=234, count=400):
                appear = True
        if not appear:
            if MAP_EXIT.match_template_luma(self.device.image):
                if self.image_color_count(MAP_EXIT, color=(235, 235, 235), threshold=221, count=50):
                    appear = True

        if appear and interval:
            self.interval_reset(p_main, interval=interval)

        return appear

    def is_in_login_confirm(self, interval=0):
        self.device.stuck_record_add(LOGIN_CONFIRM)

        if interval and not self.interval_is_reached(LOGIN_CONFIRM, interval=interval):
            return False

        appear = LOGIN_CONFIRM.match_template_luma(self.device.image)

        if appear and interval:
            self.interval_reset(LOGIN_CONFIRM, interval=interval)

        return appear

    def is_in_map_exit(self, interval=0):
        self.device.stuck_record_add(MAP_EXIT)

        if interval and not self.interval_is_reached(MAP_EXIT, interval=interval):
            return False

        appear = False
        if MAP_EXIT.match_template_luma(self.device.image):
            if self.image_color_count(MAP_EXIT, color=(235, 235, 235), threshold=221, count=50):
                appear = True
        if MAP_EXIT_OE.match_template_luma(self.device.image):
            if self.image_color_count(MAP_EXIT_OE, color=(235, 235, 235), threshold=221, count=50):
                appear = True

        if appear and interval:
            self.interval_reset(MAP_EXIT, interval=interval)

        return appear

    def handle_login_confirm(self):
        """
        If LOGIN_CONFIRM appears, do as task `Restart` not just clicking it
        """
        if self.is_in_login_confirm(interval=0):
            logger.warning('Login page appeared')
            from tasks.login.login import Login
            Login(self.config, device=self.device).handle_app_login()
            raise HandledError
        return False

    def ui_goto_main(self, extra_default=True):
        result = self.ui_ensure(destination=page_main)
        if not result:
            if extra_default:
                return self.appear_then_click(HOME_BUTTON)
            else:
                return False
        else:
            return result

    def ui_additional(self) -> bool:
        """
        Handle all possible popups during UI switching.

        Returns:
            If handled any popup.
        """
        if self.handle_reward():
            return True
        if self.handle_get_light_cone():
            return True
        # Popup story that advice you watch it, but no, later
        if self.appear_then_click(POPUP_STORY_LATER, interval=5):
            return True

        return False

    def _ui_button_confirm(
            self,
            button,
            confirm=Timer(0.1, count=0),
            timeout=Timer(2, count=6),
            skip_first_screenshot=True
    ):
        confirm.reset()
        timeout.reset()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if timeout.reached():
                logger.warning(f'_ui_button_confirm({button}) timeout')
                break

            if self.appear(button):
                if confirm.reached():
                    break
            else:
                confirm.reset()

    def ui_page_confirm(self, page):
        """
        Args:
            page (Page):

        Returns:
            bool: If handled
        """
        if page == page_main:
            self._ui_button_confirm(page.check_button)
            return True

        return False

    def ui_button_interval_reset(self, button):
        """
        Reset interval of some button to avoid mistaken clicks

        Args:
            button (Button):
        """
        pass

    def ui_leave_special(self):
        """
        Leave from:
        - Rogue domains
        - Character trials

        Returns:
            bool: If left a special plane

        Pages:
            in: Any
            out: page_main
        """
        if not self.is_in_map_exit():
            return False

        logger.info('UI leave special')
        skip_first_screenshot = True
        clicked = False
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # End
            if clicked:
                if self.is_in_main():
                    logger.info(f'Leave to {page_main}')
                    break

            if self.is_in_map_exit(interval=2):
                self.device.click(MAP_EXIT)
                continue
            if self.handle_popup_confirm():
                clicked = True
                continue
            if self.handle_ui_close(page_gacha.check_button, interval=2):
                continue
            if self.appear_then_click(ROGUE_LEAVE_FOR_NOW, interval=2):
                clicked = True
                continue
            if self.appear_then_click(ROGUE_LEAVE_FOR_NOW_OE, interval=2):
                clicked = True
                continue
    def ui_button_click(self, button: ClickButton, interval=3) -> bool:
        if not isinstance(button, ClickButton):
            logger.warning(f"handle_ocr_button received a non-click-button object: {button}")
            return False
        if self.interval_is_reached(button, interval):
            self.device.click(button)
            self.interval_reset(button)
            return True
        else:
            return False

    def ui_ocr_button_click(self, button: OcrResultButton, interval=3) -> bool:
        if not isinstance(button, OcrResultButton):
            logger.warning(f"handle_ocr_button received a non-OcrResultButton object: {button}")
            return False
        if self.interval_is_reached(button, interval):
            self.device.click(button)
            self.interval_reset(button)
            return True
        else:
            return False

    def check_if_priorty_exist(self):
        self.config.get_next_task()
        ls = self.config.get_priority_list()
        idx = ls.index(self.config.task.command.lower())
        for pend in self.config.pending_task:
            p_idx = ls.index(pend.command.lower())
            if p_idx < idx:
                return True
        return False