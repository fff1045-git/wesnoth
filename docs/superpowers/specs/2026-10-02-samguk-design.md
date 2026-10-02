# 「삼국: 한강의 패권」(가제) 토탈 컨버전 설계서

- 작성일: 2026-10-02
- 코드명: `samguk`
- 기반: Battle for Wesnoth `1.18` 브랜치 (`1.18.8+dev`, 커밋 `db4cdf5b67c`)
- 작업 브랜치: `samguk` (추적: `origin/1.18`)
- 성격: 사내 프로토타입 겸 학습용 (출시 계획 없음)

## 1. 목표

Wesnoth 엔진과 게임 규칙은 그대로 두고, 세계관을 한국 삼국시대와 신화로 바꾼 토탈 컨버전 프로토타입을 만든다.
완료 기준은 다음 두 가지다.

1. `samguk.cmd`를 실행하면 Wesnoth 기본 콘텐츠 없이 우리 코어로 시작한다.
2. 고구려 대 백제 2인 대전을 두 맵에서 사람 대 AI, AI 대 AI로 끝까지 할 수 있다.

## 2. 범위

### 포함
- 소스 빌드 (Windows, MSVC 2022, vcpkg)
- 커스텀 코어 `samguk`
- 세력 2개(고구려, 백제), 유닛 종류 40개, 종족 4개
- 2인 대전 맵 2개 (새 맵 1, 기존 맵 재사용 1)
- 게임명, 창 제목, 로고 교체, 실행기
- 우리 콘텐츠의 한국어 텍스트

### 제외 (이번 범위 아님)
- 게임 규칙 변경, 창 제목 외의 C++ 수정
- 유닛과 지형 아트 교체 (기존 그래픽을 빌려 쓰고 나중에 교체)
- 캠페인, 시나리오 스토리
- 엔진 UI 한국어 번역 보강
- 모바일, Mac, Linux 빌드와 배포 패키지

## 3. 기술 기반

### 3.1 빌드
- 도구: Visual Studio 2022 Community, VS에 들어 있는 vcpkg(매니페스트 모드, `vcpkg.json`), Ninja
- 설정: `-DCMAKE_BUILD_TYPE=Release -DVCPKG_TARGET_TRIPLET=x64-windows -DENABLE_SERVER=OFF -DENABLE_CAMPAIGN_SERVER=OFF -DENABLE_TESTS=OFF -DENABLE_NLS=OFF`
- 출력 디렉터리: `build/` (git에 넣지 않음)
- `ENABLE_NLS=OFF`이므로 한국어 엔진 번역(`.mo`)은 Git for Windows의 `msgfmt`로 `translations/ko/LC_MESSAGES/`에 따로 컴파일한다.
- 빌드 스크립트는 vcpkg 캐시(`VCPKG_DOWNLOADS`, `VCPKG_DEFAULT_BINARY_CACHE`, `X_VCPKG_REGISTRIES_CACHE`)를 `build\vcpkg-cache` 아래로 지정한다. MSIX 앱(Claude 데스크톱 등)에서 실행하면 `%LOCALAPPDATA%`가 패키지 전용 폴더로 가상화된다. 그러면 msys2가 보는 실제 루트와 vcpkg가 PATH에 넣는 논리 경로가 어긋나고, autoconf가 `install`을 찾지 못해 ICU 빌드가 `install-sh` 경로 오류로 실패한다(2026-10-02 실측, 캐시를 옮긴 뒤 `/usr/bin/install -c`로 정상 인식 확인).
- 대안: 빌드가 막히면 공식 1.18.8 실행 파일에 `--data-dir`로 이 저장소를 지정해 실행한다.

### 3.2 커스텀 코어
엔진은 `data/cores.cfg`의 `[core]` 항목을 읽고, 선택된 코어의 `path`가 가리키는 WML 파일 하나를 데이터 트리의 루트로 로드한다(`src/game_config_manager.cpp`). 기본 코어는 `path="/"`, 즉 `data/_main.cfg`이다.

`data/cores.cfg`에 아래 항목을 추가한다.

```
[core]
    id=samguk
    name= _ "삼국: 한강의 패권"
    path="samguk"
[/core]
```

`path`는 `data/` 기준 상대 경로이고(`filesystem::get_wml_location`), 디렉터리를 가리키면 그 안의 `_main.cfg`를 읽는다.

