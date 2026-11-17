import hashlib, sys, re
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
it=int(sys.argv[3]) if len(sys.argv)>3 else 10000
hexre=re.compile(rb'^[0-9a-fA-F]{32}$')
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    km=hashlib.pbkdf2_hmac('sha256',pw,salt,it,48)
    pt=Cipher(algorithms.AES(km[:32]),modes.CBC(km[32:48])).decryptor().update(ct)
    if hexre.match(pt): print(f'[+++ HEX] pw={pw.decode("latin-1")!r} pbkdf2 it={it} -> {pt.decode()}'); sys.exit(0)
    pad=pt[-1]
    if 1<=pad<=16 and pt.endswith(bytes([pad])*pad):
        b=pt[:-pad]
        if b and all(32<=c<127 or c in(9,10,13) for c in b):
            print(f'[+] pw={pw.decode("latin-1")!r} pbkdf2 it={it} -> {b!r}'); sys.exit(0)
    if n%1000000==0: print(n,flush=True)
print(f'ninguna de {n} (pbkdf2 it={it})')
