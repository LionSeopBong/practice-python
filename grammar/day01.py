# C++과 비교하면서 익혀봐요!

# C++: string name = "박한섭";
name = "박한섭"

# C++: int age = 34;
age = 34

# C++: bool is_developer = true;
is_developer = True

# C++: printf("%s\n", name);
print(name)
print(age)
print(is_developer)

# f-string (C++ printf보다 편해요)
print(f"안녕하세요, {name}입니다! 나이는 {age}살이에요")

# day01.py 아래에 추가해보세요

# ✅ 1. 타입이 자유로워요
x = 10        # 정수
x = "hello"   # 문자열로 바꿔도 됨 (C++은 불가!)
x = 3.14      # 실수로도 가능

# ✅ 2. 리스트 (C++ vector와 비슷)
items = [1, 2, 3, 4, 5]
items.append(6)        # 추가
items.remove(1)        # 삭제
print(items)

# ✅ 3. 딕셔너리 (C++ map과 비슷)
person = {
    "name": "박한섭",
    "age": 34,
    "job": "개발자"
}
print(person["name"])
person["company"] = "스튜디오랩"  # 추가
print(person)

# ✅ 4. 반복문 (C++보다 훨씬 간단!)
# C++: for(int i=0; i<5; i++)
for i in range(5):
    print(f"{i}번째")

# 리스트 바로 순회
for item in items:
    print(item)


    # day01.py 아래에 추가

# ✅ 1. 함수 (C++ 보다 간단!)
# C++: int add(int a, int b) { return a + b; }
def add(a, b):
    return a + b

print(add(3, 5))

# 기본값 설정 가능
def greet(name, message="안녕하세요"):
    print(f"{message}, {name}!")

greet("박한섭")
greet("박한섭", "반갑습니다")

# ✅ 2. 클래스 (C++ 과 개념 동일!)
# C++:
# class Camera {
#   string status;
#   void connect() {}
# }

class Camera:
    def __init__(self, name):   # C++ 생성자
        self.name = name
        self.status = "미연결"

    def connect(self):
        self.status = "연결됨"
        print(f"{self.name} 연결 완료!")

    def capture(self):
        if self.status == "연결됨":
            print(f"{self.name} 촬영 완료!")
        else:
            print("먼저 연결하세요!")

# 사용
cam = Camera("Canon EOS")
cam.capture()   # 연결 전
cam.connect()   # 연결
cam.capture()   # 연결 후