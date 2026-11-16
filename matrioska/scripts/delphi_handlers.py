#!/usr/bin/env python3
"""Resume los manejadores de eventos de un formulario Delphi desempaquetado.

Para cada manejador: contadores globales que incrementa/decrementa, cadenas Unicode que usa
(literales de Delphi) y funciones a las que llama.
Uso: python3 delphi_handlers.py volcado.exe direccion:nombre [direccion:nombre ...]
"""
import struct
import sys

from capstone import Cs, CS_ARCH_X86, CS_MODE_32

BASE = 0x400000
d = open(sys.argv[1], "rb").read()
md = Cs(CS_ARCH_X86, CS_MODE_32)
CONT = {0x9981c8: "c0", 0x9981cc: "c1", 0x9981d0: "c2", 0x9981d4: "c3"}
CAMPOS = {0x3d4: "Label(c0)", 0x3d8: "Label(c1)", 0x3e0: "Label(c2)", 0x3e4: "Label(c3)", 0x424: "Pantalla"}


def ustr(va):
    """Literal UnicodeString de Delphi: [codepage][elemsize][refcnt][len] + UTF-16."""
    off = va - BASE
    if off < 12 or off >= len(d):
        return None
    cp, es, ref, n = struct.unpack_from("<HHiI", d, off - 12)
    if cp == 1200 and es == 2 and 0 < n < 400:
        return d[off:off + 2 * n].decode("utf-16le", "replace")
    return None


def analiza(ini, nombre, fin=None):
    code = d[ini - BASE: ini - BASE + 0x400]
    incs, strs, calls, campos = [], [], [], []
    for ins in md.disasm(code, ini):
        op = ins.op_str
        for a, c in CONT.items():
            if f"{a:#x}" in op and ins.mnemonic in ("inc", "dec", "add", "sub", "mov"):
                incs.append(f"{ins.mnemonic} {c}" if ins.mnemonic in ("inc", "dec") else f"{ins.mnemonic} {op}")
        if ins.mnemonic in ("mov", "push") and "0x9" in op:
            try:
                v = int(op.split(",")[-1].strip(), 16)
                s = ustr(v)
                if s is not None:
                    strs.append(s)
            except ValueError:
                pass
        if ins.mnemonic == "call":
            calls.append(op)
        if ins.mnemonic == "ret":
            break
    return incs, strs, calls


for arg in sys.argv[2:]:
    a, nombre = arg.split(":")
    incs, strs, calls = analiza(int(a, 16), nombre)
    print(f"== {nombre} ({a})")
    print(f"   contadores: {incs}")
    print(f"   cadenas   : {strs}")
    print(f"   llamadas  : {calls}")
