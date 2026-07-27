import requests

robot_info = {
    "name": "UR5",
    "max_speed": 2.0,
}

response = requests.post("https://httpbin.org/post", json=robot_info)

print(response.status_code)
print(response.json()["json"])  # 서버가 실제로 받은 데이터