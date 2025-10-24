
from tasks.base.ui import UI
from tasks.base.page import page_naval_port,page_quiz_center
from module.ocr.ocr import OcrResultButton, OcrWhiteLetterOnComplexBackground,Digit,Ocr
from module.logger import logger
from pponnxcr.predict_system import BoxedResult
from tasks.base.assets.assets_base_page import QUIZ_START_DATA,QUIZ_QUESTION_DATA,QUIZ_CANDIDATE_DATA,QUIZ_REFRESH_DATA,MIDSHIPS_CANDIDATE,STERN_CANDIDATE,QUIZ_EMPTY_PAGE
from tasks.base.assets.assets_base_dialogue import DIALOGUE_NEXT
from module.ocr.keyword import Keyword
from dataclasses import dataclass
from typing import ClassVar
from module.exception import RequestHumanTakeover
from module.base.button import ClickButton
import re
import jellyfish
import math
import random

from tasks.quiz_center.quiz_store import QuizItem, QuizStore

class OcrAfter:
    @classmethod
    def process(cls, result: str) -> str:
        pattern = r'[^\u4e00-\u9fa5a-zA-Z0-9\s]'
        result = re.sub(pattern,'', result)
        result = re.sub(r'强大拥有一座','强大拥有座', result)
        result = re.sub(r'强大拥有二座','强大拥有座', result)
        result = re.sub(r'帮','需',result)
        result = re.sub(r'八爬|八', '八咫', result)
        result = re.sub(r'凤楼|(?<!大)凤','凤棲', result)
        return result
class DataDigit(Digit):
    def after_process(self, result):
        result = re.sub(r'[l|]', '1', result)
        result = re.sub(r'[oO]', '0', result)
        return super().after_process(result)
class NormalOcr(Ocr):
    def after_process(self, result):
        result = OcrAfter.process(result)
        return super().after_process(result)
    def _product_button(
            self,
            boxed_result: BoxedResult,
            keyword_classes,
            lang: str| None = None,
            ignore_punctuation=True,
            ignore_digit=True 
    ) -> OcrResultButton:
        return super()._product_button(
            boxed_result,
            keyword_classes,
            lang,
            ignore_punctuation,
            ignore_digit=False 
        )
class QuizOcr(OcrWhiteLetterOnComplexBackground):
    def after_process(self, result):
        result = OcrAfter.process(result)
        return super().after_process(result)
@dataclass(repr=False)
class QuizCenterKeyword(Keyword):
    instances: ClassVar = {}
    @classmethod
    def init(cls,id: int, name: str):
        return cls(id,name,cn = name,en = name,jp = name, cht = '',es = '')
@dataclass(repr=False)
class QuizCandidateKeyword(QuizCenterKeyword):
    instances: ClassVar = {}

@dataclass(repr=False)
class QuizRelationshipLevelKeyword(QuizCenterKeyword):
    instances: ClassVar = {}

@dataclass(repr=False)
class QuizQuestionKeyword(QuizCenterKeyword):
    instances: ClassVar = {}
@dataclass(repr=False)
class QuizFuzzyCompareKeyword(QuizCenterKeyword):
    instances: ClassVar = {}
    max_sim = 0.0
    max_name = ""
    max_keyword = ""
    similary = 0.0
    @classmethod
    def _compare(cls, name, keyword):
        similar = jellyfish.jaro_winkler_similarity(name, keyword)
        if similar > cls.max_sim:
            cls.max_sim = similar
            cls.max_name = name
            cls.max_keyword = keyword
        return similar > 0.85
@dataclass(repr=False)
class QuizQuestionFuzzyCompareKeyword(QuizFuzzyCompareKeyword):
    instances: ClassVar = {}
@dataclass(repr=False)
class QuizCandidateFuzzyCompareKeyword(QuizFuzzyCompareKeyword):
    instances: ClassVar = {}



    
