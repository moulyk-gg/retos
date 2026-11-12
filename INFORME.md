# Informe de retos CTF — Reversing y Forense

Formato de flag de la plataforma: `flag{md5}`, donde el md5 se calcula sobre el **valor** de la
flag, sin el prefijo `Flag: ` y sin salto de línea (`echo -n "valor" | md5sum`).
CCN-Cry ya fue validado en la plataforma con este criterio.

## Resumen de flags

| Reto | Dificultad | Valor encontrado | Flag a enviar | Estado |
|---|---|---|---|---|
| Reversing: CCN-Cry | ★★ | `JosephPopp1989` | `flag{c890082bbb38d2aad5eb182cac9fbc7e}` | ✅ validado en la plataforma |
| Reversing: The Kraken | ★★ | `Kongespeilet1250` | `flag{d11c2e023a6a0fb3105121dade32232b}` | ✅ verificado (terminador `\0` exacto) |
| Reversing: Spear Phishing… | ★ | `CVE-2017-0199` | `flag{93b146d21d3bdc8635836f8a11ba62b9}` | ✅ verificado con `rtfobj` |
| Reversing: Go go go! | ★★★ | `RobPike2009` | `flag{f389c15c0ea41f12e53806fba659e2fb}` | ✅ verificado (padding PKCS#7 válido) |
| H0rr0crux | ★ | `httpd.exe` (Cobalt Strike) — MD5 del binario | `flag{dbe0e10775e35a58e8ff463ccbe5f7d8}` | ✅ SRUM + Amcache + VirusTotal (61 detecciones) |

Hashes de los ficheros recibidos (todos coinciden con los del enunciado):

| Fichero | MD5 |
|---|---|
| `evidencia.zip` | `fc04df37aeca594a00cb1844c3bbb980` |
| `Secret.txt.CCN_CRY` | `fba2221b98cb79397ef87876c1c70938` |
| `TheKraken.exe` | `33b0654d8e104031155c999e2f163bbd` |
| `suspicious_.rar` | `6c51db1b0f92b7a8777c6822c2f9a8a5` |
| `LetsGo.zip` | `f6446fe1d43ecf9b26a6806d13528d11` |
| `evidencias_sorvologaunt.7z` | `130decf0165501e8e53148035b057bd5` |

---

## Preparación en Kali

> ⚠️ Ningún binario de malware se ejecuta en este procedimiento. Todo es análisis estático o
> emulación de CPU (Unicorn). Haz el trabajo en una VM de Kali desechable.

```bash
sudo apt update && sudo apt install -y 7zip unrar tshark xxd openssl binutils libscca-utils libesedb-utils python3-evtx python3-venv
```

```bash
python3 -m venv --system-site-packages ~/ctf-venv
```

```bash
source ~/ctf-venv/bin/activate
```

```bash
pip install unicorn capstone pefile pyelftools pycryptodome oletools regipy
```

Los scripts citados están en la carpeta `scripts/` de este repositorio.

```bash
export S=~/retos/scripts
```

---

## 1. Reversing: CCN-Cry ✅

**Enunciado:** un equipo fue cifrado por un ransomware; hay que descifrar `Secret.txt.CCN_CRY`.
Zip con contraseña `infected`.

### Qué hay

- `evidencia.zip` → `incident-a1000032.pcapng` (captura de red del incidente).
- En la captura: la víctima `192.168.1.41` (hostname `oat12`) descarga `wget.tar.gz` por HTTP,
  que contiene el ransomware `ccn_cry` (ELF x86-64), y luego hace
  `GET /user.php` a `www.aarkaposleeqaasssf.tk:8080`.
- **Cosa rara clave:** la cabecera `Content-type` no es un tipo MIME, es
  `gAu,UovL8;,B2fOT1xRZa?r3wpvD856r:B;?ShTiD:oat12` → **el ransomware exfiltra su clave**.

### Análisis del binario (estático)

- Importa `EVP_bf_cbc` → **Blowfish-CBC** (OpenSSL).
- `srand(time(0))` + `rand() % 78` sobre el alfabeto
  `a-zA-Z0-9,.-#@$%&(){};'?!` genera una cadena de **32** (clave) y otra de **8** (IV).
- Cabecera = `clave:iv:hostname`.
- **Trampa:** `EVP_CIPHER_CTX_set_key_length(ctx, 16)` → solo se usan los **16 primeros**
  caracteres de la clave de 32.

### Comandos

```bash
7z x -pinfected evidencia.zip
```

```bash
tshark -r incident-a1000032.pcapng -Y http.request -T fields -e ip.src -e ip.dst -e tcp.dstport -e http.host -e http.request.uri -e http.content_type
```

```bash
tshark -r incident-a1000032.pcapng --export-objects http,http_objs && tar -xzf http_objs/wget.tar.gz && file ccn_cry
```

```bash
objdump -T ccn_cry | grep -E 'EVP_|rand|time|gethostname'
```

```bash
objdump -d -M intel --no-show-raw-insn --start-address=0x2064 --stop-address=0x20db ccn_cry
```

```bash
CT=$(tshark -r incident-a1000032.pcapng -Y 'http.request.uri == "/user.php"' -T fields -e http.content_type)
```

```bash
KEY=$(printf '%s' "$CT" | cut -d: -f1 | cut -c1-16); IV=$(printf '%s' "$CT" | cut -d: -f2)
```

```bash
openssl enc -d -bf-cbc -provider legacy -provider default -K "$(printf '%s' "$KEY" | xxd -p)" -iv "$(printf '%s' "$IV" | xxd -p)" -in Secret.txt.CCN_CRY
```

Resultado: `Flag: JosephPopp1989`

```bash
echo -n "JosephPopp1989" | md5sum
```

### Contexto

- **CCN-Cry** = CCN (Centro Criptológico Nacional, del que depende el CCN-CERT español) +
  "Cry" de **WannaCry** (2017). La extensión `.CCN_CRY` imita la costumbre de los ransomware
  de renombrar ficheros (`.WNCRY` en WannaCry).
- El dominio de C2 `aarkaposleeqaasssf.tk` es una ristra aleatoria al estilo del famoso
  *kill-switch* de WannaCry (`iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com`).
- **Joseph Popp, 1989:** autor del **AIDS Trojan / PC Cyborg**, considerado el **primer ransomware
  de la historia**. Repartió ~20.000 disquetes a asistentes a la conferencia de la OMS sobre el
  SIDA; tras 90 arranques cifraba los nombres de ficheros y pedía 189 $ a un apartado postal de
  Panamá. Su cifrado era simétrico y la clave estaba en el propio código — igual que aquí, el
  fallo del ransomware es que la clave viaja/está disponible para el analista.
- **Blowfish:** cifrado de bloque de 64 bits de Bruce Schneier (1993). En OpenSSL 3 está en el
  *provider legacy*, por eso hace falta `-provider legacy`.
- Lección: un ransomware que manda la clave en claro por HTTP se descifra con la captura de red.
  Aunque no la mandara, `srand(time)` permitiría fuerza bruta sobre la hora de la infección.

---

## 2. Reversing: The Kraken ✅

**Enunciado:** "Encuentra la flag" en `TheKraken.exe` (932 bytes).

### Cosas raras

- PE de **932 bytes**, cabecera `MZ23PE`: el `PE\0\0` está en el offset 4, solapado con el MZ.
- **0 secciones** y `SizeOfImage` ≈ 500 MB.
- `file` lo confunde con .NET (falso positivo por la cabecera manipulada).
- Es el formato del compresor **Crinkler** (demoscene, intros de 4 KB). El `23` tras `MZ` es la
  versión (2.3). El *entry point* (0x5c) es un descompresor por *context mixing* que escribe el
  código real en `0x420000` y salta allí con un `ret`.

### Procedimiento

1. **Emular** el descompresor con Unicorn (sin ejecutar el exe) y volcar `0x420000`
   (`kraken_emu.py`, ~16 s).
2. El código desempaquetado:
   - **Resuelve imports por hash** (`rol edi,6 ; xor edi,char`) recorriendo el PEB hasta
     `kernel32.dll`. Hashes en el offset `0x108` del exe. Con la lista de exports de kernel32
     (`kernel32.spec` de Wine) se resuelven los 8: `GetACP`, `GetCurrentProcess`,
     `IsProcessorFeaturePresent`, `LoadLibraryA`, **`OutputDebugStringA`**,
     `SetUnhandledExceptionFilter`, `TerminateProcess`, `UnhandledExceptionFilter`.
   - `main` hace un bucle de relleno con `double`s que no sirve para nada (distracción), llama a
     **`GetACP()`** (página de códigos ANSI) y descifra 23 bytes:
     `c ^= 0x7C; c += ACP & 0xFF; c = -c; c = rol8(c,1); c -= i`.
   - El resultado sale por **`OutputDebugStringA`**: **no aparece en consola**, solo en un
     depurador o en DebugView. Por eso, ejecutándolo, "no hace nada".
3. Fuerza bruta de los 256 valores posibles del byte de `GetACP` → solo `0x44` da texto, y
   termina exactamente en `\0`: **`Flag: Kongespeilet1250`**.

### Comandos

```bash
python3 $S/kraken_emu.py TheKraken.exe unpacked.bin
```

```bash
curl -sSLo kernel32.spec https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/kernel32/kernel32.spec
```

```bash
python3 $S/kraken_solve.py TheKraken.exe kernel32.spec
```

```bash
echo -n "Kongespeilet1250" | md5sum
```

### Contexto

- ***Konungs skuggsjá*** (en noruego ***Kongespeilet***, "El espejo del rey") es un texto
  didáctico noruego de **hacia el año 1250**. Contiene la **primera descripción conocida del
  Kraken**, bajo el nombre de *hafgufa*: un monstruo marino tan grande que los marineros lo
  confundían con una isla. → La flag es literalmente "el origen del Kraken".
- Nombre del reto: el binario es pequeño y monstruoso por dentro, con el código "sumergido"
  y comprimido. Además, **Kraken** es también el nombre de un códec de compresión (Oodle Kraken).
- Técnicas reales de malware que enseña: packers mínimos, **resolución de APIs por hash**
  (shellcode, Cobalt Strike, etc.), salida oculta con `OutputDebugString` y dependencia de la
  configuración regional del sistema (`GetACP`), una forma de *environmental keying*.

---

## 3. Reversing: Spear Phishing… Can you catch me? ✅

**Enunciado:** un e-mail sospechoso con un documento "sin contenido" y formato poco común;
hay que decir qué **CVE** explota. RAR con contraseña `infected`.

### Qué hay

- `suspicious_.rar` (RAR 2.9, cifrado AES) → `Nominas.rtf` (5.725 bytes, fechado 09/09/2017).
- El RTF no tiene texto: solo un objeto OLE embebido:
  - `\object\objautlink\objupdate` → **se actualiza solo al abrir** el documento, sin clic.
  - Clase `OLE2Link` con CLSID `00000300-0000-0000-C000-000000000046` (StdOleLink).
  - **URL Moniker** (`79EAC9E0-BAF9-11CE-8C82-00AA004BA90B`) → `http://dagobah.local/logo.doc`.
- Patrón exacto de **CVE-2017-0199**: Word sigue el enlace, el servidor devuelve un **HTA**
  disfrazado de `.doc` y Windows lo ejecuta con `mshta.exe`.

### Por qué no es otra CVE de la familia

`rtfobj` avisa de que `OLE2Link` también se asocia con otras CVE:

| CVE | Rasgo característico | ¿Está aquí? |
|---|---|---|
| CVE-2017-8570 | *Composite Moniker* + scriptlet `.sct` | No |
| CVE-2017-8759 | `soap:wsdl=` (.NET SOAP moniker) | No |
| CVE-2018-8174 | VBScript "Double Kill" | No |
| **CVE-2017-0199** | **URL Moniker** a HTA vía `OLE2Link` | **Sí** |

### Comandos

```bash
unrar x -pinfected suspicious_.rar
```

```bash
rtfobj Nominas.rtf
```

```bash
grep -o 'objautlink\|objupdate\|OLE2Link\|4f4c45324c696e6b' Nominas.rtf | sort -u
```

```bash
echo -n "CVE-2017-0199" | md5sum
```

### Contexto

- **CVE-2017-0199:** RCE en Microsoft Office/WordPad con el manejador HTA. FireEye y McAfee la
  vieron explotada como 0-day en abril de 2017. Se parcheó el 11/04/2017 y la usaron Dridex,
  APT28, APT34 y muchas campañas de phishing durante años.
- **Dagobah:** planeta pantanoso de *Star Wars* donde Yoda vive escondido. El atacante "se
  esconde" en un servidor interno (`.local`).
- **"Nóminas":** cebo clásico de ingeniería social; todo el mundo abre un documento de nóminas.
- **"Can you catch me?":** juego de palabras con *phishing* (pescar) y *catch* (atrapar).
  *Spear phishing* es el phishing dirigido a una organización concreta.
- Dificultad ★ porque basta con `rtfobj`. La "trampa" es elegir bien entre las CVE parecidas.

---

## 4. Reversing: Go go go! ✅

**Enunciado:** obtener la flag del binario. Zip con contraseña `infected`.

### Cosas raras

- `LetsGo`: **ELF 32-bit MIPS big-endian** (arquitectura de routers/IoT), Go 1.10.3, *stripped*.
- Aunque esté *stripped*, Go conserva los nombres de funciones en `.gopclntab`. Parseándola
  (`go_pclntab.py`) aparecen `main.encrypt`, `main.Pad`, `addBase64Padding`, tres funciones con
  nombres ofuscados (`main.FWPmCP`, `main.PCCKsmOSrmbDMUGqoFINVL`, `main.quKuchsVvIEUGZDKOxl`) y las
  librerías `matishsiao/goInfo` (información del sistema) y `common-nighthawk/go-figure`
  (ASCII-art).
- Emulado con `qemu-mips`, **no imprime nada**: tiene condiciones de entorno.

### Lógica de `main.main` (desensamblado MIPS con Capstone, `go_mips_disasm.py`)

1. `goInfo.GetInfo()` → sigue solo si el **kernel contiene `4.14.0`**.
2. Prepara 3 claves AES casi iguales: `1KH1hb001Y09olU2` y `1KH1hb001Y09olU1` son
   **señuelos**. Solo **`1KH1hb001Y09olUo`** llega a `aes.NewCipher`.
3. Decodifica en Base64-URL `wD5q…D4Hk` (64 caracteres): IV = primeros 16 bytes, resto =
   cifrado. Lo descifra con **AES-128-CFB**.
4. `switch` sobre el **número de CPUs**: con 2 u 8 lanza goroutines señuelo que cifran otras
   cadenas (`Xa22SKeyAll1aadf1` y la variante `…D4Ha`). **Solo con 3 CPUs** quita el padding,
   comprueba que el SO sea `linux` y dibuja la flag con `go-figure`.

### Comandos

```bash
7z x -pinfected LetsGo.zip && file LetsGo
```

```bash
python3 $S/go_pclntab.py LetsGo main.
```

```bash
python3 $S/go_mips_disasm.py LetsGo main.main | grep -E 'jal|"'
```

```bash
python3 $S/go_decrypt.py
```

Resultado: `Flag: RobPike2009` (las otras claves dan basura y el padding PKCS#7 confirma la buena).

```bash
echo -n "RobPike2009" | md5sum
```

### Contexto

- **Rob Pike:** co-creador de **Go** en Google junto a Robert Griesemer y Ken Thompson (2007).
  Go se presentó públicamente el **10 de noviembre de 2009**. → "RobPike2009" = el padre de Go
  y el año de su nacimiento público.
- **"Go go go!" / "LetsGo":** juego con el nombre del lenguaje.
- **MIPS + Go:** combinación típica del malware IoT moderno. Go genera binarios estáticos
  fáciles de compilar para muchas arquitecturas.
- Técnicas que enseña: ***environmental keying*** (MITRE ATT&CK T1480.001: el payload solo se
  revela en un entorno concreto, con kernel 4.14.0, 3 CPUs y Linux), anti-sandbox, claves
  señuelo y goroutines de distracción.

---

## 5. H0rr0crux ✅

**Enunciado:** el SOC detectó conexiones sospechosas relacionadas con el malware **Gozi**. El
equipo fue **restaurado** tras recoger evidencias. Objetivo: `flag{<md5_binario>}` del binario
dañino responsable de las conexiones.

### Qué hay

`evidencias_sorvologaunt.7z` (870 MB → 2,6 GB, 17.550 ficheros): adquisición tipo KAPE de
`DESKTOP-VK0V8TR`, usuario **Gregor**, con `$MFT`, `$LogFile`, `Amcache.hve`, Prefetch, `.evtx`,
SRUM y logs del registro. Era una VM VirtualBox.

### Línea de tiempo (20/12/2021, UTC)

| Hora | Evento | Fuente |
|---|---|---|
| 12:50:49 | Se arrastra desde el host `runas.exe` | `$MFT` (VirtualBox Dropped Files) |
| 12:51:10 | Ejecuta `AppData\Local\Microsoft\uninstall.exe` | Prefetch, Amcache |
| 12:51:29 | Instalador Inno Setup (`PACKED.TMP`) → VMProtect Demo | Prefetch |
| 12:52:23–26 | Se arrastra `inject.exe` y **falla al arrancar** (faltan MSVCP140/VCRUNTIME140) | `$MFT`, System.evtx (ID 26) |
| 12:53:25 | `VMProtect.exe` | Prefetch |
| 12:56 / 13:08 / 15:03 | `AppData\runas.exe` ×3 | Prefetch |
| ~13:01–13:02 | Se cortan los logs Application/Security/System | `.evtx` |
| 13:08 y 15:04 | Defender detecta `inject.exe` como `Trojan:Win32/Sabsik.TE.A!ml` → cuarentena | Defender Operational |
| 13:09:01 y 15:07 | `AppData\Local\Temp\tor.exe` | Prefetch, Amcache |
| **13:09:30** | **Se arrastra `httpd.exe`** | `$MFT` (VirtualBox Dropped Files) |
| 13:10:39 y 13:11:57 | **`httpd.exe` se cuelga** (`WER\ReportArchive\AppCrash_httpd.exe_…`) | `$MFT` |
| 13:12 | `wevtutil` (12 ejecuciones en total) | Prefetch |
| **14:53–15:53** | **`AppData\Roaming\Microsoft\Windows\httpd.exe`: 800 B enviados / 1.214 B recibidos** | **SRUM** |
| 15:09–15:23 | El analista ejecuta FTK Imager y copia las evidencias a `Desktop\evidencias` | Prefetch, `$MFT` |

### Descarte de señuelos ("cosas raras" que no son la respuesta)

| Binario | Qué es en realidad | Por qué no es la respuesta |
|---|---|---|
| `Downloads\inject.exe` | `Sabsik.TE.A!ml` (detección genérica por ML) | **Nunca llegó a ejecutarse**: le faltaban DLLs. Defender lo puso en cuarentena |
| `AppData\runas.exe` | **SDelete** de Sysinternals renombrado (`OriginalFileName=sdelete.exe`) | Herramienta **antiforense**: borró el malware de forma irrecuperable |
| `AppData\Local\Microsoft\uninstall.exe` | **PE Look** (`pelook.exe`, bytepointer.com) renombrado | Visor de PE, sin funciones de red. Es el único que sigue en la evidencia |
| `packed.exe` / `PACKED.TMP` | Instalador de **VMProtect Demo** | Herramienta para empaquetar/proteger binarios |
| `Temp\tor.exe` | 231 KB, sin metadatos. VirusTotal: en realidad es **`tag_converter.exe`**, 3/70 detecciones, sin familia | Programa casi inocuo renombrado como Tor. **SRUM no le atribuye tráfico de red** |
| **`AppData\Roaming\Microsoft\Windows\httpd.exe`** | 15.360 bytes, PE32, **se hace pasar por Microsoft** (`ProductName = Microsoft Operating System`, versión `1.0.0.0`, compilado el 09/06/2020). VirusTotal: **Cobalt Strike**, 61 detecciones | ✅ **Es el único binario sospechoso con tráfico de red en SRUM** |

### Respuesta

- **Binario:** `C:\Users\Gregor\AppData\Roaming\Microsoft\Windows\httpd.exe`
- **SHA1 (Amcache):** `409aea9461d03bff3e006d3e7e7c4790a0862170`
- **MD5 (VirusTotal):** `dbe0e10775e35a58e8ff463ccbe5f7d8`
- **Flag:** `flag{dbe0e10775e35a58e8ff463ccbe5f7d8}`

El fichero se borró con SDelete y no está en la evidencia: no hay registro en la `$MFT` ni
coincidencias por hash o tamaño en los 17.548 ficheros. Por eso el MD5 sale de pivotar el
SHA1 de Amcache en VirusTotal.

Resultado de VirusTotal para los tres candidatos:

| Binario | SHA1 (Amcache) | MD5 (VirusTotal) | Nombre real | Familia | Detecciones |
|---|---|---|---|---|---|
| **`httpd.exe`** | `409aea94…0862170` | **`dbe0e10775e35a58e8ff463ccbe5f7d8`** | `httpd.exe` | **`trojan.cobaltstrike/fugrafa`** | **61** |
| `tor.exe` | `99e107ca…eaacc9e` | `3e6f1f16a4cbbf7c5a5c077ab197bb50` | `tag_converter.exe` | — | 3 |
| `inject.exe` | `de275b64…739a68a` | — (no está en VirusTotal) | — | — | — |

**Por qué la familia no es Gozi y aun así es la respuesta:** el enunciado dice que las
conexiones "*podrían* estar relacionadas con Gozi". Es una hipótesis del SOC, no un hecho. Lo
que piden es "el binario dañino **responsable de las conexiones**", y las evidencias lo señalan
sin ambigüedad: SRUM le atribuye tráfico de red, es el único de los tres que es malware
confirmado y además se disfraza de Microsoft. Las intrusiones de Gozi/Ursnif suelen terminar
desplegando **Cobalt Strike** como segunda fase, así que la sospecha inicial tiene sentido.

Consulta en Kali (necesita una clave de API gratuita de VirusTotal):

```bash
sudo apt install -y jq
```

```bash
VT_KEY="TU_API_KEY"
```

```bash
for h in 409aea9461d03bff3e006d3e7e7c4790a0862170 99e107ca419959385ca57241fb6ed3796eaacc9e de275b64985009d335ab85b38d26a3026739a68a; do echo "== $h"; curl -s -H "x-apikey: $VT_KEY" https://www.virustotal.com/api/v3/files/$h | jq -r '.data.attributes | "MD5: \(.md5)\nNombre: \(.meaningful_name)\nFamilia: \(.popular_threat_classification.suggested_threat_label)\nDetecciones: \(.last_analysis_stats.malicious)"'; sleep 16; done
```

### Comandos

```bash
7z x evidencias_sorvologaunt.7z -oevid && cd evid
```

Prefetch (qué se ejecutó, cuándo y desde dónde):

```bash
for f in Windows/Prefetch/{INJECT,RUNAS,TOR,PACKED,VMPROTECT,WEVTUTIL}*.pf; do sccainfo "$f" | grep -E 'Executable filename|Run count|Last run time: [12]\b'; done
```

Amcache (SHA1, metadatos y nombre original):

```bash
python3 $S/amcache_dump.py Windows/appcompat/Programs/Amcache.hve --todo | grep -i gregor
```

SRUM (quién usó la red):

```bash
cp Windows/System32/sru/SRUDB.dat /tmp/ && (cd /tmp && esedbexport -t srum SRUDB.dat)
```

```bash
python3 $S/srum_net.py /tmp/srum.export | grep -i 'users\\gregor'
```

Defender y errores de sistema:

```bash
python3 $S/evtx_grep.py "Windows/System32/winevt/Logs/Microsoft-Windows-Windows Defender%4Operational.evtx" inject
```

```bash
python3 $S/evtx_grep.py Windows/System32/winevt/Logs/System.evtx inject
```

`$MFT` (drag & drop desde el host y crashes de httpd.exe):

```bash
python3 $S/mft_record.py '$MFT' httpd.exe
```

PCA del registro del usuario (otra evidencia de ejecución):

```bash
strings -a Users/Gregor/ntuser.dat.LOG2 | grep -i httpd
```

Comprobar que el binario ya no está en la evidencia:

```bash
find . -type f -print0 | xargs -0 sha1sum | grep -i 409aea9461d03bff3e006d3e7e7c4790a0862170
```

### Contexto

- **Horrocrux (Harry Potter):** objeto donde Voldemort esconde un fragmento de su alma para no
  morir. Para vencerlo hay que encontrar y destruir todos.
- **Sorvolo Gaunt** (en inglés *Marvolo Gaunt*, abuelo de Voldemort): su **anillo con la Piedra de
  la Resurrección** es uno de los Horrocruxes, y es el anillo de la imagen del reto. El fichero
  se llama `evidencias_sorvologaunt`.
- **Paralelismo con el reto:** el "cuerpo" del malware fue destruido (borrado con SDelete y
  equipo restaurado), pero su "alma" quedó **fragmentada en varios artefactos**: Amcache (SHA1),
  SRUM (red), `$MFT` (drag & drop y crashes), PCA y Prefetch. Hay que reunir los fragmentos para
  identificarlo, igual que hay que localizar todos los Horrocruxes.
- **Gozi (Ursnif / ISFB / Dreambot):** troyano bancario de 2007, uno de los más longevos. Su
  código fuente se filtró en 2010 y en 2015, lo que generó decenas de variantes. Algunas usan
  **Tor** para el C2, y de ahí que el señuelo se llame `tor.exe`. En intrusiones reales Gozi
  actúa a menudo como *initial access* y después despliega **Cobalt Strike**.
- **Cobalt Strike:** plataforma comercial de *red team* (Raphael Mudge, 2012) cuyo agente se
  llama **Beacon**. Es de las herramientas más usadas por atacantes reales gracias a versiones
  crackeadas. Sus *stagers* `.exe` pesan unos 14–15 KB, como este `httpd.exe`. **Fugrafa** es el
  nombre genérico que dan algunos antivirus a binarios de este tipo.
- **Nombre `httpd.exe`:** imita al servidor web Apache (`httpd` = HTTP daemon). Un proceso
  llamado así haciendo tráfico HTTP no llama la atención. Además lleva metadatos falsos de
  Microsoft.
- Técnicas observadas (MITRE ATT&CK):
  - T1036 *Masquerading*: `httpd.exe` falsamente firmado como Microsoft, SDelete como `runas.exe`
    y `tag_converter.exe` como `tor.exe`.
  - T1070.001 *Clear Windows Event Logs*: `wevtutil`.
  - T1070.004 *File Deletion*: SDelete.
  - T1027.002 *Software Packing*: VMProtect.
  - Señuelos para despistar al analista: `inject.exe`, `tor.exe`.