엔진이 알아 두어야 할 동작:
- `[units]` 블록은 여러 개여도 하나로 합쳐 읽는다(`merged_children_view("units")`). 우리 종족과 유닛은 별도 `[units]` 블록에 둔다.
- 기본 이동 타입, 공통 특성, 기본 종족은 `data/core/units.cfg` 안에 있다. 이 파일의 기본 유닛 디렉터리 include 부분만 `#ifndef SAMGUK_CORE` … `#endif`로 감싸는 **2줄 수정**을 하고, 우리 `_main.cfg`가 `SAMGUK_CORE`를 정의한 뒤 이 파일을 include한다. 기본 코어는 `SAMGUK_CORE`를 정의하지 않으므로 동작이 그대로다.
- 디렉터리 include(`{dir/}`)는 그 디렉터리의 `.cfg` 파일과, `_main.cfg`가 있는 하위 디렉터리만 읽는다. 그래서 `units/goguryeo/`, `units/baekje/`는 따로 include한다.
- `[game_config]`는 첫 번째 블록만 읽는다(`mandatory_child`). 이미지 검색 경로(`[binary_path]`)는 선언 순서가 아니라 알파벳 순서(`std::set`)로 찾는다.

파일 구성:

```
data/samguk/
  _main.cfg                 루트. 아래 3.3의 필수 요소 + 우리 콘텐츠를 include
  README.md                 실행 방법
  units.cfg                 [units]: 기본 이동 타입, 특성, 우리 종족, 우리 유닛 디렉터리
  units/goguryeo/*.cfg      고구려 유닛 20종
  units/baekje/*.cfg        백제 유닛 20종
  multiplayer/
    _main.cfg
    era.cfg                 [era] id=samguk_era
    factions/goguryeo.cfg
    factions/baekje.cfg
    scenarios/2p_Hangang.cfg
    scenarios/2p_Gwanmiseong.cfg
    maps/2p_Hangang.map
  images/misc/samguk-logo.png, samguk-logo-bg.png
```

### 3.3 `_main.cfg`가 기본 데이터에서 가져오는 것
기본 `data/_main.cfg`와 `data/core/_main.cfg`의 구성을 따르되, 유닛, 세력, 캠페인, 기본 대전 맵만 뺀다.

| 가져옴 | 이유 |
|---|---|
| `english.cfg`, `themes/`, `game_config.cfg`, `advanced_preferences.cfg` | 엔진 설정, 인게임 UI 테마 |
| `core/macros/`, `core/terrain.cfg`, `core/terrain-graphics/`, `core/terrain-graphics.cfg` | 매크로, 지형 정의와 그래픽 |
| `core/help.cfg`, `core/hotkeys.cfg`, `core/editor/`, `core/about*.cfg` | 도움말, 단축키, 맵 편집기, 크레딧 |
| 기본 `[lua]` 블록 (`wml-tags.lua` 등) | WML 태그 구현 |
| `[ais]` 블록, `modifications.cfg` | AI, 대전 옵션 |
| `[multiplayer_side] id=Custom`, `[binary_path] data/core` | 엔진 필수, 기존 그래픽 경로 |
| `[textdomain]` 선언들 | 번역 도메인 |

| `core/units.cfg` (`SAMGUK_CORE` 정의 상태) | 이동 타입, 공통 특성, 기본 종족, `fake` 유닛. 기본 유닛 타입은 빠진다 |

뺀 것: 기본 유닛 타입, `multiplayer/`(우리 `multiplayer/`로 대체), `campaigns/`.

로고는 `game_config.cfg`를 include한 뒤 WML 병합 문법으로 경로만 바꾼다. 이미지 파일명은 기본 로고와 겹치지 않게 `misc/samguk-logo.png`로 한다(같은 이름으로 덮어쓰는 방식은 검색 순서 때문에 동작하지 않는다).

```
[+game_config]
    [+images]
        game_logo="misc/samguk-logo.png"
        game_logo_background="misc/samguk-logo-bg.png"
    [/images]
[/game_config]
```

### 3.4 유닛 제작 방식
원본 유닛 `.cfg`를 복사한 뒤 다음만 바꾼다.

- `id`, `name`, `description`, `race`, `advances_to`
- 텍스트 도메인은 원본(`wesnoth-units`) 그대로 둔다. 바꾸면 공격 이름 같은 원본 문자열의 한국어 번역이 끊긴다. 우리 한국어 문자열은 번역이 없으니 원문 그대로 표시된다.

스탯, 공격, 저항, 이동 타입, 애니메이션, 이미지 경로는 원본 그대로 둔다. 아트를 교체할 때는 이미지 경로만 바꾼다.
유닛 id는 영문 소문자로 `gog_`, `bae_` 접두어를 붙인다(예: `gog_spearman`).

