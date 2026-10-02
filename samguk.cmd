@echo off
rem 「삼국: 한강의 패권」 실행기. 먼저 utils\samguk\build.cmd로 빌드해야 한다.
rem 사용자 데이터(설정, 저장 파일)는 문서\My Games\Samguk에 따로 둔다.
if not exist "%~dp0build\wesnoth.exe" (
  echo build\wesnoth.exe가 없습니다. utils\samguk\build.cmd로 먼저 빌드하세요.
  pause
  exit /b 1
)
start "" "%~dp0build\wesnoth.exe" --data-dir "%~dp0." --userdata-dir Samguk --core samguk --language ko_KR %*
