# Day 4. 타입 힌트 (Type Hints)

Day 3에서 `devices` 패키지로 파일을 나누는 법을 배웠으니, 오늘은 함수/변수에 **타입을 명시하는 법**을 배운다.
2주차에 만날 FastAPI가 이 타입 힌트를 기반으로 동작하는 `Pydantic`이라는 라이브러리를 핵심으로 쓰기 때문에, 지금 익혀두면 나중에 훨씬 수월해진다.

---

## 1. 왜 배우는가

파이썬은 원래 타입을 안 써도 되는 언어다 (`x = 5`, `x = "hello"` 둘 다 가능). 그런데 실무 코드, 특히 여러 사람이 협업하는 프로젝트에서는 "이 함수가 뭘 받고 뭘 돌려주는지"를 명시해두는 게 훨씬 안전하다.

한섭님이 C++에서 당연하게 쓰던 `float x`, `bool move(std::string position)` 같은 타입 명시를, 파이썬에서는 **선택사항으로 추가**할 수 있다 — 그게 타입 힌트다.

---

## 2. 기본 문법

```python
def move(position: str, speed: float) -> bool:
    print(f"{speed} 속도로 {position}까지 이동")
    return True
```

- `position: str` → 매개변수 `position`은 문자열이어야 한다는 "힌트"
- `speed: float` → `speed`는 실수형이어야 한다는 힌트
- `-> bool` → 이 함수는 `bool`을 반환한다는 힌트

**중요한 포인트**: 이건 어디까지나 "힌트"다. C++ 컴파일러처럼 타입이 틀리면 강제로 막아주는 게 아니라, `move("P1", "빠르게")`처럼 타입을 어겨도 파이썬은 실행 시점에 에러를 내지 않는다. 대신:

- VS Code 같은 에디터가 실시간으로 "타입이 안 맞는 것 같다"고 경고해준다.
- 협업하는 동료가 함수만 보고도 뭘 넣어야 할지 바로 안다.
- 나중에 `mypy` 같은 도구로 전체 프로젝트의 타입 오류를 검사할 수 있다.

---

## 3. 변수에도 타입 힌트를 붙일 수 있다

```python
camera_name: str = "Camera-A"
capture_count: int = 0
is_connected: bool = False
timeout_sec: float = 2.5
```

---

## 4. 자주 쓰는 타입: 리스트, 딕셔너리

```python
from typing import List, Dict

def get_camera_list() -> List[str]:
    return ["Camera-A", "Camera-B", "Camera-C"]

def get_robot_status() -> Dict[str, bool]:
    return {"UR5": True, "RB5": False}
```

(참고: Python 3.9+부터는 `List`, `Dict` 대신 그냥 `list[str]`, `dict[str, bool]`처럼 소문자로 써도 된다. Day 1에 3.13 설치했으니 소문자 버전을 써도 무방하다.)

```python
def get_camera_list() -> list[str]:
    return ["Camera-A", "Camera-B", "Camera-C"]
```

---

## 5. 값이 없을 수도 있을 때: `Optional`

로봇이 아직 연결 안 됐으면 상태값이 없을 수도 있는 경우:

```python
from typing import Optional

def get_last_error(robot_name: str) -> Optional[str]:
    # 에러가 없으면 None, 있으면 에러 메시지 문자열
    if robot_name == "RB5":
        return "연결 타임아웃"
    return None
```

`Optional[str]`은 "`str`이거나 `None`이거나 둘 중 하나"라는 뜻이다. (Python 3.10+ 문법으로는 `str | None`으로도 쓸 수 있다.)

---

## 6. 여러 타입 중 하나: Union (`|`)

```python
def send_command(value: int | str) -> None:
    print(f"명령 전송: {value}")
```

`int | str`은 "정수 아니면 문자열, 둘 중 하나"라는 뜻. 카메라 설정값이 숫자(`exposure=100`)일 수도, 문자열(`mode="auto"`)일 수도 있는 상황에 자주 쓴다.

---

## 7. 클래스에 타입 힌트 적용하기

```python
class Robot:
    def __init__(self, name: str, max_speed: float):
        self.name: str = name
        self.max_speed: float = max_speed
        self.is_connected: bool = False

    def move(self, position: str, speed: float) -> bool:
        if speed > self.max_speed:
            print("최대 속도 초과!")
            return False
        print(f"{self.name} -> {position} 이동 ({speed} 속도)")
        return True
```

Day 1에 배운 클래스 문법에 타입만 얹은 것뿐이라 낯설지 않을 것이다.

---

## 8. 미리 보는 FastAPI 연결고리

FastAPI/Pydantic에서는 이런 클래스를 이렇게 쓰게 된다 (지금 당장 이해 안 돼도 괜찮음, 2주차에 다시 다룸):

```python
from pydantic import BaseModel

class RobotMoveRequest(BaseModel):
    position: str
    speed: float
```

지금 배운 `position: str`, `speed: float` 문법이 그대로 재사용되는 걸 볼 수 있다 — Pydantic은 타입 힌트를 "읽어서" 자동으로 데이터 검증을 해주는 라이브러리다. 오늘 배운 게 헛되지 않는다는 걸 미리 보여주려고 넣어봤다.

---

## 9. 오늘의 연습문제

1. `devices/robot.py`의 `move` 함수에 타입 힌트를 추가해보기. (`position: str, speed: float) -> bool`)
2. 카메라 이름과 연결 상태를 담는 `dict[str, bool]`을 반환하는 `get_camera_status() -> dict[str, bool]` 함수 작성해보기.
3. (심화) `Robot` 클래스를 만들어서 `name`, `max_speed` 속성에 타입 힌트를 붙이고, `move()` 메서드가 `max_speed`를 초과하는 속도로 호출되면 `False`를 반환하도록 작성해보기.

---

## 10. 다음 (Day 5) 예고

다음은 **파일 입출력(JSON)** — 장비 설정값을 JSON 파일로 저장하고 불러오는 실습으로 이어간다. 오늘 배운 타입 힌트를 활용해서, JSON으로 읽어온 데이터를 딕셔너리 타입으로 다루는 것까지 같이 해볼 예정이다.
