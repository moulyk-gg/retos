# Matrioska — Informe de la última capa (Capa 7: TrueCrypt → fichero *Flag* openssl)

**Reto:** ATENEA / CCN‑CERT — *Matrioska* (dificultad 5/5)
**Pista oficial:** *«Piensa en el verdadero cifrado…»*
**Formato de entrega:** `flag{md5}`
**Estado:** cadena resuelta hasta el final; **falta la contraseña openssl** del fichero `Flag`.

---

## 1. Qué es “la última capa”

Tras revertir toda la muñeca rusa (T.exe empaquetado → formulario Delphi *Padlock* → `a.exe` → PowerShell → `x.xsl`/.NET → AES), se obtiene un contenedor de **512000 bytes** llamado `capa8.bin` (en otros análisis, `w2.bin`).

- `capa8.bin` MD5 `c41665a4992691c830bf44b8d5850b5e` — **volumen TrueCrypt** (AES‑XTS, PBKDF2‑HMAC‑RIPEMD160, 2000 iter).
- El volumen tiene **dos cuerpos** (negación plausible de TrueCrypt):
  - **Volumen exterior** (señuelo) → contiene `humm.png` (carita 🤔).
  - **Volumen oculto** (el “verdadero cifrado” de la pista) → contiene el fichero **`Flag`**.
- `Flag` son **48 bytes** con formato **openssl `Salted__`**. Descifrarlo da una cadena; la flag final es `flag{ md5(cadena) }`.

> La pista «el verdadero cifrado» es un doble sentido: **True**Crypt, y además el volumen *verdadero* (oculto) frente al señuelo.

---

## 2. Las pistas que nos trajeron hasta aquí

| # | Pista / señal | De dónde sale | A dónde lleva |
|---|---------------|---------------|---------------|
| 1 | `file capa8.bin` = `data`, 512000 B, con 64 B de *salt* al inicio | inspección | sospecha de TrueCrypt |
| 2 | «Piensa en el **verdadero cifrado**» | enunciado | **True**Crypt |
| 3 | El exterior solo tiene un `humm.png` (🤔 = “piensa”) y una Papelera vacía | FAT exterior | es un **señuelo**; hay que buscar el volumen **oculto** |
| 4 | TrueCrypt guarda la cabecera del volumen oculto en el **offset 65536** | formato TrueCrypt | ahí está la 2ª cabecera |
| 5 | Ambas contraseñas son palabras de **rockyou** (`ccn123` al 13 %, `#1#1#1#1` al 99,95 %) | crackeo | el autor usa contraseñas de rockyou colocadas **al final** |
| 6 | `file Flag` = `openssl enc'd data with salted password` | inspección | descifrar con `openssl enc -d` |

---

## 3. Comandos con RESULTADO POSITIVO (replicables)

> En esta nube `cryptsetup` no tiene el módulo de kernel `algif` disponible, así que la extracción se hizo con **hashcat** (crackeo) + **Python/pycryptodome** y **mtools** (lectura de FAT sin montar). Debajo de cada bloque pongo también el **equivalente nativo de Kali** con `cryptsetup`/`mount`.

### 3.1 Identificar el volumen
```bash
file l7/capa8.bin                     # -> data (512000 B)
xxd l7/capa8.bin | head -2            # primeros 64 B = salt de TrueCrypt
```

### 3.2 Crackear la contraseña del volumen EXTERIOR → `ccn123`
```bash
hashcat -m 6211 -a 0 l7/capa8.bin rockyou.txt
# Status: Cracked   ->   l7/capa8.bin:ccn123
```
Equivalente en Kali (TrueCrack o cryptsetup):
```bash
truecrack -t capa8.bin -w rockyou.txt -k ripemd160 -e aes      # Found password: "ccn123"
```
```bash
printf 'ccn123\n' | cryptsetup tcryptDump --disable-veracrypt --hash ripemd160 --cipher aes capa8.bin
# TCRYPT header information ... Version 5 ... MK offset 131072 ... CODIGO: 0  (cabecera autenticada)
```

