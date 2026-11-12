# -*- coding: utf-8 -*-
"""Textos LaTeX fijos del informe (preámbulo, portada, metodología, introducciones y cierres)."""

PREAMBULO = r"""% !TEX program = pdflatex
% Compilar dos veces con pdflatex (la segunda genera el índice):
%   pdflatex informe_retos.tex && pdflatex informe_retos.tex
% Las capturas se insertan solas si existen como capturas/<id-del-paso>.png
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{textcomp}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}
\spanishplainpercent  % sin espacio fino antes de % (si no, se copiaría un espacio extra en los comandos)
\usepackage[a4paper,top=2.3cm,bottom=2.3cm,left=2.2cm,right=2.2cm,headheight=14pt]{geometry}
\usepackage{microtype}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{booktabs,longtable,array,tabularx}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{amssymb}
\usepackage{listings}
\usepackage[most]{tcolorbox}
\usepackage{seqsplit}
\usepackage[colorlinks=true,linkcolor=enlace,urlcolor=enlace,citecolor=enlace]{hyperref}

% ---------------- Colores ----------------
\definecolor{termbg}{HTML}{1E1F29}     % fondo terminal
\definecolor{termfg}{HTML}{F8F8F2}     % texto terminal
\definecolor{termbar}{HTML}{343746}    % barra de título terminal
\definecolor{prompt}{HTML}{8BE9FD}     % prompt
\definecolor{cmdc}{HTML}{50FA7B}       % programas (verde)
\definecolor{kwc}{HTML}{FF79C6}        % palabras clave del shell (rosa)
\definecolor{strc}{HTML}{F1FA8C}       % cadenas (amarillo)
\definecolor{comc}{HTML}{6272A4}       % comentarios
\definecolor{varc}{HTML}{BD93F9}       % variables (morado)
\definecolor{outbg}{HTML}{F6F8FA}      % fondo salida
\definecolor{outfg}{HTML}{24292E}      % texto salida
\definecolor{outframe}{HTML}{0366D6}   % borde salida
\definecolor{pybg}{HTML}{FBFBF8}
\definecolor{pykw}{HTML}{0033B3}
\definecolor{pystr}{HTML}{067D17}
\definecolor{pycom}{HTML}{8C8C8C}
\definecolor{pynum}{HTML}{1750EB}
\definecolor{enlace}{HTML}{1F4E9C}
\definecolor{flagbg}{HTML}{EAF7EC}
\definecolor{titulo}{HTML}{1F2A44}

% ---------------- Acentos dentro de listings (pdflatex) ----------------
\lstset{literate=
  {á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1 {ñ}{{\~n}}1
  {Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1 {Ñ}{{\~N}}1
  {ü}{{\"u}}1 {Ü}{{\"U}}1 {¿}{{?`}}1 {¡}{{!`}}1 {º}{{\textordmasculine}}1 {ª}{{\textordfeminine}}1 {°}{{\textdegree}}1,
  upquote=true, columns=fullflexible, keepspaces=true, showstringspaces=false, aboveskip=0pt, belowskip=0pt,
  breaklines=true, breakatwhitespace=false, tabsize=8, extendedchars=true}

% Estilo terminal (comandos)
\lstdefinestyle{terminal}{
  language=bash,
  basicstyle=\ttfamily\footnotesize\color{termfg},
  alsoletter={-0123456789},
  keywordstyle=\color{kwc}\bfseries,
  keywordstyle=[2]\color{cmdc}\bfseries,
  morekeywords=[2]{sudo,apt,7z,unzip,unrar,tshark,capinfos,openssl,objdump,readelf,xxd,python3,curl,
    md5sum,sha1sum,sha256sum,grep,sed,awk,cut,tar,file,strings,sccainfo,esedbexport,rtfobj,jq,pip,git,
    mkdir,cp,ls,find,head,tail,wc,sort,uniq,xargs,chmod,qemu-mips,bash},
  stringstyle=\color{strc},
  commentstyle=\color{comc}\itshape,
  emph={S,KEY,IV,CT,VT_KEY,HOME,f,h},
  emphstyle=\color{varc},
  postbreak=\mbox{\textcolor{comc}{$\hookrightarrow$}\space},
}
% Estilo salida
\lstdefinestyle{salida}{
  basicstyle=\ttfamily\footnotesize\color{outfg},
  postbreak=\mbox{\textcolor{outframe}{$\hookrightarrow$}\space},
}
% Estilo Python (apéndice)
\lstdefinestyle{py}{
  language=Python,
  basicstyle=\ttfamily\scriptsize,
  keywordstyle=\color{pykw}\bfseries,
  stringstyle=\color{pystr},
  commentstyle=\color{pycom}\itshape,
  morekeywords={as,with,None,True,False,self},
  numbers=left, numberstyle=\tiny\color{gray}, numbersep=6pt,
  postbreak=\mbox{\textcolor{pycom}{$\hookrightarrow$}\space},
}
% Estilo bash claro (apéndice)
\lstdefinestyle{bashclaro}{
  language=bash,
  basicstyle=\ttfamily\scriptsize,
  keywordstyle=\color{pykw}\bfseries,
  stringstyle=\color{pystr},
  commentstyle=\color{pycom}\itshape,
  numbers=left, numberstyle=\tiny\color{gray}, numbersep=6pt,
}

% ---------------- Cajas ----------------
\newtcblisting{comando}[1]{enhanced, breakable, listing only, listing options={style=terminal},
  colback=termbg, colframe=termbar, boxrule=0.8pt, arc=3pt, left=6pt, right=6pt, top=3pt, bottom=3pt,
  colbacktitle=termbar, coltitle=white, toptitle=1pt, bottomtitle=1pt,
  title={\ttfamily\footnotesize\textcolor{red!70}{\textbullet}\,\textcolor{yellow!80!orange}{\textbullet}\,\textcolor{green!70!black}{\textbullet}\quad
    \textcolor{prompt}{(kali@kali)-[}\textcolor{white}{\bfseries #1}\textcolor{prompt}{]\$}},
  before skip=6pt, after skip=4pt}
\newtcblisting{salida}[1]{enhanced, breakable, listing only, listing options={style=salida},
  colback=outbg, colframe=outframe!55, boxrule=0.4pt, leftrule=3pt, arc=1pt, left=6pt, right=4pt, top=2pt, bottom=2pt,
  colbacktitle=outbg, coltitle=outframe!80!black, fonttitle=\sffamily\scriptsize\bfseries,
  title={#1}, attach title to upper, before skip=2pt, after skip=6pt}
\newtcblisting{codigopython}[1]{enhanced, breakable, listing only, listing options={style=py},
  colback=pybg, colframe=gray!45, boxrule=0.4pt, arc=2pt, left=14pt,
  colbacktitle=gray!15, coltitle=black, fonttitle=\ttfamily\small\bfseries, title={#1}}
\newtcblisting{codigobash}[1]{enhanced, breakable, listing only, listing options={style=bashclaro},
  colback=pybg, colframe=gray!45, boxrule=0.4pt, arc=2pt, left=14pt,
  colbacktitle=gray!15, coltitle=black, fonttitle=\ttfamily\small\bfseries, title={#1}}
\newtcolorbox{nota}{enhanced, breakable, colback=blue!3, colframe=enlace, boxrule=0pt, leftrule=2.5pt,
  arc=0pt, left=6pt, right=4pt, top=3pt, bottom=3pt, fontupper=\small, before skip=4pt, after skip=6pt}
\newtcolorbox{aviso}[1][Atención]{enhanced, breakable, colback=red!3, colframe=red!60!black, boxrule=0.5pt,
  arc=2pt, fonttitle=\bfseries\small, title={#1}, fontupper=\small}
\newcommand{\flagbox}[2]{\begin{tcolorbox}[enhanced, colback=flagbg, colframe=green!45!black, boxrule=0.8pt, arc=3pt,
  fonttitle=\bfseries, title={#1}, halign=center]{\Large\ttfamily #2}\end{tcolorbox}}
\newcommand{\captura}[2]{%
  \IfFileExists{capturas/#1.png}{%
    \begin{center}\includegraphics[width=0.94\linewidth,height=0.42\textheight,keepaspectratio]{capturas/#1.png}
    \captionof{figure}{#2}\end{center}}{%
    \begin{tcolorbox}[enhanced, colback=orange!4, colframe=orange!70!black, boxrule=0.4pt, arc=2pt,
      left=6pt, top=2pt, bottom=2pt, fontupper=\footnotesize, before skip=2pt, after skip=8pt]
      \textbf{Captura pendiente} --- guardar la captura de este paso como \texttt{capturas/#1.png} y recompilar.
    \end{tcolorbox}}}
\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcommand{\bs}{\textbackslash\allowbreak{}}
\newcommand{\hash}[1]{{\ttfamily\footnotesize\seqsplit{#1}}}

% ---------------- Formato ----------------
\setlength{\parindent}{0pt}
\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{3em}
\setlist{itemsep=2pt, topsep=3pt}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\sffamily Informe de resolución de retos CTF}
\fancyhead[R]{\small\sffamily\nouppercase{\leftmark}}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\setcounter{tocdepth}{2}
\newcommand{\autor}{\rule{6cm}{0.4pt}}  % <-- escribe aquí tu nombre
"""

