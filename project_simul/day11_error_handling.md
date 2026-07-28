# Day 11. API 다듬기 — 개별 조회 & 일관된 에러 형식

지금까지는 "동작이 되는가"에 집중했다면, 오늘은 **다른 사람(프론트엔드 개발자, 미래의 나)이 쓰기 편한 API**로 다듬는 날이다. 실무에서 API를 만들 때 실제로 신경 쓰는 부분이 바로 이런 디테일이다.

---

## 1. 왜 필요한가

지금 `/robots`는 전체 목록만 준다. 그런데 React 쪽에서 로봇 하나의 상태만 자주 조회해야 한다면(예: 대시보드에서 카드 하나씩 갱신), 매번 전체 목록을 받아서 프론트에서 걸러내는 건 비효율적이다. **개별 조회 엔드포인트**가 필요한 이유다.

또, 지금까지 에러 응답이 제각각이었다:
```python
{"error": "존재하지 않는 로봇"}          # Day 9 스타일
{"success": False, "message": "존재하지 않는 로봇"}  # Day 10 스타일
```
이렇게 응답 형태가 엔드포인트마다 다르면, 프론트엔드에서 에러 처리 코드를 매번 다르게 짜야 한다 — 오늘 하나로 통일한다.

---

## 2. 개별 장비 상태 조회 엔드포인트

```python
# main.py
from fastapi import FastAPI, HTTPException

@app.get("/robots/{robot_name}/status")
def get_robot_status(robot_name: str):
    robot = robots.get(robot_name)
    if robot is None:
        raise HTTPException(status_code=404, detail=f"로봇 '{robot_name}'을 찾을 수 없음")
    return robot.get_status()

@app.get("/cameras/{camera_name}/status")
def get_camera_status(camera_name: str):
    camera = cameras.get(camera_name)
    if camera is None:
        raise HTTPException(status_code=404, detail=f"카메라 '{camera_name}'을 찾을 수 없음")
    return camera.get_status()
```

**`HTTPException`을 처음 쓴다** — 이게 오늘 배우는 핵심 도구다.

---

## 3. `HTTPException`이란

지금까지는 에러가 나도 그냥 `{"error": "..."}`를 **200 OK**로 반환했다. 그런데 HTTP 관점에서 "로봇을 못 찾음"은 사실 **404 Not Found**로 응답하는 게 맞다. Day 6에서 배운 `response.status_code`, `raise_for_status()`가 여기서 서버 쪽 관점으로 다시 등장한다.

```python
from fastapi import HTTPException

raise HTTPException(status_code=404, detail="로봇을 찾을 수 없음")
```

이렇게 하면 FastAPI가 자동으로:
- HTTP 상태 코드를 `404`로 설정
- 응답 본문을 `{"detail": "로봇을 찾을 수 없음"}` 형태로 통일해서 반환

**왜 중요한가**: 프론트엔드(React)에서 `requests`/`fetch`로 호출할 때, 상태 코드만 보고 성공/실패를 즉시 구분할 수 있다.

```js
const res = await fetch("http://127.0.0.1:8000/robots/UNKNOWN/status");
if (!res.ok) {  // res.ok는 상태코드가 200번대가 아니면 false
  const err = await res.json();
  console.error(err.detail);  // "로봇 'UNKNOWN'을 찾을 수 없음"
}
```

`response.ok`나 `raise_for_status()`처럼 **상태 코드로 성공/실패를 판단하는 게 REST API의 기본 관례**다. 지금까지처럼 항상 200을 주고 본문 안의 `success` 필드로만 구분하는 방식보다, 이렇게 상태 코드를 제대로 쓰는 게 더 표준적이다.

---

## 4. 기존 엔드포인트도 `HTTPException`으로 통일

```python
# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from device import Robot, Camera

app = FastAPI()

robots = {
    "UR5": Robot(name="UR5", max_speed=2.0),
    "RB5": Robot(name="RB5", max_speed=1.5),
}
cameras = {
    "Camera-A": Camera(name="Camera-A"),
}

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float

@app.get("/robots")
def list_robots():
    return [r.get_status() for r in robots.values()]

@app.get("/robots/{robot_name}/status")
def get_robot_status(robot_name: str):
    robot = robots.get(robot_name)
    if robot is None:
        raise HTTPException(status_code=404, detail=f"로봇 '{robot_name}'을 찾을 수 없음")
    return robot.get_status()

@app.post("/robots/move")
async def move_robot(request: MoveRequest):
    robot = robots.get(request.robot_name)
    if robot is None:
        raise HTTPException(status_code=404, detail=f"로봇 '{request.robot_name}'을 찾을 수 없음")

    success = await robot.move(request.position, request.speed)
    if not success:
        # 로봇은 존재하지만 "요청 자체가 잘못됨" -> 404가 아니라 400이 더 적절
        raise HTTPException(status_code=400, detail=robot.last_error)

    return {"success": True, "status": robot.get_status()}
```

**404 vs 400 구분**
- `404 Not Found`: 애초에 그 이름의 로봇이 없음 (자원 자체가 없음)
- `400 Bad Request`: 로봇은 있지만 요청 내용이 잘못됨 (예: 속도 초과)

이 구분은 Day 6에서 봤던 HTTP 상태코드 체계(200/404/500 등)를 실제로 서버 쪽에서 설계해보는 것이다.

---

## 5. 카메라 쪽도 동일하게

```python
@app.post("/cameras/{camera_name}/capture")
async def capture_camera(camera_name: str):
    camera = cameras.get(camera_name)
    if camera is None:
        raise HTTPException(status_code=404, detail=f"카메라 '{camera_name}'을 찾을 수 없음")

    image = await camera.capture()
    return {"success": True, "image": image}
```

---

## 6. `/docs`에서 확인하기

`HTTPException`을 쓰면 `/docs`에서도 응답 예시가 더 정확하게 표시된다. `GET /robots/{robot_name}/status`에서 존재하지 않는 이름(`XYZ`)을 넣고 실행해보면:

- 응답 상태 코드: `404`
- 응답 본문: `{"detail": "로봇 'XYZ'을 찾을 수 없음"}`

이렇게 나오는 걸 확인할 수 있다. 이전(Day 9~10)처럼 200과 함께 에러 메시지가 오는 것과 비교해보면 차이가 뚜렷하다.

---

## 7. 오늘의 확인 과제

1. `GET /robots/{robot_name}/status`, `GET /cameras/{camera_name}/status`를 만들고, 존재하는 이름/존재하지 않는 이름 각각 호출해서 상태 코드가 200/404로 다르게 나오는지 확인하기.
2. 기존 `POST /robots/move`를 `HTTPException` 기반으로 리팩토링하고, "존재하지 않는 로봇"은 404, "속도 초과"는 400으로 각각 다르게 응답되는지 확인하기.
3. (심화) `test.py`(또는 새 테스트 스크립트)에서 `requests`로 호출한 뒤, `response.status_code`와 `response.ok`를 직접 출력해서 404/400/200이 각각 어떻게 찍히는지 확인해보기. (`raise_for_status()`를 일부러 붙여서 예외가 발생하는 것도 확인하면 좋다.)

---

## 8. 다음 (Day 12) 예고

다음은 지금 `main.py` 안에 하드코딩된 `robots`, `cameras` 딕셔너리를 **JSON 설정 파일**로 옮긴다. Day 5에서 만든 JSON 입출력을 이번 프로젝트에 실제로 적용해서, 코드를 안 건드리고 장비를 추가/제거할 수 있게 만드는 게 목표다.
