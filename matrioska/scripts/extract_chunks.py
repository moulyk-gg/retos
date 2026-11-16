#!/usr/bin/env python3
"""Reconstruye el a.exe que el candado (T.exe desempaquetado) escribe en t.tmp por trozos.

Cada trozo es un literal AnsiString de Delphi con texto hexadecimal: cabecera de 12 bytes
[codepage(2)][elemsize(2)][refcnt(4)][longitud(4)] seguida de los caracteres.
Los trozos se añaden a t.tmp en el orden de las combinaciones del candado:
A x4 -> (4,0,0,0) | OK con (4,0,0,1) | OK con (5,1,2,1) | C con (5,2,2,5).

Uso: python3 extract_chunks.py T_unpacked.exe a.exe
"""
import binascii
import hashlib
import struct
import sys

BASE = 0x400000
# (función que escribe el trozo, dirección del literal hexadecimal) en orden de escritura
TROZOS = [(0x5cefd8, 0x5cf0ac), (0x645430, 0x645584),   # combinación (4,0,0,0) con A
          (0x6bb90c, 0x6bba60), (0x731de8, 0x731f3c),   # (4,0,0,1) con OK
          (0x7a82c4, 0x7a8418), (0x81e7a0, 0x81e8f4),   # (5,1,2,1) con OK
          (0x894c7c, 0x894dd0), (0x90b158, 0x90b2ac)]   # (5,2,2,5) con C -> renombra a a.exe

d = open(sys.argv[1], "rb").read()
salida = bytearray()
for n, (func, lit) in enumerate(TROZOS, 1):
    off = lit - BASE
    cp, es, ref, ln = struct.unpack_from("<HHiI", d, off - 12)
    texto = d[off:off + ln]
    datos = binascii.unhexlify(texto)
    salida += datos
    print(f"trozo {n}: función {func:#x}, literal {lit:#x}, {ln:,} caracteres hex -> {len(datos):,} bytes, "
          f"empieza por {datos[:8].hex()}")
open(sys.argv[2], "wb").write(salida)
print(f"\n{sys.argv[2]}: {len(salida):,} bytes  MD5 {hashlib.md5(salida).hexdigest()}")
