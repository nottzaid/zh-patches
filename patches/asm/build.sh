#!/bin/bash
# Reassemble jet_heal_wait.s at its address in Game.dat and compare with CAVE_CODE in zh_jet_heal.py.
# Needs a mingw-w64 i686 toolchain.
set -e
here=$(cd "$(dirname "$0")" && pwd)
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
i686-w64-mingw32-as "$here/jet_heal_wait.s" -o "$tmp/w.o"
i686-w64-mingw32-ld -m i386pe --image-base=0 -Ttext=0x942f10 -e _start "$tmp/w.o" -o "$tmp/w.exe"
i686-w64-mingw32-objcopy -O binary -j .text "$tmp/w.exe" "$tmp/w.bin"
python3 -I - "$tmp/w.bin" "$here/../zh_jet_heal.py" <<'PY'
import sys
built = open(sys.argv[1], 'rb').read()
ns = {}
exec(open(sys.argv[2]).read().split("if __name__")[0], ns)
code = ns['CAVE_CODE']
print('match' if built[:len(code)] == code else 'MISMATCH\n' + built[:len(code)].hex())
sys.exit(built[:len(code)] != code)
PY
