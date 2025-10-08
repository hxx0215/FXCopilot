import re

import module.config.server as server
from module.config.server import VALID_LANG
from module.exception import RequestHumanTakeover, ScriptError
from module.logger import logger
from module.ocr.ocr import OcrWhiteLetterOnComplexBackground
from tasks.base.assets.assets_base_main_page import OCR_MAP_NAME
from tasks.base.page import Page, page_main
from tasks.base.popup import PopupHandler


class OcrPlaneName(OcrWhiteLetterOnComplexBackground):
    def after_process(self, result):
        # RobotSettlement1
        result = re.sub(r'-[Ii1]$', '', result)
        result = re.sub(r'I$', '', result)
        result = re.sub(r'\d+$', '', result)
        # Herta's OfficeY/
        result = re.sub(r'Y/?$', '', result)
        # Stargazer Navatia -> Stargazer Navalia
        result = result.replace('avatia', 'avalia')
        # 苏乐达™热砂海选会场
        result = re.sub(r'(苏乐达|蘇樂達|SoulGlad|スラーダ|FelizAlma)[rtT]*M*', r'\1', result)
        # SoulGladtM Scorchsand Audition Ven
        if 'Audition' in result:
            right = result.find('Audition') + len('Audition')
            result = result[:right] + ' Venue'
        # The Radiant Feldspar
        result = re.sub(r'The\s*Rad', 'Rad', result)
        # 幽囚狱
        result = result.replace('幽因狱', '幽囚狱')
        result = result.replace('幽因獄', '幽囚獄')
        # DomainiRespite
        result = result.replace('omaini', 'omain')
        # Domain=Combat
        result = result.replace('=', '')
        # Domain--Occunrence
        # Domain'--Occurence
        # Domain-Qccurrence
        result = result.replace('cunr', 'cur').replace('uren', 'urren').replace('Qcc', 'Occ')
        # Domain-Elit
        # Domain--Etite
        result = re.sub(r'[Ee]lit$', 'Elite', result)
        result = result.replace('tite', 'lite')

        # 区域－战
        result = re.sub(r'区域.*战$', '区域战斗', result)
        # 区域－事
        result = re.sub(r'区域.*[事件]$', '区域事件', result)
        # 区域－战
        result = re.sub(r'区域.*交$', '区域交易', result)
        # 区域－战
        result = re.sub(r'区域.*[精英]$', '区域精英', result)
        # 区域-事伴, 区域－事祥
        result = re.sub(r'事[伴祥]', '事件', result)
        # 医域－战斗
        result = result.replace('医域', '区域')
        # 区域-战半, 区域-战头, 区域-战头书
        result = re.sub(r'战[半头卒三]', '战斗', result)
        # 区域一战斗
        result = re.sub(r'区域[\-—－一=]', '区域-', result)
        # 累塔的办公室
        result = result.replace('累塔', '黑塔')
        if '星港' in result:
            result = '迴星港'
        result = result.replace('太司', '太卜司')
        # IRadiantFeldspar
        result = re.sub('[Ii1|]\s*Radiant', 'Radiant', result)

        result = result.replace(' ', '')

        return super().after_process(result)


class MainPage(PopupHandler):
    # Same as BigmapPlane class

    _lang_checked = False
    _lang_check_success = True

    def check_lang_from_map_plane(self) -> str | None:
        logger.info('check_lang_from_map_plane')
        # no need check fx is always cn
        return "cn"

    def handle_lang_check(self, page: Page):
        """
        Args:
            page:

        Returns:
            bool: If checked
        """
        if MainPage._lang_checked:
            return False
        if page != page_main:
            return False

        self.check_lang_from_map_plane()
        return True

    def acquire_lang_checked(self):
        """
        Returns:
            bool: If checked
        """
        # because fx is always using cn
        return False
        if MainPage._lang_checked:
            return False

        logger.info('acquire_lang_checked')
        try:
            self.ui_goto(page_main)
        except AttributeError:
            logger.critical('Method ui_goto() not found, class MainPage must be inherited by class UI')
            raise ScriptError

        self.handle_lang_check(page=page_main)
        return True
