# 「삼국: 한강의 패권」 (가제)

Battle for Wesnoth 1.18 엔진 위에서 만든 토탈 컨버전 프로토타입이다. 고구려와 백제가 한강 유역을 두고 2인 대전을 한다. 게임 규칙은 Wesnoth와 같다.

- 설계서: `docs/superpowers/specs/2026-10-02-samguk-design.md`
- 구현 계획: `docs/superpowers/plans/2026-10-02-samguk.md`

## 빌드

Visual Studio 2022(“C++를 사용한 데스크톱 개발”, vcpkg 구성 요소 포함)가 필요하다. PowerShell이나 cmd에서 실행한다. vcpkg 다운로드와 캐시는 `build\vcpkg-cache`에 둔다(`%LOCALAPPDATA%`가 가상화되는 MSIX 앱 안에서도 빌드되게 하려는 것). `build` 폴더를 지우면 의존성 빌드를 처음부터 다시 한다.

```bash
git submodule update --init --recursive
```

```powershell
cmd /c utils\samguk\build.cmd
```

첫 빌드는 vcpkg 의존성 때문에 1시간 이상 걸린다. 결과물은 `build\wesnoth.exe`다.

엔진 메뉴의 한국어 번역은 따로 컴파일한다(Git Bash):

```bash
bash utils/samguk/compile_ko.sh
```

## 실행

저장소 루트의 `samguk.cmd`를 실행한다. 설정과 저장 파일은 `문서\My Games\Samguk`에 따로 저장된다.

## 콘텐츠

| 경로 | 내용 |
|---|---|
| `data/samguk/_main.cfg` | 코어 루트. 엔진 필수 요소는 기본 데이터에서 가져온다 |
| `data/samguk/game_config.cfg` | `data/game_config.cfg` 복사본. 로고 경로 두 줄만 다르다 |
| `data/samguk/units.cfg` | 종족 4개(고구려인, 백제인, 도깨비, 삼족오 기수) |
| `data/samguk/units/` | 유닛 40종. `utils/samguk/gen_units.py`가 기본 유닛에서 생성한다 |
| `data/samguk/multiplayer/` | 시대, 세력 2개, 대전 맵 2개 |
| `data/samguk/images/` | 삼국 전용 이미지 (현재 로고뿐) |

유닛 이름이나 설명을 바꾸려면 `utils/samguk/gen_units.py`의 `UNITS` 표를 고치고 다시 생성한다. 생성 파일을 손으로 고쳤다면 다시 생성할 때 덮어써지니 주의한다.

## 검사

```bash
python utils/samguk/check_content.py      # 정적 검사 (엔진 불필요)
python utils/samguk/smoke_test.py         # AI끼리 4판 자동 대전 (빌드 필요)
python utils/samguk/smoke_test.py --validate   # 스키마 검증 포함
```

## 기본 Wesnoth 데이터에서 바꾼 것

- `data/core/units.cfg`: 기본 유닛 디렉터리 include를 `#ifndef SAMGUK_CORE`로 감쌌다. 기본 코어 동작은 같다.
- `data/cores.cfg`: `samguk` 코어를 등록했다.
- `src/game_config.cpp`: 창 제목을 게임명으로 바꿨다.

## 알려진 문제

- 엔진 메뉴의 공식 한국어 번역률이 낮아(`wesnoth-lib` 약 22%) 메뉴에 영어가 섞인다.
- 유닛 그래픽은 Wesnoth 것을 빌려 쓴다. 백제 유닛은 Dunefolk, 수군은 인어 그래픽이다.
- 타이틀 화면의 "캠페인" 메뉴는 비어 있다.
- 화면에서 아직 확인하지 않은 것: 대전 만들기와 세력 선택 대화상자, 모집 대화상자, 유닛 도움말 페이지, 사람 대 AI 대전을 끝까지 한 판. 지금까지 확인한 것은 두 맵의 AI끼리 자동 대전(스키마 검증 포함), 타이틀 화면, 사람 대 AI 대전의 첫 턴이다.
- `data/core/help.cfg`의 도움말이 기본 유닛(`unit_Mage`, `unit_Cavalryman`)으로 링크를 거는데, 이 코어에는 그 유닛이 없다. 해당 링크는 깨져 있을 수 있다.
- 로딩 화면에는 아직 Wesnoth 방패가 나온다. `data/gui/window/loadscreen.cfg`는 코어를 고르기 전에 읽는 공용 GUI 데이터라서 코어별로 바꿀 수 없다.
- `samguk.cmd`가 `--userdata-dir`에 상대 경로를 넘겨서 로그에 사용 중단(deprecation) 오류 한 줄이 찍힌다. 1.18에서는 정상 동작한다.
- `src/game_config.cpp`의 창 제목 변경은 기본 Wesnoth 코어를 포함해 모든 코어에 적용된다.
- 빌드 스크립트(`utils/samguk/build.cmd:4`)는 Visual Studio 2022 Community 설치 경로를 가정한다. 다른 에디션은 그 경로를 고쳐야 한다.

## 라이선스

- 코드와 WML은 Wesnoth와 같은 GNU GPL v2 이상이다(`COPYING`).
- 빌려 쓴 유닛과 지형 그래픽은 파일마다 원래 라이선스를 그대로 따른다. 파일별 라이선스와 저작자는 `copyrights.csv`에 있다. 대부분은 GPL v2 이상이고, 일부는 CC BY-SA 4.0이다. 백제 유닛 대부분이 쓰는 Dunefolk 그래픽(`data/core/images/units/dunefolk/`)이 그 예로, `copyrights.csv` 기준 154개 파일 중 95개가 GPL v2 이상, 59개가 CC BY-SA 4.0이다(저작자 doofus-01 등).
- 관미성 시나리오가 쓰는 Hamlets 맵(`data/multiplayer/maps/2p_Hamlets.map`, Doc Paterson 작)은 Wesnoth 본체에 들어 있는 데이터로, 프로젝트와 같은 GPL v2 이상으로 배포된다. `copyrights.csv`는 이미지와 소리 파일만 다루므로 맵은 거기에 없다.
- 로고 PNG 두 개(`data/samguk/images/misc/samguk-logo.png`, `samguk-logo-bg.png`)는 `utils/samguk/make_logo.py`가 `fonts/DroidSansFallbackFull.ttf`로 글자를 그려 만들었다. 이 둘은 이 프로젝트의 그래픽으로서 GPL v2 이상이며 `copyrights.csv`에 올라 있다. 글꼴 파일의 라이선스는 `fonts/COPYING`에 출처 주소(`android.git.linaro.org`)만 적혀 있고 라이선스 문구는 없다. 안드로이드 Droid 글꼴은 일반적으로 Apache 2.0으로 배포되지만 이 저장소에서는 확인되지 않는다. 글꼴 파일 자체를 다시 배포할 때는 이 점을 따로 확인해야 한다.
