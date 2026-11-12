# -*- coding: utf-8 -*-
"""Definición de los pasos del informe (comando exacto + explicación LaTeX + captura).

Cada paso:
  id      identificador (también nombre de la captura: capturas/<id>.png)
  titulo  título corto del paso
  texto   explicación LaTeX antes del comando
  cmd     comando EXACTO (zsh de Kali)
  run     si se ejecuta en la réplica para obtener la salida real
  lineas  máximo de líneas de salida a mostrar (None = todas)
  nota    texto LaTeX después de la salida
  manual  salida fija (cuando no se puede ejecutar en la réplica)
"""

import re

SECCIONES = []
ANCHO = 90  # columnas máximas de un comando antes de partirlo con "\\" (continuación de shell)


def _trozos(linea):
    """Divide una línea en trozos separados por espacios que estén fuera de comillas."""
    trozos, cur, q = [], "", None
    for i, c in enumerate(linea):
        if q:
            cur += c
            if c == q and not (q == '"' and linea[i - 1] == "\\"):
                q = None
        elif c in "'\"":
            q = c
            cur += c
        elif c == " ":
            if cur:
                trozos.append(cur)
            cur = ""
        else:
            cur += c
    if cur:
        trozos.append(cur)
    return trozos


def partir(cmd, ancho=ANCHO):
    """Parte las líneas largas en espacios fuera de comillas, terminando con ' \\' (válido en bash y zsh)."""
    out = []
    for linea in cmd.splitlines():
        if len(linea) <= ancho:
            out.append(linea)
            continue
        actual = ""
        trozos = _trozos(linea)
        unidos = []  # una opción corta (-e, -K, -iv...) se mantiene pegada a su argumento
        for t in trozos:
            if unidos and re.fullmatch(r"-[A-Za-z]{1,3}", unidos[-1]):
                unidos[-1] += " " + t
            else:
                unidos.append(t)
        for t in unidos:
            cand = (actual + " " + t) if actual else t
            if actual and len(cand) + 2 > ancho:
                out.append(actual + " \\")
                actual = "  " + t
            else:
                actual = cand
        out.append(actual)
    return "\n".join(out)


def seccion(sid, titulo):
    s = {"id": sid, "titulo": titulo, "pasos": []}
    SECCIONES.append(s)
    return s


def paso(sec, pid, titulo, cmd, texto="", run=True, lineas=None, nota="", manual=None, captura=True):
    sec["pasos"].append(dict(id=pid, titulo=titulo, cmd=cmd.strip("\n"), texto=texto, run=run,
                             lineas=lineas, nota=nota, manual=manual, captura=captura))


# ---------------------------------------------------------------------------
# 0. PREPARACIÓN
# ---------------------------------------------------------------------------
P = seccion("prep", "Preparación del entorno en Kali")
paso(P, "prep-01", "Actualizar índices de paquetes", "sudo apt update", run=False, captura=False,
     texto=r"Abrir una terminal en la VM de Kali (usuario \texttt{kali}, contraseña \texttt{kali}).")
paso(P, "prep-02", "Instalar herramientas del sistema",
     "sudo DEBIAN_FRONTEND=noninteractive apt install -y 7zip unrar tshark xxd openssl binutils libscca-utils libesedb-utils python3-evtx python3-venv jq git curl qemu-user",
     run=False, captura=False,
     texto=r"\texttt{DEBIAN\_FRONTEND=noninteractive} evita la pregunta interactiva de \texttt{tshark} sobre captura "
           r"sin privilegios. \texttt{unrar} es el descompresor oficial de RAR (el \texttt{7zip} de Debian no trae soporte RAR).")
paso(P, "prep-03", "Crear un entorno virtual de Python", "python3 -m venv --system-site-packages ~/ctf-venv",
     run=False, captura=False,
     texto=r"Kali no permite \texttt{pip install} global (PEP 668). El \emph{venv} con \texttt{--system-site-packages} "
           r"ve además los módulos instalados con \texttt{apt} (\texttt{python3-evtx}).")
paso(P, "prep-04", "Activar el entorno virtual", "source ~/ctf-venv/bin/activate", run=False, captura=False,
     nota=r"\textbf{Importante:} repetir este comando (y el \texttt{export S=...} del paso~\ref{paso:prep-08}) "
          r"en \emph{cada} terminal nueva.")
