
from tasks.base.ui import UI
from module.ocr.ocr import DataDigit
from tasks.base.assets.assets_base_page import RESOURCE_DATA
import numpy.typing as npt
import numpy as np
from module.logger.logger import logger

class ResourceCheck(UI):
    def get_current_resources(self, image: npt.NDArray[np.uint8] | None = None):
        ocr = DataDigit(RESOURCE_DATA)
        if image is None:
            image = self.device.image
        r = ocr.detect_and_ocr(image, show_log=False)
        data = [int(i.ocr_text) for i in r if i.ocr_text.isdigit()]
        if len(data) == 3:
            return (data[0],data[1],data[2])
        else:
            return None
        