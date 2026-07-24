# 1안 방식(협업에서 좀더 선호)

# import camera
# result = camera.captuer("Camera-A")
# print(camera.CAMERA_COUNT)

# # 2안 방식
# from camera import captuer, CAMERA_COUNT
# result = captuer("Camera-A")

import asyncio

from devices import capture, move

async def main():
  results = await asyncio.gather(
    capture("Camera-A",2),
    move("P1",3),
  )
  print("결과:",results)

if __name__ == "__main__":
  asyncio.run(main())