#!/usr/bin/env bash
# 공식 한국어 번역(po/*/ko.po)을 엔진이 읽는 위치로 컴파일한다.
# 빌드에서 ENABLE_NLS=OFF로 번역 빌드를 끄기 때문에 따로 돌린다. Git Bash에서 실행.
set -euo pipefail
cd "$(dirname "$0")/../.."
out=translations/ko/LC_MESSAGES
mkdir -p "$out"
count=0
for po in po/*/ko.po; do
  domain=$(basename "$(dirname "$po")")
  msgfmt -o "$out/$domain.mo" "$po"
  count=$((count + 1))
done
echo "compiled $count domains into $out"
