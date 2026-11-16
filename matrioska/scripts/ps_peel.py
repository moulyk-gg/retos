#!/usr/bin/env python3
"""Pela capas de PowerShell ofuscado (estilo Invoke-Obfuscation) sin ejecutar nada.

Reconoce y deshace:
  - FromBase64String('...') + DeflateStream  -> base64 + inflate (raw deflate)
  - FromBase64String('...') + GZipStream     -> base64 + gunzip
  - FromBase64String('...') solo             -> base64 (y UTF-16 si procede)
Guarda cada capa en capaN.ps1 y muestra su inicio y final.

Uso: python3 ps_peel.py capa1.ps1 [max_capas]
"""
import base64
import gzip
import re
import sys
import zlib

texto = open(sys.argv[1], encoding="utf-8", errors="replace").read()
maximo = int(sys.argv[2]) if len(sys.argv) > 2 else 20


def decodificar(t):
    m = re.search(r"FromBase64String\s*\(\s*['\"]([A-Za-z0-9+/=\s]{40,})['\"]", t, re.I)
    if not m:
        return None, None
    raw = base64.b64decode(re.sub(r"\s", "", m.group(1)))
    low = t.lower()
    if "deflatestream" in low:
        datos, metodo = zlib.decompress(raw, -15), "base64 + Deflate"
    elif "gzipstream" in low:
        datos, metodo = gzip.decompress(raw), "base64 + GZip"
    else:
        datos, metodo = raw, "base64"
    if datos[:2] == b"\xff\xfe" or (len(datos) > 4 and datos[1:4:2] == b"\x00\x00"):
        return datos.decode("utf-16le", "replace").lstrip("﻿"), metodo + " (UTF-16)"
    return datos.decode("latin-1"), metodo


n = 1
while n < maximo:
    siguiente, metodo = decodificar(texto)
    if siguiente is None:
        print(f"capa {n}: no hay más Base64 que decodificar")
        break
    n += 1
    open(f"capa{n}.ps1", "w", encoding="utf-8").write(siguiente)
    resumen = re.sub(r"\s+", " ", siguiente)
    print(f"== capa {n} ({metodo}, {len(siguiente):,} caracteres)")
    print(f"   inicio: {resumen[:300]}")
    print(f"   final : {resumen[-200:]}")
    texto = siguiente
