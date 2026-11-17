import hashlib, sys
from Crypto.Cipher import DES, CAST, ARC2
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
cfgs=[('des',DES,8,8),('cast',CAST,16,8),('rc2',ARC2,16,8)]
def ok(pt):
    pad=pt[-1]
    if not(1<=pad<=8 and pt.endswith(bytes([pad])*pad)): return None
    b=pt[:-pad]
    return b if (b and all(32<=c<127 or c in(9,10,13) for c in b)) else None
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    for md in ('md5','sha256'):
        d=b'';p=b''
        while len(d)<24: p=hashlib.new(md,p+pw+salt).digest(); d+=p
        for name,mod,kl,il in cfgs:
            try: pt=mod.new(d[:kl],mod.MODE_CBC,d[kl:kl+il]).decrypt(ct)
            except: continue
            b=ok(pt)
            if b is not None: print(f'[+] {name} {md} pw={pw.decode("latin-1")!r} -> {b!r}'); sys.exit(0)
    if n%2000000==0: print(n,flush=True)
print(f'ninguna de {n}')