paso(P, "prep-05", "Instalar librerías de Python",
     "pip install unicorn capstone pefile pyelftools pycryptodome oletools regipy", run=False, captura=False,
     texto=r"\texttt{unicorn}: emulador de CPU; \texttt{capstone}: desensamblador; \texttt{pefile}/\texttt{pyelftools}: "
           r"formatos PE y ELF; \texttt{pycryptodome}: AES; \texttt{oletools}: \texttt{rtfobj}; \texttt{regipy}: registro de Windows.")
paso(P, "prep-06", "Carpeta de trabajo", "mkdir -p ~/ctf && cd ~/ctf", run=False, captura=False)
paso(P, "prep-07", "Descargar los scripts del análisis",
     "git clone -b informe-retos https://github.com/moulyk-gg/retos.git repo", run=False, captura=False)
paso(P, "prep-08", "Variable con la ruta de los scripts", "export S=~/ctf/repo/scripts", run=False, captura=False)
paso(P, "prep-09", "Descargar los retos (871 MB)",
     "curl -L -o retos.zip https://github.com/moulyk-gg/retos/releases/download/V1/retos.zip", run=False, captura=False)
paso(P, "prep-10", "Verificar la integridad de la descarga", "cd ~/ctf && sha256sum retos.zip",
     nota=r"Debe coincidir con el SHA-256 publicado en el \emph{release} de GitHub.")
paso(P, "prep-11", "Extraer los retos", "7z x retos.zip | tail -4")
paso(P, "prep-12", "Estructura de los retos", "ls -1 retos/")

# ---------------------------------------------------------------------------
# 1. CCN-CRY
# ---------------------------------------------------------------------------
C = seccion("ccn", "Reversing: CCN-Cry")
paso(C, "ccn-01", "Preparar la carpeta del reto",
     "mkdir -p ~/ctf/ccn-cry && cd ~/ctf/ccn-cry && cp ~/ctf/retos/'Reversing CCN-Cry'/evidencia-*.zip evidencia.zip && cp ~/ctf/retos/'Reversing CCN-Cry'/Secret-*.CCN_CRY Secret.txt.CCN_CRY && ls -l",
     texto=r"Se copian los ficheros del reto con su nombre original (sin el sufijo con el hash).")
paso(C, "ccn-02", "Verificar los MD5 contra el enunciado", "md5sum evidencia.zip Secret.txt.CCN_CRY",
     nota=r"Coinciden con los publicados: \texttt{fc04df37...} y \texttt{fba2221b...}.")
paso(C, "ccn-03", "Ver el fichero cifrado", "xxd Secret.txt.CCN_CRY",
     nota=r"24 bytes = 3 bloques de 8 bytes: compatible con un cifrado de bloque de 64 bits (Blowfish, DES, \dots) con relleno PKCS\#5.")
paso(C, "ccn-04", "Primera rareza: unzip no puede abrir el zip", "unzip -P infected evidencia.zip",
     nota=r"\texttt{need PK compat. v5.1}: el zip usa cifrado \textbf{AES}, que \texttt{unzip} no soporta. Hay que usar \texttt{7z}.")
paso(C, "ccn-05", "Método de cifrado del zip", "7z l -slt -pinfected evidencia.zip | grep -E '^(Path|Size|Method|Encrypted)'")
paso(C, "ccn-06", "Extraer la evidencia", "7z x -pinfected evidencia.zip | tail -3 && ls -l incident-a1000032.pcapng")
paso(C, "ccn-07", "Resumen de la captura", "capinfos incident-a1000032.pcapng | grep -E 'File type|Number of packets|File size|First packet|Last packet|Capture duration'")
paso(C, "ccn-08", "Jerarquía de protocolos", "tshark -r incident-a1000032.pcapng -q -z io,phs",
     nota=r"Todo es TCP y solo hay 3 tramas HTTP: el resto (2.000+) es un escaneo de puertos posterior (puerto origen 63903 contra 1000 puertos).")
paso(C, "ccn-09", "Conversaciones TCP", "tshark -r incident-a1000032.pcapng -q -z conv,tcp | head -9")
paso(C, "ccn-10", "Peticiones HTTP: descarga y \"llamada a casa\"",
     "tshark -r incident-a1000032.pcapng -Y http.request -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport -e http.host -e http.request.uri -e http.content_type",
     nota=r"La víctima \texttt{192.168.1.41} descarga \texttt{/wget.tar.gz} y después hace \texttt{GET /user.php} contra "
          r"\texttt{www.aarkaposleeqaasssf.tk:8080}. \textbf{Cosa rara clave:} la cabecera \texttt{Content-type} no es un tipo MIME.")
