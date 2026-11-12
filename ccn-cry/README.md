# Reversing: CCN-Cry — Writeup

**Flag:** `JosephPopp1989`
**MD5 de la flag:** `c890082bbb38d2aad5eb182cac9fbc7e`

> El contenido descifrado completo es `Flag: JosephPopp1989`. El MD5 de ese texto completo
> sería `22c4d9e76544c9d7300da7c09752bea3`, por si la plataforma pidiera la línea entera.

Archivos del reto:

| Archivo | MD5 |
|---|---|
| `evidencia.zip` (contraseña `infected`) | `fc04df37aeca594a00cb1844c3bbb980` |
| `Secret.txt.CCN_CRY` | `fba2221b98cb79397ef87876c1c70938` |

---

## Resumen

1. `evidencia.zip` contiene una captura de red `incident-a1000032.pcapng`.
2. En la captura, la víctima (`192.168.1.41`, hostname `oat12`) descarga `wget.tar.gz` por HTTP,
   que contiene el ransomware `ccn_cry` (ELF x86-64).
3. Luego el ransomware "llama a casa" a `www.aarkaposleeqaasssf.tk:8080/user.php` y **exfiltra
   la clave en la cabecera `Content-type`**: `clave(32):iv(8):hostname`.
4. Análisis estático del binario: cifra con **Blowfish-CBC** (`EVP_bf_cbc`) y fija la longitud de
   clave a **16 bytes** → solo se usan los primeros 16 caracteres de la clave de 32.
5. Se descifra con OpenSSL usando esa clave e IV.

---

## Comandos para Kali

> ⚠️ **No ejecutes `ccn_cry`**: es el ransomware y cifraría tus archivos. Todo el análisis es estático.

### 0. Herramientas (Kali ya las trae casi todas)

```bash
sudo apt update && sudo apt install -y 7zip tshark xxd openssl binutils
```

### 1. Verificar los archivos y descomprimir la evidencia

```bash
mkdir ~/ccn-cry && cd ~/ccn-cry
```

(copia aquí `evidencia.zip` y `Secret.txt.CCN_CRY`)

```bash
md5sum evidencia.zip Secret.txt.CCN_CRY
```

El zip usa cifrado AES, así que `unzip` no sirve (`need PK compat. v5.1`). Se usa `7z`:

```bash
7z x -pinfected evidencia.zip
```

### 2. Ver qué pasó en la red

```bash
tshark -r incident-a1000032.pcapng -q -z conv,tcp
```

```bash
tshark -r incident-a1000032.pcapng -Y http.request -T fields -e ip.src -e ip.dst -e tcp.dstport -e http.host -e http.request.uri -e http.content_type
```

Salida:

```
192.168.1.41  192.168.1.37  80    192.168.1.37               /wget.tar.gz
192.168.1.41  192.168.1.37  8080  www.aarkaposleeqaasssf.tk  /user.php  gAu,UovL8;,B2fOT1xRZa?r3wpvD856r:B;?ShTiD:oat12
```

### 3. Extraer el malware de la captura

```bash
tshark -r incident-a1000032.pcapng --export-objects http,http_objs
```

```bash
tar -xzf http_objs/wget.tar.gz
```

```bash
file ccn_cry
```

### 4. Análisis estático del binario

Funciones importadas y cadenas interesantes:

```bash
objdump -T ccn_cry | grep -E 'EVP_|rand|time|gethostname'
```

```bash
strings ccn_cry | grep -E 'CCN_CRY|Content-type|user.php|aarkap|abcdef'
```

Se ve `EVP_bf_cbc` (Blowfish-CBC), `srand(time(0))` + `rand()`, y el alfabeto
`abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-#@$%&(){};'?!` (78 caracteres).

Generación de clave (32 chars) e IV (8 chars) y lectura del hostname:

```bash
objdump -d -M intel --no-show-raw-insn --start-address=0x1cdf --stop-address=0x1d4d ccn_cry
```

- `mov edi,0x8` → `call 0x19f4` → cadena aleatoria de **8** → IV
- `mov edi,0x20` → `call 0x19f4` → cadena aleatoria de **32** → clave
- `gethostname`

Función generadora (`charset[rand() % 78]`, `0x4e = 78`):

```bash
objdump -d -M intel --no-show-raw-insn --start-address=0x19f4 --stop-address=0x1a97 ccn_cry
```

Construcción de la cabecera `Content-type` → `campo1 ":" campo2 ":" campo3 "\n"`:

```bash
objdump -d -M intel --no-show-raw-insn --start-address=0x165d --stop-address=0x17d3 ccn_cry
```

Configuración del cifrado — **longitud de clave = 16 bytes** (`mov esi,0x10` antes de `EVP_CIPHER_CTX_set_key_length`):

```bash
objdump -d -M intel --no-show-raw-insn --start-address=0x2064 --stop-address=0x20db ccn_cry
```

### 5. Sacar clave e IV de la captura y descifrar

```bash
CT=$(tshark -r incident-a1000032.pcapng -Y 'http.request.uri == "/user.php"' -T fields -e http.content_type)
```

```bash
KEY=$(printf '%s' "$CT" | cut -d: -f1 | cut -c1-16)
```

```bash
IV=$(printf '%s' "$CT" | cut -d: -f2)
```

```bash
echo "KEY=[$KEY]  IV=[$IV]"
```

Debe mostrar `KEY=[gAu,UovL8;,B2fOT]  IV=[B;?ShTiD]`.

Blowfish está en el provider *legacy* de OpenSSL 3, por eso se añade `-provider legacy -provider default`:

```bash
openssl enc -d -bf-cbc -provider legacy -provider default -K "$(printf '%s' "$KEY" | xxd -p)" -iv "$(printf '%s' "$IV" | xxd -p)" -in Secret.txt.CCN_CRY -out Secret.txt
```

```bash
cat Secret.txt
```

Resultado: `Flag: JosephPopp1989`

Equivalente con los valores en hexadecimal ya calculados:

```bash
openssl enc -d -bf-cbc -provider legacy -provider default -K 6741752c556f764c383b2c4232664f54 -iv 423b3f5368546944 -in Secret.txt.CCN_CRY
```

### 6. MD5 de la flag

```bash
echo -n "JosephPopp1989" | md5sum
```

→ `c890082bbb38d2aad5eb182cac9fbc7e`

---

## Notas

- Joseph Popp fue el autor del troyano **AIDS (1989)**, considerado el primer ransomware.
- Error típico: usar la clave completa de 32 caracteres. El binario hace
  `EVP_CIPHER_CTX_set_key_length(ctx, 16)`, así que solo cuentan los 16 primeros.
- `echo -n` es importante: sin `-n` se añade un salto de línea y el MD5 cambia.
