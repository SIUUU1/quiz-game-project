"""프로그램 진입점

실행 방법:
    python main.py

QuizGame 객체를 만들어 게임을 시작한다.
"""
from quiz_game import QuizGame

def main():
    """게임을 실행한다."""
    game = QuizGame()
    game.run()

if __name__ == "__main__":
    main()
