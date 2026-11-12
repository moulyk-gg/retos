#!/usr/bin/env python3
"""Extrae la(s) URL(s) de los URL Moniker que hay dentro de los objetos OLE de un RTF.

Busca en \\objdata el CLSID del URL Moniker {79EAC9E0-BAF9-11CE-8C82-00AA004BA90B}
(en bytes: e0c9ea79f9bace118c8200aa004ba90b), lee la longitud (4 bytes) y la URL en UTF-16LE.
Uso: python3 rtf_url.py Nominas.rtf
"""
import re
import sys

rtf = open(sys.argv[1], encoding="latin-1").read()
CLSID = bytes.fromhex("e0c9ea79f9bace118c8200aa004ba90b")
for n, part in enumerate(rtf.split(r"{\*\objdata")[1:]):
    hexdata = re.sub(r"[^0-9a-fA-F]", "", part.split("}")[0])
    data = bytes.fromhex(hexdata[: len(hexdata) // 2 * 2])
    pos = data.find(CLSID)
    while pos >= 0:
        size = int.from_bytes(data[pos + 16:pos + 20], "little")
        url = data[pos + 20:pos + 20 + size].decode("utf-16le", "replace").split("\x00")[0]
        print(f"objeto {n}: URL Moniker en offset {pos:#x}, campo de {size} bytes")
        print(f"  URL exacta: {url!r}  ({len(url)} caracteres)")
        pos = data.find(CLSID, pos + 1)
