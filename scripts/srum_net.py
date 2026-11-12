#!/usr/bin/env python3
"""Uso de red por aplicación a partir de la tabla SRUM exportada con esedbexport.

Uso:
  esedbexport -t srum SRUDB.dat
  python3 srum_net.py srum.export
"""
import csv
import glob
import os
import sys

csv.field_size_limit(10**9)
d = sys.argv[1]

def rows(pattern):
    path = glob.glob(os.path.join(d, pattern))[0]
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))

idmap = {}
for r in rows("SruDbIdMapTable.*"):
    try:
        idmap[r["IdIndex"]] = bytes.fromhex(r["IdBlob"]).decode("utf-16le").rstrip("\x00")
    except Exception:
        idmap[r["IdIndex"]] = r["IdBlob"]

# {973F5D5C-...} = Network Data Usage
for r in rows("{973F5D5C-1D90-4944-BE8E-24B94231A174}.*"):
    app = idmap.get(r["AppId"], r["AppId"])
    print(f"{r['TimeStamp']}\tsent={r['BytesSent']}\trecv={r['BytesRecvd']}\t{app}")
