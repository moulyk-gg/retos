# Informe en LaTeX

- `informe_retos.tex`: fuente del informe.
- `informe_retos.pdf`: versión compilada.
- `capturas/`: carpeta para tus capturas de pantalla. `capturas/LEEME.txt` lista el nombre exacto de cada una.

## Compilar

En Kali:

```bash
sudo apt install -y texlive-latex-recommended texlive-latex-extra texlive-lang-spanish texlive-fonts-recommended
```

```bash
pdflatex informe_retos.tex && pdflatex informe_retos.tex
```

La segunda pasada genera el índice.

En Overleaf: sube `informe_retos.tex` y la carpeta `capturas/`. En *Menu → Compiler* elige **pdfLaTeX**.

## Capturas

Cada paso tiene una caja naranja "Captura pendiente" con un nombre, por ejemplo `capturas/ccn-10.png`.

1. Ejecuta el comando del paso en Kali.
2. Haz la captura de la terminal (en Kali, `Impr Pant`, o `Shift+Impr Pant` para elegir una zona).
3. Guárdala como PNG en `capturas/` con ese nombre exacto.
4. Vuelve a compilar: la imagen sustituye a la caja naranja sola, con su pie de figura.

## Copiar comandos desde el PDF

Los comandos largos están partidos con `\` al final de la línea. Es la continuación estándar de bash y zsh: puedes copiar y pegar el bloque entero, se ejecuta como un solo comando.
