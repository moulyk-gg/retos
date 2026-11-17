import hashlib, sys, re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
hexre=re.compile(rb'^[0-9a-fA-F]{32}$'); printre=re.compile(rb'^[\x20-\x7e]{20,32}$')
def evp(pw,md,need):
    d=b''; prev=b''
    while len(d)<need: prev=hashlib.new(md,prev+pw+salt).digest(); d+=prev
    return d
cfgs=[('aes-256-cbc',32,16),('aes-128-cbc',16,16)]
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    for md in ('md5','sha256'):
        km=evp(pw,md,48)
        for name,kl,il in cfgs:
            pt=Cipher(algorithms.AES(km[:kl]),modes.CBC(km[kl:kl+il])).decryptor().update(ct)
            if hexre.match(pt): print(f'[+++ MD5 HEX] pw={pw.decode("latin-1")!r} {name} {md} -> {pt.decode()}'); sys.exit(0)
            # tambien nopad imprimible, o padding valido imprimible
            pad=pt[-1]
            body=pt[:-pad] if 1<=pad<=16 and pt.endswith(bytes([pad])*pad) else None
            if body and len(body)>=4 and printre.match(body+b' '*0) and all(32<=c<127 for c in body):
                print(f'[+] pw={pw.decode("latin-1")!r} {name} {md} (pad) -> {body!r}'); sys.exit(0)
    if n%1000000==0: print(n,flush=True)
print(f'ninguna de {n}')
