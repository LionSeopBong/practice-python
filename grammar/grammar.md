# Day 2. 비동기 처리 (asyncio) 기초

Day 1에서 변수/리스트/딕셔너리/반복문/함수/클래스/예외처리까지 끝냈으니,
오늘은 스튜디오랩 백엔드(FastAPI)와 장비 제어에서 계속 마주치게 될 **asyncio**를 다룬다.

---

## 1. 왜 지금 배우는가

- FastAPI는 기본적으로 비동기(async) 프레임워크다. `async def` 엔드포인트를 안 쓰더라도 내부 동작을 이해해야 나중에 삽질을 줄인다.
- 장비 제어 관점에서도 중요하다: 카메라 SDK 응답 대기, UR/RB 로봇 소켓 통신 응답 대기처럼 **"기다리는 시간"**이 많은 작업을 여러 개 동시에 처리해야 하는 상황이 흔하다.
- 한섭님은 C++에서 멀티스레딩(카메라 워커 스레드, BlockingCollection 큐 등)을 다뤄봤으니, 그 경험과 비교하면서 이해하는 게 훨씬 빠를 것이다.

---

## 2. 동기 vs 비동기, 그리고 멀티스레딩과의 차이

| 구분            | 동작 방식                                                                | C++ 경험과 비교                      |
| --------------- | ------------------------------------------------------------------------ | ------------------------------------ |
| 동기(sync)      | 한 작업이 끝날 때까지 다음 작업은 대기                                   | 싱글 스레드에서 순차 실행            |
| 멀티스레딩      | OS가 여러 스레드를 강제로 번갈아 실행 (preemptive)                       | STA 스레드, mutex/lock 필요          |
| 비동기(asyncio) | 하나의 스레드 안에서, "기다리는 동안"만 다른 작업에게 양보 (cooperative) | 스레드는 1개뿐, GIL 문제 자체가 없음 |

핵심: **asyncio는 스레드를 늘리는 게 아니라, I/O 대기(네트워크, 파일, 타이머) 동안 한 스레드가 다른 코루틴에게 실행을 양보하는 것**이다. CPU 연산이 오래 걸리는 작업(영상 처리 같은)은 asyncio로 빨라지지 않는다 — 그건 여전히 멀티프로세싱/스레딩 영역이다.

---

## 3. 기본 문법 3종 세트

```python
import asyncio

# 1) async def -> "코루틴 함수"를 정의
async def say_hello():
    print("시작")
    await asyncio.sleep(1)  # 1초 "대기" (그 동안 다른 코루틴 실행 가능)
    print("1초 후 완료")

# 2) 코루틴은 호출만 해서는 실행되지 않는다
coro = say_hello()  # 아직 실행 안 됨, 코루틴 객체만 생성

# 3) 실제 실행은 asyncio.run()으로
asyncio.run(say_hello())
```

- `async def`: 이 함수는 코루틴(coroutine)이다. 내부에서 `await`를 쓸 수 있다.
- `await`: "여기서 기다리는 동안 다른 작업에게 양보해도 된다"는 지점.
- `asyncio.run()`: 이벤트 루프를 만들어서 코루틴을 실제로 실행. 보통 프로그램 진입점에서 한 번만 호출.

---

## 4. 이벤트 루프(Event Loop) 감 잡기

이벤트 루프는 "할 일 목록을 계속 확인하면서, 대기 중이던 작업이 준비되면 깨워주는" 관리자다.

```python
import asyncio
import time

async def camera_capture(name, delay):
    print(f"[{name}] 촬영 요청 전송")
    await asyncio.sleep(delay)  # 카메라 SDK 응답 대기를 흉내
    print(f"[{name}] 촬영 완료 ({delay}초 소요)")
    return f"{name}_image.jpg"

async def main():
    start = time.time()
    # 동기식이었다면 2 + 1 = 3초가 걸린다
    result1 = await camera_capture("Camera-A", 2)
    result2 = await camera_capture("Camera-B", 1)
    print(f"총 소요 시간: {time.time() - start:.1f}초")

asyncio.run(main())
```