paso(C, "ccn-11", "Contenido completo de la petición al C2",
     "tshark -r incident-a1000032.pcapng -q -z follow,tcp,ascii,1",
     nota=r"Formato \texttt{campo1:campo2:campo3}: 32 caracteres, 8 caracteres y \texttt{oat12} (el \emph{hostname}).")
paso(C, "ccn-12", "Exportar los objetos HTTP de la captura",
     "tshark -r incident-a1000032.pcapng --export-objects http,http_objs > /dev/null && ls -l http_objs")
paso(C, "ccn-13", "Extraer el ransomware",
     "tar -tzvf http_objs/wget.tar.gz && tar -xzf http_objs/wget.tar.gz && file ccn_cry && md5sum ccn_cry",
     nota=r"\textbf{No ejecutar} \texttt{ccn\_cry}: es el ransomware. Todo el análisis siguiente es estático.")
paso(C, "ccn-14", "Funciones importadas relevantes",
     "objdump -T ccn_cry | grep -E 'EVP_|srand|rand|time|gethostname|socket|connect|opendir|remove'",
     nota=r"\texttt{EVP\_bf\_cbc}: Blowfish-CBC de OpenSSL. \texttt{srand}/\texttt{rand}/\texttt{time}: clave pseudoaleatoria. "
          r"\texttt{socket}/\texttt{connect}: envío al C2. \texttt{opendir}/\texttt{remove}: recorre directorios y borra los originales.")
paso(C, "ccn-15", "Cadenas interesantes",
     "strings -n 4 ccn_cry | grep -E 'CCN_CRY|Content-type|user.php|aarkap|abcdef|/home/|Key='",
     nota=r"Alfabeto de 78 caracteres para generar claves, directorio objetivo \texttt{/home/robertM/}, plantilla de la petición HTTP "
          r"y un \texttt{printf} de depuración \texttt{Key= \%s iv= \%s}.")
paso(C, "ccn-16", "Generación de clave (32) e IV (8)",
     "objdump -d -M intel --no-show-raw-insn --start-address=0x1cdf --stop-address=0x1d4d ccn_cry | tail -n +7",
     nota=r"\texttt{mov edi,0x8} y \texttt{mov edi,0x20} antes de \texttt{call 0x19f4}: cadenas aleatorias de 8 y 32 caracteres; "
          r"después \texttt{gethostname}.")
paso(C, "ccn-17", "Función generadora: charset[rand() \\% 78]",
     "objdump -d -M intel --no-show-raw-insn --start-address=0x1a23 --stop-address=0x1a73 ccn_cry | tail -n +7",
     nota=r"\texttt{imul eax,eax,0x4e} = multiplicar por 78 para calcular el resto de \texttt{rand()} entre 78 (tamaño del alfabeto).")
paso(C, "ccn-18", "Construcción de la cabecera: separadores ':' y salto de línea",
     "objdump -d -M intel --no-show-raw-insn --start-address=0x16dc --stop-address=0x17b4 ccn_cry | grep -E 'call|WORD PTR \\[rax\\]'",
     nota=r"\texttt{strcpy}, \texttt{0x3a} (\texttt{:}), \texttt{strcat}, \texttt{0x3a}, \texttt{strcat}, \texttt{0xa} (\texttt{\textbackslash n}).")
paso(C, "ccn-19", "La trampa: longitud de clave fijada a 16 bytes",
     "objdump -d -M intel --no-show-raw-insn --start-address=0x2064 --stop-address=0x20db ccn_cry | tail -n +7",
     nota=r"\texttt{mov esi,0x10} antes de \texttt{EVP\_CIPHER\_CTX\_set\_key\_length}: de los 32 caracteres de la clave "
          r"\textbf{solo se usan los 16 primeros}.")