## 4. 세력과 유닛

정렬(낮·밤 보정), 스탯, 비용은 모두 원본 값이다. 승급은 계열마다 갈래 하나만 남긴다.

### 4.1 고구려 (낮에 강한 기마·궁술 세력, 상징 삼족오)

| id | 이름 | 레벨 | 원본 |
|---|---|---|---|
| gog_spearman | 창수 | 1 | Spearman |
| gog_pikeman | 장창수 | 2 | Pikeman |
| gog_halberdier | 극수 | 3 | Halberdier |
| gog_bowman | 맥궁수 | 1 | Bowman |
| gog_longbowman | 장궁수 | 2 | Longbowman |
| gog_master_bowman | 신궁 | 3 | Master Bowman |
| gog_horseman | 개마무사 | 1 | Horseman |
| gog_knight | 개마장 | 2 | Knight |
| gog_grand_knight | 개마대장 | 3 | Grand Knight |
| gog_rider | 궁기병 | 1 | Dune Rider |
| gog_horse_archer | 기마궁수 | 2 | Dune Horse Archer |
| gog_windbolt | 질풍궁기 | 3 | Dune Windbolt |
| gog_mage | 일관 | 1 | Mage |
| gog_white_mage | 백일관 | 2 | White Mage |
| gog_mage_of_light | 태양사제 | 3 | Mage of Light |
| gog_gryphon_rider | 삼족오 기수 | 1 | Gryphon Rider |
| gog_gryphon_master | 삼족오 장수 | 2 | Gryphon Master |
| gog_lieutenant | 장군 | 2 | Lieutenant |
| gog_general | 대장군 | 3 | General |
| gog_grand_marshal | 대모달 | 4 | Grand Marshal |

- 징집: 창수, 맥궁수, 개마무사, 궁기병, 일관, 삼족오 기수
- 지휘관 후보: 장군, 장창수, 장궁수, 백일관, 기마궁수
- AI 징집 패턴: `fighter,fighter,archer,mixed fighter,scout`

### 4.2 백제 (낮에 강한 정규군, 해 질 녘과 새벽에 강한 승병, 밤에 강한 도깨비. 수군·불교·화공)

| id | 이름 | 레벨 | 원본 |
|---|---|---|---|
| bae_soldier | 백제 보병 | 1 | Dune Soldier |
| bae_swordsman | 검대 | 2 | Dune Swordsman |
| bae_blademaster | 검대장 | 3 | Dune Blademaster |
| bae_skirmisher | 척후병 | 1 | Dune Skirmisher |
| bae_strider | 유격병 | 2 | Dune Strider |
| bae_harrier | 유격대장 | 3 | Dune Harrier |
| bae_burner | 화공병 | 1 | Dune Burner |
| bae_scorcher | 화공대 | 2 | Dune Scorcher |
| bae_firetrooper | 화공대장 | 3 | Dune Firetrooper |
| bae_herbalist | 승병 | 1 | Dune Herbalist |
| bae_apothecary | 의승 | 2 | Dune Apothecary |
| bae_luminary | 대덕 | 3 | Dune Luminary |
| bae_merman_fighter | 수군 | 1 | Merman Fighter |
| bae_merman_warrior | 수군 무사 | 2 | Merman Warrior |
| bae_merman_triton | 수군 장수 | 3 | Merman Triton |
| bae_troll_whelp | 도깨비 | 1 | Troll Whelp |
| bae_troll | 큰도깨비 | 2 | Troll |
| bae_troll_warrior | 도깨비 대장 | 3 | Troll Warrior |
| bae_captain | 좌평 | 2 | Dune Captain |
| bae_warmaster | 상좌평 | 3 | Dune Warmaster |

- 징집: 백제 보병, 척후병, 화공병, 승병, 수군, 도깨비
- 지휘관 후보: 좌평, 검대, 화공대, 의승, 큰도깨비
- AI 징집 패턴: `fighter,fighter,archer,healer,fighter` (백제 징집 유닛에는 scout, mixed fighter 용도가 없다)

### 4.3 종족

| id | 이름 | 특성 규칙 출처 | 비고 |
|---|---|---|---|
| goguryeo | 고구려인 | human | 한국식 이름 목록 |
| baekje | 백제인 | human | 한국식 이름 목록 |
| dokkaebi | 도깨비 | troll | 짧은 별칭 목록 (예: 두두리, 어둑이) |
| samjogo | 삼족오 | gryphon | 기수 유닛에 사용 |

