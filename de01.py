# day01.py 아래에 추가

# ✅ 예외처리 (C++ try/catch와 동일 개념!)
# C++:
# try { ... }
# catch(exception e) { ... }
# finally { ... }

class Camera:
    def __init__(self, name):
        self.name = name
        self.status = "미연결"

    def connect(self):
        self.status = "연결됨"

    def capture(self):
        # 연결 안됐으면 예외 발생
        if self.status != "연결됨":
            raise Exception("카메라가 연결되지 않았습니다!")
        print(f"{self.name} 촬영 완료!")

# 예외처리 적용
cam = Camera("Canon EOS")

try:
    cam.capture()  # 연결 안된 상태로 촬영 시도
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    print("항상 실행되는 블록")  # C++ finally와 동일

# 연결 후 정상 촬영
try:
    cam.connect()
    cam.capture()
except Exception as e:
    print(f"오류 발생: {e}")
finally:
    print("촬영 프로세스 종료")