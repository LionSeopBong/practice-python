# Day 10. 비동기 시뮬레이션 레이어 (상태 흐름)

Day 9에서 `Robot`/`Camera`에 `status` 필드를 넣어놨으니, 오늘은 실제로 명령을 내리면 **`idle` → `moving`/`capturing` → `idle`**로 상태가 바뀌도록 만든다. Day 2에서 배운 asyncio가 여기서 실전으로 쓰인다.

---

## 1. 오늘 목표

지금까지 `get_status()`는 있었지만, 상태를 바꾸는 동작이 없었다. 실제 장비는:

1. 명령을 받으면 → `status = "moving"`으로 바뀜
2. 이동하는 동안(=시간이 걸리는 동안) → 다른 요청도 동시에 처리 가능해야 함
3. 이동이 끝나면 → `status = "idle"`로 복귀, `current_position` 갱신

이 흐름을 코루틴 메서드로 만든다.

---

## 2. `Robot`에 비동기 `move` 메서드 추가

```python
# devices/robot.py
import asyncio

class Robot:
    def __init__(self, name: str, max_speed: float):
        self.name: str = name
        self.max_speed: float = max_speed
        self.status: str = "idle"
        self.current_position: str = "HOME"
        self.last_error: str | None = None

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "position": self.current_position,
            "error": self.last_error,
        }

    async def move(self, position: str, speed: float) -> bool:
        if speed > self.max_speed:
            self.last_error = "최대 속도 초과"
            return False

        self.status = "moving"
        self.last_error = None
        print(f"[{self.name}] {self.current_position} -> {position} 이동 시작")

        # 실제 로봇의 이동 시간을 흉내 (거리/속도에 비례한다고 가정)
        move_time = 2.0 / speed
        await asyncio.sleep(move_time)

        self.current_position = position
        self.status = "idle"
        print(f"[{self.name}] {position} 도착")
        return True
```

**포인트**
- `async def move(...)`로 바꿨기 때문에, 이 메서드가 실행되는 동안(`await asyncio.sleep(move_time)`) 다른 로봇의 `move()`나 다른 API 요청이 **동시에** 처리될 수 있다.
- `status`를 `"moving"`으로 바꿔둔 상태에서 `get_status()`를 호출하면, 지금 이 로봇이 이동 중이라는 걸 실시간으로 확인할 수 있다.

---

## 3. `Camera`도 같은 방식으로

```python
# devices/camera.py
import asyncio

class Camera:
    def __init__(self, name: str, resolution: str = "1920x1080"):
        self.name: str = name
        self.resolution: str = resolution
        self.status: str = "idle"
        self.last_image: str | None = None

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "last_image": self.last_image,
        }

    async def capture(self) -> str:
        self.status = "capturing"
        await asyncio.sleep(1.0)  # 촬영 + 처리 시간을 흉내
        self.last_image = f"{self.name}_{int(asyncio.get_event_loop().time())}.jpg"
        self.status = "idle"
        return self.last_image
```

---

## 4. FastAPI 엔드포인트에 연결

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from devices import Robot, Camera

app = FastAPI()

robots = {
    "UR5": Robot(name="UR5", max_speed=2.0),
    "RB5": Robot(name="RB5", max_speed=1.5),
}
cameras = {
    "Camera-A": Camera(name="Camera-A"),
}

@app.get("/robots")
def list_robots():
    return [r.get_status() for r in robots.values()]

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float

@app.post("/robots/move")
async def move_robot(request: MoveRequest):
    robot = robots.get(request.robot_name)
    if robot is None:
        return {"success": False, "message": "존재하지 않는 로봇"}

    success = await robot.move(request.position, request.speed)
    if not success:
        return {"success": False, "message": robot.last_error}
    return {"success": True, "status": robot.get_status()}

@app.post("/cameras/{camera_name}/capture")
async def capture_camera(camera_name: str):
    camera = cameras.get(camera_name)
    if camera is None:
        return {"success": False, "message": "존재하지 않는 카메라"}

    image = await camera.capture()
    return {"success": True, "image": image}
```

`@app.post(...)` 함수도 `async def`로 바꿔야 그 안에서 `await robot.move(...)`을 쓸 수 있다는 걸 기억하자 — Day 8에서는 `def`(동기)였는데, 오늘은 `async def`로 바뀐 이유가 바로 이거다.

---

## 5. 실시간으로 상태 변화 확인해보기

서버를 켠 상태에서, 터미널을 하나 더 열고 이렇게 테스트해보면 상태가 바뀌는 걸 눈으로 볼 수 있다.

```python
# test_status.py
import requests
import time

# 1) 이동 명령을 보내자마자 (완료를 기다리지 않고 확인하고 싶다면 별도 스레드/터미널 필요하지만,
#    여기서는 이동 전/후 상태를 비교하는 것으로 충분하다)
print("이동 전:", requests.get("http://127.0.0.1:8000/robots").json())

response = requests.post(
    "http://127.0.0.1:8000/robots/move",
    json={"robot_name": "UR5", "position": "P1", "speed": 1.0},
)
print("이동 결과:", response.json())

print("이동 후:", requests.get("http://127.0.0.1:8000/robots").json())
```

**더 재미있게 확인하는 법**: `/docs`에서 `POST /robots/move`를 실행하는 **동시에** 다른 브라우저 탭에서 `GET /robots`를 빠르게 여러 번 눌러보면, `speed`를 낮게 줬을 때(예: `speed: 0.5` → 이동 시간 4초) 그 사이에 `status: "moving"`으로 찍히는 걸 볼 수 있다.

---

## 6. 여러 로봇 동시에 이동시키기 (Day 2 gather 복습)

```python
# main.py에 추가
import asyncio

@app.post("/robots/move-all")
async def move_all_robots():
    results = await asyncio.gather(
        robots["UR5"].move("P1", 1.5),
        robots["RB5"].move("P2", 1.0),
    )
    return {"results": results, "statuses": [r.get_status() for r in robots.values()]}
```

이 엔드포인트를 호출하면 UR5와 RB5가 **동시에** 이동을 시작해서, 각자의 이동 시간이 끝나는 대로 순서 상관없이 완료된다. Day 2에서 배운 `gather`가 실제 API 엔드포인트 안에서 그대로 쓰이는 걸 확인하는 부분이다.

---

## 7. 오늘의 확인 과제

1. `Robot.move()`, `Camera.capture()`를 위 코드대로 만들고, `/docs`에서 `POST /robots/move`와 `POST /cameras/{camera_name}/capture`를 각각 호출해서 정상 동작 확인하기.
2. `speed`를 아주 작게(예: `0.3`) 줘서 이동 시간을 늘린 뒤, 이동이 끝나기 전에 다른 탭에서 `GET /robots`를 호출해 `status: "moving"`이 실제로 찍히는지 확인하기.
3. (심화) `move-all` 엔드포인트를 만들어서 두 로봇을 동시에 이동시키고, 전체 소요 시간이 (각 로봇 이동시간의 합이 아니라) 더 오래 걸리는 로봇 기준으로 끝나는지 체감해보기 — 서버 로그에 찍히는 `print` 순서를 보면 확인하기 쉽다.

---

## 8. 다음 (Day 11) 예고

다음은 지금 만든 엔드포인트들을 좀 더 다듬는다 — 개별 장비 상태 조회(`GET /robots/{name}/status`), 존재하지 않는 장비에 대한 일관된 에러 응답 형식 등, "API를 실제로 다른 사람(프론트엔드 개발자)이 쓸 수 있게 다듬는" 작업이다.
