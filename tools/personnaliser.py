#!/usr/bin/env python3
"""Applique ma-personnalisation.conf à tout le projet.

Nom, slogan, couleurs, logo, fond d'écran, logiciels, applications épinglées, langue,
clavier et fuseau. L'outil est réversible : il retient ce qu'il a déjà appliqué
(tools/.personnalisation-appliquee.json), si bien qu'on peut changer d'avis autant de
fois qu'on veut, et remettre les valeurs « origine » ramène exactement le projet d'origine.

Usage :  python3 tools/personnaliser.py            (lancé aussi automatiquement par GitHub)
         python3 tools/personnaliser.py --sans-images   (sans régénérer logos et fonds)
Dépendances pour les images : python3-pil, librsvg2-bin.
"""
import colorsys
import configparser
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(ROOT, "ma-personnalisation.conf")
STATE = os.path.join(ROOT, "tools", ".personnalisation-appliquee.json")

ORIGINE = {
    "nom": "protect.OS",
    "slogan": "Le système qui vous protège",
    "principale": "#0a1a52",
    "accent": "#d4a72c",
    "langue": "fr_FR.UTF-8",
    "clavier": "fr",
    "variante": "",
    "fuseau": "Europe/Paris",
    "epingles": "explorateur, firefox, terminal, writer, discover, parametres",
}

# Fichiers concernés par le nom et les couleurs
SCOPE_DIRS = ["packages", "site", "config", "auto", ".github"]
SCOPE_FILES = ["README.md", "protectos.conf", "tools/render-images.py", "tools/make-repo.py",
               "tools/protectos-logo.svg", "tools/test-iso.py"]
SKIP_EXT = (".png", ".jpg", ".jpeg", ".gpg", ".deb", ".iso", ".ico")

EPINGLES = {
    "explorateur": "org.kde.dolphin.desktop", "fichiers": "org.kde.dolphin.desktop",
    "firefox": "firefox-esr.desktop", "navigateur": "firefox-esr.desktop",
    "terminal": "org.kde.konsole.desktop", "writer": "libreoffice-writer.desktop",
    "calc": "libreoffice-calc.desktop", "impress": "libreoffice-impress.desktop",
    "discover": "org.kde.discover.desktop", "parametres": "systemsettings.desktop",
    "paramètres": "systemsettings.desktop", "protection": "protectos-protection.desktop",
    "programmes": "protectos-programmes.desktop", "vlc": "vlc.desktop", "gimp": "gimp.desktop",
    "thunderbird": "thunderbird.desktop", "steam": "steam.desktop", "kate": "org.kde.kate.desktop",
    "calculatrice": "org.kde.kcalc.desktop", "photos": "org.kde.gwenview.desktop",
    "pdf": "org.kde.okular.desktop",
}

