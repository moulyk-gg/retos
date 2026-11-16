#!/usr/bin/env python3
"""Lista las llamadas a funciones importadas (call [IAT] o call a un thunk jmp [IAT]) de un PE x86.

Uso: python3 api_xrefs.py fichero.exe [filtro_regex]
"""
import re
import sys

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32

pe = pefile.PE(sys.argv[1])
filtro = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
base = pe.OPTIONAL_HEADER.ImageBase
iat = {}
for imp in pe.DIRECTORY_ENTRY_IMPORT:
    for i in imp.imports:
        if i.name:
            iat[i.address] = i.name.decode()
text = pe.sections[0]
code = text.get_data()
ini = base + text.VirtualAddress
md = Cs(CS_ARCH_X86, CS_MODE_32)
thunks = {}
inss = list(md.disasm(code, ini))
for ins in inss:  # thunks: jmp dword ptr [IAT]
    if ins.mnemonic == "jmp" and ins.op_str.startswith("dword ptr ["):
        try:
            a = int(ins.op_str[11:-1], 16)
        except ValueError:
            continue
        if a in iat:
            thunks[ins.address] = iat[a]
for ins in inss:
    nombre = None
    if ins.mnemonic == "call":
        op = ins.op_str
        if op.startswith("dword ptr [0x"):
            nombre = iat.get(int(op[11:-1], 16))
        elif op.startswith("0x"):
            nombre = thunks.get(int(op, 16))
    if nombre and (filtro is None or filtro.search(nombre)):
        print(f"{ins.address:#x}: call {nombre}")
