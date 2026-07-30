# Day 15. 프로젝트 마무리 & 입사 전 최종 점검

3주 계획의 마지막 날이다. 오늘은 새 문법을 배우기보다, 지금까지 만든 걸 **정리하고 스스로 설명할 수 있게 만드는** 날이다.

---

## 1. 지금까지 만든 것 되짚어보기

```
equipment_simulator/
├── main.py                  (FastAPI 서버, 엔드포인트 모음)
├── device/
│   ├── __init__.py
│   ├── robot.py              (Robot 클래스 - 상태, 이동, 에러 처리)
│   ├── camera.py             (Camera 클래스 - 상태, 촬영, 에러 처리)
│   └── config.py             (JSON 설정 로딩)
├── configs/
│   └── devices.json          (로봇/카메라 목록 - 코드 수정 없이 추가/제거 가능)
└── test_integration.py       (assert 기반 통합 테스트)
```

| 주차 | 배운 것 | 프로젝트에 적용된 부분 |
|---|---|---|
| 1주 | 변수/함수/클래스/예외처리/asyncio/모듈/타입힌트/파일입출력 | `Robot`/`Camera` 클래스, `try/except`, `async def move()`, `devices` 패키지 구조, 타입 힌트 전반, JSON 설정 |
| 2주 | requests/pyserial/FastAPI | `test_integration.py`의 요청 코드, `port` 분기(실제 장비용), `main.py` 서버 전체 |
| 3주 | 상태 관리, 에러 통일, JSON 설정 이전, 통합 테스트 | 시뮬레이터 전체 구조 |

이 표를 보면서 "내가 왜 이렇게 짰는지" 스스로 한 줄씩 설명할 수 있는지 확인해보면 좋다 — 면접이나 입사 초반에 "이 프로젝트 설명해보라"는 질문을 받을 수도 있으니까.

---

## 2. 코드 정리 체크리스트

### 2-1. 테스트용으로 임시로 넣었다 뺐다 한 코드 확인

Day 13에서 `raise RuntimeError("테스트 에러")`처럼 일부러 넣었던 코드나, `configs/devices.json`의 `"TEST"` 로봇 항목이 아직 남아있지 않은지 확인한다.

```bash
grep -rn "테스트 에러\|RuntimeError" device/
```

### 2-2. 불필요한 `print` 정리

디버깅용으로 넣었던 `print`문 중, 굳이 서버 로그에 계속 남길 필요 없는 것들을 정리한다. (`[UR5] P1 -> P2 이동 시작` 같은 로그는 실무에서도 유용하니 남겨도 되지만, "여기 도달함" 같은 확인용 print는 지운다.)

### 2-3. 타입 힌트 누락 확인

Day 4에서 배운 타입 힌트가 함수마다 일관되게 붙어있는지 훑어본다. 특히 새로 추가한 함수에 타입 힌트를 빼먹기 쉽다.

### 2-4. 하드코딩된 값 재확인

`main.py`에 `robots = {...}`가 혹시 남아있지 않은지 (Day 12에서 `load_devices()`로 옮겼어야 함), `configs/devices.json` 경로가 코드에 하드코딩돼 있다면 상수로 빼둘 만한지 검토한다.

```python
# main.py 맨 위에
CONFIG_PATH = "configs/devices.json"

robots, cameras = load_devices(CONFIG_PATH)
```

---

## 3. README 작성하기

프로젝트 폴더에 `README.md`를 하나 만든다. 실무에서 새 프로젝트를 받으면 제일 먼저 읽는 파일이 이거라, 지금부터 습관을 들여두면 좋다.

```markdown
# Equipment Simulator

## 개요
UR/RB 로봇과 카메라를 FastAPI로 제어하는 시뮬레이터.
실제 장비 없이 asyncio로 응답 지연을 흉내내며, `Robot`/`Camera`에 `port`를
지정하면 실제 시리얼 통신으로 전환 가능한 구조로 설계함.

## 구조
- `main.py`: FastAPI 엔드포인트
- `device/`: Robot, Camera 클래스 및 JSON 설정 로더
- `configs/devices.json`: 장비 목록 (코드 수정 없이 추가/제거 가능)
- `test_integration.py`: 통합 테스트

## 실행 방법
\`\`\`bash
pip install fastapi uvicorn requests pyserial
uvicorn main:app --reload
\`\`\`
`http://127.0.0.1:8000/docs`에서 API 테스트 가능.

## 테스트
\`\`\`bash
python test_integration.py
\`\`\`

## 설계 원칙
- 장비 목록은 JSON으로 관리 (코드와 데이터 분리)
- 에러는 계층별로 처리: 통신 계층은 구체적 예외, 최상위는 `except Exception` 안전망
- 시뮬레이션 ↔ 실제 장비 전환은 `port` 필드 하나로 분기
```

이런 형태로, **어떤 프로젝트든 처음 보는 사람이 5분 안에 감을 잡을 수 있게** 쓰는 게 목적이다. 지금 프로젝트 실제 구조에 맞게 조금씩 다듬어서 완성해보자.

---

## 4. 스스로 점검해보면 좋은 질문들 (입사 전 자가 점검)

1. `Robot` 클래스가 왜 `port: str | None`을 갖고 있는지, 이게 나중에 실제 장비 연동할 때 어떻게 도움이 되는지 설명할 수 있는가?
2. `asyncio.gather`와 순차적으로 `await`를 여러 번 호출하는 것의 차이를 코드 없이 말로 설명할 수 있는가?
3. `HTTPException`으로 404와 400을 나눈 이유를 설명할 수 있는가?
4. `devices.json`이 깨졌을 때 서버가 어떻게 되는지, 왜 그렇게 만들었는지 설명할 수 있는가?
5. FastAPI 엔드포인트에서 `def`와 `async def`를 언제 구분해서 써야 하는지 설명할 수 있는가?

이 5개 질문에 막힘없이 답할 수 있으면, 3주 계획의 실질적인 목표(장비 제어 + FastAPI 백엔드 감 잡기)는 충분히 달성된 것이다.

---

## 5. 오늘의 할 일

1. 위 체크리스트(2번)로 코드 한 번 훑어보고 정리하기.
2. `README.md` 작성해서 프로젝트 폴더에 추가하기.
3. 4번의 5개 질문에 스스로(또는 소리 내어) 답해보고, 막히는 부분이 있으면 어느 Day 자료였는지 찾아서 다시 훑어보기.

---

## 6. 3주 계획을 마치며

1주차 기초 문법부터 시작해서, 2주차 실무 라이브러리, 3주차 실전 프로젝트까지 — 계획했던 3주를 전부 완주했다. 특히 이번 주 프로젝트에서 겪은 자잘한 버그들(오타, 필드 누락, `try/except` 문법 실수, `await` 빠뜨림)은 사실 실무에서도 매일 일어나는 흔한 일이다. 그걸 직접 겪고 원인을 찾아 고쳐본 경험이, 단순히 강의를 눈으로만 보는 것보다 훨씬 오래 남는다.

입사 후에는 이 시뮬레이터의 `Robot`/`Camera` 클래스를 실제 SDK 호출로 바꿔나가는 것부터 시작하면, 오늘 정리한 구조가 그대로 실무 코드의 출발점이 될 것이다.
