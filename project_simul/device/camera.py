import asyncio

class Camera:
    def __init__(self, name: str, resolution: str = "1920x1080"):
        self.name: str = name
        self.resolution: str = resolution
        self.status: str = "idle"       # idle, capturing, error
        self.last_image: str | None = None
        self.last_error: str | None = None
        self.exposure:int = 1000

    def get_status(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "last_image": self.last_image,
            "exposure":self.exposure,
            "error":self.last_error,
        }
    
    async def capture(self) -> str:
        self.status = "capturing"
        self.last_error = None
        try:
          await asyncio.sleep(1.0)  # 촬영 + 처리 시간을 흉내
          self.last_image = f"{self.name}_{int(asyncio.get_event_loop().time())}.jpg"
          self.status = "idle"
          return self.last_image
        
        except Exception as e:
            self.status = "error"
            self.last_error = str(e)
            return None
          
          