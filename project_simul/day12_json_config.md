# Day 12. 장비 목록을 JSON 설정 파일로 옮기기

지금까지 `robots`, `cameras` 딕셔너리가 `main.py` 코드 안에 하드코딩돼 있었다. 오늘은 이걸 `configs/devices.json` 파일로 옮겨서, **코드를 안 건드리고 장비를 추가/제거**할 수 있게 만든다. Day 5에서 배운 JSON 입출력이 이번 주 프로젝트의 핵심으로 실전 투입되는 날이다.

---

## 1. 목표 그림

**Before (지금)**
```python
robots = {
    "UR5": Robot(name="UR5", max_speed=2.0),
    "RB5": Robot(name="RB5", max_speed=1.5),
}
```
장비를 추가하려면 `main.py`를 열어서 코드를 고치고, 서버를 재시작해야 한다.

**After (오늘 목표)**
```json
// configs/devices.json
{
  "robots": [
    {"name": "UR5", "max_speed": 2.0},
    {"name": "RB5", "max_speed": 1.5}
  ],
  "cameras": [
    {"name": "Camera-A"}
  ]
}
```
장비를 추가하려면 이 JSON 파일에 한 줄 추가하면 끝 — `main.py`는 그대로 둔다.

---

## 2. JSON을 읽어서 객체로 변환하는 함수 (`devices/config.py`)

Day 9에서 폴더 구조에 `config.py`를 미리 만들어뒀는데, 오늘 여기를 채운다.

```python
# device/config.py
import json
from .robot import Robot
from .camera import Camera

def load_devices(path: str) -> tuple[dict[str, Robot], dict[str, Camera]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    robots = {
        item["name"]: Robot(name=item["name"], max_speed=item["max_speed"])
        for item in data["robots"]
    }
    cameras = {
        item["name"]: Camera(name=item["name"])
        for item in data["cameras"]
    }
    return robots, cameras
```

- `json.load(f)`로 JSON 파일을 딕셔너리/리스트 구조로 읽는 건 Day 5 그대로다.
- `{item["name"]: Robot(...) for item in data["robots"]}` — 이건 Day 3에서 봤던 리스트 컴프리헨션의 **딕셔너리 버전**이다 (딕셔너리 컴프리헨션이라고 부른다). "JSON의 로봇 목록 각각을 `Robot` 객체로 바꿔서, 이름을 키로 하는 딕셔너리를 만든다"는 뜻이다.

---

## 3. 파일이 없거나 형식이 잘못됐을 때 (Day 1 예외처리 복습)

```python
# device/config.py
import json
from .robot import Robot
from .camera import Camera

def load_devices(path: str) -> tuple[dict[str, Robot], dict[str, Camera]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"설정 파일을 찾을 수 없음: {path}, 빈 상태로 시작")
        return {}, {}
    except json.JSONDecodeError:
        print(f"설정 파일 형식이 잘못됨: {path}, 빈 상태로 시작")
        return {}, {}

    robots = {
        item["name"]: Robot(name=item["name"], max_speed=item["max_speed"])
        for item in data["robots"]
    }
    cameras = {
        item["name"]: Camera(name=item["name"])
        for item in data["cameras"]
    }
    return robots, cameras
```

`json.JSONDecodeError`는 파일은 있는데 JSON 문법이 깨져있을 때(쉼표 실수 등) 발생한다 — 실무에서 설정 파일을 손으로 고치다가 자주 만나는 에러라 미리 대비해두면 좋다.

---

## 4. `main.py`에서 이 함수 사용하기

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from device import load_devices

app = FastAPI()

robots, cameras = load_devices("configs/devices.json")

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float

@app.get("/robots")
def list_robots():
    return [r.get_status() for r in robots.values()]

# (이하 Day 11에서 만든 엔드포인트들은 그대로 유지)
```

`robots = {...}`로 직접 쓰던 부분이 `robots, cameras = load_devices(...)` 한 줄로 바뀌었다. 나머지 엔드포인트 코드는 **단 한 줄도 안 바뀐다** — Day 9에서 얘기했던 "데이터와 로직의 분리"가 여기서 완성되는 셈이다.

---

## 5. `device/__init__.py`에 `load_devices` 노출

```python
# device/__init__.py
from .robot import Robot
from .camera import Camera
from .config import load_devices
```

---

## 6. 장비 추가해보기 (코드 안 건드리고)

`configs/devices.json`에 로봇 하나를 더 추가해보자.

```json
{
  "robots": [
    {"name": "UR5", "max_speed": 2.0},
    {"name": "RB5", "max_speed": 1.5},
    {"name": "UR3", "max_speed": 1.0}
  ],
  "cameras": [
    {"name": "Camera-A"}
  ]
}
```

`main.py`는 손도 안 대고, 서버만 재시작(`--reload`면 자동)해서 `GET /robots` 호출해보면 UR3까지 3대가 나온다. 이게 오늘 목표의 핵심 증거다.

---

## 7. 오늘의 확인 과제

1. `configs/devices.json`을 만들고, `device/config.py`에 `load_devices` 함수를 작성한 뒤, `main.py`에서 하드코딩된 딕셔너리 대신 이 함수를 쓰도록 바꿔서 기존 엔드포인트들이 그대로 잘 동작하는지 확인하기.
2. JSON 파일에 로봇을 하나 더 추가하고, 코드 수정 없이 `GET /robots`에서 새 로봇이 나오는지 확인하기.
3. (심화) 일부러 `devices.json`의 쉼표를 하나 지워서 문법을 깨뜨려보고, `json.JSONDecodeError`가 잡혀서 서버가 죽지 않고 "빈 상태로 시작"되는지 확인해보기. (확인 후 쉼표는 다시 원상복구하기)

---

## 8. 다음 (Day 13) 예고

다음은 지금까지 프로젝트 전반에 흩어져 있는 에러 처리 방식을 점검하고 통일한다. 특히 `send_serial_command`(Day 7)처럼 실제 장비와 통신하는 부분을 시뮬레이터에도 일관되게 반영해서, "지금은 시뮬레이션이지만 실제 장비로 바꿔도 에러 처리 구조는 그대로 유지된다"는 걸 확인하는 날이 된다.
