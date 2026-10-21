#!/bin/bash
# Start Zero Hour the way Steam does (Sniper runtime + the game's Proton + its prefix), without the
# Steam client UI. Usage: zh_launch.sh <proton verb> <exe> [args], e.g.
#   zh_launch.sh waitforexitandrun "$ZH_GAME/Generals.exe"
. "$(dirname "$0")/env.sh"
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$ZH_STEAM"
export STEAM_COMPAT_DATA_PATH="$ZH_COMPAT"
export STEAM_COMPAT_INSTALL_PATH="$ZH_GAME"
export STEAM_COMPAT_LIBRARY_PATHS="$(dirname "$ZH_COMPAT" | xargs dirname):$ZH_STEAM/steamapps"
export STEAM_COMPAT_TOOL_PATHS="$ZH_PROTON:$ZH_SNIPER"
export STEAM_COMPAT_APP_ID=2732960 SteamAppId=2732960 SteamGameId=2732960
verb=$1; shift
cd "$ZH_GAME" || exit 1
exec "$ZH_SNIPER/_v2-entry-point" --verb="$verb" -- "$ZH_PROTON/proton" "$verb" "$@"
