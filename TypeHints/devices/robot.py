
class Robot:
  def __init__(self, name:str, max_speed: float):
    self.name: str = name
    self.max_speed: float = max_speed
  def move(self, position: str, speed: float) -> bool:
    if speed > self.max_speed:
      print(f"[{self.name}] 최대 속도 ({self.max_speed}) 초과! 이동 취소")
      return False
    print(f"[{self.name}] {position} 까지 {speed} 속도로 이동")
    return True

  
if __name__ == "__main__":
    ur5 = Robot("UR5", max_speed=2.0)
    ur5.move("P1", 1.5)   # 정상 -> True
    ur5.move("P2", 3.0)   # 속도 초과 -> False