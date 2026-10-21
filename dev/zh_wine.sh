#!/bin/bash
# Run a Windows program inside the running game's wineserver (same Proton build, same prefix),
# e.g. zh_wine.sh wclick.exe list
. "$(dirname "$0")/env.sh"
pfx="$ZH_COMPAT/pfx"
sock=/tmp/.wine-$(id -u)/server-$(printf '%x-%x' $(stat -c '%d %i' "$pfx"))/socket
[ -S "$sock" ] || { echo "game's wineserver not running"; exit 1; }
export WINEPREFIX="$pfx/" WINEFSYNC=1 WINEESYNC=1 WINEDEBUG=-all
export WINEDLLPATH="$ZH_PROTON/files/lib/vkd3d:$ZH_PROTON/files/lib/wine" WINELOADER="$ZH_PROTON/files/bin/wine"
exec timeout 20 "$ZH_PROTON/files/bin/wine" "$@"
