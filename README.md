# Zero Hour patches

For Steam's **Command & Conquer: Generals – Zero Hour**, `Game.dat` build
Feb 20, 2025 (`0x67b6d753`). Other builds are refused.

- `zh_widescreen.py`: adds widescreen resolutions to Options → Resolution.
- `zh_jet_heal.py`: parked jets finish healing before resuming queued orders.

```sh
G="$HOME/.steam/steam/steamapps/common/Command & Conquer Generals - Zero Hour"
cp -n "$G/Game.dat" "$G/Game.dat.orig"
python3 patches/zh_widescreen.py "$G/Game.dat" apply
python3 patches/zh_jet_heal.py "$G/Game.dat" apply
```

Change `G` for your installation. Either script also accepts `check` or `revert`;
patches work independently. Steam's file verification removes them.

Multiplayer players must all use the same jet patch or games desync.
A fresh order to a parked jet still makes it take off immediately.

[Patch source](patches/asm/jet_heal_wait.s) ·
[Reassemble and verify](patches/asm/build.sh)