PORTADA_Y_RESUMEN = r"""
\begin{titlepage}
\centering
\vspace*{2cm}
{\color{titulo}\rule{\linewidth}{1.2pt}\\[0.6cm]
{\Huge\bfseries Informe técnico de resolución\\[0.25cm] de retos CTF}\\[0.4cm]
{\Large Reversing y análisis forense}\\[0.4cm]
\rule{\linewidth}{1.2pt}}
\vspace{1.5cm}

\begin{tcolorbox}[enhanced, colback=gray!4, colframe=titulo, boxrule=0.6pt, arc=3pt, width=0.85\linewidth]
\begin{tabularx}{\linewidth}{@{}lX@{}}
\textbf{Retos} & CCN-Cry · The Kraken · Spear Phishing (partes 1 y 2) · Go go go! · H0rr0crux \\[2pt]
\textbf{Entorno} & Kali Linux 2026.2 (VirtualBox) y entorno de análisis en la nube \\[2pt]
\textbf{Contenido} & Procedimiento, comandos exactos, evidencias, IOC y contexto \\[2pt]
\textbf{Autor} & \autor \\[2pt]
\textbf{Fecha} & \today \\
\end{tabularx}
\end{tcolorbox}

\vfill
{\small Todos los comandos de este documento se han ejecutado y verificado. Los binarios maliciosos
\textbf{nunca} se ejecutan: el análisis es estático o mediante emulación de CPU.}
\end{titlepage}

\section*{Resumen ejecutivo}
\addcontentsline{toc}{section}{Resumen ejecutivo}

Se han resuelto los seis retos planteados (cinco retos, uno de ellos en dos partes). Todas las flags siguen el
formato de la plataforma \texttt{flag\{md5\}}: el MD5 se calcula sobre el \emph{valor} encontrado, sin el prefijo
\texttt{Flag:~} y sin salto de línea (\texttt{echo -n "valor" | md5sum}). En H0rr0crux la flag es directamente el
MD5 del binario malicioso.

\begin{center}
\footnotesize
\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{3.1cm} >{\raggedright\arraybackslash}X >{\ttfamily\scriptsize}p{6.1cm} c@{}}
\toprule
\textbf{Reto} & \textbf{Valor encontrado} & \textbf{\normalfont Flag} & \textbf{Estado} \\ \midrule
CCN-Cry & \texttt{JosephPopp1989} & flag\{c890082bbb38d2aad5eb182cac9fbc7e\} & Validada \\
The Kraken & \texttt{Kongespeilet1250} & flag\{d11c2e023a6a0fb3105121dade32232b\} & Verificada \\
Spear Phishing (1) & \texttt{CVE-2017-0199} & flag\{93b146d21d3bdc8635836f8a11ba62b9\} & Validada \\
Spear Phishing (2) & \texttt{http://dagobah.local/logo.doc} & flag\{fb7534ecc904766563ad711331a11121\} & Verificada \\
Go go go! & \texttt{RobPike2009} & flag\{f389c15c0ea41f12e53806fba659e2fb\} & Verificada \\
H0rr0crux & \texttt{httpd.exe} (Cobalt Strike) & flag\{dbe0e10775e35a58e8ff463ccbe5f7d8\} & Verificada \\
\bottomrule
\end{tabularx}
\end{center}

\textbf{Validada}: aceptada por la plataforma. \textbf{Verificada}: comprobada técnicamente (terminador nulo exacto,
relleno PKCS\#7 válido, extracción byte a byte, o correlación de evidencias + VirusTotal).

\textbf{Hallazgos principales}
\begin{itemize}
  \item \textbf{CCN-Cry}: el ransomware envía su propia clave Blowfish al servidor de mando en la cabecera HTTP
        \texttt{Content-type}; la captura de red basta para descifrar. Trampa: solo usa 16 de los 32 caracteres.
  \item \textbf{The Kraken}: ejecutable de 932 bytes comprimido con Crinkler, imports resueltos por hash, flag
        descifrada con el valor de \texttt{GetACP()} y emitida por \texttt{OutputDebugStringA} (invisible en consola).
  \item \textbf{Spear Phishing}: RTF sin texto con un objeto \texttt{OLE2Link} + URL Moniker que se actualiza al abrir:
        CVE-2017-0199, URL \texttt{http://dagobah.local/logo.doc}.
  \item \textbf{Go go go!}: binario Go para MIPS con \emph{environmental keying} (kernel 4.14.0, 3 CPUs, Linux), tres
        claves AES (dos señuelo) y flag cifrada con AES-128-CFB.
  \item \textbf{H0rr0crux}: forense de Windows; tras descartar cinco señuelos (SDelete renombrado, PE Look renombrado,
        VMProtect, un falso \texttt{tor.exe} y un \texttt{inject.exe} que nunca arrancó), SRUM señala a
        \texttt{httpd.exe}, un \emph{stager} de Cobalt Strike disfrazado de Microsoft, como único responsable del tráfico.
\end{itemize}

\clearpage
\tableofcontents
\clearpage
"""

METODOLOGIA = r"""
\section{Metodología y convenciones}

\subsection{Principios seguidos}
\begin{enumerate}
  \item \textbf{Integridad}: verificar el hash de cada fichero contra el enunciado antes de analizarlo.
  \item \textbf{Seguridad}: no ejecutar nunca el malware. Se usa análisis estático (\texttt{objdump}, \texttt{strings},
        \texttt{readelf}, \texttt{rtfobj}), emulación de CPU (Unicorn) y, solo para el binario Go, emulación de
        espacio de usuario (\texttt{qemu-mips}) tras revisar su código.
  \item \textbf{Buscar lo que no cuadra}: nombres que no corresponden a su contenido, rutas impropias, tamaños absurdos,
        cabeceras anómalas, metadatos falsos, señuelos.
  \item \textbf{Correlacionar}: ninguna conclusión se apoya en un único artefacto.
  \item \textbf{Reproducibilidad}: cada paso tiene su comando exacto y la salida que produce.
\end{enumerate}

\subsection{Entorno}
\begin{itemize}
  \item \textbf{Análisis inicial}: contenedor Linux aislado en la nube (Ubuntu 24.04), desechable.
  \item \textbf{Réplica}: máquina virtual \textbf{Kali Linux 2026.2} en VirtualBox (2 GB RAM, 2 CPU, red NAT), shell
        \texttt{zsh}. Se recomienda tomar una instantánea (\emph{Machine $\to$ Take Snapshot}) antes de empezar.
\end{itemize}

\subsection{Cómo leer este documento}
\begin{itemize}
  \item \textbf{Caja oscura} con barra de título \texttt{(kali@kali)-[carpeta]\$}: comando exacto a escribir en la
        terminal, en la carpeta indicada. Programas en \textcolor{cmdc!70!black}{\textbf{verde}}, palabras clave del
        shell en \textcolor{kwc!80!black}{\textbf{rosa}}, cadenas en \textcolor{strc!50!black}{amarillo}, variables en
        \textcolor{varc!80!black}{morado}. Una flecha $\hookrightarrow$ indica que la línea continúa (no hay que pulsar Intro).
  \item \textbf{Caja clara con borde azul}: salida esperada. Se obtuvo ejecutando exactamente ese comando en un entorno de
        prueba; en Kali cambiarán el usuario (\texttt{kali} en lugar de \texttt{root}), las fechas de los ficheros
        extraídos y los tiempos.
  \item \textbf{Caja azul de nota}: interpretación de la salida.
  \item \textbf{Caja naranja}: hueco para la captura de pantalla del paso. Guardar la captura como
        \texttt{capturas/<id>.png} (el nombre exacto aparece en la caja) y recompilar; la imagen sustituye a la caja
        automáticamente. La lista completa está en \texttt{capturas/LEEME.txt}.
\end{itemize}

\begin{aviso}[Seguridad]
Los ficheros de los retos contienen malware real o simulado (ransomware, \emph{stagers} de Cobalt Strike, documentos
con exploits). Trabaja dentro de la VM, no ejecutes los binarios y no abras \texttt{Nominas.rtf} con Word/WordPad.
La VM tiene una carpeta compartida con el anfitrión: no copies ahí ningún fichero de los retos.
\end{aviso}
"""

