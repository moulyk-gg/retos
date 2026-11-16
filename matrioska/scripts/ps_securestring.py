#!/usr/bin/env python3
"""Descifra una SecureString de PowerShell exportada con -Key (ConvertFrom-SecureString -Key ...).

Formato: '76492d1116743f0423413b16050a5345' + Base64( UTF-16LE("2|" + Base64(IV) + "|" + HEX(cifrado)) )
Cifrado: AES-CBC con la clave dada; el texto claro es UTF-16LE (con relleno PKCS#7).
Uso: python3 ps_securestring.py capa2.ps1 salida.ps1
     (busca la cadena 76492d11... y la clave en '-K(ey) (a..b)' dentro del script)
"""
import base64
import re
import sys

from Crypto.Cipher import AES

t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
m = re.search(r"76492d1116743f0423413b16050a5345([A-Za-z0-9+/=]+)", t)
k = re.search(r"-K\w*\s*\(\s*(\d+)\s*\.\.\s*(\d+)\s*\)", t)
a, b = int(k.group(1)), int(k.group(2))
clave = bytes(range(a, b - 1, -1) if a > b else range(a, b + 1))
interior = base64.b64decode(m.group(1)).decode("utf-16le")
version, iv_b64, cifrado_hex = interior.split("|")
iv, cifrado = base64.b64decode(iv_b64), bytes.fromhex(cifrado_hex)
print(f"clave ({len(clave)} bytes): {list(clave)}")
print(f"versión {version}, IV {iv.hex()}, cifrado {len(cifrado):,} bytes")
claro = AES.new(clave, AES.MODE_CBC, iv).decrypt(cifrado)
claro = claro[:-claro[-1]] if 1 <= claro[-1] <= 16 else claro
texto = claro.decode("utf-16le", "replace")
open(sys.argv[2], "w", encoding="utf-8").write(texto)
r = re.sub(r"\s+", " ", texto)
print(f"texto descifrado ({len(texto):,} caracteres)\n inicio: {r[:400]}\n final : {r[-250:]}")
