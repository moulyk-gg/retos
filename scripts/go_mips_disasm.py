#!/usr/bin/env python3
"""Desensambla funciones de un binario Go MIPS32 big-endian stripped, anotando
llamadas (jal) con el nombre de la función (vía .gopclntab) y referencias lui/addiu
a .rodata con la cadena que apuntan.

Uso: python3 go_mips_disasm.py BINARIO nombre_funcion [nombre_funcion...]
"""
import subprocess
import sys

from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_BIG_ENDIAN
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
wanted = sys.argv[2:]
here = __file__.rsplit("/", 1)[0]
out = subprocess.run([sys.executable, "-I", f"{here}/go_pclntab.py", path],
                     capture_output=True, text=True, check=True).stdout
funcs = {}
for line in out.splitlines():
    s, e, n = line.split(maxsplit=2)
    funcs[n] = (int(s, 16), int(e, 16))
by_addr = {v[0]: k for k, v in funcs.items()}

fh = open(path, "rb")
elf = ELFFile(fh)
segs = [(s["p_vaddr"], s["p_filesz"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]

def read(addr, n):
    for va, sz, data in segs:
        if va <= addr < va + sz:
            o = addr - va
            return data[o:o + n]
    return b""

def preview(addr):
    b = read(addr, 64)
    if not b:
        return None
    s = b.split(b"\x00")[0][:48]
    if len(s) >= 3 and all(32 <= c < 127 for c in s):
        return s.decode()
    return None

md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_BIG_ENDIAN)
for name in wanted:
    s, e = funcs[name]
    print(f"\n===== {name}  [{s:#x}-{e:#x}] =====")
    lui = {}
    for ins in md.disasm(read(s, e - s), s):
        note = ""
        ops = ins.op_str.replace("$", "").split(", ")
        if ins.mnemonic == "lui":
            lui[ops[0]] = int(ops[1], 0) << 16
        elif ins.mnemonic in ("addiu", "ori", "lw", "lbu", "lh", "lhu") and len(ops) >= 2:
            if ins.mnemonic in ("addiu", "ori") and ops[1] in lui:
                imm = int(ops[2], 0)
                addr = (lui[ops[1]] + (imm if ins.mnemonic == "addiu" else imm)) & 0xFFFFFFFF
                p = preview(addr)
                note = f"  ; {addr:#x}" + (f' "{p}"' if p else "")
        if ins.mnemonic == "jal":
            tgt = int(ins.op_str, 0)
            note = f"  ; -> {by_addr.get(tgt, '?')}"
        print(f"{ins.address:#x}: {ins.mnemonic:8s} {ins.op_str}{note}")