INTRO = {}
CIERRE = {}

INTRO["prep"] = r"""
\section{Preparación del entorno}
Todos los retos se replican en \texttt{\textasciitilde/ctf}. Las herramientas se instalan una sola vez. Los scripts
propios (apéndice~\ref{ap:scripts}) se descargan del repositorio \texttt{moulyk-gg/retos} (rama \texttt{informe-retos}) y
los retos del \emph{release} \texttt{V1} del mismo repositorio.

\begin{nota}
Kali usa \texttt{zsh}. Por eso las rutas con \texttt{!} (``Reversing Go go go!'') van entre comillas
\emph{simples}: entre comillas dobles, \texttt{zsh} intentaría una expansión de historial.
\end{nota}
"""

INTRO["ccn"] = r"""
\clearpage
\section{Reversing: CCN-Cry}

\subsection{Ficha del reto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Categoría & Reversing / forense de red \\
Dificultad & 2/5 \\
Contraseña & \texttt{infected} (zip) \\
Objetivo & Descifrar \texttt{Secret.txt.CCN\_CRY} y obtener la flag \\
Herramientas & \texttt{7z}, \texttt{tshark}, \texttt{capinfos}, \texttt{objdump}, \texttt{strings}, \texttt{openssl}, \texttt{xxd} \\
\bottomrule
\end{tabularx}

\subsection{Enunciado}
\begin{quote}\itshape
Un equipo de la organización ha quedado inutilizado. Según las evidencias recogidas hasta el momento, parece que se
descargó y ejecutó algún ransomware. Entre los ficheros afectados se encuentra ``Secret.txt.CCN\_CRY'', el cual
necesitamos descifrar con urgencia. ¿Nos ayudas a descifrarlo? La contraseña del zip es \textbf{infected}.
\end{quote}

\subsection{Ficheros analizados}
"""

INTRO["ccn"] += r"""
\subsection{Resumen del análisis}
\begin{enumerate}
  \item \texttt{evidencia.zip} (cifrado AES) contiene \texttt{incident-a1000032.pcapng}, la captura de red del incidente.
  \item La víctima (\texttt{192.168.1.41}, \emph{hostname} \texttt{oat12}) descarga por HTTP \texttt{wget.tar.gz} desde
        \texttt{192.168.1.37}; dentro está el ransomware \texttt{ccn\_cry} (ELF x86-64).
  \item El ransomware genera con \texttt{srand(time(0))}/\texttt{rand()} una clave de 32 caracteres y un IV de 8, cifra
        con Blowfish-CBC y envía \texttt{clave:iv:hostname} al servidor de mando en la cabecera \texttt{Content-type}.
  \item Con la clave (\textbf{solo sus 16 primeros caracteres}, que es lo que usa el binario) y el IV recuperados de la
        captura, OpenSSL descifra el fichero.
\end{enumerate}
"""

CIERRE["ccn"] = r"""
\subsection{Resultado}
\flagbox{Flag de CCN-Cry (validada)}{flag\{c890082bbb38d2aad5eb182cac9fbc7e\}}
Contenido descifrado de \texttt{Secret.txt}: \texttt{Flag: JosephPopp1989}.

\subsection{Funcionamiento del ransomware}
\begin{itemize}
  \item \textbf{Objetivo}: recorre el directorio \texttt{/home/robertM/} (\texttt{opendir}/\texttt{readdir}/\texttt{\_\_xstat})
        buscando ficheros cuya extensión (\texttt{strrchr}) esté en una lista de unas 150 (documentos, imágenes,
        bases de datos, código, claves\dots).
  \item \textbf{Cifrado}: Blowfish-CBC (\texttt{EVP\_bf\_cbc}) con clave efectiva de 128 bits; escribe
        \texttt{<fichero>.CCN\_CRY} y borra el original (\texttt{remove}).
  \item \textbf{Clave}: 32 caracteres + IV de 8 tomados de un alfabeto de 78 símbolos con \texttt{rand() \% 78},
        sembrado con la hora (\texttt{srand(time(0))}).
  \item \textbf{Mando y control}: \texttt{GET /user.php} a \texttt{www.aarkaposleeqaasssf.tk:8080} con
        \texttt{Content-type: clave:iv:hostname}.
\end{itemize}

\textbf{Debilidades explotadas}: (1) la clave viaja en claro por HTTP y queda en la captura; (2) aunque no viajara,
\texttt{srand(time)} haría posible la fuerza bruta probando las semillas cercanas a la hora del incidente; (3) la
misma clave sirve para todos los ficheros.

\subsection{Indicadores de compromiso (IOC)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
\textbf{Tipo} & \textbf{Valor} \\ \midrule
IP víctima & \texttt{192.168.1.41} (\emph{hostname} \texttt{oat12}) \\
IP servidor & \texttt{192.168.1.37} (HTTP/80 distribución, HTTP/8080 mando y control) \\
Dominio C2 & \texttt{www.aarkaposleeqaasssf.tk} \\
URL & \nolinkurl{http://192.168.1.37/wget.tar.gz}, \nolinkurl{http://www.aarkaposleeqaasssf.tk:8080/user.php} \\
Fichero & \texttt{ccn\_cry} (ELF x86-64), MD5 \texttt{e1e1d64b6d6349ed81fa4ee0913ef931} \\
Extensión & \texttt{.CCN\_CRY} \\
Ruta objetivo & \texttt{/home/robertM/} \\
Firma de red & Cabecera \texttt{Content-type} con formato \texttt{[32 car.]:[8 car.]:[hostname]} \\
\bottomrule
\end{tabularx}

\subsection{Técnicas observadas (MITRE ATT\&CK)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
T1105 & \emph{Ingress Tool Transfer}: descarga de \texttt{wget.tar.gz} por HTTP. \\
T1486 & \emph{Data Encrypted for Impact}: cifrado Blowfish de los ficheros de la víctima. \\
T1083 & \emph{File and Directory Discovery}: recorrido de \texttt{/home/robertM/}. \\
T1082 & \emph{System Information Discovery}: \texttt{gethostname}. \\
T1071.001 & \emph{Application Layer Protocol: Web}: comunicación con el C2 por HTTP. \\
T1041 & \emph{Exfiltration Over C2 Channel}: envío de la clave y el IV. \\
T1070.004 & \emph{File Deletion}: borrado de los originales. \\
T1046 & \emph{Network Service Discovery}: la captura termina con un barrido de puertos desde \texttt{.41} hacia
        \texttt{.37} con puerto origen fijo (patrón típico de \texttt{nmap -sS}). \\
\bottomrule
\end{tabularx}

\subsection{Contexto: ¿por qué se llama así?}
\begin{itemize}
  \item \textbf{CCN-Cry} une \textbf{CCN} (Centro Criptológico Nacional, del que depende el CCN-CERT español) y
        \textbf{Cry}, por \textbf{WannaCry} (2017), el ransomware más famoso. La extensión \texttt{.CCN\_CRY} imita
        la costumbre de renombrar los ficheros cifrados (WannaCry usaba \texttt{.WNCRY}).
  \item El dominio \texttt{aarkaposleeqaasssf.tk} es una ristra aleatoria al estilo del \emph{kill-switch} de WannaCry
        (\texttt{iuqerfsodp9ifjaposdfjhgosurijfaewrwergwea.com}). \texttt{.tk} (Tokelau) fue durante años un dominio
        gratuito muy usado por malware.
  \item \textbf{Joseph Popp, 1989}: autor del \textbf{AIDS Trojan} (o \emph{PC Cyborg}), considerado el
        \textbf{primer ransomware de la historia}. Repartió unos 20.000 disquetes entre asistentes a la conferencia
        de la OMS sobre el SIDA; tras 90 arranques ocultaba los directorios y cifraba los nombres de los ficheros, y
        exigía 189 dólares a un apartado postal de Panamá. Su cifrado era simétrico y la clave estaba en el propio
        programa: igual que en este reto, el error del atacante deja la clave al alcance del analista.
  \item \textbf{Blowfish}: cifrado de bloque de 64 bits diseñado por Bruce Schneier en 1993. En OpenSSL~3 se considera
        \emph{legacy}, por eso hay que cargar ese \emph{provider}.
\end{itemize}

\subsection{Conclusión}
Un ransomware que transmite su clave en claro es reversible con la propia evidencia de red. El análisis estático del
binario fue imprescindible para descubrir el detalle que hace fallar el descifrado ingenuo: la longitud de clave
fijada a 16 bytes.
"""

