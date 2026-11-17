#!/usr/bin/env python3
"""Fuerza bruta rapida de la cabecera TrueCrypt: AES y Twofish en XTS, PRF RIPEMD-160 y SHA-512."""
import hashlib, sys
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import RIPEMD160
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from twofish import Twofish

vol=open(sys.argv[1],'rb').read()
salt,enc=vol[:64],vol[64:512]

def tf_xts_dec(k1,k2,data):
    t=Twofish(k2).encrypt((0).to_bytes(16,'little')); ci=Twofish(k1); out=bytearray()
    for i in range(0,len(data),16):
        x=bytes(a^b for a,b in zip(data[i:i+16],t)); d=ci.decrypt(x)
        out+=bytes(a^b for a,b in zip(d,t))
        n=int.from_bytes(t,'little'); c=n>>127; n=(n<<1)&((1<<128)-1)
        if c: n^=0x87
        t=n.to_bytes(16,'little')
    return bytes(out)

def try_pw(pw):
    pb=pw.encode('utf-8','ignore')
    for prf,it in (('ripemd',2000),('sha512',1000)):
        if prf=='ripemd': key=PBKDF2(pb,salt,64,it,hmac_hash_module=RIPEMD160)
        else: key=hashlib.pbkdf2_hmac('sha512',pb,salt,it,64)
        a=Cipher(algorithms.AES(key),modes.XTS(b'\0'*16)).decryptor().update(enc)
        if a[:4]==b'TRUE': return (pw,'AES',prf)
        tf=tf_xts_dec(key[:32],key[32:64],enc)
        if tf[:4]==b'TRUE': return (pw,'Twofish',prf)
    return None

src=sys.argv[2]
n=0
with open(src,'r',encoding='latin-1') as f:
    for line in f:
        pw=line.rstrip('\n')
        if not pw: continue
        n+=1
        r=try_pw(pw)
        if r: print(f'[+] ENCONTRADA: pw={r[0]!r} cifrado={r[1]} prf={r[2]}'); sys.exit(0)
        if n%2000==0: print(f'  ...{n} probadas', file=sys.stderr)
print(f'ninguna de {n} contrasenas')
