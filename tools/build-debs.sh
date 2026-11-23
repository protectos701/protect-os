#!/bin/sh
# Construit les paquets .deb de protect.OS dans build/debs/
# Usage : ./tools/build-debs.sh       (aucun droit administrateur nécessaire)
set -e
cd "$(dirname "$0")/.."

# Une adresse de dépôt passée par l'environnement (GitHub Actions) l'emporte sur protectos.conf
ENV_REPO_URL="${REPO_URL:-}"
. ./protectos.conf
[ -n "$ENV_REPO_URL" ] && REPO_URL="$ENV_REPO_URL"
VERSION=$(tr -d ' \n' < VERSION)

OUT=build/debs
STAGE=build/pkg
rm -rf "$OUT" "$STAGE"
mkdir -p "$OUT" "$STAGE"

for dir in packages/*/; do
	name=$(basename "$dir")

	if [ "$name" = "protectos-archive-keyring" ] && [ ! -f keys/protectos-archive.asc ]; then
		echo "-- $name ignoré : pas de clé publique dans keys/protectos-archive.asc (voir README)"
		continue
	fi

	st="$STAGE/$name"
	mkdir -p "$st/DEBIAN"
	[ -d "$dir/root" ] && cp -R "$dir/root/." "$st/"
	cp "$dir"/DEBIAN/* "$st/DEBIAN/"
	find "$st" -name __pycache__ -type d -prune -exec rm -rf {} +

	# Clé et adresse du dépôt
	if [ "$name" = "protectos-archive-keyring" ]; then
		case "$REPO_URL" in *VOTRE-NOM*)
			echo "!! Attention : REPO_URL n'est pas réglé dans protectos.conf ($REPO_URL)" >&2 ;;
		esac
		mkdir -p "$st/usr/share/keyrings" "$st/etc/apt/sources.list.d"
		gpg --dearmor < keys/protectos-archive.asc > "$st/usr/share/keyrings/protectos-archive-keyring.gpg"
		sed -e "s|@REPO_URL@|$REPO_URL|" -e "s|@SUITE@|$SUITE|" \
			"$dir/protectos.sources.in" > "$st/etc/apt/sources.list.d/protectos.sources"
	fi

	# Variables dans les fichiers de contrôle et l'identité du système
	for f in "$st/DEBIAN/control" "$st/usr/lib/os-release"; do
		[ -f "$f" ] && sed -i -e "s|@VERSION@|$VERSION|g" -e "s|@MAINTAINER@|$MAINTAINER|g" "$f"
	done

	# Droits : fichiers 644, dossiers et exécutables 755
	find "$st" -type d -exec chmod 0755 {} +
	find "$st" -type f -exec chmod 0644 {} +
	for s in preinst postinst prerm postrm; do
		[ -f "$st/DEBIAN/$s" ] && chmod 0755 "$st/DEBIAN/$s"
	done
	[ -d "$st/usr/bin" ] && chmod 0755 "$st"/usr/bin/*
	# Les scripts (fichiers qui commencent par « #! ») sont exécutables
	find "$st" -type f ! -path "$st/DEBIAN/*" | while read -r f; do
		if [ "$(head -c 2 "$f")" = "#!" ]; then chmod 0755 "$f"; fi
	done

	# Les fichiers de /etc sont des fichiers de configuration (gardés si l'utilisateur les modifie)
	if [ -d "$st/etc" ]; then
		(cd "$st" && find etc -type f | sort | sed 's|^|/|') > "$st/DEBIAN/conffiles"
	fi

	# Sommes de contrôle et taille installée
	(cd "$st" && find . -path ./DEBIAN -prune -o -type f -print0 | sort -z | xargs -0r md5sum | sed 's|  \./|  |') > "$st/DEBIAN/md5sums"
	size=$(du -sk --exclude=DEBIAN "$st" | cut -f1)
	echo "Installed-Size: $size" >> "$st/DEBIAN/control"

	dpkg-deb --root-owner-group -Zxz --build "$st" "$OUT/${name}_${VERSION}_all.deb" >/dev/null
	echo "OK $OUT/${name}_${VERSION}_all.deb"
done
