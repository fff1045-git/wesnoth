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
- 대안: 빌드가 막히면 공식 1.18.8 실행 파일에 `--data-dir`로 이 저장소를 지정해 실행한다.

### 3.2 커스텀 코어
엔진은 `data/cores.cfg`의 `[core]` 항목을 읽고, 선택된 코어의 `path`가 가리키는 WML 파일 하나를 데이터 트리의 루트로 로드한다(`src/game_config_manager.cpp`). 기본 코어는 `path="/"`, 즉 `data/_main.cfg`이다.

`data/cores.cfg`에 아래 항목을 추가한다.

```
[core]
    id=samguk
    name= _ "삼국: 한강의 패권"
    path="data/samguk"
[/core]
```

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
  images/misc/logo-samguk.png
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

뺀 것: `core/units.cfg`(우리 `units.cfg`로 대체), `multiplayer/`(우리 `multiplayer/`로 대체), `campaigns/`.

로고는 `game_config.cfg`를 include한 뒤 `data/samguk/_main.cfg`에서 `[game_config]`의 `game_logo` 값을 우리 이미지로 덮어쓴다. 덮어쓰기가 동작하지 않으면 9장의 대안(`[binary_path]` 순서)으로 바꾼다.

### 3.4 유닛 제작 방식
원본 유닛 `.cfg`를 복사한 뒤 다음만 바꾼다.

- `id`, `name`, `description`, `race`, `advances_to`
- 텍스트 도메인: `#textdomain wesnoth-samguk`

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

### 4.2 백제 (중립 정규군과 밤에 강한 도깨비, 수군·불교·화공)

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
- AI 징집 패턴: `fighter,fighter,archer,healer,mixed fighter,scout`

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
| 창 제목 | `src/game_config.cpp`의 `_("The Battle for Wesnoth")`를 게임명으로 바꾼다 (유일한 C++ 수정) |
| 로고 | 게임명 텍스트 로고 PNG를 Python(Pillow)으로 만든다. 한글 폰트는 저장소의 `fonts/DroidSansFallbackFull.ttf` |
| 타이틀 배경 | 기존 그림 유지 |
| 실행기 | 저장소 루트의 `samguk.cmd`: `build\wesnoth.exe --data-dir <저장소> --core samguk --language ko_KR` |

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
| `[game_config]` 로고 덮어쓰기 불가 | 이미지 경로 우선순위(`[binary_path]` 순서) 방식으로 전환 |

## 10. 산출물
- `samguk` 브랜치의 커밋들
- 이 설계서, 구현 계획서, `data/samguk/README.md`
- 검증 로그와 스크린샷
