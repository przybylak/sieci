#!/usr/bin/env python3
"""pecmp.py A.dll B.dll: say whether two PE32+ images differ only by their image base.
Checks: every differing byte is the header's ImageBase, the header's CheckSum, or an
8-byte DIR64 relocation target whose value differs by exactly (baseA - baseB)."""
import struct, sys
def pe(path):
    d = open(path, 'rb').read()
    o = struct.unpack_from('<I', d, 0x3c)[0]
    assert d[o:o+4] == b'PE\0\0'
    nsec = struct.unpack_from('<H', d, o+6)[0]
    optsz = struct.unpack_from('<H', d, o+20)[0]
    opt = o + 24
    assert struct.unpack_from('<H', d, opt)[0] == 0x20b
    base = struct.unpack_from('<Q', d, opt+24)[0]
    csum_off = opt + 64
    ts = struct.unpack_from('<I', d, o+8)[0]
    ndir = struct.unpack_from('<I', d, opt+108)[0]
    dirs = [struct.unpack_from('<II', d, opt+112+8*i) for i in range(ndir)]
    secs = []
    for i in range(nsec):
        s = opt + optsz + 40*i
        name = d[s:s+8].rstrip(b'\0').decode()
        vsz, va, rsz, raw = struct.unpack_from('<IIII', d, s+8)
        secs.append((name, va, vsz, raw, rsz))
    def off(rva):
        for n, va, vsz, raw, rsz in secs:
            if va <= rva < va + max(vsz, rsz):
                return raw + rva - va
        return None
    rel = set()
    rva, size = dirs[5]
    p = off(rva); end = p + size
    while p < end:
        page, bsz = struct.unpack_from('<II', d, p)
        if bsz == 0: break
        for i in range((bsz - 8)//2):
            e = struct.unpack_from('<H', d, p+8+2*i)[0]
            if e >> 12 == 10:
                rel.add(off(page + (e & 0xfff)))
            elif e >> 12 != 0:
                raise SystemExit('unexpected reloc type %d' % (e >> 12))
        p += bsz
    return dict(d=d, base=base, opt=opt, csum=csum_off, ts=ts, rel=rel, secs=secs)
a, b = pe(sys.argv[1]), pe(sys.argv[2])
print('A %s: size %d ImageBase 0x%x timestamp 0x%x relocs %d' % (sys.argv[1], len(a['d']), a['base'], a['ts'], len(a['rel'])))
print('B %s: size %d ImageBase 0x%x timestamp 0x%x relocs %d' % (sys.argv[2], len(b['d']), b['base'], b['ts'], len(b['rel'])))
if len(a['d']) != len(b['d']):
    raise SystemExit('DIFFERENT: sizes differ')
diff = [i for i in range(len(a['d'])) if a['d'][i] != b['d'][i]]
print('differing bytes: %d' % len(diff))
if not diff:
    print('IDENTICAL'); sys.exit(0)
if a['rel'] != b['rel']:
    raise SystemExit('DIFFERENT: relocation tables differ')
delta = a['base'] - b['base']
allowed = set(range(a['opt']+24, a['opt']+32)) | set(range(a['csum'], a['csum']+4))
nrel = 0
for r in a['rel']:
    va, vb = struct.unpack_from('<Q', a['d'], r)[0], struct.unpack_from('<Q', b['d'], r)[0]
    if va - vb != delta:
        raise SystemExit('DIFFERENT: reloc at file 0x%x: 0x%x vs 0x%x' % (r, va, vb))
    allowed |= set(range(r, r+8)); nrel += 1
other = [i for i in diff if i not in allowed]
if other:
    print('DIFFERENT: %d bytes outside ImageBase/CheckSum/relocated pointers, first at file 0x%x' % (len(other), other[0])); sys.exit(1)
hdr = [i for i in diff if i < a['opt']+112]
print('ONLY THE IMAGE BASE: delta 0x%x; %d header bytes (ImageBase/CheckSum) + %d bytes in %d relocated 8-byte pointers' % (delta & (2**64-1), len(hdr), len(diff)-len(hdr), nrel))
