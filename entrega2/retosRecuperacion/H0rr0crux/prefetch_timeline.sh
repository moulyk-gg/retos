#!/usr/bin/env bash
# Línea de tiempo de ejecución a partir de los ficheros Prefetch (.pf) de Windows 10.
# Muestra: última ejecución (UTC) | nº de ejecuciones | ruta completa del ejecutable.
# Requiere: sccainfo (paquete libscca-utils)
# Uso: prefetch_timeline.sh <carpeta Prefetch> [filtro_regex]
set -u
dir="$1"; filtro="${2:-.}"
for f in "$dir"/*.pf; do
  out=$(sccainfo "$f" 2>/dev/null) || continue
  exe=$(printf '%s\n' "$out" | grep -m1 'Executable filename' | awk -F': ' '{print $2}')
  ruta=$(printf '%s\n' "$out" | grep -E 'Filename: [0-9]+' | grep -iF "\\$exe" | head -1 | awk -F': ' '{print $NF}')
  veces=$(printf '%s\n' "$out" | grep -m1 'Run count' | awk -F': ' '{print $2}')
  ultima=$(printf '%s\n' "$out" | grep -m1 'Last run time: 1' | awk -F': ' '{print $NF}')
  printf '%s | %s | %s\n' "$ultima" "$veces" "$ruta"
done | sed 's/\\VOLUME{[^}]*}//' | grep -iE "$filtro" | sort -t'|' -k1
