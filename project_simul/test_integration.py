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
  

if __name__ == "__main__":
  test_robot_move_success()
  test_robot_move_speed_exceeded()
  test_robot_not_found()
  test_camera_capture_success()
  test_camera_not_found()
  test_scenario_move_then_capture()
  print("\n🎉 전체 통합 테스트 통과")
