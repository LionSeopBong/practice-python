import asyncio

class Robot:
  def __init__(self, name:str, max_speed:float, port: str | None = None):
    self.name:str = name
    self.max_speed:float = max_speed
    self.port:str | None = port
    self.status: str = "idle"
    self.current_position: str = "HOME"
    self.last_error:str | None = None

  def get_status(self) -> dict:
    return {
      "name":self.name,
      "status":self.status,
      "position": self.current_position,
      "error":self.last_error,
    }

  async def move(self, position:str, speed:float) -> bool:
    if speed > self.max_speed:
      self.last_error = "최대 속도 초과"
      return False

    self.status = "moving"
    self.last_error = None
    print(f"[{self.name}] {self.current_position} -> {position} 이동 시작")

    try:
      if self.port is None:
        await asyncio.sleep(2.0/ speed)
      else:
        pass
        # raise RuntimeError("테스트 에러: 장비 응답 없음")

      self.current_position = position
      self.status = "idle"
      print(f"[{self.name}] {position} 도착")
      return True

    except Exception as e:
      self.status = "error"
      self.last_error = str(e)
      return False