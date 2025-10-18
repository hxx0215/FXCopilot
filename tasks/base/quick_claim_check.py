from tasks.base.ui import UI
from module.base.button import ButtonWrapper
from tasks.base.page import page_reward
from module.ocr.ocr import QuickClaimTimeOcr,ItemOcr
from module.base.button import ItemWrapper
from module.base.timer import Timer
from datetime import timedelta


class QuickClaimCheck(UI):
    def __init__(self, config,ocr_data: ButtonWrapper, device=None, task=None):
        self.ocr_data = ocr_data
        super().__init__(config, device, task)

    def check_if_finished(self):
        self.ui_ensure(page_reward)
        ocr = QuickClaimTimeOcr(self.ocr_data)
        timer = Timer(5).start()
        for image in self.loop():
            (has_finished, deltas) = ocr.ocr_single_line(image)
            if has_finished or len(deltas) != 0:
                break
            if timer.reached():
                return (False, [timedelta(hours=2)], False)
        return (has_finished, deltas, True)

    def find_item(self, item: ItemWrapper) -> int:
        ocr = ItemOcr(item)
        timer = Timer(5).start()
        for image in self.loop():
            if self.appear(item):
                ocr_result = ocr.ocr_single_line(image)
                if ocr_result.isdigit():
                    cnt = int(ocr_result)
                else:
                    continue
                if cnt > 0:
                    return cnt
                else:
                    continue
            if timer.reached():
                return 0
        return 0
    
    def add_item(self, items: list[tuple[ItemWrapper, int]], search_area:tuple[int,int,int,int]):
        idx = 0
        for image in self.loop():
            (item, cnt) = items[idx]
            added_item = item.temp_multi_match(image, search_area)
            if len(added_item) == cnt:
                idx = idx + 1
                if idx == len(items):
                    break
                else:
                    continue
            if self.appear_then_click(item, interval=1):
                continue