# Matrioska — estado

Cadena resuelta (todo estatico/emulado):
1. matrioska.zip (pass: infected) -> T.exe
2. T.exe: empaquetado MPRESS -> desempaquetado por emulacion (Unicorn) -> candado Delphi
3. El candado ensambla a.exe por trozos (combinacion de botones)
4. a.exe: keylogger+antiVM; frase capturada = "atari v01032"; clave AES derivada = w10123shark01
5. PowerShell (XOR 0x68 + Base64/Deflate + SecureString AES) 
6. x.xsl (lista numerica) -> JScript DotNetToJScript -> ensamblado .NET
7. .NET: AES-256 (clave w10123shark01, sal Zangief) -> volumen TrueCrypt de 512000 bytes
8. Volumen TrueCrypt (pass: ccn123, hallada con hashcat -m 6211) -> humm.png (emoji, SENUELO)
9. Volumen OCULTO de TrueCrypt (pass: #1#1#1#1, hashcat) -> fichero "Flag"
10. "Flag" = openssl enc (Salted__) 48 bytes -> PENDIENTE: contrasena desconocida

artefactos/capa8.bin  = volumen TrueCrypt (exterior+oculto)
artefactos/flag.txt   = el fichero "Flag" cifrado con openssl
artefactos/humm.png   = el senuelo

Pendiente: contrasena de la capa openssl. Descartado por rockyou: AES(todos, md5/sha256/sha1),
Blowfish-md5, 3DES-md5, DES/CAST/RC2. Probablemente una palabra especifica del reto.
