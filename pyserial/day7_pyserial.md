# Day 7. pyserial (시리얼 통신)

Day 6에서 `requests`로 네트워크(HTTP) 통신을 배웠으니, 오늘은 **물리적인 케이블(USB/COM 포트)**로 통신하는 법을 배운다.

---

## 1. requests와 뭐가 다른가

| | requests | pyserial |
|---|---|---|
| 통신 방식 | 네트워크(HTTP, IP주소:포트) | 물리적 케이블(USB, COM 포트) |
| 주로 쓰는 대상 | 웹 서버, REST API | 센서, 일부 카메라/컨트롤러, 아두이노류 장비 |
| 데이터 형식 | 보통 JSON (구조화된 텍스트) | 보통 raw bytes (그냥 날것의 바이트) |

핵심 차이: `requests`는 "어느 IP의 어느 서버"에 말을 거는 거고, `pyserial`은 "내 컴퓨터에 꽂혀있는 COM 포트"에 대고 직접 말을 거는 거다. 산업 현장에서 구형 장비나 저수준 컨트롤러들이 아직도 시리얼 통신을 쓰는 경우가 많아서, 카메라 SDK가 REST API를 안 쓰는 장비라면 이쪽을 다뤄야 할 수도 있다.

---

## 2. 설치

```bash
pip install pyserial
```

주의: 모듈 이름은 `serial`이지만 설치 패키지 이름은 `pyserial`이다 (`pip install serial`이라고 치면 다른 엉뚱한 패키지가 깔리니 주의).

---

## 3. 사용 가능한 포트 확인하기

```python
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device, "-", port.description)
```

Windows에서는 보통 `COM3`, `COM4`처럼 표시된다. 지금 당장 연결된 장비가 없으면 아무것도 안 뜰 수 있는데, 정상이다 (장비회사 SDK를 실제로 다룰 때 이 코드로 먼저 포트 목록부터 확인하는 습관을 들이면 좋다).

---

## 4. 포트 열고 데이터 주고받기

```python
import serial

ser = serial.Serial(port="COM3", baudrate=9600, timeout=2)

# 데이터 보내기 (bytes로 변환해서 보내야 함)
ser.write(b"MOVE P1\n")

# 데이터 받기
response = ser.readline()
print(response)

ser.close()
```

- `baudrate`: 통신 속도(초당 비트 수). 장비 매뉴얼에 적혀있는 값을 그대로 맞춰야 한다 (안 맞으면 깨진 문자만 받게 된다).
- `timeout=2`: requests의 timeout과 같은 개념 — 2초 안에 응답 없으면 넘어간다.
- `b"MOVE P1\n"`: 앞에 `b`가 붙은 건 **bytes 타입**이라는 뜻. 시리얼 통신은 문자열(`str`)이 아니라 **바이트 단위**로 주고받는다는 게 requests와의 큰 차이다.

---

## 5. 문자열 ↔ bytes 변환 (`encode` / `decode`)

```python
command = "MOVE P1"

# 문자열 -> bytes (보낼 때)
command_bytes = command.encode("utf-8")
ser.write(command_bytes)

# bytes -> 문자열 (받을 때)
response_bytes = ser.readline()
response_text = response_bytes.decode("utf-8").strip()
print(response_text)
```

- `.encode("utf-8")`: 사람이 읽는 문자열을 컴퓨터가 실제로 전송하는 bytes로 변환.
- `.decode("utf-8")`: 받은 bytes를 다시 사람이 읽는 문자열로 변환.
- `.strip()`: 끝에 붙는 개행문자(`\n`, `\r`) 제거 — 시리얼 응답에는 항상 이런 잡음이 섞여 오는 경우가 많다.

`b"MOVE P1"` 대신 `"MOVE P1".encode()`을 써도 결과는 같다. 상황에 따라 편한 쪽을 쓰면 된다.

---

## 6. `with`문으로 안전하게 열고 닫기

Day 5에서 파일을 `with open(...)`으로 열었던 것처럼, 시리얼 포트도 `with`로 관리할 수 있다.

```python
import serial

with serial.Serial(port="COM3", baudrate=9600, timeout=2) as ser:
    ser.write(b"MOVE P1\n")
    response = ser.readline()
    print(response.decode("utf-8").strip())
# 블록을 벗어나면 자동으로 포트가 닫힌다
```

포트를 안 닫고 프로그램이 끝나버리면, 다음에 그 포트를 다른 프로그램이 못 쓰는 경우가 생길 수 있어서 `with`로 관리하는 습관이 중요하다.

---

## 7. 에러 처리 (포트가 없거나 이미 사용 중일 때)

```python
import serial

try:
    ser = serial.Serial(port="COM3", baudrate=9600, timeout=2)
    ser.write(b"MOVE P1\n")
    response = ser.readline()
    print(response.decode("utf-8").strip())
    ser.close()

except serial.SerialException as e:
    print(f"시리얼 포트 연결 실패: {e}")
```

`serial.SerialException`은 포트가 존재하지 않거나(장비 미연결), 이미 다른 프로그램이 그 포트를 점유 중일 때 발생한다. 실무에서 정말 자주 마주치는 상황이라 꼭 잡아줘야 한다.

---

## 8. Day 4~6과 이어서: `devices` 패키지에 시리얼 통신 추가

```python
# devices/robot.py
import serial

def send_serial_command(port: str, command: str, baudrate: int = 9600) -> str | None:
    try:
        with serial.Serial(port=port, baudrate=baudrate, timeout=2) as ser:
            ser.write(command.encode("utf-8") + b"\n")
            response = ser.readline().decode("utf-8").strip()
            return response
    except serial.SerialException as e:
        print(f"시리얼 통신 실패: {e}")
        return None
```

Day 4의 타입 힌트(`str | None`), Day 5의 `with`문 패턴, Day 1의 예외처리가 전부 한 함수 안에 자연스럽게 녹아있는 걸 볼 수 있다.

---

## 9. 오늘의 연습문제

1. `serial.tools.list_ports.comports()`로 현재 컴퓨터에 연결된 포트 목록을 출력해보기. (실제 장비 없으면 목록이 비어도 괜찮음 — 코드가 에러 없이 돌아가는지가 포인트)
2. 존재하지 않는 포트(예: `"COM99"`)로 `serial.Serial()`을 열어보려고 시도하고, `serial.SerialException`을 잡아서 "연결 실패" 메시지가 출력되도록 만들어보기.
3. (심화) `devices/robot.py`에 `send_serial_command` 함수를 추가하고, `main.py`에서 (실제 장비 없어도 되니) 존재하지 않는 포트로 호출해봐서 `None`이 반환되는지, 에러 메시지가 잘 뜨는지 확인해보기.

실제 시리얼 장비가 없어서 정상 동작까지는 확인 못 하더라도 괜찮다 — 오늘 목표는 "에러 상황을 안전하게 처리하는 코드 구조"에 익숙해지는 것이다.

---

## 10. 다음 (Day 8) 예고

다음은 2주차 마지막 주제인 **FastAPI**로 넘어간다. 지금까지 만든 `requests`(클라이언트), `pyserial`(장비 통신), `Robot`/`json` 설정 관리를 전부 하나의 웹 서버 안으로 모으는 작업이라고 생각하면 된다.
