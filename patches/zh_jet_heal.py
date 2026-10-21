#!/usr/bin/env python3
"""Jets wait to be fully healed before resuming a pending order (Steam Game.dat, build Feb 20 2025).

JetAIUpdate::update resumes a jet's pending command (e.g. the guard order it left to re-arm) as soon
as RELOAD_AMMO finishes, ignoring health. This adds one condition to that branch: while parked
(no ALLOW_AIR_LOCO) at a live airfield, keep waiting until getHealth() == getMaxHealth(), the same
test the helicopter branch uses. The airfield keeps healing it meanwhile; the order then runs as
before. A command the player gives to a parked jet still goes straight through aiDoCommand.

The check lives in the 251 zero bytes after .text's VirtualSize; VirtualSize is raised to cover them.
Usage: zh_jet_heal.py Game.dat {check|apply|revert}
The check's source is asm/jet_heal_wait.s; asm/build.sh reassembles it and compares with CAVE_CODE.
"""
import struct, sys

BUILD = 0x67b6d753                               # PE TimeDateStamp of the Steam build this was made for

HOOK = 0x6540b4 - 0x400000                       # file offset == VA - image base for this build
HOOK_ORIG = bytes.fromhex('6a026a008d4c2460')    # push 2; push 0; lea ecx,[esp+0x60]
HOOK_NEW = bytes.fromhex('e957ee2e00909090')     # jmp 0x942f10; nop x3
CAVE = 0x942f10 - 0x400000
CAVE_CODE = bytes.fromhex(
    'f686080300000275' '2a85ed74268b8b74' '01000051518b01ff' '500cd91c248b4c24'
    '048b01ff5010d81c' '24dfe083c408f6c4' '40740d6a026a008d' '4c2460e96c11d1ff'
    'e91012d1ff')
VSIZE_ORIG, VSIZE_NEW = 0x541f05, 0x542000


def text_vsize_off(d):
    pe = struct.unpack_from('<I', d, 0x3c)[0]
    sh = pe + 24 + struct.unpack_from('<H', d, pe + 20)[0]
    assert d[sh:sh + 8] == b'.text\0\0\0'
    return sh + 8


def state(d):
    if struct.unpack_from('<I', d, struct.unpack_from('<I', d, 0x3c)[0] + 8)[0] != BUILD:
        return 'unknown'
    v = text_vsize_off(d)
    cur = (d[HOOK:HOOK + 8], d[CAVE:CAVE + len(CAVE_CODE)], struct.unpack_from('<I', d, v)[0])
    if cur == (HOOK_ORIG, bytes(len(CAVE_CODE)), VSIZE_ORIG):
        return 'original'
    if cur == (HOOK_NEW, CAVE_CODE, VSIZE_NEW):
        return 'patched'
    return 'unknown'


def write(d, hook, cave, vsize):
    d[HOOK:HOOK + 8] = hook
    d[CAVE:CAVE + len(CAVE_CODE)] = cave
    struct.pack_into('<I', d, text_vsize_off(d), vsize)


if __name__ == '__main__':
    path, action = sys.argv[1], sys.argv[2]
    d = bytearray(open(path, 'rb').read())
    s = state(d)
    print(path, s)
    if action == 'check':
        sys.exit(0 if s != 'unknown' else 1)
    if s == 'unknown':
        sys.exit('bytes do not match this build; refusing to touch it')
    if action == 'apply' and s == 'original':
        write(d, HOOK_NEW, CAVE_CODE, VSIZE_NEW)
    elif action == 'revert' and s == 'patched':
        write(d, HOOK_ORIG, bytes(len(CAVE_CODE)), VSIZE_ORIG)
    else:
        sys.exit(0)
    open(path, 'wb').write(d)
    print(path, state(d))
