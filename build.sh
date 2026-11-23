#!/bin/sh
# Construit l'image ISO de protect.OS.
# À lancer sur une machine Debian 13 (ou une VM), avec : sudo ./build.sh
set -e

if [ "$(id -u)" -ne 0 ]; then
	echo "Ce script doit être lancé avec sudo : sudo ./build.sh" >&2
	exit 1
fi

if ! command -v lb >/dev/null 2>&1; then
	echo "live-build n'est pas installé. Installez-le avec : sudo apt install live-build" >&2
	exit 1
fi

cd "$(dirname "$0")"

# Les scripts doivent être exécutables (ils peuvent perdre ce droit en passant par un zip)
chmod +x auto/* tools/*.sh tools/*.py config/hooks/normal/*.hook.chroot 2>/dev/null || true

echo "==> Application de ma-personnalisation.conf"
python3 tools/personnaliser.py

echo "==> Construction des paquets protect.OS"
./tools/build-debs.sh
mkdir -p config/packages.chroot
rm -f config/packages.chroot/protectos-*.deb
cp build/debs/*.deb config/packages.chroot/

echo "==> Nettoyage d'une éventuelle construction précédente"
lb clean

echo "==> Configuration"
lb config

echo "==> Construction de l'ISO (30 à 60 minutes selon la connexion et la machine)"
lb build

ISO=$(ls -1 protect-os*.iso 2>/dev/null | head -n 1)
if [ -n "$ISO" ]; then
	echo ""
	echo "Terminé : $ISO ($(du -h "$ISO" | cut -f1))"
	echo "Testez-la avec : qemu-system-x86_64 -enable-kvm -m 4096 -smp 2 -cdrom $ISO"
else
	echo "La construction n'a pas produit d'ISO : regardez la fin de build.log" >&2
	exit 1
fi
