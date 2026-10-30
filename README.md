# SLOWRAIN GAMES 홈페이지

https://slowrainmdml.github.io/ — SLOWRAIN GAMES의 Steam·Roblox 게임 쇼케이스.
빌드 도구 없는 정적 사이트(`index.html`, `styles.css`, `app.js`)이고, 게임 목록은 `content/games.json`에서 읽는다.

## 게임 추가·수정

1. `content/catalog.json`을 고친다.
   - Roblox 게임: `id`, `universeId`, `placeId`, `repo`(비공개 저장소 `ROBLOX-<repo>`), `tags`, `tagline`(ko/en).
     이름과 스토어 설명(ko/en)은 Roblox에서 자동으로 가져오므로 적지 않는다. 바꾸고 싶을 때만 `title`/`description`으로 덮어쓴다.
   - `featured`: 맨 위 배너에 나오는 게임과 순서.
   - 장르 태그: `tactics story adventure action coop versus cozy puzzle rhythm` (라벨은 `app.js`의 `TEXT.*.tags`).
2. `python3 tools/build_content.py` — Roblox API로 이름·설명·아이콘·스크린샷을 받아 `assets/games/<id>/`와 `content/games.json`을 다시 만든다.
   배너 게임은 비공개 저장소의 1920px 썸네일을 받아 `hero.webp`로 쓴다(`git credential`의 GitHub 토큰 사용). `--no-hero`면 이미 있는 `hero.webp`를 그대로 쓴다.
   Steam 게임은 실제 스토어 페이지에서 메인 캡슐·스크린샷·설명 영상을 받아 오고, 배너(`hero.webp`)와 세로 카드(`poster.webp`)는
   스토어 헤더와 같은 게임 렌더(`SRPG_STD/tools/build_steam_header_ingame_20261014.py`, 복셀 성 + 아드리안·세라)로 만든다. 그림 일러스트 캡슐은 쓰지 않는다.
   스토어 페이지가 아직 없는 PC 게임(Seedborne Chronicle)은 `platforms`(steam/stove)만 적고, 이미지는 `python3 tools/seedborne_media.py`로 게임 빌드 캡처에서 만든다. 스토어 주소가 생기면 `steamAppId`를 넣으면 된다.
3. 화면에 픽셀 폰트로 그리는 글자가 바뀌었으면 `python3 tools/build_brand.py` (Galmuri 서브셋, 로고, 파비콘, 공유 이미지 `assets/brand/og.png`).
4. 로컬 확인: `python3 -m http.server 8765` → http://127.0.0.1:8765/
5. 커밋·푸시하면 GitHub Pages가 1~2분 뒤 반영한다.

## 구성

- 상단 배너(자동 넘김, 스와이프, 키보드 ←/→), 플랫폼·장르 필터, 게임 카드, 상세 팝업(`#game-<id>`로 바로 열림), 스튜디오 소개, 소식 받기 링크.
- 한국어/영어 전환(브라우저 언어로 시작, 선택은 localStorage에 저장). 화면 문구는 `app.js`의 `TEXT`.
- 글꼴: 본문 Pretendard(jsDelivr), 제목·버튼 Galmuri11(서브셋, OFL — `assets/fonts/GALMURI-LICENSE.txt`).
