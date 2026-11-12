#!/usr/bin/env python3
"""Resumen de un ejecutable PE: cabecera, secciones (con entropía), recursos de versión e imports.

Requiere: pip install pefile
Uso: python3 pe_info.py fichero.exe
"""
import datetime
import sys

import pefile

pe = pefile.PE(sys.argv[1])
fh, oh = pe.FILE_HEADER, pe.OPTIONAL_HEADER
print(f"Machine          : {hex(fh.Machine)}  ({'x86' if fh.Machine == 0x14c else 'x64' if fh.Machine == 0x8664 else '?'})")
print(f"TimeDateStamp    : {datetime.datetime.fromtimestamp(fh.TimeDateStamp, datetime.timezone.utc):%Y-%m-%d %H:%M:%S} UTC")
print(f"e_lfanew         : {hex(pe.DOS_HEADER.e_lfanew)}")
print(f"NumberOfSections : {fh.NumberOfSections}")
print(f"ImageBase        : {hex(oh.ImageBase)}")
print(f"EntryPoint (RVA) : {hex(oh.AddressOfEntryPoint)}")
print(f"SizeOfImage      : {hex(oh.SizeOfImage)}  ({oh.SizeOfImage / 1048576:.1f} MB)")
print(f"Subsystem        : {oh.Subsystem}")
dd = oh.DATA_DIRECTORY
print(f"DataDirectories  : {len(dd)}")
print(f"Firma Authenticode: {'sí' if len(dd) > 4 and dd[4].Size else 'no'}")
if pe.sections:
    print("\nSecciones:")
    for s in pe.sections:
        print(f"  {s.Name.rstrip(b'\0').decode(errors='replace'):8s} VA={hex(s.VirtualAddress):9s} "
              f"VSize={hex(s.Misc_VirtualSize):9s} Raw={hex(s.SizeOfRawData):8s} entropía={s.get_entropy():.2f}")
for fi in getattr(pe, "FileInfo", []) or []:
    for entry in fi:
        for st in getattr(entry, "StringTable", []):
            print("\nRecursos de versión:")
            for k, v in st.entries.items():
                print(f"  {k.decode(errors='replace'):18s} = {v.decode(errors='replace')}")
imports = getattr(pe, "DIRECTORY_ENTRY_IMPORT", [])
if imports:
    print("\nImports:")
    for d in imports:
        names = [i.name.decode() if i.name else f"ord{i.ordinal}" for i in d.imports]
        print(f"  {d.dll.decode()}: {len(names)} funciones -> {', '.join(names[:8])}{' ...' if len(names) > 8 else ''}")