NOMS_APPS = {  # clé de [noms_applications] → fichier .desktop du logiciel
    "explorateur": "org.kde.dolphin.desktop", "terminal": "org.kde.konsole.desktop",
    "capture": "org.kde.spectacle.desktop", "gestionnaire_taches": "org.kde.plasma-systemmonitor.desktop",
    "pdf": "org.kde.okular.desktop", "photos": "org.kde.gwenview.desktop", "editeur": "org.kde.kate.desktop",
    "calculatrice": "org.kde.kcalc.desktop", "magasin": "org.kde.discover.desktop",
    "parametres": "systemsettings.desktop", "archives": "org.kde.ark.desktop",
    "disques": "org.kde.partitionmanager.desktop",
}
NOMS_ORIGINE = {
    "explorateur": "Explorateur de fichiers", "terminal": "Terminal", "capture": "Capture d'écran",
    "gestionnaire_taches": "Gestionnaire des tâches", "pdf": "Lecteur PDF", "photos": "Photos",
    "editeur": "Bloc-notes", "calculatrice": "Calculatrice", "magasin": "Magasin d'applications",
    "parametres": "Paramètres", "archives": "Archives", "disques": "Gestionnaire de disques",
}
RACCOURCIS = {  # clé de [raccourcis] → (application, action KDE)
    "explorateur": ("org.kde.dolphin.desktop", "_launch"),
    "gestionnaire_taches": ("org.kde.plasma-systemmonitor.desktop", "_launch"),
    "parametres": ("systemsettings.desktop", "_launch"),
    "terminal": ("org.kde.konsole.desktop", "_launch"),
    "capture_zone": ("org.kde.spectacle.desktop", "RectangularRegionScreenShot"),
    "executer": ("org.kde.krunner.desktop", "_launch"),
    "centre_protection": ("protectos-protection.desktop", "_launch"),
}
RACCOURCIS_ORIGINE = {
    "explorateur": "Meta+E", "gestionnaire_taches": "Ctrl+Shift+Esc", "parametres": "Meta+I",
    "terminal": "Ctrl+Alt+T", "capture_zone": "Meta+Shift+S", "executer": "Meta+R",
    "centre_protection": "Meta+Shift+P",
}
OPTIONS_ORIGINE = {"theme": "sombre", "barre": "centree", "position": "bas", "verre": "oui", "assistant": "oui",
                   "bloqueur_pubs": "oui", "firefox_confidentiel": "oui"}
CHOIX = {"theme": ("sombre", "clair"), "barre": ("centree", "gauche"), "position": ("bas", "haut"),
         "verre": ("oui", "non"), "assistant": ("oui", "non"), "bloqueur_pubs": ("oui", "non"),
         "firefox_confidentiel": ("oui", "non")}
THEME = os.path.join(ROOT, "packages", "protectos-theme", "root")

LANGUES = {  # code langue → paquets de langue de l'image ISO
    "fr": ["task-french", "hunspell-fr", "manpages-fr", "firefox-esr-l10n-fr", "libreoffice-l10n-fr"],
    "en": ["task-english", "hunspell-en-us", "firefox-esr-l10n-en-gb"],
    "de": ["task-german", "hunspell-de-de", "manpages-de", "firefox-esr-l10n-de", "libreoffice-l10n-de"],
    "es": ["task-spanish", "hunspell-es", "manpages-es", "firefox-esr-l10n-es-es", "libreoffice-l10n-es"],
    "it": ["task-italian", "hunspell-it", "manpages-it", "firefox-esr-l10n-it", "libreoffice-l10n-it"],
    "pt": ["task-portuguese", "hunspell-pt-pt", "manpages-pt", "firefox-esr-l10n-pt-pt", "libreoffice-l10n-pt"],
    "nl": ["task-dutch", "hunspell-nl", "manpages-nl", "firefox-esr-l10n-nl", "libreoffice-l10n-nl"],
}