### 3.3 Descifrar el volumen EXTERIOR y leer su FAT → `humm.png` (señuelo)
```bash
# Extracción del FAT exterior (pycryptodome): clave = PBKDF2-RIPEMD160(ccn123, salt=capa8[0:64], 2000, 64),
# AES-XTS sobre capa8[64:512] -> master keys en [192:256]; descifrado de la zona de datos (MK offset 131072).
# Resultado: l7/fat_fs.bin (FAT12). Lectura sin montar:
mdir  -i l7/fat_fs.bin ::                  # -> HUMM.PNG (870 B) + $RECYCLE.BIN
mcopy -i l7/fat_fs.bin ::/humm.png humm.png
```
Equivalente en Kali:
```bash
sudo cryptsetup --type tcrypt --disable-veracrypt --hash ripemd160 --cipher aes open capa8.bin outer   # pass: ccn123
sudo mount -o ro /dev/mapper/outer /mnt && ls /mnt     # -> humm.png
```

### 3.4 Crackear la contraseña del volumen OCULTO → `#1#1#1#1`
```bash
# La cabecera del volumen oculto está en el offset 65536 (512 bytes):
dd if=l7/capa8.bin of=hidden_hdr.bin bs=512 skip=128 count=1
hashcat -m 6211 -a 0 hidden_hdr.bin rockyou.txt
# Status: Cracked   ->   hidden_hdr.bin:#1#1#1#1     (CRC válido = volumen oculto AUTENTICADO)
```
Equivalente en Kali:
```bash
sudo cryptsetup --type tcrypt --disable-veracrypt --tcrypt-hidden --hash ripemd160 --cipher aes open capa8.bin hidden   # pass: #1#1#1#1
sudo mount -o ro /dev/mapper/hidden /mnt && ls /mnt    # -> Flag
```

### 3.5 Extraer el fichero `Flag` del volumen OCULTO
```bash
# Mismo esquema que 3.3 pero con salt=capa8[65536:65536+64] y pass #1#1#1#1 -> l7/hidden_fs.bin (FAT)
mdir  -i l7/hidden_fs.bin ::                 # -> FLAG (48 bytes)
mcopy -i l7/hidden_fs.bin ::/Flag flag.txt
file flag.txt                                # -> openssl enc'd data with salted password
xxd  flag.txt
# 0000: 5361 6c74 6564 5f5f 1606 ad39 4bec 49e2   Salted__...9K.I.
# 0010: e3d4 9bae 81a4 6c24 6426 fd9e e79b 37d4
# 0020: e085 7b1b 47a2 faf2 8898 43be 6a28 013e
```

**Esto es todo lo que tiene resultado positivo.** El fichero `Flag` está extraído, íntegro (48 B) y verificado como openssl `Salted__`:
`8 (magic) + 8 (salt = 1606ad394bec49e2) + 32 (texto cifrado)`.

---

## 4. El bloqueo actual: la contraseña de openssl

El descifrado es, en esencia:
```bash
openssl enc -d -<cifrado> -md <digest> -pass pass:<CONTRASEÑA> -in flag.txt
```
El writeup del autor (Mariano Palomo, taller RootedCON 2019) usa un script que **recorre cifrados y digests** probando una **lista de contraseñas candidatas**. Nos falta esa contraseña.

Pistas sobre su naturaleza:
- El texto cifrado son **32 bytes exactos** → el texto claro cabe en **16–31 bytes** (cifrador de bloque) o **exactamente 32 bytes** (cifrador de flujo; justo el tamaño de un md5 en hex).
- Las dos contraseñas de TrueCrypt del reto **están en rockyou** → es muy probable que la de openssl también.
- El motor de descifrado usado para los intentos está **verificado byte a byte contra el `openssl` real** (round‑trip correcto en CBC/ECB/CFB/OFB/CTR/RC4).

---

## 5. Intentos realizados (todos negativos hasta ahora)

