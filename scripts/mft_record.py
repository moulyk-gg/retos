#!/usr/bin/env python3
"""Parsea registros FILE de la $MFT que contengan un nombre dado.

Uso: python3 mft_record.py '$MFT' nombre [--dump-resident salida_dir]
Muestra: nº de registro, flags (en uso/borrado), $STANDARD_INFORMATION y $FILE_NAME
(fechas, padre, nombre), $DATA (residente o no, tamaño real, runlist).
"""
import datetime
import os
import struct
import sys

mft_path, name = sys.argv[1], sys.argv[2]
dump_dir = sys.argv[sys.argv.index("--dump-resident") + 1] if "--dump-resident" in sys.argv else None
data = open(mft_path, "rb").read()
REC = 1024
needle = name.lower().encode("utf-16le")

def ft(v):
    if not v:
        return "-"
    return (datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=v // 10)).isoformat(sep=" ")

def fixup(rec):
    rec = bytearray(rec)
    usa_off, usa_cnt = struct.unpack_from("<HH", rec, 4)
    usn = rec[usa_off:usa_off + 2]
    for i in range(1, usa_cnt):
        pos = i * 512 - 2
        if rec[pos:pos + 2] == usn:
            rec[pos:pos + 2] = rec[usa_off + 2 * i:usa_off + 2 * i + 2]
    return bytes(rec)

def parent_path(ref, depth=0):
    """Reconstruye la ruta siguiendo las referencias al padre."""
    if depth > 30 or ref == 5:
        return ""
    off = ref * REC
    if off + REC > len(data) or data[off:off + 4] != b"FILE":
        return f"<{ref}>"
    rec = fixup(data[off:off + REC])
    a = struct.unpack_from("<H", rec, 20)[0]
    best = None
    while a < REC - 8:
        t, ln = struct.unpack_from("<II", rec, a)
        if t == 0xFFFFFFFF or ln == 0:
            break
        if t == 0x30:
            c = a + struct.unpack_from("<H", rec, a + 20)[0]
            par = struct.unpack_from("<Q", rec, c)[0] & 0xFFFFFFFFFFFF
            nl, ns = rec[c + 64], rec[c + 65]
            nm = rec[c + 66:c + 66 + nl * 2].decode("utf-16le", "replace")
            if best is None or ns != 2:
                best = (par, nm)
        a += ln
    if not best:
        return f"<{ref}>"
    return parent_path(best[0], depth + 1) + "\\" + best[1]

seen = set()
pos = 0
low = data.lower() if False else data
while True:
    i = data.find(needle, pos)
    if i < 0:
        i = data.find(name.upper().encode("utf-16le"), pos)
        if i < 0:
            break
    pos = i + 1
    recno = i // REC
    if recno in seen:
        continue
    seen.add(recno)
    raw = data[recno * REC:(recno + 1) * REC]
    if raw[:4] != b"FILE":
        print(f"[offset {i:#x}] coincidencia fuera de un registro FILE (slack/índice)")
        continue
    rec = fixup(raw)
    flags = struct.unpack_from("<H", rec, 22)[0]
    state = ("EN USO" if flags & 1 else "BORRADO") + (" DIR" if flags & 2 else "")
    print(f"\n=== Registro MFT #{recno}  ({state})")
    a = struct.unpack_from("<H", rec, 20)[0]
    while a < REC - 8:
        t, ln = struct.unpack_from("<II", rec, a)
        if t == 0xFFFFFFFF or ln == 0:
            break
        nonres = rec[a + 8]
        if t == 0x10:
            c = a + struct.unpack_from("<H", rec, a + 20)[0]
            cr, mo, mc, ac = struct.unpack_from("<QQQQ", rec, c)
            print(f"  $SI  creado={ft(cr)} modificado={ft(mo)} mft_mod={ft(mc)} acceso={ft(ac)}")
        elif t == 0x30:
            c = a + struct.unpack_from("<H", rec, a + 20)[0]
            par = struct.unpack_from("<Q", rec, c)[0] & 0xFFFFFFFFFFFF
            cr, mo, mc, ac, alloc, real = struct.unpack_from("<QQQQQQ", rec, c + 8)
            nl = rec[c + 64]
            nm = rec[c + 66:c + 66 + nl * 2].decode("utf-16le", "replace")
            print(f"  $FN  nombre={nm}  ruta={parent_path(par)}\\{nm}")
            print(f"       creado={ft(cr)} modificado={ft(mo)}")
        elif t == 0x80:
            nlen = rec[a + 9]
            if nonres:
                real = struct.unpack_from("<Q", rec, a + 48)[0]
                print(f"  $DATA no residente, tamaño real={real} bytes (contenido en disco, no en la $MFT)")
            else:
                clen, coff = struct.unpack_from("<IH", rec, a + 16)
                print(f"  $DATA RESIDENTE, {clen} bytes dentro del registro")
                if dump_dir:
                    os.makedirs(dump_dir, exist_ok=True)
                    out = os.path.join(dump_dir, f"mft_{recno}.bin")
                    open(out, "wb").write(rec[a + coff:a + coff + clen])
                    print(f"       volcado en {out}")
        a += ln
