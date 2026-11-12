#!/usr/bin/env python3
"""Número de eventos y rango de fechas (primer y último evento) de uno o varios .evtx.

Sirve para detectar logs borrados o cortados (por ejemplo, tras usar wevtutil).
Requiere: python3-evtx
Uso: python3 evtx_range.py Fichero1.evtx [Fichero2.evtx ...]
"""
import os
import re
import sys

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)  # avisos internos de python-evtx

import Evtx.Evtx as evtx

for path in sys.argv[1:]:
    ts = []
    with evtx.Evtx(path) as log:
        for rec in log.records():
            m = re.search(r'SystemTime="([^"]+)"', rec.xml())
            if m:
                ts.append(m.group(1)[:19])
    name = os.path.basename(path)
    if ts:
        print(f"{name:45s} {len(ts):6d} eventos   {min(ts)}  ->  {max(ts)}")
    else:
        print(f"{name:45s}      0 eventos")
