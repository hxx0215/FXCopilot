import re

from module.base.timer import Timer
from module.logger import logger
from module.ocr.ocr import Digit, DigitCounter
from tasks.base.page import page_item,page_main
from tasks.item.assets.assets_item_data import OCR_DATA, OCR_RELIC
from tasks.item.keywords import KEYWORDS_ITEM_TAB
from tasks.item.ui import ItemUI
from tasks.planner.model import PlannerMixin


class DataDigit(Digit):
    def after_process(self, result):
        result = re.sub(r'[l|]', '1', result)
        result = re.sub(r'[oO]', '0', result)
        result = re.sub(r'\+', '', result)
        return super().after_process(result)


class RelicOcr(DigitCounter):
    def after_process(self, result):
        result = re.sub(r'[l1|]3000', '/3000', result)
        result = re.sub(r'[oO]', '0', result)
        return super().after_process(result)


class DataUpdate(ItemUI, PlannerMixin):
    def _get_data(self):
        """
        Page:
            in: page_item, KEYWORDS_ITEM_TAB.UpgradeMaterials
        """
        ocr = DataDigit(OCR_DATA)

        timeout = Timer(2, count=6).start()
        oil, money, diamond = 0, 0, 0
        for _ in self.loop():
            data = ocr.detect_and_ocr(self.device.image)

            if len(data) == 3:
                oil, money, diamond = [int(re.sub(r'\s', '', d.ocr_text)) for d in data]
                if oil > 0 or money > 0 or diamond >0:
                    break

            logger.warning(f'Invalid credit and stellar money: {data}')
            if timeout.reached():
                logger.warning('Get data timeout')
                break

        logger.attr('Oil', oil)
        logger.attr('Money', money)
        logger.attr('Diamond', diamond)
        return oil, money, diamond

    def _get_relic(self):
        """
        Page:
            in: page_item, KEYWORDS_ITEM_TAB.Relics
        """
        ocr = RelicOcr(OCR_RELIC)
        timeout = Timer(2, count=6).start()
        relic = 0
        for _ in self.loop():
            relic, _, total = ocr.ocr_single_line(self.device.image)
            if total == 3000 or relic < 0:
                break
            logger.warning(f'Invalid relic amount: {relic}/{total}')
            if timeout.reached():
                logger.warning('Get relic timeout')
                break

        logger.attr('Relic', relic)
        return relic

    def run(self):
        logger.info('begin check update')
        self.ui_ensure(page_main, acquire_lang_checked=False)
        # item tab stays at the last used tab, switch to UpgradeMaterials
        # self.item_goto(KEYWORDS_ITEM_TAB.UpgradeMaterials, wait_until_stable=False)
        oil, money, diamond = self._get_data()
        logger.info(f'-------{oil}, {money}, {diamond}')

        # self.item_goto(KEYWORDS_ITEM_TAB.Relics, wait_until_stable=False)
        # relic = self._get_relic()

        with self.config.multi_set():
            # self.config.stored.Credit.value = credit
            # self.config.stored.StallerJade.value = jade
            # self.config.stored.Relic.value = relic
            self.config.stored.Money.value = money
            self.config.stored.Oil.value = oil
            self.config.stored.Diamond.value = diamond
            self.config.task_delay(server_update=True)
            # Sync to planner
            # require = self.config.cross_get('Dungeon.Planner.Item_Credit.total', default=0)
            # if require:
            #     self.config.cross_set('Dungeon.Planner.Item_Credit.value', credit)
            #     self.config.cross_set('Dungeon.Planner.Item_Credit.time', self.config.stored.Credit.time)
            #     self.planner_write()
