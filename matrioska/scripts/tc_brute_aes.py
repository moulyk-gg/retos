import hashlib, sys
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import RIPEMD160
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
vol=open(sys.argv[1],'rb').read(); salt,enc=vol[:64],vol[64:512]
lim=int(sys.argv[3]) if len(sys.argv)>3 else 0
n=0
for line in open(sys.argv[2],'r',encoding='latin-1'):
    pw=line.rstrip('\n')
    if not pw: continue
    n+=1
    if lim and n>lim: break
    pb=pw.encode('utf-8','ignore')
    k1=hashlib.pbkdf2_hmac('sha512',pb,salt,1000,64)
    if Cipher(algorithms.AES(k1),modes.XTS(b'\0'*16)).decryptor().update(enc)[:4]==b'TRUE':
        print(f'[+] {pw!r} AES SHA512'); sys.exit(0)
    k2=PBKDF2(pb,salt,64,2000,hmac_hash_module=RIPEMD160)
    if Cipher(algorithms.AES(k2),modes.XTS(b'\0'*16)).decryptor().update(enc)[:4]==b'TRUE':
        print(f'[+] {pw!r} AES RIPEMD160'); sys.exit(0)
    if n%5000==0: print(f'{n}', flush=True)
print(f'AES: ninguna de {n}')
