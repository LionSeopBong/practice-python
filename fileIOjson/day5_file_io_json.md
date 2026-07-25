# Day 5. 파일 입출력 & JSON

Day 4에서 만든 `Robot` 클래스(`name`, `max_speed`)를 오늘은 **JSON 파일로 저장하고, 다시 불러오는 법**을 배운다.
장비 설정값(로봇 최대 속도, 카메라 노출값 등)을 코드에 하드코딩하지 않고 파일로 관리하는 실무 패턴이다.

---

## 1. 왜 배우는가

지금까지는 `Robot("UR5", max_speed=2.0)`처럼 값을 코드 안에 직접 썼는데, 실무에서는 이렇게 안 한다.

- 설정값이 바뀔 때마다 코드를 고치고 다시 배포하는 건 비효율적이다.
- 로봇이 UR5, RB5 여러 대면 설정 파일 하나에 다 모아두는 게 관리하기 쉽다.
- FastAPI 서버도 결국 요청 데이터를 JSON으로 주고받기 때문에, JSON 다루는 감각이 미리 필요하다.

---

## 2. 파일 열고 닫기: `with open(...)`

```python
# 쓰기
with open("log.txt", "w", encoding="utf-8") as f:
    f.write("로봇 UR5 이동 완료\n")

# 읽기
with open("log.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)
```

- `with`를 쓰면 블록이 끝날 때 파일이 **자동으로 닫힌다**. C++의 RAII(스코프 벗어나면 소멸자 호출)와 같은 발상이라고 생각하면 된다 — `with` 없이 직접 `f.close()`를 깜빡하면 파일이 계속 열려있는 채로 남을 수 있다.
- `"w"` = write(덮어쓰기), `"r"` = read(읽기), `"a"` = append(이어쓰기).
- `encoding="utf-8"`은 한글 깨짐 방지용으로 항상 붙이는 습관을 들이면 좋다 (Windows 환경에서 특히 중요하다).

---

## 3. JSON이란

JSON(JavaScript Object Notation)은 파이썬의 딕셔너리/리스트와 거의 똑같이 생긴 텍스트 포맷이다.

```json
{
  "name": "UR5",
  "max_speed": 2.0,
  "positions": ["P1", "P2", "P3"]
}
```

파이썬 딕셔너리 `{"name": "UR5", "max_speed": 2.0, "positions": ["P1", "P2", "P3"]}`와 구조가 사실상 동일하다. 그래서 파이썬에서는 `json` 모듈로 딕셔너리 ↔ JSON 파일을 거의 자동 변환할 수 있다.

---

## 4. JSON 파일로 저장하기 (`json.dump`)

```python
import json

robot_config = {
    "name": "UR5",
    "max_speed": 2.0,
}

with open("robot_config.json", "w", encoding="utf-8") as f:
    json.dump(robot_config, f, ensure_ascii=False, indent=2)
```

- `json.dump(데이터, 파일객체, ...)` → 딕셔너리를 JSON 형식으로 파일에 써준다.
- `ensure_ascii=False` → 한글이 `\uXXXX` 코드로 깨져서 저장되는 걸 방지 (한글 다루려면 거의 항상 필요).
- `indent=2` → 사람이 읽기 좋게 들여쓰기해서 저장.

---

## 5. JSON 파일 불러오기 (`json.load`)

```python
import json

with open("robot_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

print(config)              # {'name': 'UR5', 'max_speed': 2.0}
print(config["max_speed"]) # 2.0
```

`json.load(f)`는 파일 내용을 읽어서 **파이썬 딕셔너리로 자동 변환**해준다. 이제 이 `config`를 Day 4에서 배운 타입 힌트와 함께 쓸 수 있다:

```python
def load_robot_config(path: str) -> dict[str, str | float]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
```

---

## 6. 실전: `Robot` 클래스와 JSON 설정 파일 연결하기

`robot_config.json`

```json
{
  "name": "UR5",
  "max_speed": 2.0
}
```

`devices/robot.py`

```python
import json

class Robot:
    def __init__(self, name: str, max_speed: float):
        self.name: str = name
        self.max_speed: float = max_speed

    def move(self, position: str, speed: float) -> bool:
        if speed > self.max_speed:
            print(f"[{self.name}] 최대 속도({self.max_speed}) 초과! 이동 취소")
            return False
        print(f"[{self.name}] {position}까지 {speed} 속도로 이동")
        return True

    @classmethod
    def from_config_file(cls, path: str) -> "Robot":
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return cls(name=config["name"], max_speed=config["max_speed"])
```

`main.py`

```python
from devices import Robot

ur5 = Robot.from_config_file("robot_config.json")
ur5.move("P1", 1.5)
ur5.move("P2", 3.0)
```

`@classmethod`와 `"Robot"`(문자열로 감싼 타입 힌트)은 오늘 처음 보는 문법이니 참고만 하면 된다 — "설정 파일 경로만 주면 `Robot` 객체를 만들어주는 대안 생성자"라고 이해하면 충분하다. 이제 로봇을 바꾸고 싶으면 코드를 안 건드리고 `robot_config.json`의 숫자만 바꾸면 된다.

---

## 7. 파일이 없을 때 대비하기 (예외처리 복습)

Day 1에 배운 `try/except`가 여기서 다시 등장한다.

```python
def load_robot_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"설정 파일을 찾을 수 없음: {path}")
        return {"name": "UNKNOWN", "max_speed": 0.0}
```

설정 파일이 없거나 경로가 틀렸을 때 프로그램이 그냥 죽어버리지 않고, 기본값으로 넘어가도록 처리한 것이다.

---

## 8. 오늘의 연습문제

1. `robot_config.json` 파일을 만들고 (`name`, `max_speed` 포함), Python 코드에서 `json.load`로 불러와서 출력해보기.
2. `devices/robot.py`의 `Robot` 클래스에 `from_config_file` 클래스메서드를 추가해서, JSON 파일로부터 `Robot` 객체를 생성해보기.
3. (심화) 카메라 설정(`camera_config.json` — 카메라 이름 리스트와 각 노출값)도 JSON으로 저장/불러오기를 만들고, 파일이 없을 때는 `FileNotFoundError`를 잡아서 기본 설정으로 대체하도록 만들어보기.

---

## 9. 1주차 마무리 & 2주차 예고

여기까지 하면 1주차(Python 기초 문법) 계획의 핵심은 거의 다 다룬 셈이다 (변수/자료구조, 반복문/함수/클래스, 예외처리, asyncio, 모듈/패키지, 타입 힌트, 파일 입출력).

2주차부터는 계획대로 실무 라이브러리 — **requests**(HTTP 통신), **pyserial**(시리얼 통신), **FastAPI**(백엔드 프레임워크)로 넘어가면 된다. 오늘 만든 `Robot` 클래스, JSON 설정 파일, asyncio 패턴이 전부 그대로 재활용되니, 지금까지 만든 `devices/` 패키지를 계속 이어서 확장해나가면 된다.