def erreur(msg):
    print(f"Erreur dans ma-personnalisation.conf : {msg}", file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------------ lecture
def lire_conf():
    cp = configparser.ConfigParser(interpolation=None, inline_comment_prefixes=None)
    cp.optionxform = str
    try:
        cp.read(CONF, encoding="utf-8")
    except configparser.Error as e:
        erreur(str(e))
    g = lambda s, k, d="": cp.get(s, k, fallback=d).strip()  # noqa: E731
    c = {
        "nom": g("identite", "nom", ORIGINE["nom"]) or ORIGINE["nom"],
        "slogan": g("identite", "slogan", ORIGINE["slogan"]),
        "principale": g("couleurs", "principale", ORIGINE["principale"]).lower(),
        "accent": g("couleurs", "accent", ORIGINE["accent"]).lower(),
        "logo": g("logo", "fichier"),
        "fond": g("fond_ecran", "fichier"),
        "ajouter": [x for x in re.split(r"[,;\s]+", g("logiciels", "ajouter")) if x],
        "retirer": [x for x in re.split(r"[,;\s]+", g("logiciels", "retirer")) if x],
        "epingles": g("logiciels", "epingles", ORIGINE["epingles"]) or ORIGINE["epingles"],
        "langue": g("langue", "langue", ORIGINE["langue"]) or ORIGINE["langue"],
        "clavier": g("langue", "clavier", ORIGINE["clavier"]) or ORIGINE["clavier"],
        "variante": g("langue", "variante"),
        "fuseau": g("langue", "fuseau", ORIGINE["fuseau"]) or ORIGINE["fuseau"],
    }
    opts = {}
    for k, d in OPTIONS_ORIGINE.items():
        section = "protection" if k in ("bloqueur_pubs", "firefox_confidentiel") else "bureau"
        v = (g(section, k, d) or d).lower().replace("é", "e")
        if v not in CHOIX[k]:
            erreur(f"« {k} » doit valoir {' ou '.join(CHOIX[k])}, pas « {v} »")
        opts[k] = v
    c["options"] = opts
    c["noms"] = {k: g("noms_applications", k, NOMS_ORIGINE[k]) if cp.has_option("noms_applications", k)
                 else NOMS_ORIGINE[k] for k in NOMS_APPS}
    c["raccourcis"] = {k: g("raccourcis", k, RACCOURCIS_ORIGINE[k]) if cp.has_option("raccourcis", k)
                       else RACCOURCIS_ORIGINE[k] for k in RACCOURCIS}
    for k, v in list(c["noms"].items()) + list(c["raccourcis"].items()):
        if any(ch in v for ch in "\"$`\\"):
            erreur(f"« {k} » ne doit pas contenir \" $ ` ou \\")
    for k in ("principale", "accent"):
        if not re.fullmatch(r"#[0-9a-f]{6}", c[k]):
            erreur(f"la couleur « {k} » doit s'écrire #RRVVBB (par exemple #0a1a52), pas « {c[k]} »")
    for k in ("logo", "fond"):
        if c[k] and not os.path.isfile(os.path.join(ROOT, c[k])):
            erreur(f"le fichier « {c[k]} » est introuvable (déposez-le dans le dossier personnalisation)")
    if not re.fullmatch(r"[a-z]{2}_[A-Z]{2}\.UTF-8", c["langue"]):
        erreur(f"la langue « {c['langue']} » doit ressembler à fr_FR.UTF-8")
    for pkg in c["ajouter"] + c["retirer"]:
        if not re.fullmatch(r"[a-z0-9][a-z0-9.+-]+", pkg):
            erreur(f"« {pkg} » n'est pas un nom de paquet valide")
    if any(ch in c["nom"] for ch in "<>\"\\$`"):
        erreur("le nom ne doit pas contenir < > \" \\ $ ou `")
    return c


def lire_etat():
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"nom": ORIGINE["nom"], "slogan": ORIGINE["slogan"], "couleurs": {}}


def fichiers_texte():
    out = []
    for d in SCOPE_DIRS:
        for dp, _dn, fn in os.walk(os.path.join(ROOT, d)):
            for f in fn:
                if not f.lower().endswith(SKIP_EXT):
                    out.append(os.path.join(dp, f))
    out += [os.path.join(ROOT, f) for f in SCOPE_FILES if os.path.isfile(os.path.join(ROOT, f))]
    res = []
    for p in out:
        try:
            with open(p, "rb") as fh:
                b = fh.read()
            if b"\0" not in b:
                b.decode("utf-8")
                res.append(p)
        except (OSError, UnicodeDecodeError):
            pass
    return res


# ------------------------------------------------------------------ couleurs
def hls(rgb):
    return colorsys.rgb_to_hls(*(x / 255 for x in rgb))


def from_hls(h, l, s):
    return tuple(max(0, min(255, round(x * 255))) for x in colorsys.hls_to_rgb(h % 1.0, l, s))


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def famille(rgb, base):
    """Vrai si la couleur appartient à la famille de teintes de « base » (or ou bleu nuit)."""
    h, l, s = hls(rgb)
    bh, _bl, _bs = hls(hex_rgb(base))
    d = min(abs(h - bh), 1 - abs(h - bh)) * 360
    return s > 0.22 and d <= 24 and 0.03 < l < 0.97