수군(원본 merfolk)은 `baekje` 종족으로 바꾼다. 이동 타입은 원본 `swimmer` 그대로라 물 지형 성능은 같다. 특성은 인간 규칙을 따르게 된다.

## 5. 맵

| id | 이름 | 크기 | 출처 | 진영 |
|---|---|---|---|---|
| samguk_2p_hangang | 한강 유역 | 약 24×20 + 테두리 | 새로 제작 | 1번 북쪽(고구려 권장), 2번 남쪽 |
| samguk_2p_gwanmiseong | 관미성 공방 | 기존과 같음 | `2p_Hamlets.map` 재사용 | 1번 북쪽, 2번 남쪽 |

한강 유역 맵 요건:
- 강이 동서로 가로지르고, 여울(얕은 물) 3곳과 다리 2곳이 교전 지점이 된다.
- 양 진영 성(본진)은 각각 리더 칸 1개 + 성 칸 6개.
- 마을 16~18개, 남북이 점대칭이 되도록 배치한다.
- 일정은 `{DEFAULT_SCHEDULE}`, 안개(fog) 켬.

## 6. 브랜딩

| 항목 | 방법 |
|---|---|
| 게임명 | 「삼국: 한강의 패권」(가제). 코어 이름, 창 제목, 로고에 쓴다 |
| 창 제목 | `src/game_config.cpp`의 `_("The Battle for Wesnoth")`를 게임명으로 바꾼다 (유일한 C++ 수정). MSVC는 `/utf-8`로 컴파일하므로 한글 리터럴을 그대로 쓴다 |
| 로고 | 게임명 텍스트 로고 PNG를 Python(Pillow)으로 만든다. 한글 폰트는 저장소의 `fonts/DroidSansFallbackFull.ttf` |
| 타이틀 배경 | 기존 그림 유지 |
| 실행기 | 저장소 루트의 `samguk.cmd`: `build\wesnoth.exe --data-dir <저장소> --userdata-dir Samguk --core samguk --language ko_KR`. 사용자 데이터는 `문서\My Games\Samguk`에 따로 둬서 설치된 Wesnoth와 섞이지 않게 한다 |

## 7. 한글화
- 우리 WML 텍스트는 한국어로 직접 쓴다. `_ "..."` 표시는 유지해 나중에 번역 파일을 만들 수 있게 한다. 번역이 없으면 gettext가 원문(한국어)을 그대로 돌려준다.
- 엔진 UI는 공식 한국어 번역을 쓴다. `wesnoth-lib` 번역률이 약 22%라 메뉴에 영어가 섞인다. 알려진 한계로 둔다.

## 8. 검증

| 단계 | 방법 | 통과 기준 |
|---|---|---|
| 정적 검사 | `data/tools/wmllint`(dry run)로 `data/samguk` 검사 | 오류 0건 |
| 스키마 검증 | 자동 대전 명령에 `--validate-core`를 붙여 실행 | 스키마 오류 0건 |
| 자동 대전 | `--nogui --multiplayer --core samguk --era samguk_era --scenario <맵> --controller 1:ai --controller 2:ai --exit-at-end` 를 두 맵에서, 세력 조합 양방향으로 | 정상 종료, 로그에 WML 오류·Lua 오류 없음 |
| 화면 확인 | 실제 실행 후 타이틀, 세력 선택, 전투 화면 스크린샷 | 우리 로고, 세력, 유닛 이름이 한국어로 보임 |

## 9. 위험과 대응

| 위험 | 대응 |
|---|---|
| vcpkg 의존성 빌드 실패 | 로그로 원인 확인, 실패하면 공식 1.18.8 실행 파일 + `--data-dir` |
| 기본 데이터 일부를 빼서 생기는 누락 참조 (도움말, Lua, 편집기가 기본 유닛을 참조) | 자동 대전과 실행 로그로 찾아내고, 해당 include를 추가하거나 참조를 제거 |
| 종족 변경(merfolk → baekje)으로 인한 특성 차이 | 의도된 변경으로 받아들임 |
| `[+game_config]` 병합으로 로고가 바뀌지 않음 | `data/game_config.cfg`를 `data/samguk/game_config.cfg`로 복사해 로고 경로를 바꾸고 그것을 include |

## 10. 산출물
- `samguk` 브랜치의 커밋들
- 이 설계서, 구현 계획서, `data/samguk/README.md`
- 검증 로그와 스크린샷
