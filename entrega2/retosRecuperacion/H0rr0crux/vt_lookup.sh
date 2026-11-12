#!/usr/bin/env bash
# Consulta hashes (MD5/SHA1/SHA256) en la API v3 de VirusTotal y muestra MD5, nombre,
# familia sugerida y número de detecciones.
# Requiere: curl, jq y una clave de API gratuita de VirusTotal en la variable VT_KEY.
# Uso: VT_KEY="tu_clave" bash vt_lookup.sh HASH [HASH ...]
# La API gratuita admite 4 consultas por minuto: se espera 16 s entre consultas.
set -u
: "${VT_KEY:?Define VT_KEY con tu clave de API de VirusTotal}"
n=0
for h in "$@"; do
  [ "$n" -gt 0 ] && sleep 16
  n=$((n + 1))
  echo "== $h"
  curl -s -H "x-apikey: $VT_KEY" "https://www.virustotal.com/api/v3/files/$h" | jq -r '
    .data.attributes
    | "MD5: \(.md5)\nNombre: \(.meaningful_name)\nFamilia: \(.popular_threat_classification.suggested_threat_label)\nDetecciones: \(.last_analysis_stats.malicious)"'
done
