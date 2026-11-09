# TRPG 마스터봇 화면 캡처

홈페이지에는 접속 주소를 싣지 않습니다(주소와 입장 코드는 이메일이나 DM으로 요청받습니다). 화면은 최신 코드를 이 Mac에서
**키 없이** 따로 띄워 찍습니다. 키가 없으면 오프라인 판단기와 응답표로만 진행하므로 크레딧을 쓰지 않고, 라이브 서비스와도 무관합니다.

1. 비공개 저장소를 `/tmp/trpgbot/repo`에 클론하고 Python 3.11 가상환경에 `fastapi uvicorn[standard] anthropic`을 설치합니다.
2. `.env` 없이 로비 서버를 다른 포트로 띄웁니다(라이브 서비스는 8765를 씁니다).
   `env -u ANTHROPIC_API_KEY -u TYPESAFE_API_KEY python -m trpg.hall --port 8790`
3. `curl -X POST -H 'Content-Type: application/json' -d '{"name":"금요일 밤 모험","public":true,"code":""}' http://127.0.0.1:8790/api/rooms`
   로 테이블을 열고(같은 기기에서 너무 자주 열면 429), `node tools/trpgbot/capture.js <테이블id>`로
   캐릭터 만들기 → 동료 앉히기 → 광장 → 판정 → 습격 전투를 390×844(3배)로 `/tmp/trpgbot/final/`에 찍습니다.
4. `python3 tools/trpgbot_media.py`가 표지와 갤러리를 만듭니다. 룰북 문장이 길게 보이는 화면(생애 표 결과 등)은 쓰지 않습니다.
