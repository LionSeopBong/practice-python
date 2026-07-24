import asyncio

async def move(position:str, delay: float=2.0):
  print(f"로봇 이동 시작 -> {position}")
  await asyncio.sleep(delay)
  print(f"로봇 이동 완료-> {position}")
  return "OK"

if __name__=="__main__":
    move("TEST_POSITION")