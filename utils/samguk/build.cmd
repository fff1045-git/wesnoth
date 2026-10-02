@echo off
rem 「삼국: 한강의 패권」 엔진 빌드 (MSVC 2022 + vcpkg + Ninja, Release).
rem PowerShell 또는 cmd에서 실행한다. 첫 실행은 vcpkg 의존성 빌드로 1시간 이상 걸린다.
setlocal
set "VSROOT=C:\Program Files\Microsoft Visual Studio\2022\Community"
call "%VSROOT%\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
set "VCPKG_ROOT=%VSROOT%\VC\vcpkg"
set "CMAKE=%VSROOT%\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe"
set "NINJA=%VSROOT%\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe"
cd /d "%~dp0..\.."

rem vcpkg 캐시를 %LOCALAPPDATA% 밖에 둔다. MSIX 앱(Claude 데스크톱 등)에서 실행하면
rem %LOCALAPPDATA%가 가상화되어, msys2가 보는 실제 경로와 vcpkg가 만든 PATH가 어긋나고
rem ICU 빌드가 install-sh 경로 오류로 실패한다.
set "VCPKG_CACHE=%CD%\build\vcpkg-cache"
set "VCPKG_DOWNLOADS=%VCPKG_CACHE%\downloads"
set "VCPKG_DEFAULT_BINARY_CACHE=%VCPKG_CACHE%\archives"
set "X_VCPKG_REGISTRIES_CACHE=%VCPKG_CACHE%\registries"
if not exist "%VCPKG_DOWNLOADS%" mkdir "%VCPKG_DOWNLOADS%"
if not exist "%VCPKG_DEFAULT_BINARY_CACHE%" mkdir "%VCPKG_DEFAULT_BINARY_CACHE%"
if not exist "%X_VCPKG_REGISTRIES_CACHE%" mkdir "%X_VCPKG_REGISTRIES_CACHE%"

echo === configure ===
"%CMAKE%" -S . -B build -G Ninja ^
  -DCMAKE_MAKE_PROGRAM="%NINJA%" ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_TOOLCHAIN_FILE="%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake" ^
  -DVCPKG_OVERLAY_TRIPLETS="%CD%\utils\samguk\triplets" ^
  -DVCPKG_TARGET_TRIPLET=x64-windows-release ^
  -DENABLE_SERVER=OFF -DENABLE_CAMPAIGN_SERVER=OFF -DENABLE_TESTS=OFF -DENABLE_NLS=OFF || exit /b 2

echo === build ===
"%CMAKE%" --build build --target wesnoth || exit /b 3
echo === BUILD OK ===