INTRO["kraken"] = r"""
\clearpage
\section{Reversing: The Kraken}

\subsection{Ficha del reto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Categoría & Reversing (Windows, PE x86) \\
Dificultad & 2/5 \\
Objetivo & Encontrar la flag dentro de \texttt{TheKraken.exe} \\
Herramientas & \texttt{xxd}, \texttt{objdump}, Python (\texttt{pefile}, \texttt{unicorn}), lista de exports de Wine \\
\bottomrule
\end{tabularx}

\subsection{Enunciado}
\begin{quote}\itshape Encuentra la flag. (Fichero: TheKraken.exe, MD5 33b0654d8e104031155c999e2f163bbd)\end{quote}

\subsection{Ficheros analizados}
"""
INTRO["kraken"] += r"""
\subsection{Resumen del análisis}
\begin{enumerate}
  \item El ejecutable mide 932 bytes, tiene la cabecera PE solapada con la DOS (\texttt{MZ23PE}), 0 secciones y
        \texttt{SizeOfImage} de 500 MB: es un ejecutable comprimido con \textbf{Crinkler} (versión 2.3).
  \item En lugar de ejecutarlo, se \textbf{emula} el descompresor con Unicorn y se vuelca el código real (0x420000).
  \item El código desempaquetado resuelve 8 APIs de \texttt{kernel32} por hash; con la lista de exports de Wine se
        identifican: entre ellas \texttt{GetACP} y \texttt{OutputDebugStringA}.
  \item \texttt{main} descifra 23 bytes usando el byte bajo de \texttt{GetACP()} y los envía al depurador. Probando los
        256 valores, solo uno produce texto legible terminado en \texttt{\textbackslash 0}.
\end{enumerate}
"""

CIERRE["kraken"] = r"""
\subsection{Resultado}
\flagbox{Flag de The Kraken}{flag\{d11c2e023a6a0fb3105121dade32232b\}}
Texto descifrado: \texttt{Flag: Kongespeilet1250} (con \texttt{k = 0x44}).

\subsection{Imports resueltos por hash}
Algoritmo del \emph{resolver}: $h \leftarrow \mathrm{rol}_{32}(h, 6) \oplus c$ para cada carácter $c$ del nombre,
incluido el nulo final.

\begin{tabularx}{\linewidth}{@{}llX@{}}
\toprule
\textbf{IAT} & \textbf{Hash} & \textbf{API} \\ \midrule
\texttt{0x430000} & \texttt{0x35002069} & \texttt{GetACP} --- página de códigos ANSI; su byte bajo es la clave \\
\texttt{0x430004} & \texttt{0x3d4b4991} & \texttt{GetCurrentProcess} \\
\texttt{0x430008} & \texttt{0x02aef17b} & \texttt{IsProcessorFeaturePresent} \\
\texttt{0x43000c} & \texttt{0xe9826fc6} & \texttt{LoadLibraryA} \\
\texttt{0x430010} & \texttt{0x12d183bb} & \texttt{OutputDebugStringA} --- salida de la flag \\
\texttt{0x430014} & \texttt{0x06a232ca} & \texttt{SetUnhandledExceptionFilter} \\
\texttt{0x430018} & \texttt{0x3ccc4310} & \texttt{TerminateProcess} \\
\texttt{0x43001c} & \texttt{0x4ba23380} & \texttt{UnhandledExceptionFilter} \\
\bottomrule
\end{tabularx}

Las cuatro últimas pertenecen al código estándar de Visual C++ para la comprobación de \emph{stack cookies}
(\texttt{\_\_report\_gsfailure}).

\subsection{Algoritmo de descifrado}
Para cada posición $i \in [0,22]$ del array de \texttt{main}:
\[ c_i' = \mathrm{rol}_8\!\big(-\,((c_i \oplus \mathtt{0x7C}) + k) \bmod 256,\ 1\big) - i \pmod{256},
   \qquad k = \mathtt{GetACP()} \,\&\, \mathtt{0xFF} \]

\textbf{Por qué al ejecutarlo ``no pasa nada''}: (1) el texto va a \texttt{OutputDebugStringA}, que solo se ve con un
depurador o con \emph{DebugView} de Sysinternals; (2) el descifrado depende de la página de códigos del sistema, y con
las habituales (1252 en Europa occidental, 65001 UTF-8\dots) sale basura. El camino previsto es el reversing.
El bucle de números \texttt{double} del principio de \texttt{main} llama a dos funciones vacías y no afecta al
resultado: es relleno para despistar.

\subsection{Técnicas observadas (MITRE ATT\&CK)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
T1027.002 & \emph{Software Packing}: Crinkler. \\
T1027.007 & \emph{Dynamic API Resolution}: imports resueltos por hash recorriendo el PEB. \\
T1614.001 & \emph{System Language Discovery}: \texttt{GetACP} condiciona el resultado. \\
T1027 & \emph{Obfuscated Files or Information}: cadena cifrada y salida por canal de depuración. \\
\bottomrule
\end{tabularx}

\subsection{Contexto: ¿por qué se llama así?}
\begin{itemize}
  \item El \textbf{Kraken} es el monstruo marino de la tradición escandinava, capaz de hundir barcos. Su
        \textbf{primera descripción conocida} está en el \emph{Konungs skuggsjá} (en noruego \textbf{Kongespeilet},
        ``El espejo del rey''), un texto noruego escrito \textbf{hacia el año 1250}, donde aparece como
        \emph{hafgufa}, una criatura tan grande que los marineros la confundían con una isla. La flag es, literalmente,
        ``el origen del Kraken''.
  \item Como el monstruo, el binario oculta su tamaño real: 932 bytes en disco que se despliegan en memoria.
        \textbf{Kraken} es además el nombre de un algoritmo de compresión (Oodle Kraken), y el reto gira en torno a un
        compresor.
  \item \textbf{Crinkler} es un compresor-enlazador creado para la demoscene (intros de 4 KB) por Rune L. H. Stubbe
        (\emph{Mentor}) y Aske Simon Christensen (\emph{Blueberry}). Su firma es la cabecera \texttt{MZ} seguida de la
        versión en ASCII y \texttt{PE} en el offset 4.
\end{itemize}

\subsection{Conclusión}
Un ejecutable diminuto puede esconder mucho: empaquetado, resolución dinámica de APIs, dependencia del idioma del
sistema y salida por un canal invisible. La emulación permite desempaquetar sin riesgo y el reconocimiento de patrones
(hash de nombres, terminador nulo) valida la solución sin necesidad de ejecutar el programa.
"""

INTRO["spear"] = r"""
\clearpage
\section{Reversing: Spear Phishing\dots{} Can you catch me? (partes 1 y 2)}

\subsection{Ficha del reto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Categoría & Reversing / análisis de documentos maliciosos \\
Dificultad & 1/5 \\
Contraseña & \texttt{infected} (rar) \\
Objetivo parte 1 & Determinar qué CVE explota el documento (formato \texttt{CVE-XXXX-XXXX}) \\
Objetivo parte 2 & Determinar la URL dañina relacionada con el documento (se desbloquea al resolver la parte 1) \\
Herramientas & \texttt{unrar}, \texttt{rtfobj} (oletools), \texttt{grep}, \texttt{xxd}, Python \\
\bottomrule
\end{tabularx}

\subsection{Enunciado}
\begin{quote}\itshape
Un empleado ha reportado al equipo de seguridad un e-mail sospechoso que podría ser fruto de una campaña de spear
phishing a la compañía. Al parecer, el documento carece de contenido alguno y presenta un formato poco común. Es
probable que el mismo se aproveche de alguna vulnerabilidad y que el equipo haya sido comprometido. Tu objetivo será
determinar qué CVE trata de explotar dicho documento (CVE-XXXX-XXXX). \textup{[Parte 2:]} \dots{} determinar qué URL
dañina está relacionada con el mismo.
\end{quote}

\subsection{Ficheros analizados}
"""
INTRO["spear"] += r"""
\subsection{Resumen del análisis}
\begin{enumerate}
  \item El RAR (formato 2.9, cifrado AES) contiene \texttt{Nominas.rtf}: un RTF \textbf{sin texto}.
  \item Su único contenido es un objeto OLE con \texttt{\bs objautlink\bs objupdate} (se actualiza solo al abrirse) de
        clase \texttt{OLE2Link}, que contiene un \textbf{URL Moniker} apuntando a \texttt{http://dagobah.local/logo.doc}.
  \item Ese patrón es exactamente el de \textbf{CVE-2017-0199}. \texttt{rtfobj} lo confirma y extrae la URL.
\end{enumerate}
"""

