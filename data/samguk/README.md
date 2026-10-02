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

## 라이선스

Wesnoth와 같이 GPL v2 이상이다. 빌려 쓴 그래픽과 맵(Hamlets, Doc Paterson 작)은 원저작자의 라이선스를 따른다(`copyrights.csv`).
