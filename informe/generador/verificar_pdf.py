#!/usr/bin/env python3
"""Comprueba que cada comando del informe se puede copiar del PDF tal cual.

Extrae el texto del PDF (pdftotext -raw) y busca cada comando (ya partido con '\\') línea a
línea, normalizando solo los espacios repetidos. Informa de discrepancias y de caracteres de
continuación automática (flechas) dentro de los comandos.
Uso: python3 verificar_pdf.py informe_retos.pdf
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from steps import SECCIONES, partir  # noqa: E402

texto = subprocess.run(["pdftotext", "-raw", sys.argv[1], "-"], capture_output=True, text=True).stdout
lineas_pdf = {re.sub(r"\s+", " ", l).strip() for l in texto.splitlines()}
mal = total = 0
for sec in SECCIONES:
    for p in sec["pasos"]:
        for linea in partir(p["cmd"]).splitlines():
            total += 1
            norm = re.sub(r"\s+", " ", linea).strip()
            if norm not in lineas_pdf:
                mal += 1
                print(f"[{p['id']}] no se encuentra tal cual: {linea}")
flechas = len(re.findall(r"[→↪]", texto))
print(f"líneas de comando comprobadas: {total}, discrepancias: {mal}")
print(f"flechas de continuación automática en todo el PDF (solo deberían estar en salidas y apéndice): {flechas}")
