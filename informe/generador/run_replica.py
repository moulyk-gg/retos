#!/usr/bin/env python3
"""Ejecuta en zsh los pasos 'run' de steps.py con un HOME simulado (~/ctf como en Kali)
y guarda la salida real de cada paso en salidas.json.

Uso: python3 run_replica.py [seccion ...]
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from steps import SECCIONES, partir  # noqa: E402

HOME = "/home/user/work/replica"
OUT = os.path.join(os.path.dirname(__file__), "salidas.json")
solo = set(a for a in sys.argv[1:] if not a.startswith("paso="))
pasos_sueltos = [a[5:] for a in sys.argv[1:] if a.startswith("paso=")]

os.makedirs(f"{HOME}/ctf", exist_ok=True)
os.makedirs(f"{HOME}/bin", exist_ok=True)
# Equivalentes a prep-07 (git clone) y prep-09 (curl): se copian para no volver a descargar 871 MB
if not os.path.exists(f"{HOME}/ctf/retos.zip"):
    shutil.copy("/home/user/work/dl/retos.zip", f"{HOME}/ctf/retos.zip")
shutil.rmtree(f"{HOME}/ctf/repo", ignore_errors=True)
shutil.copytree("/home/user/retos", f"{HOME}/ctf/repo", ignore=shutil.ignore_patterns(".git", "informe"))
qemu = f"{HOME}/bin/qemu-mips"  # en Kali el paquete qemu-user instala 'qemu-mips'
if not os.path.exists(qemu):
    os.symlink("/usr/bin/qemu-mips-static", qemu)

salidas = json.load(open(OUT)) if os.path.exists(OUT) else {}
env = dict(os.environ, HOME=HOME, PATH=f"{HOME}/bin:" + os.environ["PATH"], TERM="dumb", LC_ALL="C.UTF-8")
for sec in SECCIONES:
    if pasos_sueltos:
        # Repite pasos concretos en la carpeta donde se ejecutaron (requiere una pasada previa)
        for p in sec["pasos"]:
            if p["id"] in pasos_sueltos:
                cwd = salidas[p["id"]]["cwd"].replace("~", HOME, 1)
                script = f"export S=~/ctf/repo/scripts\ncd '{cwd}'\nprint -r -- '@@@STEP {p['id']}' \"$PWD\"\n{partir(p['cmd'])}\n"
                r = subprocess.run(["zsh", "-f", "-c", script], env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, errors="replace")
                txt = "\n".join(l for l in r.stdout.splitlines() if 'Running as user "root"' not in l)
                m = re.split(r"^@@@STEP (\S+) (.*)$", txt, flags=re.M)
                salidas[p["id"]] = {"cwd": m[2].replace(HOME, "~"), "out": m[3].strip("\n")}
                print("repetido", p["id"])
        continue
    if solo and sec["id"] not in solo:
        continue
    lines = ["export S=~/ctf/repo/scripts", "cd ~"]
    for p in sec["pasos"]:
        if not p["run"]:
            continue
        lines.append(f"print -r -- '@@@STEP {p['id']}' \"$PWD\"")
        lines.append(partir(p["cmd"]))  # se ejecuta exactamente lo que se muestra en el informe
    script = "\n".join(lines) + "\n"
    print(f"### ejecutando sección {sec['id']} ...", flush=True)
    # stdout y stderr mezclados en orden, como en una terminal
    r = subprocess.run(["zsh", "-f", "-c", script], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       text=True, errors="replace")
    # Aviso que tshark solo muestra al ejecutarse como root (en Kali se usa el usuario kali)
    out = "\n".join(l for l in r.stdout.splitlines() if 'Running as user "root"' not in l)
    parts = re.split(r"^@@@STEP (\S+) (.*)$", out, flags=re.M)
    for i in range(1, len(parts), 3):
        pid, cwd, text = parts[i], parts[i + 1], parts[i + 2]
        salidas[pid] = {"cwd": cwd.replace(HOME, "~"), "out": text.strip("\n")}
    if parts[0].strip():
        print("  salida antes del primer paso:", parts[0][:300])
json.dump(salidas, open(OUT, "w"), indent=1, ensure_ascii=False)
print("guardado", OUT)
