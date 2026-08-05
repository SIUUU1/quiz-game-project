"""사용자 입력과 예외 처리를 담당하는 도우미 함수 모음.

이 파일에 입력 관련 로직을 모아 두어
공백 제거, 재입력, 숫자 입력, 텍스트 입력 , 예외 처리 등을 담당한다.
"""


class ExitRequested(Exception):
    """Ctrl+C(KeyboardInterrupt) 또는 입력 종료(EOFError)가 발생했을 때
    "안전하게 종료하라"는 신호로 사용하는 예외.

    입력 함수에서 이 예외를 던지면, 게임의 메인 루프가 이를 붙잡아
    데이터를 저장한 뒤 정상적으로 종료할 수 있다.
    """
    pass


def read_line(prompt):
    """한 줄을 입력받아 앞뒤 공백을 제거해서 돌려준다.

    - 입력 앞뒤 공백을 제거한다. (예: " 1 " -> "1")
    - Ctrl+C(KeyboardInterrupt)나 입력 스트림 종료(EOFError)가 발생하면
      프로그램이 비정상 종료되지 않도록 ExitRequested 예외로 바꿔서 던진다.
    """
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print()  # 커서를 다음 줄로 옮겨 출력이 깨지지 않게 한다.
        raise ExitRequested()


def get_int(prompt: str, min_value: int, max_value: int):
    """min_value ~ max_value 범위의 주어진 범위의 정수를 입력받아 반환한다.

    다음 경우를 모두 처리한다.
    - 빈 입력(그냥 Enter): 안내 후 재입력
    - 숫자로 변환할 수 없는 입력(예: abc): 안내 후 재입력
    - 허용 범위를 벗어난 숫자(예: 0, 9): 안내 후 재입력
    """
    while True:
        text = read_line(prompt)

        if text == "":
            print(f" ⚠️  입력이 비어 있습니다. {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        try:
            value = int(text)
        except ValueError:
            print(f" ⚠️  숫자만 입력할 수 있습니다. {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        if value < min_value or value > max_value:
            print(f" ⚠️  {min_value}~{max_value} 사이의 숫자를 입력하세요.")
            continue

        return value


def get_text(prompt:str):
    """빈 문자열이 아닌 텍스트를 받을 때까지 반복해서 입력받는다.

    문제 지문이나 선택지처럼 반드시 내용이 있어야 하는 입력에 사용한다.
    """
    while True:
        text = read_line(prompt)
        if text == "":
            print(" ⚠️  내용을 입력해 주세요.")
            continue
        return text