paso(C, "ccn-20", "Extraer clave e IV de la captura",
     """CT=$(tshark -r incident-a1000032.pcapng -Y 'http.request.uri == "/user.php"' -T fields -e http.content_type)
KEY=$(printf %s "$CT" | cut -d: -f1 | cut -c1-16)
IV=$(printf %s "$CT" | cut -d: -f2)
echo "KEY=[$KEY]  IV=[$IV]"; printf %s "$KEY" | xxd -p; printf %s "$IV" | xxd -p""")
paso(C, "ccn-21", "Descifrar con Blowfish-CBC",
     """openssl enc -d -bf-cbc -provider legacy -provider default -K "$(printf %s "$KEY" | xxd -p)" -iv "$(printf %s "$IV" | xxd -p)" -in Secret.txt.CCN_CRY -out Secret.txt && cat Secret.txt; echo""",
     texto=r"Blowfish está en el \emph{provider legacy} de OpenSSL~3.")
paso(C, "ccn-22", "Flag en MD5", 'echo -n "JosephPopp1989" | md5sum',
     nota=r"\textbf{Flag:} \texttt{flag\{c890082bbb38d2aad5eb182cac9fbc7e\}} (validada en la plataforma).")

# ---------------------------------------------------------------------------
# 2. THE KRAKEN
# ---------------------------------------------------------------------------
K = seccion("kraken", "Reversing: The Kraken")
paso(K, "kraken-01", "Preparar la carpeta y verificar el fichero",
     "mkdir -p ~/ctf/kraken && cd ~/ctf/kraken && cp ~/ctf/retos/'Reversing The Kraken'/TheKraken-*.exe TheKraken.exe && md5sum TheKraken.exe && file TheKraken.exe && ls -l TheKraken.exe",
     nota=r"\texttt{file} lo confunde con un ensamblado .NET (falso positivo causado por la cabecera manipulada). 932 bytes es "
          r"un tamaño absurdo para un ejecutable de Windows normal.")
paso(K, "kraken-02", "Cabecera: MZ23PE", "xxd TheKraken.exe | head -8",
     nota=r"\texttt{MZ} seguido de \texttt{23} (versión 2.3 de Crinkler) y \texttt{PE\textbackslash 0\textbackslash 0} en el offset 4 "
          r"(\texttt{e\_lfanew = 4} en 0x3c): la cabecera PE está solapada con la DOS.")
paso(K, "kraken-03", "Estructura PE", "python3 $S/pe_info.py TheKraken.exe",
     nota=r"\textbf{0 secciones}, 0 \emph{data directories}, \emph{entry point} en 0x5c (dentro de la propia cabecera) y "
          r"\texttt{SizeOfImage} de unos 500 MB para reservar memoria al descompresor. La fecha de compilación (2037) es "
          r"imposible: Crinkler reutiliza esos bytes de la cabecera como código y datos.")
paso(K, "kraken-04", "Descompresor de Crinkler en el entry point",
     "objdump -D -b binary -m i386 -M intel --start-address=0x5c --stop-address=0x8a TheKraken.exe | tail -n +8",
     nota=r"\texttt{mov edi,0x420000} + \texttt{push edi}: destino del código descomprimido, al que se saltará con un \texttt{ret}.")
paso(K, "kraken-05", "Emular el descompresor con Unicorn (sin ejecutar el .exe)",
     "time python3 $S/kraken_emu.py TheKraken.exe unpacked.bin",
     nota=r"Se emula la CPU x86 hasta que el flujo salta a 0x420000 y se vuelca esa memoria.")
paso(K, "kraken-06", "Resolver de imports por hash (PEB -> kernel32)",
     "objdump -D -b binary -m i386 -M intel --adjust-vma=0x420000 --start-address=0x420000 --stop-address=0x42007f unpacked.bin | tail -n +8 | head -45",
     nota=r"\texttt{mov eax,[eax+0xc]} (PEB$\to$Ldr), recorrido de exports y \texttt{rol edi,0x6 ; xor edi,eax}: hash de cada nombre "
          r"comparado con la tabla de \texttt{0x400108}. Las direcciones resueltas van a la IAT en \texttt{0x430000}.")
paso(K, "kraken-07", "Main: llamada a [0x430000] y array cifrado de 23 bytes",
     "objdump -D -b binary -m i386 -M intel --adjust-vma=0x420000 --start-address=0x420193 --stop-address=0x420210 unpacked.bin | tail -n +8")
paso(K, "kraken-08", "Bucle de descifrado y salida por [0x430010]",
     "objdump -D -b binary -m i386 -M intel --adjust-vma=0x420000 --start-address=0x420210 --stop-address=0x420272 unpacked.bin | tail -n +8",
     nota=r"Por cada byte $c$: $c \oplus \mathtt{0x7C}$, $+$\,(byte bajo del valor devuelto por \texttt{[0x430000]}), negación, "
          r"rotación de 1~bit a la izquierda y $-\,i$. Después \texttt{call [0x430010]} con el texto.")
