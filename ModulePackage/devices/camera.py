import asyncio

async def capture(name:str, delay: float = 1.0):
    print(f"[{name}] 촬영 요청전송")
    await asyncio.sleep(delay)
    print(f"[{name}] 촬영 완료")
    return f"{name}_iamge.jpg"