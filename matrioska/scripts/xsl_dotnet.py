#!/usr/bin/env python3
"""Reconstruye el objeto serializado de un x.xsl con DotNetToJScript ofuscado (obfuscator.io)
y extrae los ejecutables PE (.NET) que contiene. No ejecuta JScript: lo interpreta en Python.

Uso: python3 xsl_dotnet.py x.xsl carpeta_salida
"""
import base64
import hashlib
import os
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
out = sys.argv[2]
os.makedirs(out, exist_ok=True)

# 1) Lista de cadenas y rotación: (function(a,n){ f=function(k){while(--k){a.push(a.shift())}}; f(++n) }(lista, 0x6e))
nombre, cuerpo = re.search(r"var (_0x[0-9a-f]+)=\[(.*?)\];", t, re.S).groups()
lista = re.findall(r"'([^']*)'", cuerpo)
rot = int(re.search(r"\}\(" + nombre + r",(0x[0-9a-f]+|\d+)\)\);", t).group(1), 0)
for _ in range(rot):          # ++n y luego while(--k): exactamente 'rot' rotaciones
    lista.append(lista.pop(0))
print(f"lista {nombre}: {len(lista)} cadenas, rotada {rot} posiciones")

# 2) Función de acceso: _0x5108('0xN') -> lista[N]
acc = re.search(r"var (_0x[0-9a-f]+)=function\(_0x[0-9a-f]+,_0x[0-9a-f]+\)\{_0x[0-9a-f]+=_0x[0-9a-f]+-0x0;", t).group(1)

# 3) Evaluar la concatenación de serialized_obj
expr = re.search(r"var serialized_obj=(.*?);", t, re.S).group(1)
piezas = re.findall(r"'([^']*)'|" + acc + r"\('(0x[0-9a-f]+)'\)", expr)
b64 = "".join(lit if lit else lista[int(idx, 16)] for lit, idx in piezas)
blob = base64.b64decode(b64)
open(os.path.join(out, "serialized_obj.bin"), "wb").write(blob)
print(f"serialized_obj: {len(b64):,} caracteres Base64 -> {len(blob):,} bytes (BinaryFormatter)")

# 4) Extraer los PE incrustados (cabecera MZ + 'PE\0\0' en e_lfanew)
n = 0
for m in re.finditer(rb"MZ", blob):
    i = m.start()
    if i + 0x40 > len(blob):
        continue
    lfanew = int.from_bytes(blob[i + 0x3C:i + 0x40], "little")
    if blob[i + lfanew:i + lfanew + 4] != b"PE\x00\x00":
        continue
    # La longitud del array de bytes .NET (BinaryFormatter) va en los 4 bytes previos al MZ
    largo = int.from_bytes(blob[i - 4:i], "little")
    pe = blob[i:i + largo] if 0 < largo <= len(blob) - i else blob[i:]
    n += 1
    ruta = os.path.join(out, f"payload{n}.dll")
    open(ruta, "wb").write(pe)
    print(f"PE {n}: offset {i:#x}, {len(pe):,} bytes, MD5 {hashlib.md5(pe).hexdigest()} -> {ruta}")
