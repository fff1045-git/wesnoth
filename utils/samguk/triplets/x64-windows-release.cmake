# x64-windows와 같되 릴리스 라이브러리만 빌드한다 (게임은 Release로만 빌드하므로 디버그 빌드는 시간 낭비).
set(VCPKG_TARGET_ARCHITECTURE x64)
set(VCPKG_CRT_LINKAGE dynamic)
set(VCPKG_LIBRARY_LINKAGE dynamic)
set(VCPKG_BUILD_TYPE release)
