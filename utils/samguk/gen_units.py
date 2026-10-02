#!/usr/bin/env python3
"""기본 Wesnoth 유닛을 복사해 삼국 유닛 .cfg를 만든다.

스탯, 공격, 애니메이션, 이미지 경로, 텍스트 도메인은 원본 그대로 두고
id, 이름, 종족, 승급 대상, 설명만 바꾼다. 다시 실행하면 data/samguk/units
아래 생성 파일을 덮어쓴다. 생성 뒤 손으로 고친 파일이 있다면 다시 돌리기 전에 확인할 것.

  python utils/samguk/gen_units.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "core" / "units"
OUT = ROOT / "data" / "samguk" / "units"

# (세력 디렉터리, id, 이름, 원본 파일(data/core/units 기준), 종족, 승급 대상, 설명)
UNITS = [
    # ---- 고구려 ----
    ("goguryeo", "gog_spearman", "창수", "humans/Loyalist_Spearman.cfg", "goguryeo", "gog_pikeman",
     "고구려 군대의 근간을 이루는 보병이다. 긴 창과 가죽 갑옷으로 무장하고 전열 맨 앞에서 기병의 돌격을 받아낸다."),
    ("goguryeo", "gog_pikeman", "장창수", "humans/Loyalist_Pikeman.cfg", "goguryeo", "gog_halberdier",
     "더 긴 창을 다루도록 훈련받은 창수다. 기병의 돌격을 정면으로 받아내는 데 특히 뛰어나다."),
    ("goguryeo", "gog_halberdier", "극수", "humans/Loyalist_Halberdier.cfg", "goguryeo", "null",
     "날이 달린 극으로 찌르고 베는 노련한 보병이다. 성문과 고갯길을 지키는 데 주로 배치된다."),
    ("goguryeo", "gog_bowman", "맥궁수", "humans/Loyalist_Bowman.cfg", "goguryeo", "gog_longbowman",
     "물소 뿔로 만든 짧고 강한 활, 맥궁을 쏘는 궁수다. 사냥으로 단련된 고구려 사람들은 어려서부터 활을 잡았다."),
    ("goguryeo", "gog_longbowman", "장궁수", "humans/Loyalist_Longbowman.cfg", "goguryeo", "gog_master_bowman",
     "맥궁을 오래 다뤄 먼 거리의 표적도 꿰뚫는 궁수다. 가까이 붙은 적에게는 칼을 뽑아 맞선다."),
    ("goguryeo", "gog_master_bowman", "신궁", "humans/Loyalist_Master_Bowman.cfg", "goguryeo", "null",
     "주몽의 이름을 떠올리게 할 만큼 활솜씨가 빼어난 궁수다. 그가 시위를 당기면 적의 장수부터 쓰러진다."),
    ("goguryeo", "gog_horseman", "개마무사", "humans/Horseman.cfg", "goguryeo", "gog_knight",
     "사람과 말 모두 비늘 갑옷을 두른 고구려의 중장기병이다. 긴 창을 앞세운 돌격은 적의 전열을 단번에 무너뜨리지만, 창끝을 세우고 맞서는 보병에게는 큰 피해를 입는다."),
    ("goguryeo", "gog_knight", "개마장", "humans/Horse_Knight.cfg", "goguryeo", "gog_grand_knight",
     "여러 차례 돌격에서 살아남아 개마무사들을 이끄는 기병 장교다. 창과 칼을 모두 능숙하게 다룬다."),
    ("goguryeo", "gog_grand_knight", "개마대장", "humans/Horse_Grand_Knight.cfg", "goguryeo", "null",
     "고구려 중장기병 전체를 지휘하는 장수다. 그의 깃발이 오르면 개마무사들이 일제히 땅을 울린다."),
    ("goguryeo", "gog_rider", "궁기병", "dunefolk/Rider.cfg", "goguryeo", "gog_horse_archer",
     "가볍게 무장하고 말을 달리는 기병이다. 넓은 들판을 빠르게 누비며 마을을 차지하고 적의 움직임을 살핀다."),
    ("goguryeo", "gog_horse_archer", "기마궁수", "dunefolk/Horse_Archer.cfg", "goguryeo", "gog_windbolt",
     "달리는 말 위에서 몸을 돌려 활을 쏘는 고구려 기마궁술의 달인이다. 무용총 수렵도에 그려진 사냥꾼들이 바로 이들이다."),
    ("goguryeo", "gog_windbolt", "질풍궁기", "dunefolk/Windbolt.cfg", "goguryeo", "null",
     "바람처럼 나타나 화살 비를 퍼붓고 사라지는 기마궁수의 정예다."),
    ("goguryeo", "gog_mage", "일관", "humans/Mage.cfg", "goguryeo", "gog_white_mage",
     "해와 별의 움직임을 살펴 나라의 길흉을 점치는 관리다. 하늘의 기운을 끌어내 적을 태우는 술법을 익혔지만 몸은 약하다."),
    ("goguryeo", "gog_white_mage", "백일관", "humans/Mage_White.cfg", "goguryeo", "gog_mage_of_light",
     "해의 신성한 빛을 다루는 경지에 이른 일관이다. 아군의 상처를 치료하고, 어둠에서 온 존재에게 특히 큰 피해를 준다."),
    ("goguryeo", "gog_mage_of_light", "태양사제", "humans/Mage_of_Light.cfg", "goguryeo", "null",
     "삼족오가 머무는 해를 섬기는 최고위 사제다. 그 주위는 밤에도 대낮처럼 밝다."),
    ("goguryeo", "gog_gryphon_rider", "삼족오 기수", "gryphons/Gryphon_Rider.cfg", "samjogo", "gog_gryphon_master",
     "해에 산다는 세 발 까마귀, 삼족오를 길들여 타는 기수다. 산과 강을 가리지 않고 날아가 적진을 정찰한다."),
    ("goguryeo", "gog_gryphon_master", "삼족오 장수", "gryphons/Gryphon_Master.cfg", "samjogo", "null",
     "삼족오와 오랜 세월을 함께해 하나처럼 움직이는 기수다. 날카로운 발톱으로 적의 후방을 휘젓는다."),
    ("goguryeo", "gog_lieutenant", "장군", "humans/Loyalist_Lieutenant.cfg", "goguryeo", "gog_general",
     "고구려군의 한 부대를 맡은 장수다. 직접 싸우는 실력도 있지만, 곁에 있는 병사들의 사기를 높이는 지휘력이 더 큰 힘이다."),
    ("goguryeo", "gog_general", "대장군", "humans/Loyalist_General.cfg", "goguryeo", "gog_grand_marshal",
     "여러 부대를 거느리고 전쟁을 이끄는 장수다. 수많은 전투를 거치며 전장의 흐름을 읽는 눈을 길렀다."),
    ("goguryeo", "gog_grand_marshal", "대모달", "humans/Loyalist_Grand_Marshal.cfg", "goguryeo", "null",
     "고구려 군사 조직의 꼭대기에 선 최고 지휘관이다. 그의 이름만으로도 적국의 성이 문을 연다는 말이 있다."),
    # ---- 백제 ----
    ("baekje", "bae_soldier", "백제 보병", "dunefolk/Soldier.cfg", "baekje", "bae_swordsman",
     "찰갑을 입고 창과 방패를 든 백제의 정규 보병이다. 단단한 방어로 전선을 지킨다."),
    ("baekje", "bae_swordsman", "검대", "dunefolk/Swordsman.cfg", "baekje", "bae_blademaster",
     "고리자루 큰칼, 환두대도를 휘두르는 백제의 정예 검사다. 무거운 갑옷을 입고도 빠르게 칼을 놀린다."),
    ("baekje", "bae_blademaster", "검대장", "dunefolk/Blademaster.cfg", "baekje", "null",
     "검대를 이끄는 노련한 검객이다. 한 번의 칼질로 여러 적을 베어 넘긴다."),
    ("baekje", "bae_skirmisher", "척후병", "dunefolk/Skirmisher.cfg", "baekje", "bae_strider",
     "가벼운 차림으로 적진 깊숙이 스며드는 척후병이다. 적의 진형 사이를 빠져나가 후방을 어지럽힌다."),
    ("baekje", "bae_strider", "유격병", "dunefolk/Strider.cfg", "baekje", "bae_harrier",
     "산길과 물가를 가리지 않고 움직이는 유격병이다. 적이 눈치채기 전에 길목을 끊어 놓는다."),
    ("baekje", "bae_harrier", "유격대장", "dunefolk/Harrier.cfg", "baekje", "null",
     "유격병들을 이끌고 적의 보급로를 끊는 데 이골이 난 장수다."),
    ("baekje", "bae_burner", "화공병", "dunefolk/Burner.cfg", "baekje", "bae_scorcher",
     "기름 먹인 횃불과 불화살로 적을 태우는 병사다. 숲과 마을에 숨은 적을 몰아내는 데 쓰인다."),
    ("baekje", "bae_scorcher", "화공대", "dunefolk/Scorcher.cfg", "baekje", "bae_firetrooper",
     "더 큰 불을 다룰 줄 아는 화공병이다. 백제 수군이 적의 배를 불태울 때 앞장선다."),
    ("baekje", "bae_firetrooper", "화공대장", "dunefolk/Firetrooper.cfg", "baekje", "null",
     "화공 부대 전체를 지휘하며 전장을 불바다로 만드는 장수다."),
    ("baekje", "bae_herbalist", "승병", "dunefolk/Herbalist.cfg", "baekje", "bae_apothecary",
     "부처의 가르침을 따르면서도 나라를 지키려 무기를 든 승려다. 약초와 기도로 다친 아군을 돌본다."),
    ("baekje", "bae_apothecary", "의승", "dunefolk/Apothecary.cfg", "baekje", "bae_luminary",
     "의술에 정통한 승려다. 상처를 치료할 뿐 아니라 독도 풀어낸다."),
    ("baekje", "bae_luminary", "대덕", "dunefolk/Luminary.cfg", "baekje", "null",
     "높은 덕을 쌓은 큰스님이다. 그 곁에 있으면 지친 병사들도 다시 일어선다."),
    ("baekje", "bae_merman_fighter", "수군", "merfolk/Fighter.cfg", "baekje", "bae_merman_warrior",
     "바다 건너 왜와 중국을 오가던 백제 수군의 병사다. 물 위와 물가에서 누구보다 잘 싸운다."),
    ("baekje", "bae_merman_warrior", "수군 무사", "merfolk/Warrior.cfg", "baekje", "bae_merman_triton",
     "수많은 해전을 치른 수군 무사다. 강과 바다를 자기 집처럼 누빈다."),
    ("baekje", "bae_merman_triton", "수군 장수", "merfolk/Triton.cfg", "baekje", "null",
     "백제 함대를 이끄는 수군 장수다. 물길을 훤히 아는 그를 강 위에서 이기기는 어렵다."),
    ("baekje", "bae_troll_whelp", "도깨비", "trolls/Whelp.cfg", "dokkaebi", "bae_troll",
     "밤이면 나타나 장난을 치던 도깨비들이 백제와 손을 잡았다. 맞아도 금세 상처가 아물고, 어두울수록 힘이 세진다."),
    ("baekje", "bae_troll", "큰도깨비", "trolls/Troll.cfg", "dokkaebi", "bae_troll_warrior",
     "방망이 하나로 바위도 깨뜨린다는 큰 도깨비다. 웬만한 상처는 하룻밤이면 다 낫는다."),
    ("baekje", "bae_troll_warrior", "도깨비 대장", "trolls/Warrior.cfg", "dokkaebi", "null",
     "도깨비들의 우두머리다. 금은보화보다 씨름 한 판을 더 좋아한다고 전해진다."),
    ("baekje", "bae_captain", "좌평", "dunefolk/Captain.cfg", "baekje", "bae_warmaster",
     "백제 최고 관직인 좌평은 전쟁이 나면 직접 군대를 이끈다. 곁에 선 병사들의 사기를 북돋는다."),
    ("baekje", "bae_warmaster", "상좌평", "dunefolk/Warmaster.cfg", "baekje", "null",
     "좌평들 가운데 으뜸인 상좌평이다. 나라의 군사와 정사를 함께 맡는다."),
]


def wml_string(text):
    return '_ "' + text.replace('"', '""') + '"'


def convert(src_text, uid, name, race, advances_to, description, src_rel):
    lines = src_text.splitlines()
    out = []
    counts = {"id": 0, "name": 0, "race": 0, "advances_to": 0, "description": 0}
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^    id=", line):
            out.append(f"    id={uid}")
            counts["id"] += 1
        elif re.match(r'^    name= *_ *"', line):
            out.append(f"    name= {wml_string(name)}")
            counts["name"] += 1
        elif re.match(r'^ +name= *_ *"female\^', line):
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f"{indent}name= {wml_string(name)}")
        elif re.match(r"^    race=", line):
            out.append(f"    race={race}")
            counts["race"] += 1
        elif re.match(r"^    advances_to=", line):
            out.append(f"    advances_to={advances_to}")
            counts["advances_to"] += 1
        elif re.match(r"^    description=", line):
            # 여러 줄 문자열: 따옴표 개수가 짝수가 될 때까지 다음 줄을 함께 버린다
            block = line
            while block.count('"') % 2 == 1:
                i += 1
                block += "\n" + lines[i]
            out.append(f"    description= {wml_string(description)}")
            counts["description"] += 1
        else:
            out.append(line)
        i += 1

    for key in ("id", "name", "race", "description"):
        if counts[key] != 1:
            sys.exit(f"{src_rel}: '{key}' 줄이 {counts[key]}개라 변환할 수 없다")
    if counts["advances_to"] != 1 and not (counts["advances_to"] == 0 and advances_to == "null"):
        sys.exit(f"{src_rel}: advances_to 줄이 {counts['advances_to']}개다")

    header = f"# 생성 파일: utils/samguk/gen_units.py가 data/core/units/{src_rel}에서 만들었다."
    if out and out[0].startswith("#textdomain"):
        out.insert(1, header)
    else:
        out.insert(0, header)
    return "\n".join(out) + "\n"


def main():
    for faction, uid, name, src_rel, race, advances_to, description in UNITS:
        src = SRC / src_rel
        text = convert(src.read_text(encoding="utf-8"), uid, name, race, advances_to,
                       description, src_rel)
        dest = OUT / faction / f"{uid}.cfg"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(UNITS)} unit files under {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
