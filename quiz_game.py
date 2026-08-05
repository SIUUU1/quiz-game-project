"""퀴즈 게임 전체를 관리하는 QuizGame 클래스와 기본 퀴즈 데이터."""

import json
import os
import random

from quiz import Quiz
from record import ScoreRecord
from io_utils import read_line, get_int, get_text, ExitRequested

# state.json 은 이 파일(quiz_game.py)이 있는 폴더(= 프로젝트 루트)에 둔다.
# 이렇게 하면 어느 위치에서 프로그램을 실행하더라도 항상 같은 파일을 사용한다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")


def default_quizzes():
    """저장 파일이 없거나 손상됐을 때 사용할 기본 퀴즈 데이터.

    주제: '한국사 기초 상식' (5개 이상)
    각 퀴즈는 문제 / 선택지 4개 / 정답 번호(1~4) / 힌트로 구성된다.
    """
    return [
        Quiz(
            "조선을 건국한 태조는 누구인가?",
            ["이성계", "왕건", "이방원", "정도전"],
            1,
            hint="위화도 회군으로 정권을 잡았습니다.",
        ),
        Quiz(
            "훈민정음(한글)을 창제한 조선의 왕은?",
            ["태종", "세종대왕", "성종", "정조"],
            2,
            hint="만 원권 지폐에 그려진 왕입니다.",
        ),
        Quiz(
            "고구려·백제·신라 중 삼국을 통일한 나라는?",
            ["고구려", "백제", "신라", "가야"],
            3,
        ),
        Quiz(
            "임진왜란 때 한산도 대첩 등에서 활약한 장군은?",
            ["강감찬", "이순신", "을지문덕", "김유신"],
            2,
            hint="거북선을 이끈 장군입니다.",
        ),
        Quiz(
            "후삼국을 통일하고 고려를 건국한 왕은?",
            ["왕건", "견훤", "궁예", "이성계"],
            1,
        ),
        Quiz(
            "1919년 일제강점기에 일어난 대규모 독립운동은?",
            ["6·10 만세운동", "3·1 운동", "광주 학생운동", "갑오개혁"],
            2,
            hint="유관순 열사가 참여했습니다.",
        ),
        Quiz(
            "698년에 발해를 건국한 인물은?",
            ["대조영", "온조", "주몽", "김수로"],
            1,
        ),
    ]


class QuizGame:
    """퀴즈 게임 전체를 관리하는 클래스.

    퀴즈 목록, 최고 점수, 점수 기록 등의 데이터를 관리하고,
    메뉴 표시, 퀴즈 풀이, 퀴즈 추가·삭제, 점수 확인,
    데이터 저장·불러오기 등의 기능을 제공한다.

    Attributes:
    quizzes (list[Quiz]): 퀴즈 목록
    best_score (int): 최고 점수
    history (list[ScoreRecord]): 게임 점수 기록
    """

    def __init____init__(
            self,
            quizzes: list[Quiz] | None = None,
            best_score: int = 0,
            history: list[ScoreRecord] | None = None
    ):
        # 인자를 주지 않으면 빈 목록/0점으로 시작한다.
        self.quizzes = quizzes if quizzes is not None else []
        self.best_score = best_score
        self.history = history if history is not None else []

    # ------------------------------------------------------------------
    # 파일 저장 / 불러오기 (state.json)
    # ------------------------------------------------------------------

    def load(self):
        """state.json 에서 데이터를 불러온다.

        - 파일이 없으면(첫 실행) 기본 퀴즈로 시작한다.
        - 파일이 손상됐거나 읽기 오류가 나면 안내 후 기본 퀴즈로 복구한다.
        """
        if not os.path.exists(STATE_FILE):
            self._reset_to_default()
            print("ℹ️  저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            return

        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.quizzes = [Quiz.from_dict(q) for q in data["quizzes"]]
            self.best_score = data.get("best_score", 0)
            self.history = [ScoreRecord.from_dict(r) for r in data.get("history", [])]
            print(
                f"📂 저장된 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)"
            )
        except (json.JSONDecodeError, KeyError, TypeError, OSError):
            #JSONDecodeError → JSON 문법 문제, KeyError → 딕셔너리 키 문제, 
            #TypeError →. 자료형 문제, OSError → 파일 문제
            # 파일이 깨졌거나 형식이 이상하거나 읽기 오류가 난 모든 경우를 처리한다.
            print("⚠️  데이터 파일이 손상되어 기본 퀴즈로 복구합니다.")
            self._reset_to_default()

    def _reset_to_default(self):
        """기본 퀴즈 데이터로 상태를 초기화한다.(내부용)"""
        self.quizzes = default_quizzes()
        self.best_score = 0
        self.history = []

    def save(self):
        """현재 데이터를 state.json 에 UTF-8 인코딩으로 저장한다."""
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "best_score": self.best_score,
            "history": [r.to_dict() for r in self.history],
        }
        try:
            # with open(...) 파일을 열고 작업이 끝나면 자동으로 파일을 닫아주는 구조
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                # ensure_ascii=False -> 한글이 그대로 저장된다.
                # indent=2 -> 사람이 읽기 편하게 들여쓰기해서 저장
                # "w" -> 기존 내용 삭제 후 작성
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            print("⚠️  데이터를 저장하는 중 오류가 발생했습니다.")

    # ------------------------------------------------------------------
    # 메뉴 & 메인 루프
    # ------------------------------------------------------------------

    def show_menu(self):
        """메뉴 화면을 출력한다."""
        print()
        print("=" * 42)
        print("            🎯 나만의 퀴즈 게임 🎯")
        print("=" * 42)
        print(" 1. 퀴즈 풀기")
        print(" 2. 퀴즈 추가")
        print(" 3. 퀴즈 목록")
        print(" 4. 퀴즈 삭제")
        print(" 5. 점수 확인")
        print(" 6. 종료")
        print("=" * 42)

    def run(self):
        """게임의 메인 루프. 메뉴를 반복 출력하고 선택에 따라 기능을 실행한다."""
        self.load()
        try:
            while True:
                self.show_menu()
                choice = get_int(" 선택: ", 1, 6)

                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    self.add_quiz()
                elif choice == 3:
                    self.list_quizzes()
                elif choice == 4:
                    self.delete_quiz()
                elif choice == 5:
                    self.show_score()
                elif choice == 6:
                    print("👋 게임을 종료합니다. 안녕히 가세요!")
                    break
        except ExitRequested:
            # Ctrl+C 또는 입력 종료 시: 비정상 종료 대신 안내 후 안전하게 종료한다.
            print("ℹ️  입력이 중단되어 데이터를 저장하고 안전하게 종료합니다.")
        finally:
            # 어떤 경로로 종료되든 마지막에 항상 저장한다.
            self.save()

    def play_quiz(self):
        pass

    def add_quiz(self):
        pass
    
    def list_quizzes(self):
        pass
    
    def delete_quiz(self):
        pass
    
    def show_score(self):
        pass