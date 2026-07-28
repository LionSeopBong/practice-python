import requests
import time

# 1) 이동 명령을 보내자마자 (완료를 기다리지 않고 확인하고 싶다면 별도 스레드/터미널 필요하지만,
#    여기서는 이동 전/후 상태를 비교하는 것으로 충분하다)
print("이동 전:", requests.get("http://127.0.0.1:8000/robots").json())

response = requests.post(
    "http://127.0.0.1:8000/robots/move",
    json={"robot_name": "UR5", "position": "P1", "speed": 0.3},
)
print("이동 결과:", response.json())

print("이동 후:", requests.get("http://127.0.0.1:8000/robots").json())