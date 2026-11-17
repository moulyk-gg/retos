import hashlib, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
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
    for md in ('md5','sha256','sha1'):
        km=evp(pw,md,48)
        for name,kl,il in cfgs:
            pt=Cipher(algorithms.AES(km[:kl]),modes.CBC(km[kl:kl+il])).decryptor().update(ct)
            # bloque de relleno completo => texto claro = 16 bytes exactos
            if pt[16:]==b'\x10'*16:
                print(f'[+++] pw={pw.decode("latin-1")!r} {name} {md}  md5_bytes={pt[:16].hex()}  texto={pt[:16]!r}'); sys.exit(0)
            # o padding valido con cuerpo imprimible (17-31 bytes)
            pad=pt[-1]
            if 1<=pad<=15 and pt.endswith(bytes([pad])*pad):
                b=pt[:-pad]
                if all(32<=c<127 for c in b):
                    print(f'[+] pw={pw.decode("latin-1")!r} {name} {md} -> {b!r}'); sys.exit(0)
    if n%2000000==0: print(n,flush=True)
print(f'ninguna de {n}')
