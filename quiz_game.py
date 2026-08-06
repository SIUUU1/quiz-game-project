"""퀴즈 게임 전체를 관리하는 QuizGame 클래스와 기본 퀴즈 데이터."""

import json
import os
import random

from quiz import Quiz
from record import ScoreRecord
from io_utils import read_line, get_int, get_text, ExitRequested

# state.json 은 이 파일(quiz_game.py)이 있는 폴더(= 프로젝트 루트)에 둔다.
# 이렇게 하면 어느 위치에서 프로그램을 실행하더라도 항상 같은 파일을 사용한다.
# BASE_DIR : 현재 파일이 위치한 폴더의 절대경로
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

    def __init__(
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
            
    # ------------------------------------------------------------------
    # 1) 퀴즈 풀기  (보너스: 랜덤 출제, 문제 수 선택, 힌트)
    # ------------------------------------------------------------------

    def play_quiz(self):
        """저장된 퀴즈를 출제하고 채점한다."""
        if not self.quizzes:
            print("ℹ️  등록된 퀴즈가 없습니다. 먼저 '2. 퀴즈 추가'로 문제를 만들어 주세요.")
            return

        total = len(self.quizzes)
        print(f"\n총 {total}개의 퀴즈가 있습니다.")
        count = get_int(f" 몇 문제를 풀까요? (1~{total}): ", 1, total)

        # 보너스: random.sample 로 순서를 섞고 원하는 개수만큼 뽑는다.
        selected = random.sample(self.quizzes, count)

        print(f"\n📝 퀴즈를 시작합니다! (총 {count}문제)")
        print("-" * 42)

        correct_count = 0 #정답 갯수
        hints_used = 0 #사용한 힌트 갯수

        for index, quiz in enumerate(selected, start=1):
            print(f"\n[문제 {index}]")
            quiz.display()
            answer, used_hint = self._ask_answer(quiz)
            if used_hint:
                hints_used += 1

            if quiz.is_correct(answer):
                print(" ✅ 정답입니다!")
                correct_count += 1
            else:
                print(f" ❌ 오답입니다. 정답은 {quiz.answer}번({quiz.correct_text()})입니다.")

        # 보너스(힌트): 힌트를 사용한 만큼 점수를 1점씩 차감한다. (최소 0점)
        final_score = max(0, correct_count - hints_used)

        print("\n" + "=" * 42)
        print(f" 🏆 결과: {count}문제 중 {correct_count}문제 정답!")
        if hints_used > 0:
            print(f"    (힌트 {hints_used}회 사용 → 최종 {final_score}점)")
        else:
            print(f"    (최종 {final_score}점)")

        # 보너스(히스토리): 날짜/시간·문제 수·점수를 담은 ScoreRecord 객체로 기록한다.
        # (날짜는 ScoreRecord 안에서 자동으로 현재 시각이 채워진다.)
        self.history.append(ScoreRecord(count=count, score=final_score))

        if final_score > self.best_score:
            self.best_score = final_score
            print(" 🎉 새로운 최고 점수입니다!")
        print("=" * 42)

        self.save()

    def _ask_answer(self, quiz):
        """정답 번호(1~4)를 입력받아 (정답번호, 힌트사용여부)를 돌려준다.

        'h' 를 입력하면 힌트를 보여 준다.(힌트가 있는 경우)
        빈 입력 / 숫자 아님 / 범위 밖(0, 5 등)은 안내 후 재입력한다.
        """
        used_hint = False
        while True:
            raw = read_line(" 정답 입력 (1-4, 힌트는 h): ")

            if raw == "":
                print(" ⚠️  입력이 비어 있습니다. 1~4 사이의 숫자를 입력하세요.")
                continue

            if raw.lower() == "h":
                if quiz.hint:
                    print(f"   💡 힌트: {quiz.hint}  (힌트 사용 시 점수가 1점 차감됩니다)")
                    used_hint = True
                else:
                    print("   (이 문제에는 힌트가 없습니다.)")
                continue

            try:
                number = int(raw)
            except ValueError:
                print(" ⚠️  숫자만 입력할 수 있습니다. 1~4 사이의 숫자를 입력하세요.")
                continue

            if number < 1 or number > 4:
                print(" ⚠️  1~4 사이의 숫자를 입력하세요.")
                continue

            return number, used_hint
        
    # ------------------------------------------------------------------
    # 2) 퀴즈 추가
    # ------------------------------------------------------------------

    def add_quiz(self):
        """사용자에게 정보를 입력받아 새 퀴즈를 등록하고 파일에 저장한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = get_text(" 문제를 입력하세요: ")

        choices = []
        for i in range(1, 5):  # 선택지 4개
            choice = get_text(f" 선택지 {i}: ")
            choices.append(choice)

        answer = get_int(" 정답 번호 (1-4): ", 1, 4)
        hint = read_line(" 힌트 (없으면 그냥 Enter): ")  # 힌트는 비워 둘 수 있다.

        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save()
        print("✅ 퀴즈가 추가되었습니다!")

    # ------------------------------------------------------------------
    # 3) 퀴즈 목록
    # ------------------------------------------------------------------

    def list_quizzes(self):
        """등록된 퀴즈 목록을 보여 준다."""
        if not self.quizzes:
            print("ℹ️  등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 42)
        for i, quiz in enumerate(self.quizzes, start=1):
            print(f" [{i}] {quiz.question}")
        print("-" * 42)

    # ------------------------------------------------------------------
    # 4) 퀴즈 삭제 (보너스)
    # ------------------------------------------------------------------

    def delete_quiz(self):
        """번호를 선택해 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("ℹ️  삭제할 퀴즈가 없습니다.")
            return

        self.list_quizzes()
        number = get_int(" 삭제할 퀴즈 번호를 입력하세요: ", 1, len(self.quizzes))
        removed = self.quizzes.pop(number - 1)
        self.save()
        print(f"🗑️  삭제되었습니다: {removed.question}")
    
    # ------------------------------------------------------------------
    # 5) 점수 확인
    # ------------------------------------------------------------------

    def show_score(self):
        """최고 점수와 최근 플레이 기록을 보여 준다."""
        if not self.history:
            print("ℹ️  아직 퀴즈를 풀지 않았습니다. 먼저 '1. 퀴즈 풀기'를 해 보세요!")
            return

        print(f"\n🏆 최고 점수: {self.best_score}점")
        print(f" 지금까지 {len(self.history)}번 플레이했습니다.")
        print(" 최근 기록:")
        for record in self.history[-5:]:  # 최근 5개만 표시
            print(f"   - {record.summary()}")