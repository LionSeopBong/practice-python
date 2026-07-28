import json
from .robot import Robot
from .camera import Camera

def load_device(path:str) -> tuple[dict[str, Robot], dict[str, Camera]]:
  try:
    with open(path, "r", encoding="utf-8") as f:
      data = json.load(f)
  except FileNotFoundError:
    print(f"설정파일을 찾을 수 없음: {path}, 빈 상태로 시작")    
    return {},{}
  except json.JSONDecodeError:
      print(f"설정파일 형식이 잘못됨: {path}, 빈 상태로 시작")    
      return {},{}

  robots = {
    item["name"]: Robot(name=item["name"], max_speed=item["max_speed"],port=item.get("port"))
    for item in data["robots"]
  }
  cameras = {
    item["name"]: Camera(name=item["name"])
    for item in data["cameras"]
  }
  return robots, cameras