paso(K, "kraken-09", "Lista de exports de kernel32 (Wine)",
     "curl -sSLo kernel32.spec https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/kernel32/kernel32.spec && wc -l kernel32.spec")
paso(K, "kraken-10", "Identificar APIs por hash y descifrar",
     "python3 $S/kraken_solve.py TheKraken.exe kernel32.spec",
     nota=r"\texttt{[0x430000]} = \texttt{GetACP} (página de códigos ANSI) y \texttt{[0x430010]} = \texttt{OutputDebugStringA}: la flag "
          r"\textbf{nunca sale por consola}, solo por el canal de depuración. De los 256 valores posibles solo uno da texto legible "
          r"terminado exactamente en \texttt{\textbackslash x00}.")
paso(K, "kraken-11", "Flag en MD5", 'echo -n "Kongespeilet1250" | md5sum',
     nota=r"\textbf{Flag:} \texttt{flag\{d11c2e023a6a0fb3105121dade32232b\}}.")

# ---------------------------------------------------------------------------
# 3. SPEAR PHISHING (partes 1 y 2)
# ---------------------------------------------------------------------------
SP = seccion("spear", "Reversing: Spear Phishing... Can you catch me? (partes 1 y 2)")
paso(SP, "spear-01", "Preparar la carpeta y verificar el RAR",
     "mkdir -p ~/ctf/spear && cd ~/ctf/spear && cp ~/ctf/retos/'Reversing Spear Phising... Can you catch me'/suspicious_*.rar suspicious_.rar && md5sum suspicious_.rar")
paso(SP, "spear-02", "Listar el RAR", "unrar lt -pinfected suspicious_.rar | grep -E 'Name|Type|Size|Packed|mtime|Flags|Compression'",
     nota=r"Un único fichero \texttt{Nominas.rtf} (nóminas), cifrado, con fecha 09/09/2017.")
paso(SP, "spear-03", "Extraer y verificar", "unrar x -o+ -pinfected suspicious_.rar > /dev/null && ls -l Nominas.rtf && md5sum Nominas.rtf && file Nominas.rtf")
paso(SP, "spear-04", "Contenido del RTF: no tiene texto", "head -c 760 Nominas.rtf; echo",
     nota=r"Solo hay un \texttt{\textbackslash object} con \texttt{\textbackslash objautlink} y \texttt{\textbackslash objupdate} "
          r"(el enlace se actualiza solo al abrir) y un \texttt{\textbackslash objdata} en hexadecimal.")
paso(SP, "spear-05", "Palabras de control y firmas clave",
     "grep -oE -e objautlink -e objupdate -e 'objclass [A-Za-z.0-9]+' -e 4f4c45324c696e6b -e e0c9ea79f9bace118c8200aa004ba90b Nominas.rtf | sort | uniq -c")
paso(SP, "spear-06", "Decodificar la clase del objeto", "echo 4f4c45324c696e6b | xxd -r -p; echo",
     nota=r"\texttt{OLE2Link}: objeto OLE \emph{enlazado} (no incrustado). El CLSID \texttt{e0c9ea79...} es el \textbf{URL Moniker}.")
paso(SP, "spear-07", "Análisis con rtfobj (oletools)", "rtfobj Nominas.rtf | tail -n +5")
paso(SP, "spear-08", "Parte 2: URL exacta del URL Moniker", "python3 $S/rtf_url.py Nominas.rtf",
     nota=r"Se confirma byte a byte que la URL no tiene espacios ni caracteres invisibles.")
paso(SP, "spear-09", "Flags en MD5", 'echo -n "CVE-2017-0199" | md5sum; echo -n "http://dagobah.local/logo.doc" | md5sum',
     nota=r"\textbf{Parte 1:} \texttt{flag\{93b146d21d3bdc8635836f8a11ba62b9\}} (validada). "
          r"\textbf{Parte 2:} \texttt{flag\{fb7534ecc904766563ad711331a11121\}}.")

