# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from devices import send_serial_command

app = FastAPI()

robots = {
    "UR5": {"max_speed": 2.0, "connected": True},
    "RB5": {"max_speed": 1.5, "connected": False},
}

class MoveRequest(BaseModel):
    robot_name: str
    position: str
    speed: float
    port: str

# 1번 연습문제: 로봇 정보 조회
@app.get("/robots/{robot_name}")
def get_robot(robot_name: str):
    return robots.get(robot_name, {"error": "존재하지 않는 로봇"})

# 2번 + 3번 연습문제: 이동 명령 (검증 + 실제 시리얼 통신)
@app.post("/robots/move")
def move_robot(request: MoveRequest):
    if request.speed > 2.0:
        return {"success": False, "message": "최대 속도 초과"}

    command = f"MOVE {request.position} {request.speed}"
    result = send_serial_command(port=request.port, command=command)

    if result is None:
        return {"success": False, "message": "장비 통신 실패"}
    return {"success": True, "response": result}