def transformer(rgb, ancienne, nouvelle):
    """Décale la teinte et la saturation comme de l'ancienne base vers la nouvelle."""
    if rgb == hex_rgb(ancienne):
        return hex_rgb(nouvelle)  # la couleur de base devient exactement la vôtre
    h, l, s = hls(rgb)
    oh, ol, os_ = hls(hex_rgb(ancienne))
    nh, nl, ns = hls(hex_rgb(nouvelle))
    ratio = (ns / os_) if os_ > 0.01 else 1
    # La luminosité suit celle de votre couleur, d'autant moins que la nuance est éloignée de la base
    poids = max(0.0, 1 - abs(l - ol) / max(ol, 1 - ol))
    return from_hls(h + (nh - oh), min(0.97, max(0.03, l + (nl - ol) * poids)), min(1.0, s * ratio))


RX_HEX = re.compile(r"#([0-9a-fA-F]{6})\b")
RX_RGB_CSS = re.compile(r"(rgba?\(\s*)(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})")
RX_RGB_INI = re.compile(r"^([A-Za-z]+=)(\d{1,3}),(\d{1,3}),(\d{1,3})$", re.M)
RX_FLOAT = re.compile(r"(?<![\d.])(0\.\d{2,3}), (0\.\d{2,3}), (0\.\d{2,3})(?![\d])")


def recolorer(texte, chemin, bases, table):
    """Remplace les couleurs des deux familles. « table » garde nouvelle → origine pour revenir en arrière."""
    def nouveau(rgb):
        for anc, nouv in bases:
            if anc != nouv and famille(rgb, anc):
                return transformer(rgb, anc, nouv)
        return rgb

    def sub_hex(m):
        rgb = hex_rgb("#" + m.group(1))
        n = nouveau(rgb)
        if n == rgb:
            return m.group(0)
        out = "#%02x%02x%02x" % n
        if m.group(1).isupper():
            out = out.upper()
        table[out.lower()] = "#" + m.group(1).lower()
        return out

    def sub_triple(prefix, r, g, b, sep):
        rgb = (int(r), int(g), int(b))
        if max(rgb) > 255:
            return None
        n = nouveau(rgb)
        if n == rgb:
            return None
        out = sep.join(str(x) for x in n)
        table[out] = sep.join(str(x) for x in rgb)
        return prefix + out

    texte = RX_HEX.sub(sub_hex, texte)
    texte = RX_RGB_CSS.sub(lambda m: sub_triple(m.group(1), m.group(2), m.group(3), m.group(4), ",") or m.group(0),
                           texte)
    if chemin.endswith((".colors", ".colorscheme")) or os.path.basename(chemin) in ("kdeglobals",):
        texte = RX_RGB_INI.sub(lambda m: sub_triple(m.group(1), m.group(2), m.group(3), m.group(4), ",") or m.group(0),
                               texte)
    if chemin.endswith(".script"):
        def sub_float(m):
            rgb = tuple(round(float(x) * 255) for x in m.groups())
            n = nouveau(rgb)
            if n == rgb:
                return m.group(0)
            out = ", ".join(f"{x / 255:.3f}" for x in n)
            table[out] = m.group(0)
            return out
        texte = RX_FLOAT.sub(sub_float, texte)
    return texte


def annuler_couleurs(texte, table):
    """Remet les couleurs d'origine notées lors du passage précédent."""
    if not table:
        return texte
    def rep_hex(m):
        k = "#" + m.group(1).lower()
        if k in table:
            orig = table[k]
            return orig.upper() if m.group(1).isupper() else orig
        return m.group(0)
    texte = RX_HEX.sub(rep_hex, texte)
    for new, old in table.items():
        if not new.startswith("#"):
            texte = re.sub(r"(?<![\d.])" + re.escape(new) + r"(?![\d])", old, texte)
    return texte


