# Day 8. FastAPI 기초 (2주차 마지막)

지금까지 만든 `Robot` 클래스, JSON 설정, `requests`, `pyserial` 코드를 오늘은 **하나의 웹 서버**로 모은다.
지금까지는 파이썬 코드가 "요청을 보내는 쪽"(requests)이었다면, 오늘은 반대로 **요청을 받아서 처리하는 쪽**을 만든다.

---

## 1. 왜 FastAPI인가

```
[React 프론트엔드] --- HTTP 요청 ---> [FastAPI 서버] --- pyserial/카메라 SDK ---> [실제 장비]
```

React에서 Next.js API Route를 만들어보셨다면, FastAPI가 파이썬으로 그 역할을 한다고 이해하면 된다 (Day 6에서 얘기했던 그 비유 그대로). Day 4의 타입 힌트가 여기서부터는 "설명용"이 아니라 **실제로 동작에 관여하는 문법**이 된다.

---

## 2. 설치

```bash
pip install fastapi uvicorn
```

- `fastapi`: 프레임워크 본체
- `uvicorn`: 서버를 실제로 구동시켜주는 프로그램 (ASGI 서버)

---

## 3. 제일 작은 FastAPI 서버

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "로봇 제어 서버 동작 중"}
```

실행:

```bash
uvicorn main:app --reload
```

- `main:app` → `main.py` 파일 안의 `app`이라는 변수(FastAPI 인스턴스)를 실행하라는 뜻.
- `--reload` → 코드 수정하면 서버가 자동으로 재시작됨 (개발 중에만 씀).

터미널에 `http://127.0.0.1:8000` 같은 주소가 뜨면, 브라우저로 그 주소를 열어보면 `{"message": "로봇 제어 서버 동작 중"}`이 그대로 보인다.

**바로 확인해볼 것 — Swagger UI**: `http://127.0.0.1:8000/docs`로 들어가면 API 문서가 자동으로 생성돼 있고, 브라우저에서 바로 테스트도 가능하다. Day 6에서 언급했던 "Thunder Client 없이도 어느 정도 커버된다"는 게 바로 이거다.

---

## 4. GET 엔드포인트 — 로봇 상태 조회

```python
from fastapi import FastAPI

app = FastAPI()

robots = {
    "UR5": {"max_speed": 2.0, "connected": True},
    "RB5": {"max_speed": 1.5, "connected": False},
}

@app.get("/robots/{robot_name}")
def get_robot(robot_name: str):
    return robots.get(robot_name, {"error": "존재하지 않는 로봇"})
```

`{robot_name}`처럼 중괄호로 감싼 부분을 **경로 파라미터(path parameter)**라고 한다. `/robots/UR5`로 요청이 오면 `robot_name`에 자동으로 `"UR5"`가 담겨서 함수에 전달된다.

React 쪽에서 확인하려면 (지금까지 하셨던 `fetch`/`axios` 그대로):

```js
fetch("http://127.0.0.1:8000/robots/UR5")
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 5. POST 엔드포인트 + Pydantic — 로봇 이동 명령

여기서 Day 4의 타입 힌트가 실제로 "검증"까지 해주는 걸 확인할 수 있다.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float

@app.post("/robots/move")
def move_robot(request: MoveRequest):
    if request.speed > 2.0:
        return {"success": False, "message": "최대 속도 초과"}
    return {
        "success": True,
        "message": f"{request.robot_name}를 {request.position}으로 이동 (속도 {request.speed})",
    }
```

- `class MoveRequest(BaseModel):` — Day 4에서 미리 봤던 그 문법이다. `robot_name: str`, `position: str`, `speed: float`이라고 선언해두면, FastAPI가 요청 본문(body)을 자동으로 이 형태로 검증하고 파싱해준다.
- 만약 클라이언트가 `speed`에 문자열("빠르게")을 보내면, 함수 코드를 실행하기도 전에 FastAPI가 **자동으로 422 에러**를 응답한다 — Day 4에서 얘기했던 "타입이 틀려도 파이썬은 안 막아준다"는 규칙이, Pydantic이 끼면 예외적으로 실제 검증까지 해주는 거다.

React 쪽에서 호출:

```js
fetch("http://127.0.0.1:8000/robots/move", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ robot_name: "UR5", position: "P1", speed: 1.5 }),
})
  .then(res => res.json())
  .then(data => console.log(data));
```

파이썬 `requests`로 테스트하려면 Day 6에서 배운 그대로 쓸 수 있다:

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/robots/move",
    json={"robot_name": "UR5", "position": "P1", "speed": 1.5},
)
print(response.json())
```

---

## 6. 실제 장비와 연결하기 (여기가 오늘 배운 것들의 종착지)

Day 7에서 만든 `send_serial_command`를 FastAPI 엔드포인트 안에서 그대로 호출하면 된다.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from devices.robot import send_serial_command

app = FastAPI()

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float
    port: str

@app.post("/robots/move")
def move_robot(request: MoveRequest):
    command = f"MOVE {request.position} {request.speed}"
    result = send_serial_command(port=request.port, command=command)

    if result is None:
        return {"success": False, "message": "장비 통신 실패"}
    return {"success": True, "response": result}
```

이게 지금까지 배운 걸 다 연결한 그림이다: **React가 FastAPI에 POST 요청 → FastAPI가 Pydantic으로 데이터 검증 → FastAPI가 pyserial로 실제 로봇에 명령 전송 → 결과를 다시 JSON으로 React에 응답.**

---

## 7. 비동기로 만들기 (Day 2 asyncio 등장)

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.get("/robots/status-all")
async def get_all_status():
    async def check_one(name: str, delay: float):
        await asyncio.sleep(delay)  # 실제로는 장비 응답 대기를 흉내
        return {"name": name, "connected": True}

    results = await asyncio.gather(
        check_one("UR5", 1),
        check_one("RB5", 1.5),
    )
    return {"robots": results}
```

`def` 대신 `async def`로 엔드포인트를 만들면, Day 2에서 배운 `asyncio.gather`를 그대로 쓸 수 있다. 로봇 여러 대의 상태를 동시에 조회하는 상황이 실제로 이렇게 만들어진다.

---

## 8. 오늘의 연습문제

1. `GET /robots/{robot_name}` 엔드포인트를 만들어서, 존재하는 로봇 이름과 존재하지 않는 이름 둘 다 호출해보고 `/docs`에서 결과 확인해보기.
2. `MoveRequest` Pydantic 모델을 이용한 `POST /robots/move` 엔드포인트를 만들고, `/docs`의 "Try it out" 버튼으로 정상 요청과 (speed에 문자열을 넣는) 잘못된 요청을 각각 보내서 차이를 확인해보기.
3. (심화) Day 7의 `send_serial_command`를 실제로 엔드포인트 안에서 호출하도록 연결하고, 존재하지 않는 포트로 요청을 보내서 `{"success": False, "message": "장비 통신 실패"}`가 응답되는지 확인해보기.

---

## 9. 2주차 마무리 & 3주차 예고

여기까지 하면 2주차(실무 라이브러리: requests, pyserial, FastAPI)가 끝난다. 3주차는 계획대로 **실전 프로젝트 — 장비 제어 시뮬레이터**로, 지금까지 만든 `devices/` 패키지 전체(Robot, Camera, JSON 설정, requests, pyserial, FastAPI 서버)를 하나의 완성된 프로젝트로 합치는 마지막 주가 된다.
