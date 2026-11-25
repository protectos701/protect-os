#!/usr/bin/python3
"""Construit le catalogue des programmes Windows du Magasin protect.OS à partir du catalogue winget.

Pour chaque programme de tools/catalogue-liste.json : dernière version, lien de téléchargement officiel,
empreinte SHA-256, éditeur, licence. Résultat : apps/catalogue-windows.json (+ copie hors ligne dans le paquet).

  GITHUB_TOKEN=… python3 tools/catalogue-windows.py
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com/repos/microsoft/winget-pkgs/contents/"
TYPES_OK = ("inno", "nullsoft", "exe", "msi", "wix", "burn")


def obtenir(url, api=True):
    req = urllib.request.Request(url, headers={"User-Agent": "protect.OS-catalogue"})
    if api and os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"])
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def lister(chemin):
    return json.loads(obtenir(API + urllib.parse.quote(chemin)))


def cle_version(v):
    return [int(x) if x.isdigit() else -1 for x in re.split(r"[.\-+_]", v)]


def choisir_installateur(doc):
    """Meilleur installateur : 64 bits de préférence, type compatible, français ou anglais."""
    commun = {k: v for k, v in doc.items() if k != "Installers"}
    candidats = []
    for inst in doc.get("Installers", []):
        i = {**commun, **inst}
        type_ = (i.get("NestedInstallerType") if i.get("InstallerType") == "zip" else i.get("InstallerType", "")).lower()
        if type_ not in TYPES_OK or i.get("InstallerType", "").lower() == "zip":
            continue
        score = {"x64": 3, "x86": 2, "neutral": 1}.get(i.get("Architecture", ""), 0)
        score += {"fr-FR": 2, "en-US": 1}.get(i.get("InstallerLocale", ""), 1 if not i.get("InstallerLocale") else 0)
        score += 1 if i.get("Scope", "user") != "machine" else 0
        candidats.append((score, type_, i))
    if not candidats:
        return None
    _s, type_, i = max(candidats, key=lambda c: c[0])
    return {"type": type_, "url": i["InstallerUrl"], "sha256": i["InstallerSha256"].lower(),
            "architecture": i.get("Architecture", ""),
            "silencieux": (i.get("InstallerSwitches") or {}).get("Silent", "")}


def icone(ident, sites):
    """Icône officielle : celle déclarée par le site de l'éditeur (la plus grande), sinon son favicon.
    Enregistrée en PNG 96×96 dans apps/icones/ (et dans le paquet, pour l'usage hors ligne)."""
    import html.parser
    import io
    from PIL import Image

    class Liens(html.parser.HTMLParser):
        def __init__(self):
            super().__init__()
            self.icones = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "link" and "icon" in (a.get("rel") or "").lower() and a.get("href"):
                taille = max([int(x) for x in re.findall(r"(\d+)x\d+", a.get("sizes") or "")] or [0])
                bonus = 1000 if "apple-touch" in a["rel"].lower() else 0
                self.icones.append((taille + bonus, a["href"]))

    candidats = []
    for site in [s for s in sites if s]:
        try:
            p = Liens()
            p.feed(obtenir(site, api=False).decode("utf-8", "replace")[:400000])
            candidats += [urllib.parse.urljoin(site, h) for _t, h in sorted(p.icones, reverse=True)]
        except Exception:
            pass
        racine = "{0.scheme}://{0.netloc}".format(urllib.parse.urlsplit(site))
        candidats += [racine + "/apple-touch-icon.png", racine + "/favicon.ico"]
    for url in candidats:
        if url.lower().endswith(".svg"):
            continue
        try:
            im = Image.open(io.BytesIO(obtenir(url, api=False)))
            if im.format == "ICO":  # un .ico contient plusieurs tailles : on prend la plus grande
                im = im.ico.getimage(max(im.ico.sizes()))
            im = im.convert("RGBA")
            if im.width < 16:
                continue
            echelle = 96 / max(im.width, im.height)   # agrandit aussi les petites icônes (favicon 16 ou 32 px)
            im = im.resize((max(1, round(im.width * echelle)), max(1, round(im.height * echelle))),
                           Image.NEAREST if im.width <= 32 else Image.LANCZOS)
            fond = Image.new("RGBA", (96, 96), (0, 0, 0, 0))
            fond.paste(im, ((96 - im.width) // 2, (96 - im.height) // 2), im)
            nom = re.sub(r"[^A-Za-z0-9.+-]", "_", ident) + ".png"
            for dossier in ("apps/icones", "packages/protectos-programmes/root/usr/share/protectos/icones-windows"):
                os.makedirs(os.path.join(ROOT, dossier), exist_ok=True)
                fond.save(os.path.join(ROOT, dossier, nom))
            return nom
        except Exception:
            continue
    return ""


def programme(entree):
    ident = entree["id"]
    chemin = "manifests/" + ident[0].lower() + "/" + "/".join(ident.split("."))
    versions = [e["name"] for e in lister(chemin) if e["type"] == "dir" and re.match(r"^\d", e["name"])]
    if not versions:
        raise ValueError("aucune version")
    version = max(versions, key=cle_version)
    fichiers = {e["name"]: e["download_url"] for e in lister(chemin + "/" + version)}
    inst = yaml.safe_load(obtenir(fichiers[f"{ident}.installer.yaml"], api=False))
    racine = yaml.safe_load(obtenir(fichiers[f"{ident}.yaml"], api=False)) if f"{ident}.yaml" in fichiers else {}
    langue = racine.get("DefaultLocale", "en-US")
    loc = {}
    for nom in (f"{ident}.locale.fr-FR.yaml", f"{ident}.locale.{langue}.yaml"):
        if nom in fichiers:
            loc = {**yaml.safe_load(obtenir(fichiers[nom], api=False)), **loc}
    choix = choisir_installateur(inst)
    if not choix:
        raise ValueError("aucun installateur compatible (seulement msix/zip ?)")
    ic = icone(ident, [loc.get("PackageUrl"), loc.get("PublisherUrl")])
    return {"id": ident, "nom": loc.get("PackageName", ident.split(".")[-1]), "editeur": loc.get("Publisher", ""),
            "icone": ic,
            "version": str(version), "categorie": entree["categorie"],
            "description": entree.get("description") or loc.get("ShortDescription", ""),
            "licence": loc.get("License", ""), "site": loc.get("PackageUrl") or loc.get("PublisherUrl", ""),
            **choix}


def main():
    liste = json.load(open(os.path.join(ROOT, "tools", "catalogue-liste.json"), encoding="utf-8"))["programmes"]
    sortie, erreurs = [], 0
    for e in liste:
        try:
            p = programme(e)
            sortie.append(p)
            print(f"  ✓ {p['nom']} {p['version']} ({p['type']}, {p['architecture']}) icône : {p['icone'] or 'aucune'}")
        except Exception as ex:
            erreurs += 1
            print(f"  ✗ {e['id']} : {ex}")
    if not sortie:
        print("Catalogue vide : rien n'est écrit")
        return 1
    donnees = {"version": 1, "programmes": sorted(sortie, key=lambda p: (p["categorie"], p["nom"].lower()))}
    texte = json.dumps(donnees, ensure_ascii=False, indent=1) + "\n"
    for chemin in ("apps/catalogue-windows.json",
                   "packages/protectos-programmes/root/usr/share/protectos/catalogue-windows.json"):
        os.makedirs(os.path.join(ROOT, os.path.dirname(chemin)), exist_ok=True)
        with open(os.path.join(ROOT, chemin), "w", encoding="utf-8") as f:
            f.write(texte)
    print(f"{len(sortie)} programmes dans le catalogue, {erreurs} ignorés")
    return 0


if __name__ == "__main__":
    sys.exit(main())