# ------------------------------------------------------------------ étapes
def appliquer_textes(c, etat):
    anc_nom, anc_slogan = etat.get("nom", ORIGINE["nom"]), etat.get("slogan", ORIGINE["slogan"])
    table_anc = etat.get("couleurs", {})
    table = {}
    bases = [(ORIGINE["accent"], c["accent"]), (ORIGINE["principale"], c["principale"])]
    n = 0
    for p in fichiers_texte():
        s = open(p, encoding="utf-8").read()
        o = s
        s = annuler_couleurs(s, table_anc)
        if anc_nom != c["nom"]:
            s = s.replace(anc_nom, c["nom"])
        if anc_slogan and c["slogan"] and anc_slogan != c["slogan"]:
            s = s.replace(anc_slogan, c["slogan"])
        if bases[0][0] != bases[0][1] or bases[1][0] != bases[1][1]:
            s = recolorer(s, p, bases, table)
        if s != o:
            with open(p, "w", encoding="utf-8") as f:
                f.write(s)
            n += 1
    return n, table


def appliquer_logiciels(c):
    base_path = os.path.join(ROOT, "packages", "protectos-desktop", "recommends.base")
    base = [ln.strip() for ln in open(base_path, encoding="utf-8") if ln.strip() and not ln.startswith("#")]
    absents = [x for x in c["retirer"] if x not in base]
    liste = [x for x in base if x not in c["retirer"]] + [x for x in c["ajouter"] if x not in base]
    modele = open(os.path.join(ROOT, "packages", "protectos-desktop", "control.modele"), encoding="utf-8").read()
    with open(os.path.join(ROOT, "packages", "protectos-desktop", "DEBIAN", "control"), "w", encoding="utf-8") as f:
        f.write(modele.replace("@RECOMMENDS@", ", ".join(liste)))
    if absents:
        print("  Remarque : ces logiciels à retirer ne faisaient pas partie de la liste d'origine : " + ", ".join(absents))

    ids = []
    for nom in [x.strip() for x in c["epingles"].split(",") if x.strip()]:
        key = nom.lower()
        ids.append(EPINGLES.get(key) or (nom if nom.endswith(".desktop") else nom + ".desktop"))
    js_path = os.path.join(ROOT, "packages", "protectos-theme", "root", "usr", "share", "plasma", "look-and-feel",
                           "org.protectos.desktop", "contents", "layouts", "org.kde.plasma.desktop-layout.js")
    js = open(js_path, encoding="utf-8").read()
    bloc = 'tasks.writeConfig("launchers", [\n' + ",\n".join(f'    "applications:{i}"' for i in ids) + "\n]);"
    js = re.sub(r'tasks\.writeConfig\("launchers", \[.*?\]\);', lambda _m: bloc, js, flags=re.S)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    return len(liste), ids


def appliquer_langue(c):
    lang = c["langue"][:2]
    paquets = LANGUES.get(lang, [])
    if not paquets:
        print(f"  Remarque : pas de paquets de langue prévus pour « {lang} » : seuls les réglages sont appliqués.")
    with open(os.path.join(ROOT, "config", "package-lists", "protectos-langue.list.chroot"), "w",
              encoding="utf-8") as f:
        f.write("# Créé par tools/personnaliser.py à partir de ma-personnalisation.conf — ne pas modifier.\n")
        f.write("\n".join(paquets) + "\n")
    p = os.path.join(ROOT, "auto", "config")
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"locales=\S+", f"locales={c['langue']}", s)
    s = re.sub(r"keyboard-layouts=\S+", f"keyboard-layouts={c['clavier']}", s)
    s = re.sub(r" keyboard-variants=\S+", "", s)
    if c["variante"]:
        s = s.replace(f"keyboard-layouts={c['clavier']}", f"keyboard-layouts={c['clavier']} keyboard-variants={c['variante']}")
    s = re.sub(r"timezone=[^\s\"]+", f"timezone={c['fuseau']}", s)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)
    if lang != "fr":
        print("  Remarque : les programmes propres au système (Centre de protection, Installateur…) restent en français.")


