import json

def load_camera_config(path:str)->dict:
  try:
    with open(path,"r", encoding="utf-8") as f:
      return json.load(f)
  except FileNotFoundError:
    print(f"카메라 설정 파일을 찾을 수 없음: {path}, 기본값으로 대체")
    return {"cameras":[{"name": "UNKNOWN","exposure": 100}]}