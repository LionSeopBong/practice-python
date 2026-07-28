from fastapi import FastAPI
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

@app.get("/robots")
def list_robots():
  return [r.get_status() for r in robots.values()]

class MoveRequest(BaseModel):
   robot_naem:str
   position:str
   speed: float

@app.post("/robots/move")
async def move_robot(request: MoveRequest):
   robot = robots.get(request.robot_naem)
   if robot is None:
      return {"success": False, "message": "존재하지 않는 로봇"}
   success = await robot.move(request.position, request.speed)
   if not success:
      return {"success": False, "message": robot.last_error}
   return {"success":True, "status": robot.get_status()}

@app.post("/cameras/{camera_name}/capture")
# def list_cameras():
#     return [c.get_status() for c in cameras.values()]
async def capture_camera(camera_name:str):
   camera = cameras.get(camera_name)
   if camera is None:
      return {"success": False, "message":"존재하지 않는 카메라"}
   image = await camera.capture()
   return {"success": True, "image":image}