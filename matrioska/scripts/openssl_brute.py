import hashlib, sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
blob=open(sys.argv[1],'rb').read()
assert blob[:8]==b'Salted__'
salt=blob[8:16]; ct=blob[16:]
def evp(pw,md,klen,ivlen):
    d=b''; prev=b''
    while len(d)<klen+ivlen:
        prev=hashlib.new(md,prev+pw+salt).digest(); d+=prev
    return d[:klen], d[klen:klen+ivlen]
configs=[('aes-256-cbc',32,16),('aes-128-cbc',16,16),('aes-192-cbc',24,16)]
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    for md in ('md5','sha256'):
        for name,kl,il in configs:
            k,iv=evp(pw,md,kl,il)
            pt=Cipher(algorithms.AES(k),modes.CBC(iv)).decryptor().update(ct)
            pad=pt[-1]
            if 1<=pad<=16 and pt.endswith(bytes([pad])*pad):
                body=pt[:-pad]
                if body and all(32<=c<127 or c in (9,10,13) for c in body):
                    print(f'[+] pw={pw.decode("latin-1")!r} {name} {md} -> {body!r}'); sys.exit(0)
    if n%200000==0: print(n, flush=True)
print(f'ninguna de {n}')
