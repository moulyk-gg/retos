#!/usr/bin/env python3
"""Imprime los eventos de un .evtx (EventID, fecha y campos de EventData) que contengan un texto.

Uso: python3 evtx_grep.py fichero.evtx [texto] [--ids 1116,1117]
"""
import re
import sys

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)  # avisos internos de python-evtx

import Evtx.Evtx as evtx

path = sys.argv[1]
needle = sys.argv[2].lower() if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
ids = None
if "--ids" in sys.argv:
    ids = set(sys.argv[sys.argv.index("--ids") + 1].split(","))

with evtx.Evtx(path) as log:
    for rec in log.records():
        xml = rec.xml()
        eid = re.search(r"<EventID[^>]*>(\d+)<", xml).group(1)
        if ids and eid not in ids:
            continue
        if needle and needle not in xml.lower():
            continue
        ts = re.search(r'SystemTime="([^"]+)"', xml).group(1)
        print(f"=== EventID {eid}  {ts}")
        for name, val in re.findall(r'<Data Name="([^"]+)">([^<]*)</Data>', xml):
            if val and val not in ("%%830", "0", "0x0"):
                print(f"   {name}: {val}")
        if "<Data Name" not in xml:
            for val in re.findall(r"<Data>([^<]*)</Data>", xml):
                print("   ", val)
