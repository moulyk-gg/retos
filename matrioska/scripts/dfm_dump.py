#!/usr/bin/env python3
"""Convierte un formulario Delphi binario (DFM, cabecera TPF0) a texto legible.

Uso: python3 dfm_dump.py res_TFORM1.bin
"""
import struct
import sys

d = open(sys.argv[1], "rb").read()
p = 0


def u8():
    global p
    v = d[p]; p += 1
    return v


def sstr():
    global p
    n = u8(); s = d[p:p + n]; p += n
    return s.decode("latin-1")


def valor():
    global p
    t = u8()
    if t == 0: return None
    if t == 2: v = struct.unpack_from("<b", d, p)[0]; p += 1; return v
    if t == 3: v = struct.unpack_from("<h", d, p)[0]; p += 2; return v
    if t == 4: v = struct.unpack_from("<i", d, p)[0]; p += 4; return v
    if t == 5: v = d[p:p + 10]; p += 10; return f"<extended {v.hex()}>"
    if t in (6, 7): return sstr() if t == 6 else sstr()
    if t == 8: return False
    if t == 9: return True
    if t == 10:
        n = struct.unpack_from("<I", d, p)[0]; p += 4; v = d[p:p + n]; p += n
        return f"<binario {n} bytes: {v[:32].hex()}...>"
    if t == 11:
        items = []
        while True:
            s = sstr()
            if not s: break
            items.append(s)
        return "[" + ", ".join(items) + "]"
    if t == 12:
        n = struct.unpack_from("<I", d, p)[0]; p += 4; v = d[p:p + n]; p += n
        return v.decode("latin-1")
    if t == 13: return "nil"
    if t == 14:
        items = []
        while d[p] != 0:
            items.append(lista_props_en_item())
        p += 1
        return f"<colección {items}>"
    if t == 18:
        n = struct.unpack_from("<I", d, p)[0]; p += 4; v = d[p:p + 2 * n]; p += 2 * n
        return v.decode("utf-16le")
    if t == 20:
        n = struct.unpack_from("<I", d, p)[0]; p += 4; v = d[p:p + n]; p += n
        return v.decode("utf-8")
    if t == 19:  # vaInt64
        v = struct.unpack_from("<q", d, p)[0]; p += 8; return v
    raise ValueError(f"tipo {t} no soportado en offset {p - 1}")


def lista_props_en_item():
    global p
    out = {}
    while True:
        nombre = sstr()
        if not nombre: break
        out[nombre] = valor()
    return out


def componente(nivel):
    global p
    flags = 0
    if d[p] & 0xF0 == 0xF0:
        flags = u8()
        if flags & 2:
            valor()
    clase, nombre = sstr(), sstr()
    print("  " * nivel + f"object {nombre}: {clase}")
    while True:
        prop = sstr()
        if not prop: break
        v = valor()
        print("  " * (nivel + 1) + f"{prop} = {v!r}")
    while d[p] != 0:
        componente(nivel + 1)
    p += 1
    print("  " * nivel + "end")


assert d[:4] == b"TPF0"
p = 4
componente(0)
