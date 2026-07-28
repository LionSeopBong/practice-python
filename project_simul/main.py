from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from device import Robot, Camera

app = FastAPI()

robots = {
    "UR5": Robot(name="UR5", max_speed=2.0),
    "RB5": Robot(name="RB5", max_speed=1.5),
}

cameras = {
    "Camera-A": Camera(name="Camera-A"),
}

class MoveRequest(BaseModel):
   robot_name:str
   position:str
   speed: float

@app.get("/robots")
def list_robots():
  return [r.get_status() for r in robots.values()]

@app.get("/robots/{robot_name}/status")
def get_robot_status(robot_name:str):
   robot = robots.get(robot_name)
   if robot is None:
    raise HTTPException(status_code=404, detail=f"로봇 '{robot_name}'을 찾을 수 없음")
   return robot.get_status()

@app.post("/robots/move")
async def move_robot(request: MoveRequest):
   robot = robots.get(request.robot_name)
   if robot is None:
    raise HTTPException(status_code=404, detail=f"로봇 '{request.robot_name}'을 찾을 수 없음")
   success = await robot.move(request.position, request.speed)
   if not success:
      raise HTTPException(status_code=400, detail=robot.last_error)
   return {"success":True, "status": robot.get_status()}

@app.post("/cameras/{camera_name}/capture")
async def capture_camera(camera_name:str):
   camera = cameras.get(camera_name)
   if camera is None:
    raise HTTPException(status_code=404, detail=f"'{camera_name}'을 찾을 수 없음")
   image = await camera.capture()
   return {"success": True, "image":image}