# ---------------------------------------------------------------------------
# 4. GO GO GO!
# ---------------------------------------------------------------------------
G = seccion("go", "Reversing: Go go go!")
paso(G, "go-01", "Preparar la carpeta y extraer",
     "mkdir -p ~/ctf/gogogo && cd ~/ctf/gogogo && cp ~/ctf/retos/'Reversing Go go go!'/LetsGo-*.zip LetsGo.zip && md5sum LetsGo.zip && 7z x -y -pinfected LetsGo.zip | tail -3",
     texto=r"Se usan comillas simples en la ruta: en \texttt{zsh} un \texttt{!} entre comillas dobles provoca expansión de historial.")
paso(G, "go-02", "Tipo de binario", "file LetsGo && md5sum LetsGo && readelf -h LetsGo | grep -E 'Class|Data|Machine|Entry'",
     nota=r"ELF de 32 bits \textbf{MIPS big-endian} (arquitectura de routers/IoT), estático, Go, \emph{stripped}.")
paso(G, "go-03", "Versión de Go y secciones", "strings -n 6 LetsGo | grep -oE 'go1\\.[0-9]+\\.[0-9]+' | sort -u && readelf -S LetsGo | grep -E 'text|rodata|gopclntab'",
     nota=r"Aunque esté \emph{stripped}, Go conserva \texttt{.gopclntab} con los nombres de todas las funciones.")
paso(G, "go-04", "Funciones del paquete main (desde .gopclntab)", "python3 $S/go_pclntab.py LetsGo main. | grep -v runtime",
     nota=r"Además de \texttt{encrypt}/\texttt{Pad}/\texttt{addBase64Padding} hay tres funciones con nombres ofuscados.")
paso(G, "go-05", "Librerías de terceros y crypto usadas",
     "python3 $S/go_pclntab.py LetsGo | grep -E -e 'goInfo\\.GetInfo$' -e 'go-figure\\.NewFigure$' -e 'figure\\.Print$' -e 'aes\\.NewCipher$' -e 'NewCFBDecrypter$' -e 'base64.*Encoding.*DecodeString$'")
paso(G, "go-06", "Cadenas sospechosas",
     "strings -n 16 LetsGo | grep -oE -e 'wD5q[A-Za-z0-9_-]{60}' -e '1KH1hb001Y09olU.' -e dwnoDlybPWZTYRdbFpit -e Xa22SKeyAll1aadf1 -e 'GoOS:%v[A-Za-z:%v,]*CPUs:%v' | sort -u")
paso(G, "go-07", "Ejecución emulada: no imprime nada", "chmod +x LetsGo && qemu-mips ./LetsGo; echo \"codigo de salida: $?\"",
     texto=r"Opcional. Se ejecuta con \texttt{qemu-user} (emulación de MIPS en espacio de usuario). El análisis estático no muestra "
           r"acciones dañinas, pero hágase en la VM desechable.",
     nota=r"No muestra nada: el binario comprueba el entorno antes de revelar la flag.")
paso(G, "go-08", "Desensamblar main.main (MIPS, Capstone)",
     "python3 $S/go_mips_disasm.py LetsGo main.main > main_main.txt && wc -l main_main.txt && grep -E 'jal|\"' main_main.txt | cut -c1-105",
     nota=r"Llamadas anotadas con su nombre y cadenas referenciadas: secuencia completa del programa.")
paso(G, "go-09", "Condición 1: kernel que contenga 4.14.0", "awk '/0x119ef0/,/0x119f34/' main_main.txt")
paso(G, "go-10", "Clave real (la tercera) y llamada a aes.NewCipher", "awk '/0x119fb4/,/0x11a008/' main_main.txt",
     nota=r"Solo el \emph{slice} de \texttt{1KH1hb001Y09olUo} (0x153544) llega a \texttt{aes.NewCipher}; las otras dos claves son señuelos.")
paso(G, "go-11", "Condición 2: número de CPUs (switch 2 / 8 / 3)", "awk '/0x11a154/,/0x11a178/' main_main.txt",
     nota=r"\texttt{CPUs==2} y \texttt{CPUs==8} lanzan goroutines señuelo; \texttt{CPUs!=3} sale; solo con 3 CPUs (y SO \texttt{linux}) se imprime la flag.")
paso(G, "go-12", "Descifrar AES-128-CFB con las tres claves", "python3 $S/go_decrypt.py",
     nota=r"Solo la clave terminada en \texttt{o} da texto con relleno PKCS\#7 válido.")
paso(G, "go-13", "Flag en MD5", 'echo -n "RobPike2009" | md5sum',
     nota=r"\textbf{Flag:} \texttt{flag\{f389c15c0ea41f12e53806fba659e2fb\}}.")

