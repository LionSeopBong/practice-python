# Day 14. 통합 테스트 스크립트

지금까지는 `/docs`에서 엔드포인트를 하나씩 눌러가며 확인했는데, 오늘은 **여러 엔드포인트를 이어서 자동으로 검증하는 스크립트**를 만든다. Day 6의 `requests`가 오늘 "테스트 도구"로 재활용된다.

---

## 1. 왜 필요한가

지금까지 확인한 방식(`/docs`에서 하나씩 클릭)은 기능이 늘어날수록 매번 손으로 반복해야 해서 느리고, 실수로 빠뜨리기 쉽다. 실무에서는 이런 반복 확인을 **스크립트로 자동화**해서, 코드를 고칠 때마다 스크립트 하나만 실행하면 전체가 여전히 잘 동작하는지 몇 초 안에 확인한다.

오늘 만들 시나리오:
> 1) 로봇 UR5에게 P1으로 이동 명령 → 2) 이동 완료 후 상태가 idle인지 확인 → 3) Camera-A로 촬영 → 4) 촬영된 이미지 파일명이 응답에 포함됐는지 확인 → 5) 존재하지 않는 로봇/카메라에 대해 404가 오는지도 확인

---

## 2. `assert`로 자동 검증하기 (오늘의 새 문법)

지금까지는 결과를 `print`로 찍어서 **눈으로** 확인했는데, `assert`를 쓰면 **코드가 스스로 확인**하게 만들 수 있다.

```python
result = 1 + 1
assert result == 2   # 참이면 아무 일도 안 일어남
assert result == 3   # 거짓이면 AssertionError 발생
```

- `assert 조건`: 조건이 `True`면 그냥 넘어가고, `False`면 `AssertionError`를 발생시켜서 그 자리에서 스크립트가 멈춘다.
- `assert 조건, "메시지"`: 실패했을 때 어떤 메시지를 보여줄지 지정할 수 있다.

```python
assert result == 3, f"예상값은 3인데 실제로는 {result}"
```

Day 1의 예외처리와 연결하면, `assert`도 결국 `AssertionError`라는 예외를 발생시키는 것뿐이라 `try/except AssertionError`로 잡을 수도 있지만, 테스트 스크립트에서는 보통 안 잡고 **실패하면 바로 멈추게** 두는 게 일반적이다.

---

## 3. 통합 테스트 스크립트 작성

```python
# test_integration.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_robot_move_success():
    response = requests.post(
        f"{BASE_URL}/robots/move",
        json={"robot_name": "UR5", "position": "P1", "speed": 1.5},
    )
    assert response.status_code == 200, f"기대: 200, 실제: {response.status_code}"

    data = response.json()
    assert data["success"] is True
    assert data["status"]["position"] == "P1"
    assert data["status"]["status"] == "idle"
    print("✅ 로봇 이동 성공 테스트 통과")


def test_robot_move_speed_exceeded():
    response = requests.post(
        f"{BASE_URL}/robots/move",
        json={"robot_name": "UR5", "position": "P2", "speed": 99.0},
    )
    assert response.status_code == 400, f"기대: 400, 실제: {response.status_code}"
    print("✅ 로봇 속도 초과 테스트 통과")


def test_robot_not_found():
    response = requests.post(
        f"{BASE_URL}/robots/move",
        json={"robot_name": "UNKNOWN", "position": "P1", "speed": 1.0},
    )
    assert response.status_code == 404, f"기대: 404, 실제: {response.status_code}"
    print("✅ 존재하지 않는 로봇 테스트 통과")


def test_camera_capture_success():
    response = requests.post(f"{BASE_URL}/cameras/Camera-A/capture")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "image" in data
    assert data["image"].endswith(".jpg")
    print("✅ 카메라 촬영 테스트 통과")


def test_camera_not_found():
    response = requests.post(f"{BASE_URL}/cameras/UNKNOWN/capture")
    assert response.status_code == 404
    print("✅ 존재하지 않는 카메라 테스트 통과")


if __name__ == "__main__":
    test_robot_move_success()
    test_robot_move_speed_exceeded()
    test_robot_not_found()
    test_camera_capture_success()
    test_camera_not_found()
    print("\n🎉 전체 통합 테스트 통과")
```

---

## 4. 실행

서버(`uvicorn main:app --reload`)를 켜둔 상태에서, 새 터미널로:

```bash
python test_integration.py
```

전부 통과하면:
```
✅ 로봇 이동 성공 테스트 통과
✅ 로봇 속도 초과 테스트 통과
✅ 존재하지 않는 로봇 테스트 통과
✅ 카메라 촬영 테스트 통과
✅ 존재하지 않는 카메라 테스트 통과

🎉 전체 통합 테스트 통과
```

만약 중간에 실패하면, 그 지점에서 `AssertionError`와 함께 멈추고 어디서 실패했는지 바로 알 수 있다 — 이게 `print`로 눈으로 확인하던 것과의 결정적 차이다.

---

## 5. 시나리오 이어붙이기: 로봇 이동 → 카메라 촬영

각 테스트를 독립적으로 만드는 것도 중요하지만, "실제 작업 흐름"을 흉내내는 시나리오 테스트도 하나 만들어보자.

```python
def test_scenario_move_then_capture():
    # 1) 로봇을 P1으로 이동
    move_response = requests.post(
        f"{BASE_URL}/robots/move",
        json={"robot_name": "RB5", "position": "P1", "speed": 1.0},
    )
    assert move_response.status_code == 200

    # 2) 이동 후 실제로 위치가 반영됐는지 상태 조회로 재확인
    status_response = requests.get(f"{BASE_URL}/robots/RB5/status")
    assert status_response.json()["position"] == "P1"

    # 3) 도착했으니 카메라로 촬영
    capture_response = requests.post(f"{BASE_URL}/cameras/Camera-A/capture")
    assert capture_response.status_code == 200
    assert "image" in capture_response.json()

    print("✅ [시나리오] 이동 후 촬영 테스트 통과")
```

이 함수도 `if __name__ == "__main__":` 아래에 추가해서 같이 실행하면 된다. 개별 엔드포인트를 따로 테스트하는 것과 달리, **여러 엔드포인트가 순서대로 이어져도 잘 동작하는지**를 확인하는 게 "통합" 테스트라는 이름의 의미다.

---

## 6. 오늘의 확인 과제

1. 위 `test_integration.py`를 그대로 만들어서 실행하고, 5개 테스트가 전부 통과하는지 확인하기.
2. `test_scenario_move_then_capture` 함수를 추가하고, `__main__` 블록에도 추가해서 실행 결과 확인하기.
3. (심화) 일부러 `assert data["status"]["position"] == "P1"` 부분을 `== "P2"`로 바꿔서 **일부러 테스트를 실패시켜보고**, `AssertionError` 메시지가 어떻게 출력되는지 확인한 뒤 다시 원상복구하기. (테스트가 실패할 때 어떤 모습인지 알아두는 것도 중요하다.)

---

## 7. 다음 (Day 15) 예고

3주차, 그리고 입사 전 학습의 마지막 날이다. 지금까지 만든 프로젝트 전체 코드를 정리하고(불필요한 테스트 코드 제거, 주석 정리), 간단한 README를 작성해서 "어떤 구조로, 왜 이렇게 만들었는지"를 스스로 설명할 수 있게 정리하는 시간을 가진다.