CIERRE["spear"] = r"""
\subsection{Resultado}
\flagbox{Parte 1: CVE (validada)}{flag\{93b146d21d3bdc8635836f8a11ba62b9\}}
\flagbox{Parte 2: URL dañina}{flag\{fb7534ecc904766563ad711331a11121\}}
Valores: \texttt{CVE-2017-0199} y \texttt{http://dagobah.local/logo.doc}. Si la plataforma no aceptara la URL
completa, las variantes son \texttt{dagobah.local/logo.doc} (\texttt{39187b419652a52cb5bca8ed2d8952c7}) y
\texttt{dagobah.local} (\texttt{d19e4c1cde7f30c64aadd9b2aff5cf49}).

\subsection{Cómo funciona CVE-2017-0199}
\begin{enumerate}
  \item La víctima abre \texttt{Nominas.rtf} con Word.
  \item \texttt{\bs objupdate} obliga a Word a actualizar el objeto enlazado sin pedir confirmación.
  \item El objeto \texttt{OLE2Link} (\texttt{StdOleLink}, CLSID \texttt{00000300-\allowbreak 0000-\allowbreak 0000-\allowbreak C000-\allowbreak 000000000046}) usa un
        \emph{URL Moniker} (\texttt{79EAC9E0-\allowbreak BAF9-\allowbreak 11CE-\allowbreak 8C82-\allowbreak 00AA004BA90B}) para descargar
        \texttt{http://dagobah.local/logo.doc}.
  \item El servidor responde con \texttt{Content-Type: application/hta}. Aunque la extensión sea \texttt{.doc}, Windows
        entrega el contenido al manejador de HTA, \texttt{mshta.exe}, que ejecuta el VBScript/JScript incrustado.
  \item El script descarga e instala la carga final. Todo ocurre al abrir el documento, sin macros.
\end{enumerate}

\subsection{Descarte de CVE similares}
\texttt{rtfobj} avisa de que \texttt{OLE2Link} también aparece en otras vulnerabilidades; cada una deja una huella
distinta que no está en este fichero:

\begin{tabularx}{\linewidth}{@{}lXc@{}}
\toprule
\textbf{CVE} & \textbf{Rasgo característico} & \textbf{¿Presente?} \\ \midrule
CVE-2017-8570 & \emph{Composite Moniker} + scriptlet \texttt{.sct} & No \\
CVE-2017-8759 & \texttt{soap:wsdl=} (moniker SOAP de .NET) & No \\
CVE-2018-8174 & VBScript ``Double Kill'' & No \\
\textbf{CVE-2017-0199} & \textbf{URL Moniker a un HTA vía \texttt{OLE2Link}} & \textbf{Sí} \\
\bottomrule
\end{tabularx}

\subsection{Indicadores de compromiso (IOC)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Fichero & \texttt{Nominas.rtf}, MD5 \texttt{799417ddacb87275c7121e1620415be3} \\
URL & \texttt{http://dagobah.local/logo.doc} \\
Dominio & \texttt{dagobah.local} (red interna) \\
Firma RTF & \texttt{\bs objautlink}, \texttt{\bs objupdate}, \texttt{OLE2Link} (\texttt{4f4c45324c696e6b}) \\
CLSID & URL Moniker \texttt{\{79EAC9E0-\allowbreak BAF9-\allowbreak 11CE-\allowbreak 8C82-\allowbreak 00AA004BA90B\}} \\
\bottomrule
\end{tabularx}

\subsection{Técnicas observadas (MITRE ATT\&CK)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
T1566.001 & \emph{Spearphishing Attachment}: correo dirigido con un adjunto de ``nóminas''. \\
T1204.002 & \emph{User Execution: Malicious File}: basta con que la víctima abra el documento. \\
T1203 & \emph{Exploitation for Client Execution}: CVE-2017-0199 en Office. \\
T1218.005 & \emph{System Binary Proxy Execution: Mshta}: el HTA se ejecuta con \texttt{mshta.exe}. \\
T1105 & \emph{Ingress Tool Transfer}: descarga de la carga desde la URL. \\
\bottomrule
\end{tabularx}

\subsection{Contexto: ¿por qué se llama así?}
\begin{itemize}
  \item \textbf{Spear phishing} es el phishing ``con arpón'': dirigido a una organización o persona concreta, con un
        cebo creíble. ``\textbf{Can you catch me?}'' juega con el doble sentido de \emph{phishing} (pescar) y
        \emph{catch} (atrapar), y recuerda a \emph{Catch Me If You Can}, la historia del estafador Frank Abagnale.
  \item \textbf{Nóminas}: uno de los cebos más eficaces; casi nadie resiste abrir un documento sobre sueldos.
  \item \textbf{Dagobah} es el planeta pantanoso de \emph{Star Wars} donde Yoda vive escondido. El atacante también se
        esconde, en un servidor de la red interna (\texttt{.local}).
  \item \textbf{CVE-2017-0199} fue un \emph{0-day} detectado en abril de 2017 (FireEye y McAfee) y parcheado el 11 de
        abril de 2017. Grupos como APT28 o APT34 y campañas de Dridex lo usaron durante años; este documento es de
        septiembre de 2017, cuando seguía siendo muy explotado.
\end{itemize}

\subsection{Conclusión}
Un documento ``vacío'' no es inofensivo: todo el ataque está en un objeto enlazado. Detectarlo requiere mirar la
estructura del fichero (\texttt{rtfobj}), no su contenido visible. Mitigaciones: parchear Office, bloquear objetos OLE
en RTF y limitar \texttt{mshta.exe}.
"""

INTRO["go"] = r"""
\clearpage
\section{Reversing: Go go go!}

\subsection{Ficha del reto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Categoría & Reversing (Linux, Go, MIPS) \\
Dificultad & 3/5 \\
Contraseña & \texttt{infected} (zip) \\
Objetivo & Obtener la flag del binario \\
Herramientas & \texttt{7z}, \texttt{readelf}, \texttt{strings}, Python (\texttt{pyelftools}, \texttt{capstone},
  \texttt{pycryptodome}), \texttt{qemu-mips} (opcional) \\
\bottomrule
\end{tabularx}

\subsection{Enunciado}
\begin{quote}\itshape Obtén el flag del siguiente binario. NOTA: el password del zip es infected.\end{quote}

\subsection{Ficheros analizados}
"""
INTRO["go"] += r"""
\subsection{Resumen del análisis}
\begin{enumerate}
  \item \texttt{LetsGo} es un ELF de 32 bits para \textbf{MIPS big-endian}, escrito en Go 1.10.3 y sin símbolos.
  \item La tabla \texttt{.gopclntab} conserva los nombres de las funciones; un parser propio los recupera.
  \item \texttt{main.main} (desensamblado con Capstone) solo revela la flag si el kernel contiene \texttt{4.14.0}, hay
        exactamente \textbf{3 CPUs} y el sistema es \texttt{linux}. Por eso, al ejecutarlo, no imprime nada.
  \item Usa la tercera de tres claves casi iguales (\texttt{1KH1hb001Y09olUo}) para descifrar con AES-128-CFB una
        cadena Base64-URL. Se descifra directamente en Python sin ejecutar el binario.
\end{enumerate}
"""

