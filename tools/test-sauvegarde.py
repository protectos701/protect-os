#!/usr/bin/python3
"""Test de la sauvegarde protect.OS : deux sauvegardes, les fichiers inchangés ne prennent pas de place en plus."""
import os
import sys
import tempfile

T = tempfile.mkdtemp()
for d in ("home/Documents", "home/Images", "cle"):
    os.makedirs(os.path.join(T, d))
open(os.path.join(T, "home/Documents/lettre.txt"), "w").write("lettre\n")
open(os.path.join(T, "home/Images/photo.jpg"), "wb").write(os.urandom(2_000_000))
os.environ.update(HOME=os.path.join(T, "home"), USER="anthony")
src = open(os.path.join(os.path.dirname(__file__), "..", "packages/protectos-protection/root/usr/bin/protectos-sauvegarde")).read()
ns = {"__name__": "test"}
exec(src.split('if "--auto" in sys.argv:')[0], ns)
ns["os"].path.ismount = lambda p: True
ns["dossier_xdg"] = lambda c: {"DOCUMENTS": f"{T}/home/Documents", "PICTURES": f"{T}/home/Images"}.get(c, "")
c = ns["lire_conf"]()
c.update(destination=f"{T}/cle", dossiers=["DOCUMENTS", "PICTURES"])
print("1re :", ns["sauvegarder"](c, journal=lambda m: None))
open(f"{T}/home/Documents/lettre.txt", "a").write("modifiée\n")
print("2e  :", ns["sauvegarder"](c, journal=lambda m: None))
r, s = ns["racine"](f"{T}/cle"), ns["sauvegardes"](f"{T}/cle")
a = os.stat(os.path.join(r, s[0], "Images", "photo.jpg"))
b = os.stat(os.path.join(r, s[1], "Images", "photo.jpg"))
lettre = open(os.path.join(r, s[1], "Documents", "lettre.txt")).read()
ok = len(s) == 2 and a.st_ino == b.st_ino and "modifiée" in lettre and "modifiée" not in open(os.path.join(r, s[0], "Documents", "lettre.txt")).read()
print("Sauvegardes :", s, "| photo partagée (même fichier sur le disque) :", a.st_ino == b.st_ino, "| lettre à jour :", "modifiée" in lettre)
print("✅ Sauvegarde : OK" if ok else "❌ Sauvegarde : ÉCHEC")
sys.exit(0 if ok else 1)
