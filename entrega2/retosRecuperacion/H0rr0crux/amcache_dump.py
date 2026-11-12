#!/usr/bin/env python3
"""Vuelca InventoryApplicationFile de Amcache.hve (ruta, SHA1, tamaño, fecha de enlace, publisher).

Uso: python3 amcache_dump.py Amcache.hve [--todo]
Sin --todo oculta binarios de Windows/Program Files (salvo Temp y VMProtect).
"""
import sys

from regipy.registry import RegistryHive

hive = RegistryHive(sys.argv[1])
show_all = "--todo" in sys.argv
key = hive.get_key(r"\Root\InventoryApplicationFile")
n = 0
for sk in key.iter_subkeys():
    v = {x.name: x.value for x in sk.iter_values()}
    path = (v.get("LowerCaseLongPath") or "")
    n += 1
    if not show_all:
        if "\\windows\\" in path and "\\temp\\" not in path:
            continue
        if "\\program files" in path and "vmprotect" not in path:
            continue
    sha1 = (v.get("FileId") or "")[4:]
    print(f"{sha1}\t{v.get('Size')}\t{v.get('LinkDate')}\t{v.get('Publisher')}\t{v.get('OriginalFileName')}\t{path}")
print(f"# entradas totales: {n}", file=sys.stderr)
