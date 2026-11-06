# TRPG 마스터봇 화면 캡처

공개 주소가 없는 프로젝트라, 실제 엔진과 실제 웹 화면으로 장면을 만들어 찍습니다.

1. 비공개 저장소를 `/tmp/trpgbot/repo`에 클론하고 Python 3.11 가상환경에 `pytest`를 설치합니다.
2. `make_views.py`: 저장소의 `Table` 엔진을 테스트용 가상 콘텐츠(`tests/content_fixture.py`)로 돌려
   대화 → 판정 → 습격 전투의 실제 화면 상태를 `views.json`으로 남깁니다. 모험·마을 이름은 예시 이름이고,
   마스터 문장은 프로젝트의 응답표에서 나옵니다. 룰북 문장은 들어가지 않습니다.
3. `shoot.js`: `repo/web`을 `/static`으로 내보내는 정적 서버(`/tmp/trpgbot/root`, 포트 8766)에서 실제 앱을 열고,
   WebSocket 대신 위 상태를 넣어 390×844(3배) 폰 화면을 찍습니다.
4. `python3 tools/trpgbot_media.py`가 표지와 갤러리 이미지를 만듭니다.
