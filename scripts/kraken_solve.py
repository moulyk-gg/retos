#!/usr/bin/env python3
"""Resuelve The Kraken.

1) Identifica las 8 APIs de kernel32 que importa el código desempaquetado, comparando
   el hash del resolver (rol edi,6 ; xor edi,char  — incluye el byte nulo final)
   con la tabla de hashes que hay en el exe (offset 0x108).
2) Reproduce el bucle de descifrado del main (0x42009f) para los 256 posibles valores
   del byte bajo devuelto por la API [0x430000] y muestra los que dan texto legible.

Uso: python3 kraken_solve.py TheKraken.exe kernel32.spec
"""
import re
import struct
import sys

exe = open(sys.argv[1], "rb").read()
spec = open(sys.argv[2]).read()

def rol32(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

def crinkler_hash(name: bytes) -> int:
    h = 0
    for c in name + b"\x00":
        h = rol32(h, 6) ^ c
    return h

names = set()
for line in spec.splitlines():
    line = line.split("#")[0].strip()
    m = re.match(r"^(?:@|\d+)\s+\S+\s+(?:-\S+\s+)*([A-Za-z_][A-Za-z0-9_]*)", line)
    if m:
        names.add(m.group(1))
table = {crinkler_hash(n.encode()): n for n in names}

hashes = struct.unpack_from("<8I", exe, 0x108)
print("== Imports resueltos (IAT en 0x430000) ==")
for i, h in enumerate(hashes):
    print(f"  [0x{0x430000 + 4*i:06x}]  hash={h:#010x}  ->  {table.get(h, '???')}")

# Array de 23 bytes construido en el main (mov byte [ebp-0x1c+i], imm8)
enc = bytes.fromhex("e57a77fbe15668fdfdf8790102ff7d837e8667666466cd")

def decrypt(k: int) -> bytes:
    out = bytearray()
    for i, c in enumerate(enc):
        c ^= 0x7C
        c = (c + k) & 0xFF
        c = (-c) & 0xFF
        c = ((c >> 7) | (c << 1)) & 0xFF   # rol8(c, 1)
        c = (c - i) & 0xFF
        out.append(c)
    return bytes(out)

print("\n== Candidatos legibles según el byte bajo devuelto por [0x430000] ==")
for k in range(256):
    p = decrypt(k)
    if all(32 <= b < 127 for b in p):
        print(f"  k={k:#04x} ({k:3d}): {p.decode()}")