CIERRE["go"] = r"""
\subsection{Resultado}
\flagbox{Flag de Go go go!}{flag\{f389c15c0ea41f12e53806fba659e2fb\}}
Texto descifrado: \texttt{Flag: RobPike2009} (relleno PKCS\#7 de 15 bytes \texttt{0x0f}, que confirma la clave).

\subsection{Flujo de \texttt{main.main}}
\begin{enumerate}
  \item \texttt{goInfo.GetInfo()} recoge SO, kernel, núcleo, plataforma, \emph{hostname} y CPUs
        (cadena de formato \texttt{GoOS:\%v,} \texttt{Kernel:\%v,}\,\dots).
  \item Si \texttt{Kernel} no contiene \texttt{4.14.0} $\to$ termina sin decir nada.
  \item Convierte a \emph{slice} las tres claves \texttt{1KH1hb001Y09olU2}, \texttt{1KH1hb001Y09olU1} y
        \texttt{1KH1hb001Y09olUo}; solo la tercera llega a \texttt{aes.NewCipher}.
  \item Decodifica \texttt{wD5q\dots D4Hk} (Base64-URL, 64 caracteres = 48 bytes): IV = 16 primeros bytes; resto =
        32 bytes cifrados. Descifra con \texttt{cipher.NewCFBDecrypter}.
  \item \texttt{switch CPUs}: con 2 u 8 lanza goroutines que cifran cadenas señuelo; con un valor distinto de 3 termina.
  \item Con 3 CPUs quita el relleno, comprueba que el SO contenga \texttt{linux} y dibuja la flag en ASCII-art con
        \texttt{go-figure}; si no, vuelca la información del sistema (\texttt{VarDump}).
\end{enumerate}

\subsection{Señuelos}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
\texttt{1KH1hb001Y09olU1}, \texttt{\dots U2} & Claves casi idénticas a la real que producen basura. \\
\texttt{wD5q\dots D4Ha} & Cadena casi idéntica a la real (cambia el último carácter), usada por las goroutines. \\
\texttt{Xa22SKeyAll1aadf1} & Cadena con aspecto de clave para la goroutine del caso 2 CPUs. \\
\texttt{dwnoDlybPWZTYRdbFpit} + \texttt{SAgpdWyEhTjWmAmqBNaBgPJv} & Concatenadas por \texttt{main.FWPmCP}; no llegan a usarse para la flag. \\
Nombres ofuscados & \texttt{main.FWPmCP}, \texttt{main.PCCKsmOSrmbDMUGqoFINVL}, \texttt{main.quKuchsVvIEUGZDKOxl}. \\
\bottomrule
\end{tabularx}

\subsection{Técnicas observadas (MITRE ATT\&CK)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
T1480.001 & \emph{Execution Guardrails: Environmental Keying}: el secreto solo se revela con kernel 4.14.0, 3 CPUs y Linux. \\
T1497.001 & \emph{Virtualization/Sandbox Evasion: System Checks}: comprobaciones del entorno antes de actuar. \\
T1082 & \emph{System Information Discovery}: \texttt{goInfo.GetInfo}. \\
T1027 & \emph{Obfuscated Files or Information}: cadena cifrada, claves señuelo y nombres de funciones ofuscados. \\
T1140 & \emph{Deobfuscate/Decode Files or Information}: Base64 + AES-CFB en tiempo de ejecución. \\
\bottomrule
\end{tabularx}

\subsection{Contexto: ¿por qué se llama así?}
\begin{itemize}
  \item \textbf{``Go go go!'' / ``LetsGo''}: juego de palabras con el nombre del lenguaje \textbf{Go}.
  \item \textbf{Rob Pike} es uno de los tres creadores de Go en Google, junto con Robert Griesemer y Ken Thompson
        (diseño iniciado en 2007). Antes trabajó en Bell Labs en Unix y Plan~9 y co-diseñó UTF-8 con Ken Thompson.
        Go se presentó públicamente el \textbf{10 de noviembre de 2009}. ``RobPike2009'' es, por tanto, el creador y
        el año de nacimiento público del lenguaje.
  \item \textbf{Go + MIPS} es una combinación muy habitual en el malware IoT actual: Go genera binarios estáticos que se
        compilan fácilmente para routers y cámaras.
\end{itemize}

\subsection{Conclusión}
Los binarios Go \emph{stripped} siguen siendo analizables gracias a \texttt{.gopclntab}. El \emph{environmental
keying} hace inútil el análisis dinámico ingenuo; el estático revela las condiciones y permite descifrar la flag sin
recrear el entorno.
"""

INTRO["horcrux"] = r"""
\clearpage
\section{H0rr0crux}

\subsection{Ficha del reto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Categoría & Forense de Windows (post-incidente) \\
Dificultad & 1/5 (125 puntos) \\
Objetivo & MD5 del binario dañino responsable de las conexiones (\texttt{flag\{<md5\_binario>\}}) \\
Herramientas & \texttt{7z}, \texttt{sccainfo}, \texttt{esedbexport}, Python (\texttt{regipy}, \texttt{python-evtx},
  \texttt{pefile}), \texttt{strings}, VirusTotal API v3 \\
\bottomrule
\end{tabularx}

\subsection{Enunciado}
\begin{quote}\itshape
Nuestros compañeros del SOC nos han avisado de que cierta máquina ha realizado conexiones sospechosas que podrían
estar relacionadas con el malware Gozi. Tras recoger evidencias se ha restaurado el equipo. Necesitamos identificar el
binario dañino responsable de las conexiones. Objetivo: proporciona el MD5 del binario dañino (flag\{<md5\_binario>\}).
\end{quote}

\subsection{Ficheros analizados}
"""
INTRO["horcrux"] += r"""
\subsection{Resumen del análisis}
\begin{enumerate}
  \item La evidencia es una adquisición tipo KAPE del equipo \texttt{DESKTOP-VK0V8TR} (usuario \textbf{Gregor}, VM de
        VirtualBox): \texttt{\$MFT}, \texttt{\$LogFile}, Amcache, SRUM, 247 Prefetch, 141 \texttt{.evtx}, logs del registro.
  \item Prefetch y Amcache muestran varios ejecutables sospechosos; la mayoría resultan ser \textbf{señuelos}:
        \texttt{inject.exe} (nunca arrancó), \texttt{runas.exe} (= SDelete), \texttt{uninstall.exe} (= PE Look),
        VMProtect y un \texttt{tor.exe} falso.
  \item \textbf{SRUM} (uso de red por aplicación) atribuye tráfico a un único binario sospechoso:
        \texttt{C:\bs Users\bs Gregor\bs AppData\bs Roaming\bs Microsoft\bs Windows\bs httpd.exe}, que se hace pasar
        por un componente de Microsoft.
  \item La \texttt{\$MFT} prueba que llegó por \emph{drag \& drop} desde el anfitrión y que se colgó dos veces; el
        fichero fue borrado (SDelete) y los logs de Windows recortados (\texttt{wevtutil}).
  \item Amcache conserva su \textbf{SHA1}; VirusTotal lo identifica como \textbf{Cobalt Strike} (61 detecciones) y da
        su \textbf{MD5}.
\end{enumerate}
"""

