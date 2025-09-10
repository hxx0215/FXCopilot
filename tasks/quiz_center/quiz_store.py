from dataclasses import dataclass
import re
@dataclass
class QuizItem:
    question: str
    option: list[str]

class QuizStore():
    QUIZ_DATA_FILE = './assets/quiz/quiz.txt'
    quiz_data: list[QuizItem] = []
    def load(self) -> None:
        with open(self.QUIZ_DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            b = content.strip().split('\n')
            pattern = r'[^\u4e00-\u9fa5a-zA-Z0-9\s]'
            blocks = [re.sub(pattern,'',bl) for bl in b ]
            self.quiz_data = [QuizItem(question=blocks[i], option=blocks[i+1:i+4]) for i in range(0, len(blocks), 4)]
if __name__ == '__main__':
    q = QuizStore()
    q.load()