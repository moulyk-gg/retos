#!/usr/bin/env python3
"""Desempaqueta por emulación (Unicorn) un PE x86 empaquetado (MPRESS, UPX y similares).

Carga el PE en memoria, simula GetModuleHandleA/LoadLibraryA/GetProcAddress y otras APIs
devolviendo valores falsos, y emula desde el punto de entrada hasta que el código salta a la
primera sección (OEP). Vuelca la imagen en memoria como un PE analizable (raw = virtual).
No ejecuta nada en el sistema: es una CPU simulada.

Uso: python3 unpack_emu.py entrada.exe salida.exe [--completo]
  --completo: no se detiene al entrar en la primera sección; sigue hasta que el programa original llama
              a una API que no es del cargador (desempaquetado y correcciones terminados).
"""
import struct
import sys

import pefile
from unicorn import Uc, UcError, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_HOOK_MEM_UNMAPPED
from unicorn.x86_const import (UC_X86_REG_EAX, UC_X86_REG_ESP, UC_X86_REG_EIP, UC_X86_REG_EBX,
                               UC_X86_REG_FS_BASE)

src, dst = sys.argv[1], sys.argv[2]
COMPLETO = "--completo" in sys.argv
CARGADOR = {"GetModuleHandleA", "GetModuleHandleW", "LoadLibraryA", "LoadLibraryW", "GetProcAddress",
            "VirtualProtect", "VirtualAlloc", "VirtualFree"}
pe = pefile.PE(src)
base = pe.OPTIONAL_HEADER.ImageBase
size = (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF
ep = base + pe.OPTIONAL_HEADER.AddressOfEntryPoint
img = pe.get_memory_mapped_image()

mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(base, size)
mu.mem_write(base, img[:size])

STACK, STACK_SZ = 0x00100000, 0x00200000
mu.mem_map(STACK, STACK_SZ)
esp = STACK + STACK_SZ - 0x1000
API, API_SZ = 0x70000000, 0x00100000          # direcciones falsas de funciones de Windows
mu.mem_map(API, API_SZ)
mu.mem_write(API, b"\xc3" * API_SZ)
MODS = 0x71000000                              # "módulos" falsos (handles de DLL)
mu.mem_map(MODS, 0x01000000)
TEB, PEB = 0x7FFD0000, 0x7FFDE000
mu.mem_map(TEB, 0x10000)
mu.mem_write(TEB + 0x18, struct.pack("<I", TEB))
mu.mem_write(TEB + 0x30, struct.pack("<I", PEB))
mu.mem_write(PEB + 0x08, struct.pack("<I", base))   # PEB.ImageBaseAddress
mu.reg_write(UC_X86_REG_FS_BASE, TEB)

apis = {}      # dirección falsa -> nombre
modulos = {}   # handle -> nombre de DLL


def nueva_api(nombre):
    addr = API + 0x10 * (len(apis) + 1)
    apis[addr] = nombre
    return addr


def leer_cadena(addr, wide=False):
    out = b""
    while addr and len(out) < 512:
        c = bytes(mu.mem_read(addr, 2 if wide else 1))
        if c in (b"\x00", b"\x00\x00"):
            break
        out += c
        addr += len(c)
    return out.decode("utf-16le" if wide else "latin-1", "replace")


# Rellenar la IAT original con direcciones falsas
for imp in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []):
    for i in imp.imports:
        nombre = f"{imp.dll.decode()}!{i.name.decode() if i.name else i.ordinal}"
        mu.mem_write(i.address, struct.pack("<I", nueva_api(nombre)))

# Argumentos (stdcall) que hay que quitar de la pila para cada API conocida
NARGS = {"GetModuleHandleA": 1, "GetModuleHandleW": 1, "LoadLibraryA": 1, "LoadLibraryW": 1, "GetProcAddress": 2,
         "VirtualAlloc": 4, "VirtualFree": 3, "VirtualProtect": 4, "ExitProcess": 1, "GetVersion": 0,
         "GetCommandLineA": 0, "GetCommandLineW": 0, "GetModuleFileNameA": 3, "GetTickCount": 0}
estado = {"oep": None, "llamadas": 0, "heap": 0x60000000}
mu.mem_map(estado["heap"], 0x08000000)
sec0_ini = base + pe.sections[0].VirtualAddress
sec0_fin = sec0_ini + pe.sections[0].Misc_VirtualSize


