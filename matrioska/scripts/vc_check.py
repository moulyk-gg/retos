#!/usr/bin/env python3
"""Comprueba contraseñas contra la cabecera de un volumen TrueCrypt/VeraCrypt (solo cifrado AES).

Cabecera: sal = bytes 0..63; clave de cabecera = PBKDF2(prf, contraseña, sal, iteraciones, 64 bytes);
bytes 64..511 descifrados con AES-256-XTS (sector 0) deben empezar por b'VERA' o b'TRUE'.
Uso: python3 vc_check.py volumen contraseña1 [contraseña2 ...]
"""
import hashlib
import sys

from Crypto.Hash import RIPEMD160, SHA256, SHA512
from Crypto.Protocol.KDF import PBKDF2
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

vol = open(sys.argv[1], "rb").read(65536 + 512)
# (nombre, prf, iteraciones, firma esperada); también se prueba la cabecera oculta (offset 65536)
PRFS = [("VeraCrypt SHA-512", "sha512", 500000, b"VERA"), ("VeraCrypt SHA-256", "sha256", 500000, b"VERA"),
        ("TrueCrypt SHA-512", "sha512", 1000, b"TRUE"), ("TrueCrypt RIPEMD-160", "ripemd160", 2000, b"TRUE")]


def derivar(prf, pw, sal, it):
    if prf in ("sha512", "sha256"):
        return hashlib.pbkdf2_hmac(prf, pw, sal, it, 64)
    return PBKDF2(pw, sal, 64, it, hmac_hash_module=RIPEMD160)


for pw in sys.argv[2:]:
    for off, tipo in ((0, "normal"), (65536, "oculto")):
        hdr = vol[off:off + 512]
        if len(hdr) < 512:
            continue
        sal, cif = hdr[:64], hdr[64:512]
        for nombre, prf, it, firma in PRFS:
            k = derivar(prf, pw.encode(), sal, it)
            dec = Cipher(algorithms.AES(k), modes.XTS(b"\x00" * 16)).decryptor().update(cif)
            if dec[:4] in (b"VERA", b"TRUE"):
                print(f"[+] ¡ENCONTRADA! contraseña={pw!r} formato={nombre} volumen {tipo}")
                print(f"    cabecera: {dec[:64].hex()}")
                sys.exit(0)
    print(f"[-] {pw!r}: no")
print("Ninguna contraseña funcionó (con AES)")
