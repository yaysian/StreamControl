#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
root="$PWD"
[[ "$(uname -s)" == Darwin ]] || { echo 'Run this script on macOS.' >&2; exit 1; }
arch="${BUILD_ARCH:-$(uname -m)}"
[[ "$arch" == "$(uname -m)" ]] || { echo 'Use a native runner for the target architecture.' >&2; exit 1; }
case "$arch" in arm64|x86_64) ;; *) echo 'Unsupported architecture' >&2; exit 1;; esac
export PATH="$(brew --prefix qt@5)/bin:$PATH"
qmake -v
[[ "$(qmake -query QT_VERSION)" == 5.* ]] || { echo 'Qt 5 is required.' >&2; exit 1; }
# Confirm the Qt modules the project needs are installed (Qt Script is no longer used).
qt_libs="$(qmake -query QT_INSTALL_LIBS)"
for module in QtCore QtGui QtWidgets QtXml QtNetwork QtTest; do
  [[ -d "$qt_libs/$module.framework" ]] || { echo "Missing Qt module: $module" >&2; exit 1; }
done
echo "Qt modules present in $qt_libs"

mkdir -p build build-tests dist
cd build
qmake "$root/StreamControl/StreamControl.pro" CONFIG+=release "QMAKE_APPLE_DEVICE_ARCHS=$arch"
make -j"$(sysctl -n hw.ncpu)"

cd "$root/build-tests"
qmake "$root/tests/macos-tests.pro" CONFIG+=release "QMAKE_APPLE_DEVICE_ARCHS=$arch"
make -j"$(sysctl -n hw.ncpu)"
QT_QPA_PLATFORM=offscreen ./streamcontrol-tests -o results.xml,junitxml

cd "$root/build"
app=StreamControl.app
macdeployqt "$app" -always-overwrite
# StreamControl is a desktop app; the on-screen keyboard only adds Qt Quick plugins.
ls -l "$app/Contents/PlugIns/platforminputcontexts" || true
rm -rf "$app/Contents/PlugIns/virtualkeyboard"   "$app/Contents/PlugIns/platforminputcontexts/libqtvirtualkeyboardplugin.dylib"
# macdeployqt skips some transitive @rpath dylibs and external symlinks/rpaths.
python3 "$root/scripts/bundle-missing-libs.py" "$app" "$(brew --prefix)/lib" "$(brew --prefix qt@5)/lib"
mkdir -p "$app/Contents/Resources/licenses"
cp "$root/LICENSE" "$app/Contents/Resources/licenses/StreamControl.txt"
cp "$root/MACOS.md" "$app/Contents/Resources/BUILD-NOTES.md"
# Include the Qt package's installed license notices.
qt_prefix="$(brew --prefix qt@5)"
find "$qt_prefix/" -maxdepth 1 -type f \( -name 'LICENSE*' -o -name 'LGPL*' \) \
  -exec cp {} "$app/Contents/Resources/licenses/" \;

# Ad-hoc sign nested code after all deployment changes, then sign the bundle.
python3 "$root/scripts/sign-macos-bundle.py" "$app"
codesign --verify --deep --strict "$app"
python3 "$root/scripts/verify-macos-bundle.py" "$app" "$arch"

artifact="${ARTIFACT_NAME:-StreamControl-$arch}"
ditto -c -k --sequesterRsrc --keepParent "$app" "$root/dist/$artifact.zip"
echo "Created dist/$artifact.zip"
