#!/usr/bin/env python3
"""Replica DecryptStringAES de ShellCodeLauncher.Program (payload .NET del x.xsl).

clave = PBKDF2-HMAC-SHA1(secreto, sal=UTF-16LE("Zangief"), 1000 iteraciones) -> 32 bytes (AES-256)
datos = Base64 -> [int32 longitud IV][IV][cifrado AES-CBC con PKCS#7]
secreto = contenido de 'dork' ("w10123") + "shark01"
El texto cifrado es el Base64 de la sección .UPX0 de a.exe (lo que a.exe escribe en el fichero 'p').

Uso: python3 dotnet_aes.py a.exe salida
"""
import base64
import hashlib
import re
import sys

import pefile
from Crypto.Cipher import AES

pe = pefile.PE(sys.argv[1])
sec = [s for s in pe.sections if s.Name.rstrip(b"\x00") == b".UPX0"][0]
b64 = re.match(rb"[A-Za-z0-9+/=]+", sec.get_data()).group()
datos = base64.b64decode(b64 + b"=" * (-len(b64) % 4))

secreto = "w10123" + "shark01"
sal = "Zangief".encode("utf-16le")
clave = hashlib.pbkdf2_hmac("sha1", secreto.encode(), sal, 1000, 32)
n = int.from_bytes(datos[:4], "little")
iv, cifrado = datos[4:4 + n], datos[4 + n:]
print(f"secreto: {secreto!r}  sal: UTF-16('Zangief')  clave: {clave.hex()}")
print(f"IV ({n} bytes): {iv.hex()}  cifrado: {len(cifrado):,} bytes")
claro = AES.new(clave, AES.MODE_CBC, iv).decrypt(cifrado)
pad = claro[-1]
claro = claro[:-pad] if 1 <= pad <= 16 and claro.endswith(bytes([pad]) * pad) else claro
open(sys.argv[2], "wb").write(claro)
print(f"descifrado: {len(claro):,} bytes, MD5 {hashlib.md5(claro).hexdigest()}, inicio {claro[:80]!r}")
