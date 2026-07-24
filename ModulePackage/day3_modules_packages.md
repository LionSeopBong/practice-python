# Day 3. 모듈 & 패키지 (Module & Package)

Day 2에서 asyncio로 카메라/로봇을 동시에 다루는 법을 배웠으니,
오늘은 그 코드를 **파일 여러 개로 나눠서 관리하는 법**을 배운다. 나중에 FastAPI 프로젝트 구조를 잡을 때 그대로 쓰게 될 내용이다.

---

## 1. 왜 배우는가

지금까지는 스크립트 하나(`main.py`)에 모든 코드를 다 넣었을 텐데, 실무에서는 이렇게 안 한다.

```
project/
├── main.py
├── camera.py      # 카메라 SDK 관련 코드
├── robot.py       # UR/RB 로봇 제어 코드
└── config.py      # 설정값
```

이렇게 파일(=모듈)을 역할별로 나누고, 서로 `import`해서 쓰는 게 기본이다. FastAPI 프로젝트도 결국 `routers/`, `models/`, `services/` 같은 폴더(=패키지) 구조로 쪼개는 것뿐이라, 지금 감을 잡아두면 나중에 자연스럽게 넘어갈 수 있다.

**용어 정리**
- **모듈(module)**: `.py` 파일 하나. 예) `camera.py`
- **패키지(package)**: 모듈들을 모아놓은 폴더. `__init__.py` 파일이 있으면 패키지로 인식됨.

---

## 2. 가장 기본적인 import

`camera.py`

```python
# camera.py

def capture(name: str):
    print(f"[{name}] 촬영 완료")
    return f"{name}_image.jpg"

CAMERA_COUNT = 3
```

`main.py`

```python
# main.py
import camera

result = camera.capture("Camera-A")
print(camera.CAMERA_COUNT)
```

또는 필요한 것만 콕 집어서 가져올 수도 있다:

```python
from camera import capture, CAMERA_COUNT

result = capture("Camera-A")
```

`import camera` 방식은 `camera.capture()`처럼 어디서 온 함수인지 명확하다는 장점이 있고, `from camera import capture`는 짧게 쓸 수 있는 대신 여러 모듈에서 같은 이름을 가져오면 충돌할 수 있다는 단점이 있다. 팀 프로젝트에서는 보통 앞의 방식(`import camera` 후 `camera.capture()`)을 더 선호하는 편이다.

---

## 3. `if __name__ == "__main__":` — 반드시 알아야 하는 관용구

```python
# robot.py

def move(position: str):
    print(f"로봇 이동 -> {position}")

if __name__ == "__main__":
    # 이 파일을 "직접" 실행했을 때만 아래 코드가 실행됨
    move("TEST_POSITION")
```

- `robot.py`를 직접 `python robot.py`로 실행하면 `__name__`이 `"__main__"`이 되어서 아래 테스트 코드가 실행된다.
- 반대로 다른 파일에서 `import robot`으로 가져다 쓰면 `__name__`이 `"robot"`이 되어서 테스트 코드는 실행되지 않는다.

이 패턴을 안 쓰면, `camera.py`를 다른 곳에서 import만 했는데 테스트용 코드까지 같이 실행돼버리는 사고가 난다. C++에서 각 소스 파일에 `main()`을 하나만 두는 것과 비슷한 이유로, 파이썬은 파일마다 "이 파일이 직접 실행됐는지"를 구분할 방법이 필요해서 생긴 관용구다.

---

## 4. 패키지로 묶기 (`__init__.py`)

폴더 여러 개로 나눌 때는 이렇게 구성한다.

```
project/
├── main.py
└── devices/
    ├── __init__.py
    ├── camera.py
    └── robot.py
```

`devices/__init__.py` (비어있어도 되고, 아래처럼 자주 쓰는 것만 노출시켜도 됨)

```python
# devices/__init__.py
from .camera import capture
from .robot import move
```

`main.py`

```python
from devices import capture, move
# 또는
from devices.camera import capture
from devices.robot import move
```

`__init__.py`는 "이 폴더는 그냥 폴더가 아니라 패키지다"라는 표시이자, 패키지 내부에서 뭘 바깥으로 노출할지 정리하는 역할을 한다. `devices.camera`처럼 점(`.`)으로 경로를 따라가는 방식이 핵심이다.

---

## 5. 상대 경로 import (패키지 내부에서)

`devices/robot.py`가 같은 패키지 안의 `devices/config.py`를 쓰고 싶다면:

```python
# devices/robot.py
from .config import DEFAULT_SPEED   # . 은 "같은 패키지 안"이라는 뜻

def move(position: str):
    print(f"{DEFAULT_SPEED} 속도로 이동 -> {position}")
```

`.config`처럼 점으로 시작하는 걸 **상대 import**라고 하는데, 패키지 안에서 서로 참조할 때 쓴다. 헷갈리면 처음엔 그냥 절대 경로(`from devices.config import ...`)로 써도 무방하다 — 실무에서도 프로젝트 루트 기준 절대 import를 더 선호하는 경우가 많다.

---

## 6. 오늘의 연습문제

1. `devices/` 패키지를 만들고 그 안에 `camera.py`(촬영 함수), `robot.py`(이동 함수)를 나눠서 작성한 뒤, `main.py`에서 두 모듈을 import해서 각각 호출해보기.
2. `robot.py`에 `if __name__ == "__main__":` 블록을 추가해서, `python robot.py`로 직접 실행했을 때만 테스트 이동이 되도록 만들어보기.
3. (심화) Day 2에서 만든 asyncio 카메라/로봇 코드를 `devices/camera.py`, `devices/robot.py`로 나누고, `main.py`에서 `asyncio.gather`로 동시 실행하도록 리팩토링해보기.

---

## 7. 다음 예고

다음은 **파일 입출력(with open, JSON)** 또는 **타입 힌트(typing)** 중 이어서 원하시는 걸로 진행하면 된다. 장비 설정값을 JSON 파일로 저장/불러오는 실습을 하고 싶으면 파일 입출력을, FastAPI 진입 전 준비를 더 탄탄히 하고 싶으면 타입 힌트를 추천한다.
