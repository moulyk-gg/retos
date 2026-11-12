#!/usr/bin/env python3
"""Emula el descompresor de TheKraken.exe con Unicorn y vuelca el código desempaquetado.

Uso: python3 kraken_emu.py TheKraken.exe salida.bin
No ejecuta el binario en el sistema: solo emula la CPU x86 sobre un buffer de memoria.
"""
import sys
from unicorn import Uc, UcError, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP

src, out = sys.argv[1], sys.argv[2]
data = open(src, "rb").read()

BASE = 0x400000
IMG = 0x1F430000          # SizeOfImage completo (~500 MB): el descompresor usa tablas hash ahí
STACK = 0x00100000

mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(BASE, IMG)
mu.mem_write(BASE, data)
mu.mem_map(STACK, 0x100000)
mu.reg_write(UC_X86_REG_ESP, STACK + 0x100000 - 0x100)

EP = BASE + 0x5C
state = {"n": 0, "target": None}

def on_code(uc, addr, size, _):
    state["n"] += 1
    # El descompresor vive en la cabecera (0x400000-0x401000); cuando salta
    # a la zona de destino (>= 0x420000) el código ya está desempaquetado.
    if addr >= 0x420000 and state["target"] is None:
        state["target"] = addr
        uc.emu_stop()

def on_unmapped(uc, access, addr, size, value, _):
    print(f"[!] acceso a memoria no mapeada en {addr:#x} (eip={uc.reg_read(UC_X86_REG_EIP):#x})")
    return False

# Hook solo sobre la zona destino: el descompresor corre sin callbacks (mucho más rápido)
mu.hook_add(UC_HOOK_CODE, on_code, begin=0x420000, end=0x7FFFFFFF)
mu.hook_add(UC_HOOK_MEM_UNMAPPED, on_unmapped)
try:
    mu.emu_start(EP, BASE + IMG, count=0)
except UcError as e:
    print("[!] UcError:", e, "eip=", hex(mu.reg_read(UC_X86_REG_EIP)))

print(f"instrucciones emuladas: {state['n']:,}")
print("salto a código desempaquetado:", hex(state["target"]) if state["target"] else None)
dump = bytes(mu.mem_read(0x420000, 0x10000))
open(out, "wb").write(dump)
print(f"volcado 0x420000..0x430000 -> {out}")
