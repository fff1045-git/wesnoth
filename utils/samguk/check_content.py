#!/usr/bin/env python3
"""삼국 코어 정적 검사. 엔진 없이 data/samguk의 일관성을 확인한다.

  python utils/samguk/check_content.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CORE = DATA / "samguk"
HANGUL = re.compile(r"[가-힣]")
EXPECTED_UNITS = 40
EXPECTED_RACES = {"goguryeo", "baekje", "dokkaebi", "samjogo"}
CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


def read(path):
    return path.read_text(encoding="utf-8")


def unit_files():
    return sorted((CORE / "units").glob("*/*.cfg"))


def unit_ids():
    return {p.stem for p in unit_files()}


def race_ids():
    path = CORE / "units.cfg"
    if not path.exists():
        return set()
    return set(re.findall(r"\[race\]\s*\n\s*id=(\w+)", read(path)))


def top_level(text, key):
    """[unit_type] 바로 아래(들여쓰기 4칸) 키의 값 목록."""
    return re.findall(rf"^    {key}=(.*)$", text, re.M)


@check
def races_defined():
    found = race_ids()
    if found != EXPECTED_RACES:
        return [f"종족 정의가 다르다: {sorted(found)} (기대값 {sorted(EXPECTED_RACES)})"]
    return []


@check
def units_exist():
    files = unit_files()
    if len(files) != EXPECTED_UNITS:
        return [f"유닛 파일이 {len(files)}개다 (기대값 {EXPECTED_UNITS})"]
    return []


@check
def units_are_consistent():
    problems = []
    ids = unit_ids()
    races = race_ids()
    for path in unit_files():
        text = read(path)
        rel = path.relative_to(ROOT).as_posix()
        if text.count("[unit_type]") != 1:
            problems.append(f"{rel}: [unit_type]가 1개가 아니다")
        if top_level(text, "id") != [path.stem]:
            problems.append(f"{rel}: id가 파일 이름과 다르다: {top_level(text, 'id')}")
        names = top_level(text, "name")
        if len(names) != 1 or not HANGUL.search(names[0]):
            problems.append(f"{rel}: 이름이 한국어가 아니다: {names}")
        race = top_level(text, "race")
        if len(race) != 1 or race[0] not in races:
            problems.append(f"{rel}: 알 수 없는 종족 {race}")
        for value in top_level(text, "advances_to"):
            for target in (v.strip() for v in value.split(",")):
                if target != "null" and target not in ids:
                    problems.append(f"{rel}: 없는 승급 대상 {target}")
        desc = top_level(text, "description")
        if len(desc) != 1 or not HANGUL.search(desc[0]):
            problems.append(f"{rel}: 설명이 한 줄짜리 한국어가 아니다")
        if "female^" in text:
            problems.append(f"{rel}: 원본 여성형 이름이 남아 있다")
        if not text.startswith("#textdomain wesnoth-units"):
            problems.append(f"{rel}: 텍스트 도메인이 wesnoth-units가 아니다")
    return problems


def faction_files():
    return sorted((CORE / "multiplayer" / "factions").glob("*.cfg"))


def scenario_files():
    return sorted((CORE / "multiplayer" / "scenarios").glob("*.cfg"))


@check
def factions_reference_known_units():
    problems = []
    ids = unit_ids()
    files = faction_files()
    if {p.stem for p in files} != {"goguryeo", "baekje"}:
        problems.append(f"세력 파일이 다르다: {[p.name for p in files]}")
    for path in files:
        text = read(path)
        for key in ("recruit", "leader", "random_leader"):
            for value in re.findall(rf"^    {key}=(.*)$", text, re.M):
                for uid in (v.strip() for v in value.split(",")):
                    if uid not in ids:
                        problems.append(f"{path.relative_to(ROOT).as_posix()}: {key}에 없는 유닛 {uid}")
    return problems


@check
def era_includes_all_factions():
    era = CORE / "multiplayer" / "era.cfg"
    if not era.exists():
        return ["data/samguk/multiplayer/era.cfg가 없다"]
    text = read(era)
    return [f"era.cfg가 {p.name}를 include하지 않는다"
            for p in faction_files()
            if f"{{samguk/multiplayer/factions/{p.name}}}" not in text]


@check
def scenario_maps_exist():
    files = scenario_files()
    if not files:
        return ["시나리오가 없다"]
    problems = []
    for path in files:
        for map_file in re.findall(r"^    map_file=(.*)$", read(path), re.M):
            if not (DATA / map_file.strip()).exists():
                problems.append(f"{path.relative_to(ROOT).as_posix()}: 맵 파일이 없다 {map_file}")
    return problems


def main():
    failed = 0
    for fn in CHECKS:
        problems = fn()
        print(f"[{'PASS' if not problems else 'FAIL'}] {fn.__name__}")
        for p in problems[:20]:
            print("    " + p)
        failed += bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
