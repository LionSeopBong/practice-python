import requests

def send_move_command(robot_name: str, position: str, speed: float, server_url:str)-> bool:
  try:
    response = requests.post(
      f"{server_url}/move",json={"robot_name": robot_name, "position":position, "speed":speed},
      timeout=3,
    )
    response.raise_for_status()
    return True
  except requests.exceptions.RequestEception as e:
    print(f"자동 명령 전송 실패: {e}")
    return False