class QuizCenter(UI):

    def __init__(self, config, device=None, task=None):
        self._store = QuizStore()
        self._store.load()
        super().__init__(config, device, task)

    def choose_quiz_ship(self):
        relationship_level = ['陌生','相识','亲近','喜欢','誓约','依偎','守护','至爱','铭心','永恒','爱']# 爱不用做题
        keywords = [QuizRelationshipLevelKeyword.init(idx,l) for idx,l in enumerate(relationship_level)]
        ocr = QuizOcr(QUIZ_START_DATA)
        result = []
        for _ in self.loop():
            result = ocr.matched_ocr(self.device.image, keyword_classes=keywords)
            if (len(result) > 0):
                break
            elif self.appear(QUIZ_EMPTY_PAGE):
                return True
        ocr_btn = result[0]
        filtered_result = [x for x in result if x not in ['爱','永恒']]
        if filtered_result:
            ocr_btn = random.choice(filtered_result)
        else:
            ocr_btn = random.choice(result)
        for _ in self.loop():
            if self.handle_popup_confirm():
                break
            if self.ui_ocr_button_click(ocr_btn):
                continue
        for _ in self.loop():
            if self.appear_then_click(DIALOGUE_NEXT):
                break
        return False
    def find_question(self) -> QuizItem | None:
        question_ocr = QuizOcr(QUIZ_QUESTION_DATA)
        detected_question = set()
        max_question_similary = 0.85
        max_question = None
        cnt = 0
        for _ in self.loop():
            questions = question_ocr.detect_and_ocr(self.device.image)
            if (len(questions) > 0):
                cnt = cnt + 1
                cur_question = None
                cur_similary = 0.85
                ocr_q = None
                for q in questions:
                    if math.isclose(cur_similary, 1.0):
                        break
                    for data in self._store.quiz_data:
                        if q.ocr_text == OcrAfter.process(data.question):
                            cur_similary = 1.0
                            cur_question = data
                            ocr_q = q
                            break
                        similar = jellyfish.jaro_winkler_similarity(OcrAfter.process(data.question), q.ocr_text)
                        if similar > cur_similary:
                            cur_similary = similar
                            cur_question = data
                            ocr_q = q
                logger.info(f"current : {cur_similary} - {max_question_similary} - {cur_question} - {detected_question}")
                if (cur_similary > max_question_similary and cur_question and (not (OcrAfter.process(cur_question.question) in detected_question))) or math.isclose(cur_similary, 1.0):
                    max_question = cur_question
                    max_question_similary = cur_similary
                    if math.isclose(cur_similary, 1.0):
                        break
                    detected_question.add(OcrAfter.process(cur_question.question if cur_question else ''))
                if cur_question and ocr_q:
                    logger.info(f"question similar <{OcrAfter.process(cur_question.question)}> <{ocr_q.ocr_text}> <{max_question_similary}> <{OcrAfter.process(cur_question.question) == ocr_q.ocr_text}>")
                logger.info(f"current cnt: {cnt}")
                if cnt >= 10:
                    break
        # if not max_question:
        #     self.device.save_screenshot(genre='quiz_center')
        #     raise RequestHumanTakeover
        return max_question
    
    def special_answer(self, question: QuizItem) -> int:
        if (question.question == "舰船的烟雾发生器通常布置在"):
            button = STERN_CANDIDATE
            f = button.match_template(self.device.image)
            if f:
                logger.info(f"click at {button.button}")
            if self.appear(STERN_CANDIDATE):
                return 1
            else:
                return -1
        if (question.question == "防雷装置通常安装在战舰的哪个区域"):
            button = MIDSHIPS_CANDIDATE
            f = button.match_template(self.device.image)
            if f:
                logger.info(f"click at {button.button}")
            if self.appear(MIDSHIPS_CANDIDATE): # change to apear and click
                return 1
            else:
                return -1
        return 0
    
    def find_answer(self, max_question: QuizItem) -> BoxedResult | int:
        special_check = self.special_answer(max_question)
        if special_check:
            return special_check
        right_answer = max_question.option[0]
        answer_ocr = NormalOcr(QUIZ_CANDIDATE_DATA)
        cnt = 0
        detected_answer = set()
        max_answer_similary = 0.85
        max_answer = None
        for _ in self.loop():
            answers = answer_ocr.detect_and_ocr(self.device.image)
            if (len(answers) > 0):
                cnt = cnt + 1
                cur_answer = None
                cur_similary = 0.65
                for ans in answers:
                    if OcrAfter.process(right_answer)==ans.ocr_text:
                        cur_similary = 1.0
                        cur_answer = ans
                        break
                    similar = jellyfish.jaro_winkler_similarity(OcrAfter.process(right_answer), ans.ocr_text)
                    logger.info(f"answer similar <{OcrAfter.process(right_answer)}> <{ans.ocr_text}> <{similar}> <{OcrAfter.process(right_answer) == ans.ocr_text}>")
                    if similar > cur_similary:
                        cur_similary = similar
                        cur_answer = ans
                if cur_similary > max_answer_similary and cur_answer and (not cur_answer.ocr_text in detected_answer) or math.isclose(max_answer_similary, 1.0):
                    max_answer_similary = cur_similary
                    max_answer = cur_answer
                    if math.isclose(max_answer_similary, 1.0):
                        break
                    detected_answer.add(cur_answer.ocr_text if cur_answer else '')
                if cnt >= 10:
                    break
        if not max_answer:
            self.device.save_screenshot(genre='quiz_center')
            raise RequestHumanTakeover
        return max_answer

    def remain_times(self):
        ocr = DataDigit(QUIZ_REFRESH_DATA)
        c = -1
        for _ in self.loop():
            r = ocr.detect_and_ocr(self.device.image)
            if len(r) > 0:
                c = [re.sub(r'\s','',d.ocr_text) for d in r][0]
                return c.find('0') != 0
        return False
    
    def quiz_and_answer(self):
        empty = self.choose_quiz_ship()
        if empty:
            return True
        #if not find
        question = self.find_question()
        if not question:
            logger.warning("find question failed reroll quiz")
            self.device.adb_shell(['input', 'keyevent', '4'])
            return False

        answer = self.find_answer(question)
        match answer:
            case 1:
                logger.info(f"find in special has been clicked")
            case -1:
                logger.warning("find answer failed reroll quiz")
                self.device.adb_shell(['input', 'keyevent', '4'])
            case BoxedResult():
                ocr_button = OcrResultButton(answer, None) 
                self.ui_ocr_button_click(ocr_button)
                self.device.sleep(8)
        for _ in self.loop():
            if self.appear_then_click(DIALOGUE_NEXT):
                break
        self.device.sleep(12)
        return False
                
                    
    def run(self):
        self.ui_ensure(page_quiz_center)
        empty = False
        while not empty:
            empty = self.quiz_and_answer()
        self.config.task_delay(server_update=True)
if __name__ == '__main__':
    task = QuizCenter('src', task='QuizCenter')
    import os
    path = os.path.dirname(__file__)
    image_path = os.path.join(path,"special_quiz","test7.png")
    task.image_file=image_path
    print(task.remain_times())
    # store = QuizStore()
    # store.load()
    # question = task.find_question()
    # logger.info(f"find question {question}")
    # answer = task.find_answer(question)
    # match answer:
    #     case bool():
    #         logger.info(f"find in special has been clicked")
    #     case _:
    #         logger.info(f"click {answer}")
