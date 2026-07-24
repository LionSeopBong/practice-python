import asyncio
import time

async def camera_capture(name, delay):
  print(f"[{name}] 촬영 요청 전송")
  await asyncio.sleep(delay)
  print(f"[{name}] 촬영완료 ({delay}) 초 소요")
  return f"{name}_image_jpg"

async def main():
  start = time.time()
  results = await asyncio.gather(
    camera_capture("Camera-A",2),
    camera_capture("Camera-B",1),
    camera_capture("Camera-C",3),
  )
  print(results)
  print(f"총 소요시간: {time.time() - start:.1f}초")

asyncio.run(main())