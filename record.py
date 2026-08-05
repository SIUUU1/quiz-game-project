"""한 번의 게임 플레이 결과를 표현하는 ScoreRecord 클래스."""

from datetime import datetime

class ScoreRecord:
    """게임 한 판의 기록을 나타내는 클래스.

    속성(attribute):
        date (str): 플레이한 날짜/시간 ("YYYY-MM-DD HH:MM" 형식)
        count (int): 그 판에서 푼 문제 수
        score (int): 최종 점수
    """

    def __init__(self, count: int, score: int, date=None):
        self.count = count
        self.score = score
        # date 를 따로 주지 않으면 지금 시각을 자동으로 기록한다.
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.date = date

    def summary(self):
        """화면에 보여 줄 한 줄 요약 문자열을 돌려준다."""
        return f"[{self.date}] {self.count}문제 중 {self.score}점"

    def to_dict(self):
        """JSON 저장을 위해 딕셔너리로 변환한다."""
        return {"date": self.date, "count": self.count, "score": self.score}

    @classmethod
    def from_dict(cls, data):
        """JSON 에서 읽어 온 딕셔너리로부터 ScoreRecord 객체를 만든다."""
        return cls(
            count=data["count"],
            score=data["score"],
            date=data.get("date", "날짜 미상"),
        )