# ---------------------------------------------------------------------------
# 5. H0RR0CRUX
# ---------------------------------------------------------------------------
H = seccion("horcrux", "H0rr0crux")
paso(H, "horcrux-01", "Preparar la carpeta y verificar la evidencia",
     "mkdir -p ~/ctf/horcrux && cd ~/ctf/horcrux && cp ~/ctf/retos/H0rr0crux/evidencias_sorvologaunt*.7z evidencias.7z && md5sum evidencias.7z")
paso(H, "horcrux-02", "Contenido del 7z", "7z l evidencias.7z | tail -3",
     nota=r"17.550 ficheros y 2,6 GB sin comprimir.")
paso(H, "horcrux-03", "Extraer (tarda unos minutos)", "7z x -y evidencias.7z -oevid | tail -4 && ls evid")
paso(H, "horcrux-04", "Qué artefactos hay", "ls evid/Windows/appcompat/Programs evid/Windows/System32/sru evid/Users/Gregor | head -30; ls evid/Windows/Prefetch | wc -l; ls evid/Windows/System32/winevt/Logs | wc -l",
     nota=r"Adquisición tipo KAPE: \texttt{\$MFT}, \texttt{\$LogFile}, Amcache, SRUM, Prefetch, 141 logs \texttt{.evtx} y los "
          r"logs de transacciones del registro del usuario \textbf{Gregor}.")
paso(H, "horcrux-05", "Prefetch con nombres sospechosos",
     "ls evid/Windows/Prefetch | grep -iE -e inject -e packed -e vmprotect -e 'tor\\.exe' -e runas -e fodhelper -e wevtutil -e taskkill -e '^sc\\.exe' -e ftk -e hxd -e httpd")
paso(H, "horcrux-06", "Línea de tiempo de ejecuciones desde rutas de usuario",
     "bash $S/prefetch_timeline.sh evid/Windows/Prefetch 'USERS|PROGRAMDATA|TEMP' | grep -viE 'onedrive|google|brave|edge|chrome|defender|mpsigstub'",
     nota=r"Formato: última ejecución (UTC) \texttt{|} número de ejecuciones \texttt{|} ruta.")
paso(H, "horcrux-07", "Detalle de ejecuciones (runas, tor, wevtutil, inject)",
     "for f in RUNAS TOR WEVTUTIL INJECT; do sccainfo evid/Windows/Prefetch/$f.EXE-*.pf | grep -E 'Executable filename|Run count|Last run time: [123]'; echo; done")
paso(H, "horcrux-08", "Amcache: SHA1 y metadatos de los ejecutables de Gregor",
     "python3 $S/amcache_dump.py evid/Windows/appcompat/Programs/Amcache.hve --todo 2>/dev/null | grep -i 'users\\\\gregor' | grep -viE 'onedrive|google|brave|edge' | cut -f1,2,4,5,6",
     nota=r"Columnas: SHA1, tamaño, \emph{publisher}, \texttt{OriginalFileName}, ruta. \textbf{Cosas raras:} \texttt{runas.exe} es "
          r"\texttt{sdelete.exe}; \texttt{uninstall.exe} es \texttt{pelook.exe}; \texttt{tor.exe} no tiene metadatos; "
          r"\texttt{httpd.exe} dice ser de Microsoft desde \texttt{AppData\textbackslash Roaming}.")
paso(H, "horcrux-09", "Windows Defender: detección de inject.exe",
     "python3 $S/evtx_grep.py 'evid/Windows/System32/winevt/Logs/Microsoft-Windows-Windows Defender%4Operational.evtx' inject --ids 1116,1117 | grep -E 'EventID|Threat Name|Path|Action Name'")
paso(H, "horcrux-10", "inject.exe nunca llegó a ejecutarse",
     "python3 $S/evtx_grep.py evid/Windows/System32/winevt/Logs/System.evtx inject")
paso(H, "horcrux-11", "Logs cortados (limpieza con wevtutil)",
     "cd evid/Windows/System32/winevt/Logs && python3 $S/evtx_range.py Application.evtx Security.evtx System.evtx 'Microsoft-Windows-Windows Defender%4Operational.evtx'; cd ~/ctf/horcrux",
     nota=r"Application, Security y System terminan entre las 13:01 y las 13:02, mientras Defender sigue registrando hasta las 15:30.")
