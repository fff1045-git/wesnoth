#!/usr/bin/env python3
"""삼국 코어 자동 대전 스모크 테스트.

화면 없이(--nogui) AI끼리 대전시키고, 종료 코드와 로그의 error 줄을 검사한다.

  python utils/samguk/smoke_test.py
      삼국 맵 2개 x 세력 배치 2가지 = 4판
  python utils/samguk/smoke_test.py --core default --era era_default \
      --scenario multiplayer_Hamlets --sides Loyalists Rebels
      기본 코어 기준선 1판
"""
import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXE = ROOT / "build" / "wesnoth.exe"
USERDATA = ROOT / "build" / "smoke-userdata"
LOG_DIR = ROOT / "build" / "smoke-logs"

SCENARIOS = ["samguk_2p_gwanmiseong", "samguk_2p_hangang"]
MATCHUPS = [("Goguryeo", "Baekje"), ("Baekje", "Goguryeo")]

# 로그 줄 예: "20261002 14:22:11 error config: ..." (타임스탬프는 없을 수도 있다)
LOG_LINE = re.compile(r"^(?:\d{8} \d{2}:\d{2}:\d{2}(?:\.\d+)? )?(error|warning) [\w/.-]+:")

# 기본 코어 기준선에서도 나오는 엔진 쪽 error 줄의 정규식. 기준선 실행에서 확인된 것만 넣는다.
BASELINE_ALLOW = [
    # 기본 코어 기준선(2026-10-02)에서도 발생: --validate-core가 core/help.cfg의 GPL 전문 topic을 t_string으로 못 읽음
    r"error validation: Invalid value '\s*GNU GENERAL PUBLIC LICENSE",
    # 기본 코어 기준선(2026-10-02)에서도 발생: core/terrain.cfg의 editor_name 값을 t_string으로 못 읽음
    r"error validation: Invalid value 'Reinforced Earthy Cave Wall' in key 'editor_name='",
]

# 엔진이 접두사 없이 한 줄만 남기고 exit 0으로 조용히 끝내는 실패 (multiplayer.cpp의 PLAIN_LOG).
# era/시나리오 ID 오타 같은 경우라 대전이 실제로 돌지 않았는데도 PASS가 되므로 error로 센다.
SILENT_FAILURE = re.compile(r"^Could not find (?:era|\[multiplayer\]) ")


def run_battle(exe, core, era, scenario, side1, side2, turns, validate):
    if USERDATA.exists():
        shutil.rmtree(USERDATA)
    cmd = [
        str(exe), "--data-dir", str(ROOT), "--userdata-dir", str(USERDATA),
        "--core", core, "--nogui", "--nosound", "--nobanner", "--log-to-file",
        "--multiplayer", "--era", era, "--scenario", scenario,
        "--side", f"1:{side1}", "--side", f"2:{side2}",
        "--controller", "1:ai", "--controller", "2:ai",
        "--turns", str(turns), "--exit-at-end",
    ]
    if validate:
        cmd.append("--validate-core")
    started = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=1800)
    text = proc.stdout + proc.stderr
    for log in sorted(USERDATA.rglob("*.log")):
        text += log.read_text(encoding="utf-8", errors="replace")
    errors, warnings = [], []
    for line in text.splitlines():
        if SILENT_FAILURE.match(line):
            errors.append(line)
            continue
        m = LOG_LINE.match(line)
        if not m:
            continue
        if m.group(1) == "warning":
            warnings.append(line)
        elif not any(re.search(p, line) for p in BASELINE_ALLOW):
            errors.append(line)
    return proc.returncode, errors, warnings, time.time() - started, text


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    ap.add_argument("--core", default="samguk")
    ap.add_argument("--era", default="samguk_era")
    ap.add_argument("--scenario", action="append",
                    help="여러 번 줄 수 있다. 없으면 삼국 맵 전부")
    ap.add_argument("--sides", nargs=2, metavar=("SIDE1", "SIDE2"),
                    help="없으면 고구려/백제 양방향")
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--validate", action="store_true",
                    help="--validate-core로 스키마 검증도 한다")
    args = ap.parse_args()
    if not args.exe.exists():
        sys.exit(f"실행 파일이 없습니다: {args.exe} (utils/samguk/build.cmd로 먼저 빌드)")

    scenarios = args.scenario or SCENARIOS
    matchups = [tuple(args.sides)] if args.sides else MATCHUPS
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    failed = 0
    for scenario in scenarios:
        for side1, side2 in matchups:
            code, errors, warnings, secs, text = run_battle(
                args.exe, args.core, args.era, scenario, side1, side2,
                args.turns, args.validate)
            ok = code == 0 and not errors
            print(f"[{'PASS' if ok else 'FAIL'}] {scenario} {side1} vs {side2}: "
                  f"exit={code} errors={len(errors)} warnings={len(warnings)} {secs:.0f}s")
            for line in errors[:20]:
                print("    " + line)
            if not ok:
                failed += 1
                (LOG_DIR / f"{scenario}-{side1}-{side2}.log").write_text(text, encoding="utf-8")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