def _remplacer(path, motif, remplacement, flags=0):
    s = open(path, encoding="utf-8").read()
    n = re.sub(motif, remplacement, s, flags=flags)
    if n != s:
        with open(path, "w", encoding="utf-8") as f:
            f.write(n)


def appliquer_bureau(c):
    o = c["options"]
    clair = o["theme"] == "clair"
    for p in (os.path.join(THEME, "etc", "xdg", "kdeglobals"),
              os.path.join(THEME, "usr", "share", "plasma", "look-and-feel", "org.protectos.desktop", "contents", "defaults")):
        _remplacer(p, r"ColorScheme=ProtectBleuOr(Clair)?\b", "ColorScheme=ProtectBleuOr" + ("Clair" if clair else ""))
        _remplacer(p, r"(\[Icons\]\nTheme=)ProtectOS(-Clair)?\b", r"\g<1>ProtectOS" + ("-Clair" if clair else ""))
    js = os.path.join(THEME, "usr", "share", "plasma", "look-and-feel", "org.protectos.desktop", "contents",
                      "layouts", "org.kde.plasma.desktop-layout.js")
    spacer = 'panel.addWidget("org.kde.plasma.panelspacer"); // barre-centree'
    _remplacer(js, r"^(// )?" + re.escape(spacer), ("" if o["barre"] == "centree" else "// ") + spacer, re.M)
    _remplacer(js, r'panel\.location = "(bottom|top)";', f'panel.location = "{"top" if o["position"] == "haut" else "bottom"}";')
    verre = o["verre"] == "oui"
    _remplacer(os.path.join(THEME, "etc", "xdg", "kwinrc"), r"translucencyEnabled=(true|false)",
               f"translucencyEnabled={'true' if verre else 'false'}")
    _remplacer(os.path.join(THEME, "etc", "xdg", "breezerc"), r"MenuOpacity=\d+", f"MenuOpacity={82 if verre else 100}")
    ks = os.path.join(THEME, "usr", "share", "konsole", "ProtectOS.colorscheme")
    _remplacer(ks, r"Opacity=[\d.]+", f"Opacity={'0.82' if verre else '1'}")
    _remplacer(ks, r"Blur=(true|false)", f"Blur={'true' if verre else 'false'}")
    auto = os.path.join(ROOT, "packages", "protectos-bienvenue", "root", "etc", "xdg", "autostart",
                        "protectos-bienvenue.desktop")
    _remplacer(auto, r"\nHidden=true", "")
    if o["assistant"] == "non":
        with open(auto, "a", encoding="utf-8") as f:
            f.write("Hidden=true\n")


