#!/usr/bin/env python3
"""Crée le dépôt APT de protect.OS dans repo/ à partir des paquets de build/debs/.

Usage :
  python3 tools/make-repo.py --key <ID de la clé GPG>   dépôt signé (à publier)
  python3 tools/make-repo.py                            dépôt non signé (tests uniquement)

Dépendances : python3, dpkg-deb, gpg. Le dossier repo/ peut ensuite être servi
par n'importe quel serveur web (GitHub Pages, Netlify, un VPS…).
"""
import argparse
import email.utils
import gzip
import hashlib
import html
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def conf(key, default):
    try:
        with open(os.path.join(ROOT, "protectos.conf"), encoding="utf-8") as f:
            m = re.search(rf'^{key}="?([^"\n]*)"?', f.read(), re.M)
            return m.group(1) if m else default
    except OSError:
        return default


def digests(path):
    data = open(path, "rb").read()
    return len(data), hashlib.md5(data).hexdigest(), hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", default=os.environ.get("PROTECTOS_GPG_KEY", ""), help="ID de la clé GPG de signature")
    ap.add_argument("--debs", default=os.path.join(ROOT, "build", "debs"))
    ap.add_argument("--out", default=os.path.join(ROOT, "repo"))
    args = ap.parse_args()

    suite = conf("SUITE", "trixie")
    repo_url = os.environ.get("REPO_URL") or conf("REPO_URL", "")
    # Paquets protect.OS (build/debs) + vos propres programmes (dossier apps/, faits avec protectos-pack)
    debs = []
    for folder in (args.debs, os.path.join(ROOT, "apps")):
        if os.path.isdir(folder):
            debs += [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".deb")]
    if not debs:
        sys.exit("Aucun paquet dans build/debs : lancez d'abord ./tools/build-debs.sh")

    out = args.out
    shutil.rmtree(out, ignore_errors=True)
    bindir = os.path.join(out, "dists", suite, "main", "binary-amd64")
    os.makedirs(bindir)

    # Pool + index des paquets
    entries, listing = [], []
    for src in debs:
        deb = os.path.basename(src)
        name = deb.split("_")[0]
        rel = f"pool/main/{name[0]}/{name}/{deb}"
        dst = os.path.join(out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        control = subprocess.run(["dpkg-deb", "-f", src], check=True, capture_output=True, text=True).stdout.strip()
        size, md5, sha256 = digests(dst)
        entries.append(f"{control}\nFilename: {rel}\nSize: {size}\nMD5sum: {md5}\nSHA256: {sha256}")
        fields = dict(re.findall(r"^(Package|Version|Description): (.*)$", control, re.M))
        listing.append((fields.get("Package", name), fields.get("Version", ""), fields.get("Description", "")))

    packages = "\n\n".join(entries) + "\n"
    with open(os.path.join(bindir, "Packages"), "w", encoding="utf-8") as f:
        f.write(packages)
    with gzip.GzipFile(os.path.join(bindir, "Packages.gz"), "wb", mtime=0) as f:
        f.write(packages.encode("utf-8"))

    # Fichier Release
    dist = os.path.join(out, "dists", suite)
    md5_lines, sha_lines = [], []
    for fname in ("main/binary-amd64/Packages", "main/binary-amd64/Packages.gz"):
        size, md5, sha256 = digests(os.path.join(dist, fname))
        md5_lines.append(f" {md5} {size:>10} {fname}")
        sha_lines.append(f" {sha256} {size:>10} {fname}")
    release = "\n".join([
        "Origin: protect.OS",
        "Label: protect.OS",
        f"Suite: {suite}",
        f"Codename: {suite}",
        f"Date: {email.utils.formatdate(usegmt=True)}",
        "Architectures: amd64",
        "Components: main",
        "Description: Dépôt de mises à jour de protect.OS",
        "MD5Sum:", *md5_lines,
        "SHA256:", *sha_lines,
    ]) + "\n"
    release_path = os.path.join(dist, "Release")
    with open(release_path, "w", encoding="utf-8") as f:
        f.write(release)

    # Signature
    if args.key:
        gpg = ["gpg", "--batch", "--yes", "--local-user", args.key]
        subprocess.run(gpg + ["--clearsign", "-o", os.path.join(dist, "InRelease"), release_path], check=True)
        subprocess.run(gpg + ["--armor", "--detach-sign", "-o", os.path.join(dist, "Release.gpg"), release_path], check=True)
        with open(os.path.join(out, "protectos-archive.asc"), "w") as f:
            f.write(subprocess.run(["gpg", "--armor", "--export", args.key], check=True,
                                   capture_output=True, text=True).stdout)
        signed = True
    else:
        print("Attention : dépôt NON signé (aucune clé donnée). À n'utiliser que pour des tests.", file=sys.stderr)
        signed = False

    # Page du dépôt (le site de protect.OS, dans site/, sert de page d'accueil)
    rows = "".join(f"<tr><td>{html.escape(p)}</td><td>{html.escape(v)}</td><td>{html.escape(d)}</td></tr>"
                   for p, v, d in listing)
    url = html.escape(repo_url or "https://ADRESSE-DU-DEPOT")
    with open(os.path.join(out, "depot.html"), "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Dépôt protect.OS</title>
<style>body{{margin:0;font:16px/1.6 system-ui,sans-serif;background:#0a1a52;color:#eef2fb}}
main{{max-width:860px;margin:auto;padding:48px 20px}}h1{{color:#e8c15a;margin:0 0 8px;font-size:40px}}
pre{{background:#06103a;border:1px solid #8a6a0c;border-radius:10px;padding:14px;overflow-x:auto;color:#f3e3b0}}
table{{width:100%;border-collapse:collapse;margin-top:12px}}td,th{{text-align:left;padding:8px;border-bottom:1px solid #22357a}}
th{{color:#e8c15a}}</style></head><body><main>
<h1>Dépôt protect.OS</h1><p>Paquets et mises à jour de protect.OS (base Debian 13 « {html.escape(suite)} »).</p>
<h2>Ajouter ce dépôt à un système Debian 13</h2>
<pre>sudo curl -fsSL {url}/protectos-archive.asc | sudo gpg --dearmor -o /usr/share/keyrings/protectos-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/protectos-archive-keyring.gpg] {url} {html.escape(suite)} main" | sudo tee /etc/apt/sources.list.d/protectos.list
sudo apt update
sudo apt install protectos-desktop</pre>
<h2>Paquets disponibles</h2><table><tr><th>Paquet</th><th>Version</th><th>Description</th></tr>{rows}</table>
</main></body></html>
""")

    print(f"Dépôt {'signé' if signed else 'non signé'} créé dans {os.path.relpath(out, ROOT)}/ ({len(debs)} paquets, suite {suite})")


if __name__ == "__main__":
    main()
