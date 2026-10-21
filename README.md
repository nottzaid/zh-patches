# zh-patches

Binary patches for **Command & Conquer: Generals – Zero Hour**, Steam release (app 2732960).
They edit `Game.dat`, the real game executable (`Generals.exe` is only a launcher).

| Patch | What it fixes |
|---|---|
| `patches/zh_widescreen.py` | The Options menu only lists 4:3 resolutions. This lists every mode the display reports (still ≥ 800 wide, ≥ 24-bit), so 1920×1080 and other widescreen modes can be picked. |
| `patches/zh_jet_heal.py` | Jets guarding an area fly home to re-arm, but take off again as soon as their ammo is full, often still damaged. Now a parked jet waits until the airfield has fully healed it, then resumes its order (guard, hunt…) as before. |

Both target one build only: the Feb 20 2025 Steam `Game.dat` (PE timestamp `0x67b6d753`).
They refuse to touch any other file, and each can be applied or reverted on its own, in either order.

## Use

```sh
G="$HOME/.steam/steam/steamapps/common/Command & Conquer Generals - Zero Hour"   # your install
cp "$G/Game.dat" "$G/Game.dat.orig"          # keep a pristine copy

python3 patches/zh_widescreen.py "$G/Game.dat" apply
python3 patches/zh_jet_heal.py   "$G/Game.dat" apply

python3 patches/zh_jet_heal.py   "$G/Game.dat" check    # original / patched / unknown
python3 patches/zh_jet_heal.py   "$G/Game.dat" revert
```

After the widescreen patch, choose the resolution in Options → Resolution.
A Steam "verify integrity of game files" restores the stock `Game.dat`; just apply again.

**Multiplayer:** the jet patch changes game logic, so online games against unpatched players
will go out of sync. Skirmish, campaign and LAN games where everyone is patched are fine.
The widescreen patch is display-only.

## How they work

### Widescreen
`W3DDisplay::getDisplayModeCount` (`0x73c050`) and `getDisplayModeDescription` (`0x73c0d0`) keep a
mode only if `1.332 < width/height < 1.334`. The patch NOPs the two conditional jumps of that test
in each function (8 bytes). The FPU stack stays balanced because the following `fcomp` still pops
the ratio.

### Jet heal-wait
In `JetAIUpdate::update`, once `RELOAD_AMMO` ends a jet with a pending command runs it at once:

```cpp
else if (getFlag(HAS_PENDING_COMMAND) && getStateMachine()->getCurrentStateID() != RELOAD_AMMO)
```

Helicopters already wait for `getHealth() == getMaxHealth()`; jets never did. The patch adds that
condition for a jet that is parked (no `ALLOW_AIR_LOCO`) at a live airfield. The 8 bytes at
`0x6540b4` become a jump to a short check placed in the unused tail of `.text` (`0x942f10`, with the
section's VirtualSize raised to cover it). While it waits, the airfield keeps healing it (10 HP/s on
every stock airfield) and the order stays queued.

- A new order you give a parked jet still makes it take off immediately.
- An order given while the jet is landing or taxiing is queued, so it also waits for the heal;
  give it again once the jet is parked to force it.
- No airfield (destroyed or sold) means no wait.

Source for the check: `patches/asm/jet_heal_wait.s`. `patches/asm/build.sh` reassembles it with
mingw-w64 and confirms it matches the bytes the patcher writes.

Reference: EA's GPL source release, [electronicarts/CnC_Generals_Zero_Hour](https://github.com/electronicarts/CnC_Generals_Zero_Hour),
`GeneralsMD/Code/GameEngine/Source/GameLogic/Object/Update/AIUpdate/JetAIUpdate.cpp`.

## Other tools

- `tools/bigx.py archive.big outdir [filter]` extracts `.big` archives (e.g. `INIZH.big` for the object INIs).
- `dev/` holds helpers for testing on Linux:
  - `zh_launch.sh` starts the game the way Steam does (Sniper runtime + Proton + the game's prefix) without the Steam UI.
  - `zh_wine.sh` runs a Windows program inside the running game's wineserver.
  - `wclick.c` (`make -C dev`) lists the game's windows and sends mouse clicks to one without focusing it.
  - `env.sh` holds the paths they use; override them in the environment.