CIERRE["horcrux"] = r"""
\subsection{Resultado}
\flagbox{Flag de H0rr0crux}{flag\{dbe0e10775e35a58e8ff463ccbe5f7d8\}}
Binario: \texttt{C:\bs Users\bs Gregor\bs AppData\bs Roaming\bs Microsoft\bs Windows\bs httpd.exe} ---
15.360 bytes, PE32, SHA1 \hash{409aea9461d03bff3e006d3e7e7c4790a0862170}, MD5
\hash{dbe0e10775e35a58e8ff463ccbe5f7d8}, detectado como \texttt{trojan.cobaltstrike/fugrafa}.

\subsection{Línea de tiempo (20/12/2021, UTC)}
\begin{longtable}{@{}L{2.3cm}L{9.6cm}L{3.2cm}@{}}
\toprule
\textbf{Hora} & \textbf{Evento} & \textbf{Fuente} \\ \midrule \endhead
12:44--12:45 & Instalación de WinSCP 5.19.5 & Prefetch \\
12:50:49 & \texttt{runas.exe} llega por \emph{drag \& drop} desde el anfitrión & \texttt{\$MFT} \\
12:51:10 & Ejecución de \texttt{AppData\bs Local\bs Microsoft\bs uninstall.exe} (PE Look) & Prefetch, Amcache \\
12:51:29--12:51:45 & Instalador Inno Setup (\texttt{PACKED.TMP}) de VMProtect Demo & Prefetch \\
12:52:23--26 & Llega \texttt{inject.exe}; falla al arrancar (faltan MSVCP140 y VCRUNTIME140) & \texttt{\$MFT}, System.evtx (ID 26) \\
12:53:25 & \texttt{VMProtect.exe} & Prefetch \\
12:56:21 & Primera ejecución de \texttt{AppData\bs runas.exe} (SDelete) & Prefetch \\
13:01--13:02 & Último evento en Application, Security y System & \texttt{.evtx} \\
13:08:03 & Defender detecta \texttt{inject.exe} (\texttt{Trojan:Win32/Sabsik.TE.A!ml}) & Defender \\
13:08:50 & Segunda ejecución de SDelete & Prefetch \\
13:09:01 & Ejecución de \texttt{AppData\bs Local\bs Temp\bs tor.exe} & Prefetch \\
\textbf{13:09:30} & \textbf{Llega \texttt{httpd.exe} por \emph{drag \& drop}} & \texttt{\$MFT} \\
13:10:39, 13:11:57 & \textbf{\texttt{httpd.exe} se cuelga} (informes WER \texttt{AppCrash\_httpd.exe\_\dots}) & \texttt{\$MFT} \\
13:12:15 & Última de 12 ejecuciones de \texttt{wevtutil} & Prefetch \\
15:03:39 & Tercera ejecución de SDelete & Prefetch \\
15:04 & Defender pone en cuarentena \texttt{inject.exe} & Defender \\
15:07:16 & Segunda ejecución de \texttt{tor.exe} & Prefetch \\
\textbf{14:53--15:53} & \textbf{\texttt{httpd.exe}: 800 B enviados / 1.214 B recibidos} & \textbf{SRUM} \\
15:09--15:23 & El analista ejecuta FTK Imager y copia las evidencias a \texttt{Desktop\bs evidencias} & Prefetch, \texttt{\$MFT} \\
\bottomrule
\end{longtable}

\subsection{Candidatos y señuelos}
\begin{longtable}{@{}L{3.6cm}L{6.2cm}L{5.3cm}@{}}
\toprule
\textbf{Binario} & \textbf{Qué es realmente} & \textbf{Veredicto} \\ \midrule \endhead
\texttt{Downloads\bs inject.exe} & 226.304 B, x64. Defender: \texttt{Sabsik.TE.A!ml} (detección genérica por ML). No está en VirusTotal & Señuelo: \textbf{nunca llegó a ejecutarse} (faltaban DLL) \\
\texttt{AppData\bs runas.exe} & \textbf{SDelete} 2.04 de Sysinternals (\texttt{OriginalFileName = sdelete.exe}) & Herramienta \textbf{antiforense}: borró el malware \\
\texttt{AppData\bs Local\bs Microsoft\bs uninstall.exe} & \textbf{PE Look} 1.73 (\texttt{pelook.exe}, bytepointer.com) & Herramienta de análisis renombrada, sin red \\
\texttt{packed.exe}, \texttt{PACKED.TMP} & Instalador de \textbf{VMProtect Demo} & Herramienta de empaquetado \\
\texttt{AppData\bs Local\bs Temp\bs tor.exe} & 231.936 B, sin metadatos; VirusTotal: \texttt{tag\_converter.exe}, 3 detecciones, sin familia & Señuelo (el Tor real pesa varios MB); \textbf{sin tráfico en SRUM} \\
\textbf{\texttt{AppData\bs Roaming\bs Microsoft\bs Windows\bs httpd.exe}} & 15.360 B, PE32, \emph{Microsoft Operating System 1.0.0.0} (falso), compilado el 09/06/2020; VirusTotal: \textbf{Cobalt Strike}, 61 detecciones & \textbf{Responsable de las conexiones} \\
\bottomrule
\end{longtable}

\subsection{Qué aporta cada artefacto}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
\textbf{Prefetch} & Qué se ejecutó, cuántas veces, cuándo y desde qué ruta. \\
\textbf{Amcache.hve} & SHA1, tamaño, fecha de compilación y metadatos de versión (\texttt{OriginalFileName}, \emph{publisher}):
  destapa los ejecutables renombrados y conserva el hash de ficheros ya borrados. \\
\textbf{SRUM} (\texttt{SRUDB.dat}) & Bytes enviados y recibidos por aplicación y por hora: \textbf{decide quién hizo las conexiones}. \\
\textbf{\$MFT} & Nombres e índices de directorios: \emph{drag \& drop} de VirtualBox, informes WER de \emph{crash} y
  ausencia del fichero borrado. \\
\textbf{PCA} (\texttt{ntuser.dat.LOG2}) & El \emph{Program Compatibility Assistant} registra la ruta de \texttt{httpd.exe} como ejecutada. \\
\textbf{.evtx} & Detección de Defender, fallo de arranque de \texttt{inject.exe} y logs recortados. \\
\textbf{VirusTotal} & Convierte el SHA1 de Amcache en MD5 e identifica la familia. \\
\bottomrule
\end{tabularx}

\subsection{¿Por qué Cobalt Strike y no Gozi?}
El enunciado dice que las conexiones ``\emph{podrían} estar relacionadas con el malware Gozi'': es una hipótesis del
SOC, no un hecho. Lo que se pide es ``el binario dañino \textbf{responsable de las conexiones}'', y las evidencias son
unánimes: SRUM atribuye el tráfico a \texttt{httpd.exe}, es el único de los candidatos que es malware confirmado y se
disfraza de Microsoft. Además, en intrusiones reales \textbf{Gozi/Ursnif} se usa a menudo como acceso inicial y después
despliega \textbf{Cobalt Strike}, así que la sospecha inicial del SOC encaja con lo encontrado.

\subsection{Indicadores de compromiso (IOC)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
Ruta & \texttt{C:\bs Users\bs Gregor\bs AppData\bs Roaming\bs Microsoft\bs Windows\bs httpd.exe} \\
MD5 & \texttt{dbe0e10775e35a58e8ff463ccbe5f7d8} \\
SHA1 & \texttt{409aea9461d03bff3e006d3e7e7c4790a0862170} \\
Metadatos falsos & \texttt{ProductName: Microsoft Operating System}, \texttt{FileVersion 1.0.0.0}, \texttt{LinkDate 2020-06-09 00:17:15} \\
Herramientas del atacante & SDelete renombrado (\texttt{AppData\bs runas.exe}, SHA1 \texttt{4aa4b498\dots 5c3af5f6b8d97}),
  \texttt{wevtutil} \\
\bottomrule
\end{tabularx}

\subsection{Técnicas observadas (MITRE ATT\&CK)}
\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
T1036 & \emph{Masquerading}: \texttt{httpd.exe} con metadatos de Microsoft; SDelete como \texttt{runas.exe};
        \texttt{tag\_converter.exe} como \texttt{tor.exe}. \\
T1071.001 & \emph{Application Layer Protocol: Web}: el \emph{stager} de Cobalt Strike se comunica por HTTP. \\
T1070.001 & \emph{Indicator Removal: Clear Windows Event Logs}: \texttt{wevtutil}. \\
T1070.004 & \emph{Indicator Removal: File Deletion}: SDelete. \\
T1027.002 & \emph{Software Packing}: VMProtect Demo instalado en el equipo. \\
\bottomrule
\end{tabularx}

\subsection{Contexto: ¿por qué se llama así?}
\begin{itemize}
  \item Un \textbf{Horrocrux} (\emph{Harry Potter}) es un objeto en el que Voldemort esconde un fragmento de su alma
        para no morir: para vencerlo hay que encontrarlos y destruirlos todos.
  \item \textbf{Sorvolo Gaunt} (\emph{Marvolo Gaunt} en inglés), abuelo de Voldemort, poseía el \textbf{anillo con la
        Piedra de la Resurrección} que Voldemort convirtió en Horrocrux: es el anillo de la imagen del reto y da nombre
        al fichero \texttt{evidencias\_sorvologaunt}.
  \item \textbf{Paralelismo}: el ``cuerpo'' del malware fue destruido (borrado con SDelete y equipo restaurado), pero su
        ``alma'' quedó repartida en varios artefactos: Amcache (SHA1), SRUM (red), \texttt{\$MFT} (llegada y
        \emph{crashes}), PCA y Prefetch. Hay que reunir los fragmentos para identificarlo, igual que hay que localizar
        todos los Horrocruxes.
  \item \textbf{Gozi} (Ursnif, ISFB, Dreambot) es un troyano bancario de 2007, uno de los más longevos. Su código se
        filtró en 2010 y 2015 y dio lugar a decenas de variantes; algunas usan Tor para el C2 (de ahí el señuelo
        \texttt{tor.exe}).
  \item \textbf{Cobalt Strike} es una plataforma comercial de \emph{red team} (Raphael Mudge, 2012) cuyo agente se llama
        \emph{Beacon}. Las versiones crackeadas la han convertido en una de las herramientas favoritas de los atacantes.
        Sus \emph{stagers} \texttt{.exe} pesan unos 14--15 KB, como este \texttt{httpd.exe}. \textbf{Fugrafa} es el
        nombre genérico que dan algunos antivirus a este tipo de binarios.
  \item \textbf{httpd.exe} imita al demonio del servidor web Apache (\emph{HTTP daemon}): un proceso con ese nombre
        haciendo tráfico HTTP pasa desapercibido.
\end{itemize}

\subsection{Conclusión}
Con el fichero borrado, ningún artefacto por sí solo bastaba: Prefetch y Amcache dan la lista de sospechosos y el
SHA1; los eventos y la \texttt{\$MFT} descartan señuelos y reconstruyen la secuencia; SRUM identifica sin ambigüedad
qué binario generó el tráfico; y la inteligencia de amenazas convierte el SHA1 en MD5 y confirma la familia.
"""

