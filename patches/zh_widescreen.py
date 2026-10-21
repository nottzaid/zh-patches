#!/usr/bin/env python3
"""Remove Zero Hour's 4:3-only filter from the resolution list (Steam Game.dat, build Feb 20 2025).

W3DDisplay::getDisplayModeCount (0x73c050) and getDisplayModeDescription (0x73c0d0) keep a mode
only if 1.332 < width/height < 1.334. NOPing the two conditional jumps of that test in each
function accepts every aspect ratio; the >=24-bit and width>=800 checks stay. The FPU stack stays
balanced: the fcomp that follows still pops the ratio.
Usage: zh_widescreen.py Game.dat {check|apply|revert}
"""
import struct, sys

BUILD = 0x67b6d753  # PE TimeDateStamp of the Steam build this was made for
BASE = 0x400000     # no .reloc, every section has VA - file offset == 0x400000
PATCHES = [  # (VA, original, patched)
    (0x73c0a6, b'\x75\x10', b'\x90\x90'),  # count: jne reject  (ratio <= 1.332)
    (0x73c0b3, b'\x74\x05', b'\x90\x90'),  # count: je  skip    (ratio >= 1.334)
    (0x73c133, b'\x75\x16', b'\x90\x90'),  # describe: jne reject
    (0x73c140, b'\x74\x0b', b'\x90\x90'),  # describe: je  skip
]


def build(d):
    return struct.unpack_from('<I', d, struct.unpack_from('<I', d, 0x3c)[0] + 8)[0]


def state(d):
    if build(d) != BUILD:
        return 'unknown'
    if all(d[va - BASE:va - BASE + 2] == o for va, o, _ in PATCHES):
        return 'original'
    if all(d[va - BASE:va - BASE + 2] == p for va, _, p in PATCHES):
        return 'patched'
    return 'unknown'


if __name__ == '__main__':
    path, action = sys.argv[1], sys.argv[2]
    d = bytearray(open(path, 'rb').read())
    s = state(d)
    print(path, s)
    if action == 'check':
        sys.exit(0 if s != 'unknown' else 1)
    if s == 'unknown':
        sys.exit('bytes do not match this build; refusing to touch it')
    if (action, s) not in (('apply', 'original'), ('revert', 'patched')):
        sys.exit(0)
    for va, o, p in PATCHES:
        d[va - BASE:va - BASE + 2] = p if action == 'apply' else o
    open(path, 'wb').write(d)
    print(path, state(d))
