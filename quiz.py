"""개별 퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """퀴즈 한 문제를 나타내는 클래스.

    속성(attribute):
        question (str): 문제 지문
        choices (list[str]): 선택지 목록(기본 4개)
        answer (int): 정답 번호 (1~4 중 하나)
        hint (str): 힌트(선택 사항, 없으면 빈 문자열)
    """

    def __init__(self, question: str, choices: list[str], answer: int, hint: str=""):
        # __init__ 은 객체가 만들어질 때 자동으로 호출되어 속성을 초기화한다.
        # self 는 "지금 만들어지는 바로 그 객체 자신"을 가리킨다.
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self):
        """문제 지문과 선택지를 화면에 출력하는 메서드."""
        print(self.question)
        for number, choice in enumerate(self.choices, start=1):
            print(f"   {number}. {choice}")

    def is_correct(self, number: int):
        """입력한 번호(number)가 정답인지 True/False 로 알려주는 메서드."""
        return number == self.answer

    def correct_text(self):
        """정답 선택지의 실제 내용을 돌려준다. (오답 안내에 사용)"""
        return self.choices[self.answer - 1]

    def to_dict(self):
        """JSON 파일로 저장하기 위해 딕셔너리 형태로 변환한다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """JSON 파일에서 읽어 온 딕셔너리(data)로부터 Quiz 객체를 만든다.

        classmethod 를 사용하면 Quiz.from_dict(...) 형태로
        객체를 생성하는 별도의 방법을 제공할 수 있다.
        """
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint", ""),  # 옛 데이터에 hint 가 없어도 오류 없이 동작
        )
