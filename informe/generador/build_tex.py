#!/usr/bin/env python3
"""Genera informe_retos.tex a partir de steps.py + salidas.json + los ficheros reales de la réplica."""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from steps import SECCIONES, partir  # noqa: E402
from textos import PREAMBULO, PORTADA_Y_RESUMEN, METODOLOGIA, INTRO, CIERRE, APENDICE_INICIO, REFERENCIAS, FICHEROS  # noqa: E402

BASE = os.path.dirname(__file__)
REPLICA = "/home/user/work/replica"
SCRIPTS = "/home/user/retos/scripts"
OUTDIR = "/home/user/retos/informe"
salidas = json.load(open(os.path.join(BASE, "salidas.json")))

MAP = {"→": "->", "—": "--", "–": "-", "≥": ">=", "≤": "<=", "…": "...", "㉿": "@", "─": "-", "└": "+", "┌": "+",
       "✅": "OK", "⏳": "..", "×": "x", "“": '"', "”": '"', "‘": "'", "’": "'", " ": " "}
LATIN = set("áéíóúñÁÉÍÓÚÑüÜ¿¡ºª°")


def limpiar_codigo(t):
    """Texto apto para listings bajo pdflatex: tabs expandidos, solo ASCII + acentos castellanos."""
    t = t.expandtabs(8)
    out = []
    for ch in t:
        if ch in MAP:
            out.append(MAP[ch])
        elif ord(ch) < 128 or ch in LATIN:
            out.append(ch)
        else:
            out.append("?")
    return "".join(out)


def partir_tokens(t, ancho=95):
    """Parte (solo en las salidas) las secuencias sin espacios más largas que 'ancho', que listings no sabe cortar."""
    def cortar(m):
        w = m.group(0)
        return "\n".join(w[i:i + ancho] for i in range(0, len(w), ancho))
    return re.sub(r"\S{%d,}" % (ancho + 1), cortar, t)


def esc(t):
    """Escapa texto plano para LaTeX."""
    rep = {"\\": r"\textbackslash{}", "~": r"\textasciitilde{}", "^": r"\^{}", "_": r"\_", "$": r"\$", "%": r"\%",
           "&": r"\&", "#": r"\#", "{": r"\{", "}": r"\}"}
    return "".join(rep.get(c, c) for c in t)


def hashes(path):
    data = open(path, "rb").read()
    return len(data), hashlib.md5(data).hexdigest(), hashlib.sha1(data).hexdigest(), hashlib.sha256(data).hexdigest()


def tabla_ficheros(sid):
    filas = []
    for nombre, ruta, desc in FICHEROS.get(sid, []):
        if ruta.startswith("manual:"):
            size, md5, sha1, sha256 = ruta[7:].split("|")
        else:
            size, md5, sha1, sha256 = hashes(os.path.join(REPLICA, ruta))
            size = f"{size:,}".replace(",", ".")
        filas.append(
            rf"\texttt{{{esc(nombre)}}} & {size} & {desc} \\ \nopagebreak" "\n"
            rf"\multicolumn{{3}}{{l}}{{\hspace{{1em}}\footnotesize\ttfamily MD5 {md5}\quad SHA1 {sha1}}} \\ \nopagebreak" "\n"
            rf"\multicolumn{{3}}{{l}}{{\hspace{{1em}}\footnotesize\ttfamily SHA256 {sha256}}} \\ \midrule" "\n")
    if not filas:
        return ""
    return (r"\begin{longtable}{@{}L{0.30\linewidth}r L{0.50\linewidth}@{}}" "\n"
            r"\toprule \textbf{Fichero} & \textbf{Bytes} & \textbf{Descripción} \\ \midrule \endhead" "\n"
            + "".join(filas) + r"\end{longtable}" "\n")


