#!/usr/bin/env bash
# Prepara Kali (como root) para todos los retos: herramientas del sistema y librerías de Python.
# Uso: bash /home/kali/Downloads/retosRecuperacion/instalar.sh
set -e
apt update
DEBIAN_FRONTEND=noninteractive apt install -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold 7zip unrar unzip tshark xxd openssl binutils \
  libscca-utils libesedb-utils python3-evtx python3-pip jq curl qemu-user
pip install --break-system-packages unicorn capstone pefile pyelftools pycryptodome oletools regipy
python3 -c 'import unicorn, capstone, pefile, elftools, Crypto, oletools, regipy, Evtx' && echo "Python OK"
for p in 7z unrar tshark rtfobj sccainfo esedbexport qemu-mips jq; do command -v "$p" >/dev/null && echo "OK  $p" || echo "FALTA  $p"; done
