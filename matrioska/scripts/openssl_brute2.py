import hashlib, sys
from Crypto.Cipher import DES, DES3, Blowfish, CAST, ARC2
blob=open(sys.argv[1],'rb').read(); salt=blob[8:16]; ct=blob[16:]
def evp(pw,md,need):
    d=b''; prev=b''
    while len(d)<need:
        prev=hashlib.new(md,prev+pw+salt).digest(); d+=prev
    return d
# (nombre, modulo, keylen, ivlen)
cfgs=[('des',DES,8,8),('des3',DES3,24,8),('bf',Blowfish,16,8),('cast',CAST,16,8),('rc2',ARC2,16,8)]
def ok(pt):
    if not pt: return False
    pad=pt[-1]
    if not (1<=pad<=8 and pt.endswith(bytes([pad])*pad)): return False
    b=pt[:-pad]
    return bool(b) and all(32<=c<127 or c in (9,10,13) for c in b)
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n').encode('utf-8','ignore')
    if not pw: continue
    n+=1
    for md in ('md5','sha256'):
        km=evp(pw,md,32+8)
        for name,mod,kl,il in cfgs:
            try:
                k=km[:kl]; iv=km[kl:kl+il]
                pt=mod.new(k,mod.MODE_CBC,iv).decrypt(ct)
            except Exception: continue
            if ok(pt):
                pad=pt[-1]; print(f'[+] pw={pw.decode("latin-1")!r} {name} {md} -> {pt[:-pad]!r}'); sys.exit(0)
    if n%300000==0: print(n,flush=True)
print(f'ninguna de {n}')
