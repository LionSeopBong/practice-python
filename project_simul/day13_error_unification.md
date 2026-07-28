# Day 13. 에러 처리 통일 & 실제 장비 연동 대비

이번 주 지금까지 각 Day마다 따로따로 에러 처리를 해왔다. 오늘은 이걸 프로젝트 전체 관점에서 정리하고, **"지금은 시뮬레이션이지만 실제 UR/RB 로봇이 연결돼도 구조가 그대로 유지되는지"**를 점검한다.

---

## 1. 지금까지 흩어져 있던 에러 처리 되짚어보기

| Day | 처리한 에러 | 방식 |
|---|---|---|
| 1 | 일반 예외 | `try/except/finally` |
| 6 | requests 타임아웃/연결실패 | `requests.exceptions.*` |
| 7 | 시리얼 포트 없음 | `serial.SerialException` |
| 8 | 잘못된 요청 데이터 | Pydantic 자동 검증(422) |
| 11 | 존재하지 않는 자원 / 잘못된 요청 | `HTTPException` (404/400) |
| 12 | 설정 파일 문제 | `FileNotFoundError`, `json.JSONDecodeError` |

오늘은 이 6가지를 **하나의 일관된 계층 구조**로 정리한다.

---

## 2. 핵심 아이디어: "시뮬레이션 계층"과 "실제 장비 계층"을 분리

지금 `Robot.move()`는 `asyncio.sleep()`으로 시간을 흉내내고 있다. 나중에 실제 로봇이 연결되면 이 부분만 Day 7의 `send_serial_command`로 바뀌어야 한다. 그런데 **호출하는 쪽(FastAPI 엔드포인트)은 바뀌면 안 된다** — 이게 오늘 지켜야 할 원칙이다.

```python
# device/robot.py

class Robot:
    def __init__(self, name: str, max_speed: float, port: str | None = None):
        self.name: str = name
        self.max_speed: float = max_speed
        self.port: str | None = port   # 실제 장비 연결 시 쓸 시리얼 포트 (지금은 None 가능)
        self.status: str = "idle"
        self.current_position: str = "HOME"
        self.last_error: str | None = None

    async def move(self, position: str, speed: float) -> bool:
        if speed > self.max_speed:
            self.last_error = "최대 속도 초과"
            return False

        self.status = "moving"
        self.last_error = None

        try:
            if self.port is None:
                # 시뮬레이션 모드: 실제 장비 없이 시간만 흉내
                await asyncio.sleep(2.0 / speed)
            else:
                # 실제 장비 모드: Day 7의 시리얼 통신 사용 (여기서는 개념만 표시)
                # result = send_serial_command(self.port, f"MOVE {position} {speed}")
                # if result is None:
                #     raise RuntimeError("장비 응답 없음")
                pass

            self.current_position = position
            self.status = "idle"
            return True

        except Exception as e:
            self.status = "error"
            self.last_error = str(e)
            return False
```

**포인트**: `port`가 `None`이면 시뮬레이션, 값이 있으면 실제 장비 — 이런 식으로 **분기점 하나만 만들어두면**, FastAPI 쪽 코드(`await robot.move(...)`)는 시뮬레이션이든 실제 장비든 똑같이 호출하면 된다.

---

## 3. `try/except Exception`을 광범위하게 잡는 것에 대해

방금 코드에서 `except Exception as e:`처럼 넓게 잡은 걸 눈치채셨을 수 있다. Day 1~7에서는 `FileNotFoundError`, `SerialException`처럼 **구체적인 예외**만 잡으라고 강조했는데, 왜 여기서는 다른가?

- **원칙은 그대로다**: 진짜 프로덕션 코드라면 `serial.SerialException`, `TimeoutError` 등 구체적으로 나눠서 각각 다르게 대응하는 게 맞다.
- 다만 **여기(`Robot.move` 최상위)는 "무슨 에러가 나든 로봇 상태를 `error`로 바꾸고 API에는 실패로 응답한다"는 최후의 안전망** 역할이다. 웹 서버에서 예상 못 한 에러 때문에 서버 전체가 죽는 것보다, 그 요청만 실패 처리하고 서버는 계속 살아있는 게 훨씬 중요하다.
- 그래서 **"구체적인 예외는 최대한 세분화해서 처리하되, 맨 바깥쪽에 하나의 안전망을 둔다"**는 게 실무에서 쓰는 절충안이다.

---

## 4. FastAPI 쪽에서 500 에러 방지하기

지금 `main.py`의 `move_robot`은 `robot.move()`가 `False`를 반환하면 `HTTPException(400, ...)`을 던진다. 그런데 만약 `robot.move()` **내부에서 예외가 새어나오면** 어떻게 될까?

```python
@app.post("/robots/move")
async def move_robot(request: MoveRequest):
    robot = robots.get(request.robot_name)
    if robot is None:
        raise HTTPException(status_code=404, detail=f"로봇 '{request.robot_name}'을 찾을 수 없음")

    success = await robot.move(request.position, request.speed)
    if not success:
        raise HTTPException(status_code=400, detail=robot.last_error)

    return {"success": True, "status": robot.get_status()}
```

`robot.move()` 안에서 이미 `try/except`로 예외를 잡아서 `False`를 반환하도록 만들어뒀기 때문에(2번 코드), 여기까지 예외가 새어나올 일이 없다. 이게 바로 **"계층마다 자기 책임의 에러는 자기가 처리하고, 위로는 깔끔한 결과(성공/실패)만 전달한다"**는 설계 원칙이다. Day 7의 `send_serial_command`도 원래 이렇게 만들어져 있었다는 걸 다시 떠올려보면 좋다.

---

## 5. 오늘의 확인 과제

1. `Robot.move()`를 위 코드처럼 `try/except Exception`으로 감싸서, 시뮬레이션 모드(`port=None`)에서는 기존과 동일하게 잘 동작하는지 확인하기.
2. 일부러 `Robot.move()` 안에 (테스트용으로) `raise RuntimeError("테스트 에러")`를 시뮬레이션 코드 자리에 넣어보고, 서버가 500으로 죽지 않고 `{"success": False, ...}` 형태의 400 응답으로 안전하게 처리되는지 확인한 뒤, 테스트 코드는 다시 제거하기.
3. (심화) `Camera.capture()`에도 같은 패턴(`try/except Exception`, 상태를 `error`로)을 적용해보기.

---

## 6. 다음 (Day 14) 예고

다음은 지금까지 만든 엔드포인트 전체를 하나의 시나리오로 이어서 테스트하는 **통합 테스트 스크립트**를 작성한다 (예: 로봇 이동 → 도착 확인 → 카메라 촬영 → 결과 확인, 이 흐름을 `requests`로 자동화). 3주차 목표의 실질적인 완성 단계다.