def paso_tex(n, p):
    s = salidas.get(p["id"])
    cwd = s["cwd"] if s else "~/ctf"
    out = []
    out.append(rf"\subsubsection*{{Paso {n}. {esc(p['titulo'])}}}\label{{paso:{p['id']}}}" "\n")
    out.append(r"\addcontentsline{toc}{subsubsection}{" + f"Paso {n}. {esc(p['titulo'])}" + "}\n")
    if p["texto"]:
        out.append(p["texto"] + "\n\n")
    out.append(r"\begin{comando}{" + esc(cwd) + "}\n" + limpiar_codigo(partir(p["cmd"])) + "\n" + r"\end{comando}" + "\n")
    texto_salida = p["manual"] if p["manual"] is not None else (s["out"] if s else None)
    if texto_salida:
        lines = texto_salida.splitlines()
        if p["lineas"] and len(lines) > p["lineas"]:
            lines = lines[: p["lineas"]] + [f"[... {len(texto_salida.splitlines()) - p['lineas']} líneas más ...]"]
        etiqueta = "Salida obtenida en la máquina del usuario" if p["manual"] is not None and p["id"].startswith("horcrux-18") else "Salida esperada"
        out.append(r"\begin{salida}{" + etiqueta + "}\n" + partir_tokens(limpiar_codigo("\n".join(lines))) + "\n" + r"\end{salida}" + "\n")
    elif p["run"]:
        out.append(r"\noindent{\small\itshape (El comando no muestra nada si todo va bien.)}" "\n\n")
    if p["nota"]:
        out.append(r"\begin{nota}" + p["nota"] + r"\end{nota}" + "\n")
    if p["captura"]:
        out.append(r"\captura{" + p["id"] + "}{" + esc(p["titulo"]) + "}\n")
    return "".join(out)


def apendice_scripts():
    out = [APENDICE_INICIO]
    for f in sorted(os.listdir(SCRIPTS)):
        path = os.path.join(SCRIPTS, f)
        code = limpiar_codigo(open(path, encoding="utf-8").read().rstrip("\n"))
        env = "codigopython" if f.endswith(".py") else "codigobash"
        out.append(rf"\subsection{{\texttt{{{esc(f)}}}}}" "\n")
        out.append(rf"\begin{{{env}}}{{{esc(f)}}}" "\n" + code + "\n" + rf"\end{{{env}}}" "\n")
    return "".join(out)


def main():
    os.makedirs(os.path.join(OUTDIR, "capturas"), exist_ok=True)
    doc = [PREAMBULO, r"\begin{document}", PORTADA_Y_RESUMEN, METODOLOGIA]
    for sec in SECCIONES:
        marca = "\\subsection{Ficheros analizados}\n"
        intro = INTRO[sec["id"]]
        if marca in intro:  # la tabla va justo debajo de su título, antes del resumen
            intro = intro.replace(marca, marca + tabla_ficheros(sec["id"]), 1)
        doc.append(intro)
        if sec["id"] != "prep":
            doc.append(r"\subsection{Procedimiento paso a paso}" "\n")
        for n, p in enumerate(sec["pasos"], 1):
            doc.append(paso_tex(n, p))
        doc.append(CIERRE.get(sec["id"], ""))
    doc.append(r"\appendix")
    doc.append(apendice_scripts())
    doc.append(REFERENCIAS)
    doc.append(r"\end{document}")
    tex = "\n".join(doc)
    open(os.path.join(OUTDIR, "informe_retos.tex"), "w", encoding="utf-8").write(tex)
    # Lista de capturas a tomar
    caps = [(p["id"], p["titulo"]) for s in SECCIONES for p in s["pasos"] if p["captura"]]
    with open(os.path.join(OUTDIR, "capturas", "LEEME.txt"), "w", encoding="utf-8") as fh:
        fh.write("Guarda aquí cada captura con el nombre indicado (PNG). Al recompilar aparecen solas en el informe.\n\n")
        for cid, tit in caps:
            fh.write(f"{cid}.png\t{tit}\n")
    print(f"informe_retos.tex generado ({len(tex):,} caracteres, {len(caps)} capturas previstas)")


if __name__ == "__main__":
    main()
