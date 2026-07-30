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
