import hashlib, sys
from Crypto.Cipher import DES3
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
md=sys.argv[3] if len(sys.argv)>3 else 'md5'
def ok(pt):
    pad=pt[-1]
    if not(1<=pad<=8 and pt.endswith(bytes([pad])*pad)): return None
    b=pt[:-pad]
    if b and all(32<=c<127 or c in (9,10,13) for c in b): return b
    return None
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    d=b'';p=b''
    while len(d)<32: p=hashlib.new(md,p+pw+salt).digest(); d+=p
    try: pt=DES3.new(d[:24],DES3.MODE_CBC,d[24:32]).decrypt(ct)
    except: continue
    b=ok(pt)
    if b is not None: print(f'[+] des3-cbc {md} pw={pw.decode("latin-1")!r} -> {b!r}'); sys.exit(0)
    if n%2000000==0: print(n,flush=True)
print(f'ninguna de {n} ({md})')
