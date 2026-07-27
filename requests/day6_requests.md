# Day 6. requests 라이브러리 (2주차 시작)

1주차(기초 문법)를 다 끝냈으니, 오늘부터 2주차 — 실무 라이브러리로 넘어간다.
첫 주제는 `requests`: 파이썬에서 HTTP 통신을 하는 가장 기본적인 라이브러리다.

---

## 1. 왜 배우는가

스튜디오랩에서 만들 시스템 구조를 떠올려보면:

```
[React 프론트엔드] <--HTTP--> [FastAPI 백엔드] <---?---> [카메라 SDK / UR·RB 로봇]
```

지금까지는 "FastAPI가 요청을 어떻게 받는지" 쪽(서버)에 가까운 걸 배웠다면, `requests`는 그 반대 — **파이썬 코드가 클라이언트가 되어 다른 서버에 요청을 보내는 법**이다.

실무에서 자주 나오는 상황들:
- 카메라 SDK가 REST API 형태로 제공되는 경우, `requests`로 촬영 명령을 보낸다.
- 로봇 컨트롤러가 HTTP 인터페이스를 제공하면 `requests`로 이동 명령을 보낸다.
- 여러 마이크로서비스(FastAPI 서버들)끼리 서로 데이터를 주고받을 때도 `requests`를 쓴다.
- 테스트할 때 내가 만든 FastAPI 서버가 잘 동작하는지 `requests`로 직접 호출해서 확인한다.

---

## 2. 설치

```bash
pip install requests
```

---

## 3. 기본 GET 요청

```python
import requests

response = requests.get("https://httpbin.org/get")

print(response.status_code)  # 200 (성공)
print(response.text)         # 응답 본문 (문자열)
print(response.json())       # 응답 본문을 JSON -> 딕셔너리로 자동 변환
```

- `status_code`: HTTP 상태 코드. `200`은 성공, `404`는 못 찾음, `500`은 서버 에러 — 이 세 개는 실무에서 정말 자주 보게 된다.
- `response.json()`: 서버가 JSON으로 응답하면, Day 5에서 배운 `json.load`를 자동으로 해주는 셈이다.

---

## 4. 파라미터를 붙여서 GET 요청 (카메라 상태 조회 예제)

```python
import requests

# 예: 카메라 서버에 "Camera-A"의 상태를 물어보는 상황을 흉내
params = {"camera_name": "Camera-A"}
response = requests.get("https://httpbin.org/get", params=params)

print(response.url)   # https://httpbin.org/get?camera_name=Camera-A
print(response.json())
```

URL 뒤에 `?key=value`를 직접 문자열로 이어붙이지 않고, `params` 딕셔너리로 넘기면 `requests`가 알아서 올바른 형식으로 조립해준다.

---

## 5. POST 요청 (로봇에 이동 명령 보내기)

Day 4~5에서 만든 `Robot` 관련 데이터를 그대로 재활용해서, "로봇 이동 명령을 서버에 보낸다"는 상황을 흉내내보자.

```python
import requests

move_command = {
    "robot_name": "UR5",
    "position": "P1",
    "speed": 1.5,
}

response = requests.post("https://httpbin.org/post", json=move_command)

print(response.status_code)
print(response.json())
```

- `json=move_command`로 넘기면, `requests`가 딕셔너리를 자동으로 JSON 문자열로 변환하고, `Content-Type: application/json` 헤더도 알아서 붙여준다.
- GET은 "데이터 조회"에, POST는 "서버에 뭔가를 하도록 명령/생성"에 주로 쓴다는 감각만 지금은 잡아두면 된다. (2주차 후반 FastAPI에서 이 구분이 서버 쪽 관점에서 다시 나온다.)

---

## 6. 에러 처리 (네트워크는 항상 실패할 수 있다)

장비 통신은 특히 타임아웃, 연결 끊김이 흔하다. Day 1의 예외처리가 다시 등장한다.

```python
import requests

try:
    response = requests.post(
        "https://httpbin.org/post",
        json={"robot_name": "UR5", "position": "P1"},
        timeout=3,  # 3초 안에 응답 없으면 예외 발생
    )
    response.raise_for_status()  # 상태코드가 4xx/5xx면 예외를 발생시킴
    print(response.json())

except requests.exceptions.Timeout:
    print("로봇 서버 응답 시간 초과 (3초)")
except requests.exceptions.ConnectionError:
    print("로봇 서버에 연결할 수 없음")
except requests.exceptions.HTTPError as e:
    print(f"서버가 에러 응답을 반환함: {e}")
```

- `timeout`을 안 주면 응답이 영원히 안 올 경우 코드가 멈춰버릴 수 있다 — 실무에서는 **timeout 없는 requests 호출은 거의 금기**라고 봐도 된다.
- `raise_for_status()`: 상태 코드가 200번대가 아니면 예외를 강제로 발생시켜서, 아래에서 `except`로 잡을 수 있게 해준다.

---

## 7. Day 4~5 코드와 연결해보기

`devices/robot.py`에 "실제 로봇 서버로 이동 명령을 보내는" 함수를 하나 추가한다고 하면 이런 모양이 된다.

```python
# devices/robot.py
import requests

def send_move_command(robot_name: str, position: str, speed: float, server_url: str) -> bool:
    try:
        response = requests.post(
            f"{server_url}/move",
            json={"robot_name": robot_name, "position": position, "speed": speed},
            timeout=3,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"이동 명령 전송 실패: {e}")
        return False
```

`requests.exceptions.RequestException`은 앞서 나온 `Timeout`, `ConnectionError`, `HTTPError`를 전부 포함하는 상위 예외라서, 개별적으로 다 안 잡고 한 번에 처리하고 싶을 때 이렇게 묶어서 쓸 수 있다.

---

## 8. 오늘의 연습문제

1. `https://httpbin.org/get`에 GET 요청을 보내서 `status_code`와 `response.json()`을 출력해보기.
2. Day 4의 `Robot` 클래스 정보(`name`, `max_speed`)를 딕셔너리로 만들어서 `https://httpbin.org/post`에 POST 요청으로 보내보고, 서버가 받은 내용을 응답에서 확인해보기 (`response.json()["json"]` 부분을 보면 서버가 실제로 받은 데이터가 그대로 찍힌다).
3. (심화) `timeout=0.001`처럼 일부러 아주 짧은 타임아웃을 줘서 `requests.exceptions.Timeout`이 실제로 발생하는지 확인하고, `try/except`로 잡아서 "타임아웃 발생"이라는 메시지가 출력되도록 만들어보기.

---

## 9. 다음 (Day 7) 예고

다음은 **pyserial** — USB/시리얼 포트로 통신하는 장비(일부 카메라 컨트롤러, 센서 등)를 다루는 법으로 이어간다. `requests`가 네트워크(HTTP) 통신이었다면, `pyserial`은 물리적인 케이블(COM 포트) 통신이라는 차이를 염두에 두고 넘어가면 된다.