def on_api(uc, addr, size, _):
    nombre = apis.get(addr)
    if nombre is None:
        return
    corto = nombre.split("!")[-1]
    esp_ = uc.reg_read(UC_X86_REG_ESP)
    if COMPLETO and corto not in CARGADOR:
        ret0, = struct.unpack("<I", uc.mem_read(esp_, 4))
        print(f"[+] El programa original llama a {nombre} desde {ret0:#x}: desempaquetado completo")
        estado["primera_api"] = (nombre, ret0)
        uc.emu_stop()
        return
    ret, = struct.unpack("<I", uc.mem_read(esp_, 4))
    args = struct.unpack("<4I", uc.mem_read(esp_ + 4, 16))
    eax = 0
    if corto in ("GetModuleHandleA", "LoadLibraryA", "GetModuleHandleW", "LoadLibraryW"):
        dll = leer_cadena(args[0], corto.endswith("W")) if args[0] else "(principal)"
        eax = base if not args[0] else MODS + 0x10000 * (len(modulos) + 1)
        if args[0]:
            modulos[eax] = dll
    elif corto == "GetProcAddress":
        fn = leer_cadena(args[1]) if args[1] > 0xFFFF else f"#{args[1]}"
        eax = nueva_api(f"{modulos.get(args[0], hex(args[0]))}!{fn}")
    elif corto == "VirtualAlloc":
        eax = args[0] or estado["heap"]
        estado["heap"] += (args[1] + 0xFFFF) & ~0xFFFF
    elif corto in ("VirtualProtect", "VirtualFree"):
        eax = 1
        if corto == "VirtualProtect" and args[3]:
            uc.mem_write(args[3], struct.pack("<I", 0x40))
    elif corto == "ExitProcess":
        print("[!] ExitProcess llamado: el stub decidió terminar")
        uc.emu_stop()
        return
    else:
        eax = 1
    estado["llamadas"] += 1
    uc.reg_write(UC_X86_REG_EAX, eax)
    uc.reg_write(UC_X86_REG_ESP, esp_ + 4 + 4 * NARGS.get(corto, 0))
    uc.reg_write(UC_X86_REG_EIP, ret)


def on_text(uc, addr, size, _):
    if estado["oep"] is None:
        estado["oep"] = addr
        if not COMPLETO:
            uc.emu_stop()


def on_unmapped(uc, access, addr, size, value, _):
    print(f"[!] acceso a memoria no mapeada {addr:#x} (eip={uc.reg_read(UC_X86_REG_EIP):#x})")
    return False


mu.hook_add(UC_HOOK_CODE, on_api, begin=API, end=API + API_SZ - 1)
h_text = mu.hook_add(UC_HOOK_CODE, on_text, begin=sec0_ini, end=sec0_fin - 1)
mu.hook_add(UC_HOOK_MEM_UNMAPPED, on_unmapped)
mu.reg_write(UC_X86_REG_ESP, esp)
mu.reg_write(UC_X86_REG_EBX, PEB)
print(f"Punto de entrada del empaquetador: {ep:#x}; primera sección {sec0_ini:#x}-{sec0_fin:#x}")
try:
    mu.emu_start(ep, 0, count=2_000_000_000)
except UcError as e:
    print("[!] UcError:", e, "eip=", hex(mu.reg_read(UC_X86_REG_EIP)))

print(f"APIs emuladas: {estado['llamadas']}")
for a, n in list(apis.items()):
    if "!" in n and not n.startswith(("KERNEL32.DLL!", "winspool", "comctl32", "shell32", "ole32", "version",
                                      "user32", "oleaut32", "netapi32", "advapi32", "gdi32")):
        pass
print(f"Funciones resueltas por el stub: {len(apis)}")
if estado["oep"] is None:
    print("[!] No se alcanzó el OEP")
    sys.exit(1)
print(f"OEP (punto de entrada original): {estado['oep']:#x}  (RVA {estado['oep'] - base:#x})")

# Volcado: imagen en memoria con raw = virtual
dump = bytearray(mu.mem_read(base, size))
d = pefile.PE(data=bytes(dump))
d.OPTIONAL_HEADER.AddressOfEntryPoint = estado["oep"] - base
d.OPTIONAL_HEADER.FileAlignment = d.OPTIONAL_HEADER.SectionAlignment
for s in d.sections:
    s.PointerToRawData = s.VirtualAddress
    s.SizeOfRawData = s.Misc_VirtualSize
dump[:0x1000] = d.write()[:0x1000]
open(dst, "wb").write(dump)
print(f"Volcado escrito en {dst} ({len(dump):,} bytes)")
dlls = sorted(set(v.split("!")[0] for v in apis.values()))
print("DLL usadas:", ", ".join(dlls))