APENDICE_INICIO = r"""
\clearpage
\section{Scripts utilizados}\label{ap:scripts}
Código completo de los scripts de \texttt{\textasciitilde/ctf/repo/scripts}. Todos son de análisis: leen ficheros y
no ejecutan nunca el malware.

\begin{tabularx}{\linewidth}{@{}lX@{}}
\toprule
\texttt{amcache\_dump.py} & Vuelca \texttt{InventoryApplicationFile} de Amcache (SHA1, metadatos, ruta). \\
\texttt{evtx\_grep.py} & Busca eventos en un \texttt{.evtx} por texto e ID. \\
\texttt{evtx\_range.py} & Número de eventos y rango de fechas de cada log. \\
\texttt{go\_decrypt.py} & Descifra la cadena AES-CFB de \texttt{LetsGo} con las tres claves. \\
\texttt{go\_mips\_disasm.py} & Desensambla funciones Go MIPS anotando llamadas y cadenas. \\
\texttt{go\_pclntab.py} & Recupera nombres de funciones de \texttt{.gopclntab} en binarios Go \emph{stripped}. \\
\texttt{kraken\_emu.py} & Emula con Unicorn el descompresor de Crinkler y vuelca el código. \\
\texttt{kraken\_solve.py} & Resuelve los hashes de APIs y descifra la flag de The Kraken. \\
\texttt{mft\_record.py} & Parsea registros de la \texttt{\$MFT} que contienen un nombre. \\
\texttt{pe\_info.py} & Resumen de un ejecutable PE (cabecera, secciones, versión, imports). \\
\texttt{prefetch\_timeline.sh} & Línea de tiempo de ejecuciones a partir de Prefetch. \\
\texttt{rtf\_url.py} & Extrae la URL de los URL Moniker de un RTF. \\
\texttt{srum\_net.py} & Uso de red por aplicación desde SRUM. \\
\bottomrule
\end{tabularx}
"""

REFERENCIAS = r"""
\section{Referencias}
\begin{itemize}\small
  \item MITRE ATT\&CK: \url{https://attack.mitre.org/}
  \item CVE-2017-0199 (NVD): \url{https://nvd.nist.gov/vuln/detail/CVE-2017-0199}
  \item oletools / rtfobj: \url{https://github.com/decalage2/oletools}
  \item Crinkler: \url{https://github.com/runestubbe/Crinkler}
  \item Unicorn Engine: \url{https://www.unicorn-engine.org/}
  \item Capstone: \url{https://www.capstone-engine.org/}
  \item Lista de exports de kernel32 (Wine): \url{https://raw.githubusercontent.com/wine-mirror/wine/master/dlls/kernel32/kernel32.spec}
  \item libscca (Prefetch): \url{https://github.com/libyal/libscca}
  \item libesedb (SRUM): \url{https://github.com/libyal/libesedb}
  \item regipy: \url{https://github.com/mkorman90/regipy}
  \item SDelete (Sysinternals): \url{https://learn.microsoft.com/sysinternals/downloads/sdelete}
  \item VirusTotal API v3: \url{https://docs.virustotal.com/reference/file-info}
  \item go-figure: \url{https://github.com/common-nighthawk/go-figure}
  \item goInfo: \url{https://github.com/matishsiao/goInfo}
  \item Historia de Go: \url{https://go.dev/doc/faq}
\end{itemize}
"""

# Ficheros por reto: (nombre mostrado, ruta relativa a la réplica o 'manual:tam|md5|sha1|sha256', descripción)
FICHEROS = {
    "ccn": [
        ("evidencia.zip", "ctf/ccn-cry/evidencia.zip", "Zip cifrado (AES) del enunciado"),
        ("Secret.txt.CCN_CRY", "ctf/ccn-cry/Secret.txt.CCN_CRY", "Fichero cifrado por el ransomware"),
        ("incident-a1000032.pcapng", "ctf/ccn-cry/incident-a1000032.pcapng", "Captura de red del incidente"),
        ("wget.tar.gz", "ctf/ccn-cry/http_objs/wget.tar.gz", "Descargado por la víctima (extraído de la captura)"),
        ("ccn_cry", "ctf/ccn-cry/ccn_cry", "Ransomware, ELF x86-64 \\emph{stripped}"),
        ("Secret.txt", "ctf/ccn-cry/Secret.txt", "Fichero descifrado"),
    ],
    "kraken": [
        ("TheKraken.exe", "ctf/kraken/TheKraken.exe", "PE x86 comprimido con Crinkler"),
        ("unpacked.bin", "ctf/kraken/unpacked.bin", "Volcado 0x420000--0x430000 tras emular el descompresor"),
    ],
    "spear": [
        ("suspicious_.rar", "ctf/spear/suspicious_.rar", "RAR 2.9 cifrado del enunciado (partes 1 y 2)"),
        ("Nominas.rtf", "ctf/spear/Nominas.rtf", "Documento RTF malicioso, sin texto"),
    ],
    "go": [
        ("LetsGo.zip", "ctf/gogogo/LetsGo.zip", "Zip cifrado del enunciado"),
        ("LetsGo", "ctf/gogogo/LetsGo", "ELF 32 bits MIPS big-endian, Go 1.10.3, \\emph{stripped}"),
    ],
    "horcrux": [
        ("evidencias.7z", "ctf/horcrux/evidencias.7z", "Evidencias (\\texttt{evidencias\\_sorvologaunt.7z})"),
        ("$MFT", "ctf/horcrux/evid/$MFT", "Tabla maestra de ficheros NTFS"),
        ("Amcache.hve", "ctf/horcrux/evid/Windows/appcompat/Programs/Amcache.hve", "Inventario de ejecutables (SHA1)"),
        ("SRUDB.dat", "ctf/horcrux/evid/Windows/System32/sru/SRUDB.dat", "Base de datos SRUM"),
        ("ntuser.dat.LOG2", "ctf/horcrux/evid/Users/Gregor/ntuser.dat.LOG2", "Log de transacciones del registro de Gregor"),
        ("uninstall.exe", "ctf/horcrux/evid/Users/Gregor/AppData/Local/Microsoft/uninstall.exe", "Señuelo: PE Look renombrado"),
        ("httpd.exe (borrado)", "manual:15.360|dbe0e10775e35a58e8ff463ccbe5f7d8|409aea9461d03bff3e006d3e7e7c4790a0862170|(no disponible: fichero borrado)",
         "\\textbf{Binario malicioso} (Cobalt Strike). SHA1 de Amcache, MD5 de VirusTotal"),
        ("tor.exe (borrado)", "manual:231.936|3e6f1f16a4cbbf7c5a5c077ab197bb50|99e107ca419959385ca57241fb6ed3796eaacc9e|(no disponible: fichero borrado)",
         "Señuelo (\\texttt{tag\\_converter.exe})"),
        ("inject.exe (borrado)", "manual:226.304|(no está en VirusTotal)|de275b64985009d335ab85b38d26a3026739a68a|(no disponible: fichero borrado)",
         "Señuelo detectado por Defender"),
    ],
}
