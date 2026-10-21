#!/usr/bin/env python3
"""Extract files from a C&C Generals .big archive. Usage: bigx.py archive.big outdir [substring]"""
import os, struct, sys

def entries(d):
    assert d[:4] in (b'BIGF', b'BIG4'), d[:4]
    n = struct.unpack_from('>I', d, 8)[0]
    p = 16
    for _ in range(n):
        off, size = struct.unpack_from('>II', d, p)
        end = d.index(b'\0', p + 8)
        yield d[p + 8:end].decode('latin-1'), off, size
        p = end + 1

if __name__ == '__main__':
    d = open(sys.argv[1], 'rb').read()
    want = sys.argv[3].lower() if len(sys.argv) > 3 else ''
    for name, off, size in entries(d):
        if want not in name.lower():
            continue
        out = os.path.join(sys.argv[2], *name.replace('\\', '/').split('/'))
        assert os.path.realpath(out).startswith(os.path.realpath(sys.argv[2]))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'wb').write(d[off:off + size])