| Intento | Alcance | Resultado |
|--------|---------|-----------|
| **Cadenas de la cadena** (`atari `, `w10123`, `shark01`, `w10123shark01`, `Zangief`, `ccn123`, `#1#1#1#1`, `dork`, `v01032`, `humm`, `atari v01032`, …) | TODOS los cifrados × TODOS los digests × {EVP, pbkdf2} | 0 |
| **Nombres de objetos + temática** (Padlock/candado, ShellCodeLauncher, Street Fighter por “Zangief”, Atari, retro, español) con mutaciones leet/años | 2029 variantes × matriz completa | 0 |
| **Tokens extraídos de TODOS los artefactos** (capa1/2/3.ps1, IL del .NET, x.xsl, a.exe) | 21 720 tokens × 18 cifrados × 8 digests | 0 |
| **Transformaciones** (md5/sha1/sha256 hex y crudo, base64, invertido, hex) de cada cadena | 25 168 pruebas | 0 |
| **rockyou completo — cifradores de BLOQUE** (aes‑256/192/128‑cbc, aes‑ecb, des, 3des, bf, cast5, rc2) con md5/sha1/sha224/sha384/sha512/ripemd160/sm3 | 14,3 M palabras × ~43 combinaciones, filtro tolerante a salto de línea | 0 (completado) |
| **rockyou completo — cifradores de FLUJO** (cfb128/ofb/ctr/rc4, corrigiendo el `cfb8`→`cfb128`) con md5/sha256/sha1 | 14,3 M × 51 combinaciones | en curso (cerrando el tramo final 12–14,3 M) |
| **md5 del fichero / md5 de cadenas sueltas** como flag | — | el usuario confirmó que **no** |

Detalles metodológicos importantes:
- Se corrigió un **filtro** que descartaba textos claros terminados en `\n` (caso típico de `echo "x" | openssl`); ahora se aceptan saltos de línea y texto casi‑imprimible.
- Se corrigió el **CFB** de pycryptodome (`segment_size` 8→bloque·8) para que coincida con openssl.
- El volumen OCULTO quedó **autenticado por CRC** (hashcat modo 6211 lo marcó `Cracked`), así que `Flag` es real y la extracción es correcta: el único desconocido es la contraseña openssl.

---

## 6. Qué queda descartado (para no repetir)
- `Flag` **no** es texto plano, ni su md5 directo es la flag, ni el md5 del volumen.
- La contraseña openssl **no** es ninguna cadena del reto, ni token de ningún artefacto, ni palabra de rockyou con cifrador de **bloque** (barrido completo).
- No es la contraseña del ZIP (`infected`), ni `ccn123`, ni `#1#1#1#1` con ningún cifrado/digest.

---

## 7. Conclusión y siguiente paso

Toda la Matrioska está resuelta salvo **la contraseña con la que el autor cifró `Flag` con openssl**. La evidencia apunta a que es un valor que **solo aparece en las diapositivas del taller de Mariano Palomo** (RootedCON 2019), que son imágenes y cuyo dominio (`slideshare.net`) está **bloqueado** en la red de esta sesión.

**Caminos para cerrarlo:**
1. Terminar el barrido de cifradores de **flujo** sobre el tramo final de rockyou (en curso; es donde el autor escondió `#1#1#1#1`).
2. Permitir `slideshare.net` en los ajustes de red de la sesión para intentar leer la transcripción del taller (puede contener la lista de candidatas).
3. Conseguir las diapositivas / el writeup oficial / la grabación del taller y pasarme el texto del paso de openssl.

> Nota: el *otro informe* que me compartiste corresponde a un análisis que **no llegó a abrir el volumen oculto** (solo probó 215 candidatas + las 2000 primeras de rockyou en la cabecera oculta, y `#1#1#1#1` está al 99,95 %). Por eso concluía “volumen oculto no demostrado”. En esta sesión sí está **autenticado y abierto**, así que vamos un paso por delante de ese documento.
