#!/usr/bin/env python3
"""Prueba contrasenas contra un volumen TrueCrypt cifrado con Twofish (modo XTS)."""
import hashlib, sys
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import RIPEMD160
from twofish import Twofish

def xts_decrypt(cipher_factory, key1, key2, data, unit=0):
    tw=Twofish(key2)
    t=tw.encrypt(unit.to_bytes(16,'little'))
    ci=Twofish(key1); out=bytearray()
    for i in range(0,len(data),16):
        blk=data[i:i+16]
        x=bytes(a^b for a,b in zip(blk,t))
        d=ci.decrypt(x)
        out+=bytes(a^b for a,b in zip(d,t))
        # t = t * alpha en GF(2^128)
        n=int.from_bytes(t,'little'); c=(n>>127)&1; n=((n<<1)&((1<<128)-1))
        if c: n^=0x87
        t=n.to_bytes(16,'little')
    return bytes(out)

vol=open(sys.argv[1],'rb').read()
pws=sys.argv[2:] or ['atari v01032']
for off,label in ((0,'normal'),(65536,'oculta')):
    hdr=vol[off:off+512]
    if len(hdr)<512: continue
    salt,enc=hdr[:64],hdr[64:512]
    for pw in pws:
        for prf,it in (('sha512',1000),('ripemd',2000),('whirlpool',1000)):
            try:
                if prf=='ripemd': key=PBKDF2(pw.encode(),salt,64,it,hmac_hash_module=RIPEMD160)
                elif prf=='whirlpool':
                    import hashlib as h
                    key=PBKDF2(pw.encode(),salt,64,it,prf=lambda p,s:__import__('hmac').new(p,s,'whirlpool').digest()) if 'whirlpool' in hashlib.algorithms_available else None
                    if key is None: continue
                else: key=hashlib.pbkdf2_hmac(prf,pw.encode(),salt,it,64)
            except Exception: continue
            dec=xts_decrypt(Twofish,key[:32],key[32:64],enc)
            if dec[:4]==b'TRUE':
                print(f'[+] TWOFISH ENCONTRADA pw={pw!r} {prf} cab {label}'); print('   ',dec[:64].hex()); sys.exit(0)
print('Twofish-XTS: ninguna')
