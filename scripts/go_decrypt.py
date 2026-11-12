#!/usr/bin/env python3
"""Go go go!: descifra la cadena AES-CFB embebida en LetsGo con las 3 claves candidatas.

Requiere: pip install pycryptodome
Uso: python3 go_decrypt.py
"""
import base64

from Crypto.Cipher import AES

CT_B64 = "wD5qPxNCP5yKQaYC7MzpWTNmZRQctNbaDCoJqGDSBkNjzwqkSQ_F7F6FYhFyD4Hk"  # rodata 0x159cb1
raw = base64.urlsafe_b64decode(CT_B64 + "=" * (-len(CT_B64) % 4))
iv, ct = raw[:16], raw[16:]
for key in (b"1KH1hb001Y09olUo", b"1KH1hb001Y09olU1", b"1KH1hb001Y09olU2"):
    pt = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=128).decrypt(ct)
    pad = pt[-1]
    ok = 1 <= pad <= 16 and pt.endswith(bytes([pad]) * pad)
    print(key.decode(), "->", pt[:-pad] if ok else pt, "(PKCS7 OK)" if ok else "")