paso(H, "horcrux-12", "SRUM: exportar la base de datos", "mkdir -p srum && cp evid/Windows/System32/sru/SRUDB.dat srum/ && cd srum && esedbexport -t srum SRUDB.dat | tail -2 && cd ..")
paso(H, "horcrux-13", "SRUM: qué binarios de usuario usaron la red",
     "python3 $S/srum_net.py srum/srum.export | grep -iE 'users\\\\gregor\\\\appdata\\\\(roaming|local\\\\temp)|users\\\\gregor\\\\downloads\\\\inject|runas'",
     nota=r"\textbf{Evidencia clave:} el único binario sospechoso con tráfico de red es \texttt{httpd.exe} (800 B enviados, 1.214 B recibidos). "
          r"\texttt{tor.exe}, \texttt{runas.exe} e \texttt{inject.exe} no aparecen.")
paso(H, "horcrux-14", "$MFT: llegada por drag & drop y crashes de httpd.exe", "python3 $S/mft_record.py 'evid/$MFT' httpd.exe",
     nota=r"\texttt{VirtualBox Dropped Files\textbackslash 2021-12-20T13\_09\_30...}: \texttt{httpd.exe} se arrastró desde el host a las 13:09:30. "
          r"Dos informes WER \texttt{AppCrash\_httpd.exe\_...} a las 13:10:39 y 13:11:57. No queda registro del propio fichero (borrado).")
paso(H, "horcrux-15", "PCA (Compatibility Assistant) en el registro del usuario",
     "strings -a evid/Users/Gregor/ntuser.dat.LOG2 | grep -i 'httpd'")
paso(H, "horcrux-16", "El binario ya no está en la evidencia",
     "cd evid && find . -type f -print0 | xargs -0 sha1sum | grep -ci -e 409aea9461d03bff3e006d3e7e7c4790a0862170 -e 99e107ca419959385ca57241fb6ed3796eaacc9e -e de275b64985009d335ab85b38d26a3026739a68a; cd ..",
     nota=r"0 coincidencias: el malware se borró (SDelete) y el equipo se restauró. Solo queda su SHA1 en Amcache.")
paso(H, "horcrux-17", "Señuelo restante: uninstall.exe es PE Look",
     "python3 $S/pe_info.py evid/Users/Gregor/AppData/Local/Microsoft/uninstall.exe",
     nota=r"Visor de PE legítimo de bytepointer.com, sin imports de red.")
paso(H, "horcrux-18", "Pivotar los SHA1 en VirusTotal (API v3)",
     """VT_KEY="TU_API_KEY" bash $S/vt_lookup.sh 409aea9461d03bff3e006d3e7e7c4790a0862170 99e107ca419959385ca57241fb6ed3796eaacc9e de275b64985009d335ab85b38d26a3026739a68a""",
     run=False,
     texto=r"Requiere una clave gratuita de VirusTotal (perfil $\to$ \emph{API key}); sustituir \texttt{TU\_API\_KEY} por ella. "
           r"El script espera 16~s entre consultas para respetar el límite de 4 por minuto. Tras el reto, conviene regenerar la clave.",
     manual="""== 409aea9461d03bff3e006d3e7e7c4790a0862170
MD5: dbe0e10775e35a58e8ff463ccbe5f7d8
Nombre: httpd.exe
Familia: trojan.cobaltstrike/fugrafa
Detecciones: 61
== 99e107ca419959385ca57241fb6ed3796eaacc9e
MD5: 3e6f1f16a4cbbf7c5a5c077ab197bb50
Nombre: tag_converter.exe
Familia: null
Detecciones: 3
== de275b64985009d335ab85b38d26a3026739a68a
MD5: null
Nombre: null
Familia: null""",
     nota=r"\texttt{httpd.exe} es un \emph{stager} de \textbf{Cobalt Strike} (61 detecciones). \texttt{tor.exe} es un "
          r"\texttt{tag\_converter.exe} renombrado (3 detecciones, sin familia). \texttt{inject.exe} no está en VirusTotal.")
paso(H, "horcrux-19", "Flag", 'echo "flag{dbe0e10775e35a58e8ff463ccbe5f7d8}"', run=False, captura=False,
     manual="flag{dbe0e10775e35a58e8ff463ccbe5f7d8}",
     nota=r"Aquí la flag es directamente el MD5 del binario (no se hace MD5 de ningún texto).")
