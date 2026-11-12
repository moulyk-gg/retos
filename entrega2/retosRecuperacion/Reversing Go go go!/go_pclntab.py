#!/usr/bin/env python3
"""Parser mínimo de .gopclntab (Go 1.2–1.15, magic 0xfffffffb) para binarios stripped.

Uso: python3 go_pclntab.py BINARIO [filtro]
Imprime: dirección_inicio  dirección_fin  nombre_función
"""
import struct
import sys

from elftools.elf.elffile import ELFFile

path = sys.argv[1]
filt = sys.argv[2] if len(sys.argv) > 2 else None

with open(path, "rb") as fh:
    elf = ELFFile(fh)
    sec = elf.get_section_by_name(".gopclntab")
    tab = sec.data()
    end = ">" if not elf.little_endian else "<"

magic = struct.unpack_from(end + "I", tab, 0)[0]
assert magic == 0xFFFFFFFB, hex(magic)
ptrsize = tab[7]
P = "I" if ptrsize == 4 else "Q"
nftab = struct.unpack_from(end + P, tab, 8)[0]
off = 8 + ptrsize
funcs = []
for i in range(nftab):
    pc, foff = struct.unpack_from(end + P + P, tab, off + i * 2 * ptrsize)
    nameoff = struct.unpack_from(end + "i", tab, foff + ptrsize)[0]
    name = tab[nameoff:tab.index(b"\x00", nameoff)].decode(errors="replace")
    funcs.append((pc, name))
endpc = struct.unpack_from(end + P, tab, off + nftab * 2 * ptrsize)[0]
for i, (pc, name) in enumerate(funcs):
    nxt = funcs[i + 1][0] if i + 1 < len(funcs) else endpc
    if filt is None or filt in name:
        print(f"{pc:#010x} {nxt:#010x} {name}")
