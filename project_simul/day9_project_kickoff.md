# Day 9. 3주차 실전 프로젝트 — 장비 제어 시뮬레이터

1주차(기초 문법)와 2주차(requests, pyserial, FastAPI)에서 만든 조각들을 이번 주에 **하나의 프로젝트**로 합친다.
목표는 "실제 UR/RB 로봇, 카메라가 없어도 동작을 확인할 수 있는 시뮬레이터 + 이를 제어하는 FastAPI 서버"를 완성하는 것이다.

---

## 1. 프로젝트 개요

**만들 것**: 여러 대의 가상 로봇/카메라를 등록하고, FastAPI를 통해 이동/촬영 명령을 내리고, 상태를 조회할 수 있는 시스템.

**왜 "시뮬레이터"인가**: 실제 장비(UR5, RB5, 카메라 SDK)가 지금 손에 없어도, `asyncio.sleep`으로 "장비가 명령을 처리하는 시간"을 흉내내면 동일한 구조로 개발/테스트할 수 있다. 나중에 실제 장비가 연결되면, 시뮬레이터 부분만 Day 7의 `send_serial_command`나 실제 SDK 호출로 바꿔치면 된다 — **인터페이스는 그대로, 내부 구현만 교체**하는 게 이번 프로젝트의 핵심 설계 의도다.

---

## 2. 전체 아키텍처

```
[클라이언트 (requests 또는 /docs)]
        |  HTTP (GET/POST)
        v
[FastAPI 서버 (main.py)]
        |
        v
[devices 패키지]
   ├── robot.py   (Robot 클래스 - 상태, 이동 로직)
   ├── camera.py  (Camera 클래스 - 상태, 촬영 로직)
   └── config.py  (JSON 설정 로드/저장)
        |
        v
[시뮬레이션 레이어 (asyncio.sleep로 응답 지연 흉내)]
```

지금까지 만든 것과 매칭해보면:
- `Robot`/`Camera` 클래스 → Day 4~5
- JSON 설정 파일 → Day 5
- 동시 제어 → Day 2 (asyncio)
- 실제 장비 연동 지점 → Day 7 (pyserial), 나중에 교체 가능하도록 분리
- 전체를 묶는 서버 → Day 8 (FastAPI)

---

## 3. 3주차 로드맵 (Day 9~15 제안)

| Day | 내용 |
|---|---|
| **9 (오늘)** | 프로젝트 구조 설계, `devices` 패키지 스캐폴딩, `Robot`/`Camera` 클래스에 상태 관리 추가 |
| 10 | 비동기 시뮬레이션 레이어 — 로봇/카메라가 "명령 처리 중" 상태를 가지도록 asyncio로 구현 |
| 11 | FastAPI 엔드포인트 확장 — 여러 장비 목록 조회, 개별 상태 조회, 이동/촬영 명령 |
| 12 | JSON 설정 파일로 장비 목록을 관리 (코드 수정 없이 장비 추가/제거) |
| 13 | 에러 처리 통합 정리 — 지금까지 배운 예외처리를 프로젝트 전체에 일관되게 적용 |
| 14 | 통합 테스트 — `requests`로 시나리오 테스트 스크립트 작성 (예: 로봇 이동 → 카메라 촬영 순서) |
| 15 | 마무리 — 코드 정리, README 작성, 입사 전 최종 점검 |

(진행 속도에 따라 하루씩 당기거나 미뤄도 무방하다. 오늘은 1번, 즉 뼈대 잡는 날이다.)

---

## 4. 오늘(Day 9) 할 일

### 4-1. 프로젝트 폴더 구조

```
equipment_simulator/
├── main.py
├── devices/
│   ├── __init__.py
│   ├── robot.py
│   ├── camera.py
│   └── config.py
└── configs/
    └── devices.json
```

### 4-2. `Robot` 클래스에 "상태" 추가

지금까지의 `Robot`은 명령을 받으면 바로 결과를 반환했는데, 실제 장비는 "이동 중", "대기 중" 같은 상태가 존재한다. 오늘은 이 상태를 클래스 안에 갖도록 확장한다.

```python
# devices/robot.py

class Robot:
    def __init__(self, name: str, max_speed: float):
        self.name: str = name
        self.max_speed: float = max_speed
        self.status: str = "idle"       # idle, moving, error
        self.current_position: str = "HOME"

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "position": self.current_position,
        }
```

### 4-3. `Camera` 클래스도 같은 방식으로

```python
# devices/camera.py

class Camera:
    def __init__(self, name: str, resolution: str = "1920x1080"):
        self.name: str = name
        self.resolution: str = resolution
        self.status: str = "idle"       # idle, capturing, error
        self.last_image: str | None = None

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "last_image": self.last_image,
        }
```

### 4-4. `devices/__init__.py`

```python
# devices/__init__.py
from .robot import Robot
from .camera import Camera
```

### 4-5. `main.py` — 일단 여러 대를 등록만 해두기 (이동/촬영 로직은 Day 10에서)

```python
# main.py
from fastapi import FastAPI
from devices import Robot, Camera

app = FastAPI()

robots = {
    "UR5": Robot(name="UR5", max_speed=2.0),
    "RB5": Robot(name="RB5", max_speed=1.5),
}

cameras = {
    "Camera-A": Camera(name="Camera-A"),
    "Camera-B": Camera(name="Camera-B"),
}

@app.get("/robots")
def list_robots():
    return [r.get_status() for r in robots.values()]

@app.get("/cameras")
def list_cameras():
    return [c.get_status() for c in cameras.values()]
```

`uvicorn main:app --reload`로 실행하고 `/docs`에서 `GET /robots`, `GET /cameras`를 호출해서, 등록해둔 장비들의 초기 상태(`status: "idle"`)가 리스트로 잘 나오는지 확인한다.

---

## 5. 오늘의 확인 과제

1. 위 구조대로 폴더/파일을 만들고, `GET /robots`, `GET /cameras`가 각각 리스트를 정상적으로 반환하는지 `/docs`에서 확인.
2. `Robot`과 `Camera`에 필드를 하나씩 더 추가해보기 (예: `Robot`에 `last_error: str | None`, `Camera`에 `exposure: int`) — 지금까지 배운 타입 힌트를 그대로 활용.
3. (여유 있으면) 로봇/카메라를 3~4대로 늘려서, 딕셔너리에 계속 추가해도 `list_robots`/`list_cameras` 코드는 안 바뀌는 걸 확인해보기 — "장비 개수가 늘어나도 코드 구조는 그대로"라는 감각이 이번 주 프로젝트의 핵심이다.

오늘은 로직(이동, 촬영)은 아직 안 만든다 — 뼈대와 상태 조회까지만. Day 10에서 asyncio로 실제 "명령 처리 중" 흐름을 붙인다.