위 코드는 `await`를 순서대로 호출했기 때문에 여전히 **직렬 실행**이다 (2초+1초=3초). 진짜 힘은 다음 섹션에서 나온다.

---

## 5. 여러 작업 동시 실행: `asyncio.gather`

```python
import asyncio
import time

async def camera_capture(name, delay):
    print(f"[{name}] 촬영 요청 전송")
    await asyncio.sleep(delay)
    print(f"[{name}] 촬영 완료 ({delay}초 소요)")
    return f"{name}_image.jpg"

async def main():
    start = time.time()
    results = await asyncio.gather(
        camera_capture("Camera-A", 2),
        camera_capture("Camera-B", 1),
        camera_capture("Camera-C", 3),
    )
    print(results)
    print(f"총 소요 시간: {time.time() - start:.1f}초")  # 약 3초 (가장 오래 걸린 것 기준)

asyncio.run(main())
```

`gather`는 여러 코루틴을 "동시에" 던져놓고 전부 끝날 때까지 기다린다. 카메라 3대에 각각 촬영 명령을 보내고 응답을 기다리는 상황을 그대로 흉내낸 것 — 실무에서 다중 장비를 제어할 때 거의 이 패턴을 쓰게 된다.

---

## 6. `create_task`로 백그라운드 실행하기

`gather`는 "다 끝날 때까지 기다리는" 용도라면, `create_task`는 작업을 던져놓고 다른 일을 먼저 하다가 나중에 결과를 받고 싶을 때 쓴다.

```python
import asyncio

async def robot_move(position):
    print(f"로봇 이동 시작 -> {position}")
    await asyncio.sleep(2)
    print(f"로봇 이동 완료 -> {position}")
    return "OK"

async def main():
    task = asyncio.create_task(robot_move("P1"))  # 백그라운드로 던짐
    print("로봇이 움직이는 동안 다른 준비 작업 수행 중...")
    await asyncio.sleep(0.5)
    print("준비 작업 끝, 이제 로봇 이동 결과를 기다림")
    result = await task  # 여기서 결과를 기다림
    print("결과:", result)

asyncio.run(main())
```

---

## 7. 비동기 버전 Lock (C++ mutex와 비교)

여러 코루틴이 같은 자원(예: 로봇 한 대)에 동시에 명령을 보내면 안 될 때 사용.

```python
import asyncio

robot_lock = asyncio.Lock()

async def send_command(cmd_name):
    async with robot_lock:  # C++의 std::lock_guard<std::mutex>와 비슷한 역할
        print(f"{cmd_name} 명령 실행 중...")
        await asyncio.sleep(1)
        print(f"{cmd_name} 명령 완료")

async def main():
    await asyncio.gather(
        send_command("이동"),
        send_command("그리퍼 열기"),
    )

asyncio.run(main())
```

차이점: C++ mutex는 여러 OS 스레드 간 경쟁을 막는 것이고, `asyncio.Lock`은 같은 스레드 안에서 코루틴들이 순서를 지키게 하는 것 — 스레드 경쟁이 아니라 "순서 보장"이 목적이라는 점이 다르다.

---

## 8. 오늘의 연습문제

1. `camera_capture` 함수를 참고해서, 서로 다른 지연시간을 가진 로봇 3대(`robot_A`, `robot_B`, `robot_C`)를 `asyncio.gather`로 동시에 이동시키고 전체 소요 시간을 출력해보기.
2. `asyncio.create_task`를 이용해서 "로봇이 이동하는 동안 카메라 워밍업을 동시에 진행"하는 코드 작성해보기 (두 작업이 서로 다른 코루틴).
3. (심화) `try/except`를 asyncio 코드에 추가해서, 특정 장비 응답이 2초 안에 안 오면 `asyncio.TimeoutError`를 발생시키는 코드를 `asyncio.wait_for()`로 만들어보기. (힌트: `await asyncio.wait_for(some_coroutine(), timeout=2)`)

---

## 9. 다음 (Day 3) 예고

Day 3부터는 1주차 나머지 기초 문법(모듈/패키지, 파일 입출력, 가상환경 venv)을 마무리하고,
2주차부터는 `requests`, `pyserial`, `FastAPI`로 넘어간다.