def appliquer_noms_raccourcis(c):
    # Noms des applications : lus par protectos-identite sur le système (et réappliqués après chaque mise à jour)
    conf = os.path.join(ROOT, "packages", "protectos-base", "root", "etc", "protectos", "noms-applications.conf")
    os.makedirs(os.path.dirname(conf), exist_ok=True)
    lignes = ["# Créé par tools/personnaliser.py à partir de ma-personnalisation.conf — ne pas modifier ici.",
              "# Nom affiché de chaque application (raccourci = nom)."]
    for k, desktop in NOMS_APPS.items():
        if c["noms"][k]:
            lignes.append(f"{desktop}={c['noms'][k]}")
    with open(conf, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")
    ancien = os.path.join(ROOT, "config", "hooks", "normal", "0700-noms-applications.hook.chroot")
    if os.path.exists(ancien):
        os.remove(ancien)

    # Raccourcis clavier : réglages par défaut de KDE pour tous les comptes
    out = ["# Créé par tools/personnaliser.py à partir de ma-personnalisation.conf — ne pas modifier.",
           "# Raccourcis clavier par défaut de protect.OS (modifiables dans Paramètres → Raccourcis)."]
    groupes = {}
    for k, (desktop, action) in RACCOURCIS.items():
        v = c["raccourcis"][k]
        if k == "executer":
            v = "\t".join(x for x in ("Alt+Space", v) if x)
        if v:
            groupes.setdefault(desktop, []).append(f"{action}={v}")
    for desktop, entrees in groupes.items():
        out += ["", f"[services][{desktop}]"] + entrees
    with open(os.path.join(THEME, "etc", "xdg", "kglobalshortcutsrc"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


def appliquer_protection(c):
    o = c["options"]
    conf = os.path.join(ROOT, "packages", "protectos-protection", "root", "etc", "protectos", "vie-privee.conf")
    os.makedirs(os.path.dirname(conf), exist_ok=True)
    with open(conf, "w", encoding="utf-8") as f:
        f.write("# Vie privée de protect.OS (réglé à l'origine par ma-personnalisation.conf).\n"
                "# Le Centre de protection peut aussi activer ou désactiver le bloqueur.\n"
                f"BLOQUEUR={o['bloqueur_pubs']}\n")
    modele = os.path.join(ROOT, "packages", "protectos-protection", "firefox-policies.json")
    for d in ("firefox-esr", "firefox"):
        cible = os.path.join(ROOT, "packages", "protectos-protection", "root", "etc", d, "policies", "policies.json")
        if o["firefox_confidentiel"] == "oui":
            os.makedirs(os.path.dirname(cible), exist_ok=True)
            shutil.copy(modele, cible)
        elif os.path.exists(cible):
            os.remove(cible)
            for parent in (os.path.dirname(cible), os.path.dirname(os.path.dirname(cible))):
                if os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)


def regenerer_images():
    if not (shutil.which("rsvg-convert") and _a_pil()):
        print("  Images non régénérées ici (il faut python3-pil et librsvg2-bin) : GitHub le fera.")
        return False
    subprocess.run([sys.executable, os.path.join(ROOT, "tools", "render-images.py")], check=True)
    shutil.rmtree(os.path.join(ROOT, "tools", "build"), ignore_errors=True)
    return True


def _a_pil():
    try:
        import PIL  # noqa: F401
        return True
    except ImportError:
        return False


def main():
    c = lire_conf()
    etat = lire_etat()
    print(f"Personnalisation : « {c['nom']} », couleurs {c['principale']} / {c['accent']}, "
          f"{c['langue']}, clavier {c['clavier']}{' ' + c['variante'] if c['variante'] else ''}")
    n, table = appliquer_textes(c, etat)
    print(f"  Nom, slogan et couleurs : {n} fichier{'s' if n > 1 else ''} mis à jour")
    nb, ids = appliquer_logiciels(c)
    print(f"  Logiciels inclus : {nb} ; épinglés : {', '.join(i.replace('.desktop', '') for i in ids)}")
    appliquer_bureau(c)
    o = c["options"]
    print(f"  Bureau : thème {o['theme']}, barre {o['barre']} en {o['position']}, verre {o['verre']}, "
          f"assistant {o['assistant']}")
    appliquer_noms_raccourcis(c)
    print(f"  Noms d'applications et raccourcis clavier appliqués")
    appliquer_protection(c)
    print(f"  Vie privée : bloqueur {o['bloqueur_pubs']}, Firefox confidentiel {o['firefox_confidentiel']}")
    appliquer_langue(c)
    print(f"  Langue, clavier et fuseau : {c['langue']}, {c['clavier']}, {c['fuseau']}")
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump({"nom": c["nom"], "slogan": c["slogan"], "couleurs": table}, f, ensure_ascii=False, indent=1)
    if "--sans-images" not in sys.argv:
        if regenerer_images():
            print("  Logo, fond d'écran et images de démarrage régénérés")
    print("Terminé.")


if __name__ == "__main__":
    main()
