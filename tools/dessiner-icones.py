#!/usr/bin/python3
"""Dessine les icônes protect.OS (applications et dossiers) en SVG, bleu nuit et or, effet verre.

À lancer seulement pour modifier les dessins : les SVG produits sont enregistrés dans le projet,
et tools/personnaliser.py les recolore automatiquement selon ma-personnalisation.conf.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONES = os.path.join(ROOT, "packages", "protectos-theme", "root", "usr", "share", "icons")
DOSSIER = os.path.join(ICONES, "ProtectOS", "scalable")

BLEU_HAUT, BLEU, BLEU_NUIT = "#2a4fb8", "#16307a", "#0a1a52"
OR_CLAIR, OR, OR_FONCE = "#f3d27a", "#d4a72c", "#9c7414"

DEFS = f"""<defs>
  <linearGradient id="fond" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLEU_HAUT}"/><stop offset="0.55" stop-color="{BLEU}"/><stop offset="1" stop-color="{BLEU_NUIT}"/>
  </linearGradient>
  <linearGradient id="or" gradientUnits="userSpaceOnUse" x1="0" y1="10" x2="0" y2="54">
    <stop offset="0" stop-color="{OR_CLAIR}"/><stop offset="1" stop-color="{OR}"/>
  </linearGradient>
  <linearGradient id="reflet" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.32"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="dos" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BLEU}"/><stop offset="1" stop-color="{BLEU_NUIT}"/>
  </linearGradient>
</defs>"""


def svg(corps):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">\n{DEFS}\n{corps}\n</svg>\n'


def tuile(motif):
    """Carré arrondi en verre bleu, liseré or, motif doré au centre."""
    return svg(f"""<rect x="4" y="4" width="56" height="56" rx="14" fill="url(#fond)"/>
<rect x="4.75" y="4.75" width="54.5" height="54.5" rx="13.3" fill="none" stroke="{OR}" stroke-opacity="0.75" stroke-width="1.5"/>
<path d="M6 18 Q6 6 18 6 H46 Q58 6 58 18 V24 Q32 32 6 24 Z" fill="url(#reflet)"/>
<g fill="url(#or)" stroke="url(#or)" stroke-linecap="round" stroke-linejoin="round">{motif}</g>""")


O = 'fill="none" stroke-width="3.2"'


def roue_dentee(cx=32, cy=32, r_ext=19, r_int=14.5, dents=8):
    import math
    pts = []
    for k in range(dents):
        a0 = 2 * math.pi * k / dents
        for da, r in ((-0.20, r_int), (-0.13, r_ext), (0.13, r_ext), (0.20, r_int)):
            a = a0 + da
            pts.append(f"{cx + r * math.cos(a):.2f} {cy + r * math.sin(a):.2f}")
    return "M" + " L".join(pts) + " Z"  # trait doré sans remplissage
APPS = {
    "explorateur": ('<path d="M15 22 Q15 19 18 19 H27 L31 23 H46 Q49 23 49 26 V44 Q49 47 46 47 H18 Q15 47 15 44 Z" stroke="none"/>'
                    f'<path d="M15 29 H49" stroke="{BLEU_NUIT}" stroke-width="2" fill="none" opacity="0.5"/>'),
    "terminal": (f'<rect x="13" y="17" width="38" height="30" rx="4" {O}/>'
                 f'<path d="M20 27 L26 32 L20 37" {O}/><path d="M30 38 H41" {O}/>'),
    "bloc-notes": (f'<path d="M19 13 H38 L46 21 V50 H19 Z" {O}/><path d="M25 28 H40 M25 34 H40 M25 40 H34" {O}/>'),
    "pdf": (f'<path d="M19 12 H37 L46 21 V52 H19 Z" {O}/><path d="M37 12 V21 H46" {O}/>'
            '<text x="32.5" y="42" font-family="DejaVu Sans, sans-serif" font-weight="bold" font-size="11" '
            'text-anchor="middle" stroke="none">PDF</text>'),
    "photos": (f'<rect x="12" y="16" width="40" height="32" rx="4" {O}/><circle cx="23" cy="26" r="3.6" stroke="none"/>'
               '<path d="M14 45 L26 33 L33 40 L39 34 L50 45 Z" stroke="none"/>'),
    "capture": (f'<path d="M14 24 V16 H22 M42 16 H50 V24 M50 40 V48 H42 M22 48 H14 V40" {O}/>'
                f'<circle cx="32" cy="32" r="7" {O}/><circle cx="32" cy="32" r="2.6" stroke="none"/>'),
    "calculatrice": (f'<rect x="17" y="11" width="30" height="42" rx="5" {O}/>'
                     '<rect x="22" y="16" width="20" height="8" rx="1.5" stroke="none"/>'
                     + "".join(f'<circle cx="{x}" cy="{y}" r="2.4" stroke="none"/>'
                               for y in (31, 38, 45) for x in (24, 32, 40))),
    "magasin": (f'<path d="M16 24 H48 L45 51 H19 Z" {O}/><path d="M25 27 V20 Q25 13 32 13 Q39 13 39 20 V27" {O}/>'
                '<path d="M32 33 L34.2 37.5 L39 38.2 L35.5 41.5 L36.4 46.3 L32 44 L27.6 46.3 L28.5 41.5 L25 38.2 '
                'L29.8 37.5 Z" stroke="none"/>'),
    "parametres": (f'<path d="{roue_dentee()}" stroke="none"/>'
                   f'<circle cx="32" cy="32" r="7.5" fill="{BLEU}" stroke="none"/>'),
    "archives": (f'<rect x="14" y="20" width="36" height="30" rx="3" {O}/><path d="M12 14 H52 V20 H12 Z" stroke="none"/>'
                 '<path d="M29 26 H35 M29 31 H35 M29 36 H35" stroke-width="2.6" fill="none"/>'
                 '<rect x="28" y="39" width="8" height="6" rx="1.5" stroke="none"/>'),
    "disques": (f'<rect x="12" y="20" width="40" height="24" rx="5" {O}/><circle cx="43" cy="32" r="2.8" stroke="none"/>'
                '<path d="M18 32 H33" stroke-width="3.2" fill="none"/>'),
    "taches": (f'<rect x="11" y="15" width="42" height="34" rx="4" {O}/>'
               f'<path d="M15 34 H23 L27 24 L33 42 L38 29 L41 34 H49" {O}/>'),
    "sauvegardes": (f'<path d="M17 25 A16 16 0 1 1 16.5 38" {O}/><path d="M11 21 L17 26.5 L22.5 20.5" {O}/>'
                    f'<path d="M32 23 V33 L39 37" {O}/>'),
    "pare-feu": ('<path d="M32 10 L50 17 V30 Q50 46 32 54 Q14 46 14 30 V17 Z" stroke="none"/>'
                 f'<path d="M24 32 L30 38 L41 26" fill="none" stroke="{BLEU_NUIT}" stroke-width="3.6"/>'),
    "imprimantes": (f'<path d="M21 24 V12 H43 V24" {O}/><rect x="11" y="24" width="42" height="18" rx="4" {O}/>'
                    f'<path d="M21 36 H43 V52 H21 Z" {O}/><circle cx="45" cy="30" r="2" stroke="none"/>'),
    "numeriseur": (f'<rect x="10" y="30" width="44" height="16" rx="4" {O}/><path d="M14 24 L48 18" {O}/>'
                   '<path d="M16 38 H40" stroke-width="3.2"/>'),
    "multimedia": ('<path d="M25 18 L47 32 L25 46 Z" stroke="none"/>'),
    "musique": ('<path d="M26 44 V18 L46 14 V40" fill="none" stroke-width="3.2"/>'
                '<ellipse cx="21.5" cy="44" rx="5.5" ry="4.5" stroke="none"/>'
                '<ellipse cx="41.5" cy="40" rx="5.5" ry="4.5" stroke="none"/>'),
}

# Noms d'icônes du système qui reçoivent chaque dessin
NOMS_APPS = {
    "explorateur": ["system-file-manager", "org.kde.dolphin", "dolphin", "file-manager"],
    "terminal": ["utilities-terminal", "org.kde.konsole", "konsole", "terminal", "xterm-color"],
    "bloc-notes": ["accessories-text-editor", "org.kde.kate", "kate", "org.kde.kwrite", "kwrite", "text-editor"],
    "pdf": ["okular", "org.kde.okular", "application-pdf-viewer"],
    "photos": ["gwenview", "org.kde.gwenview", "image-viewer", "multimedia-photo-viewer"],
    "capture": ["spectacle", "org.kde.spectacle", "applets-screenshooter", "accessories-screenshot"],
    "calculatrice": ["accessories-calculator", "kcalc", "org.kde.kcalc", "calc"],
    "magasin": ["plasmadiscover", "org.kde.discover", "system-software-install", "system-software-update"],
    "parametres": ["preferences-system", "systemsettings", "org.kde.systemsettings", "configure"],
    "archives": ["ark", "org.kde.ark", "utilities-file-archiver"],
    "disques": ["partitionmanager", "org.kde.partitionmanager", "gnome-disks"],
    "taches": ["utilities-system-monitor", "org.kde.plasma-systemmonitor", "ksysguard", "plasma-systemmonitor"],
    "sauvegardes": ["timeshift", "backups-app", "deja-dup"],
    "pare-feu": ["firewall-config", "security-high", "preferences-security-firewall"],
    "imprimantes": ["printer", "preferences-devices-printer", "printer-manager", "system-config-printer"],
    "numeriseur": ["org.kde.skanlite", "skanlite", "scanner"],
    "multimedia": ["multimedia-video-player", "org.kde.haruna", "haruna", "video-player"],
    "musique": ["multimedia-audio-player", "org.kde.elisa", "elisa", "audio-player"],
}


def dossier(embleme=""):
    """Dossier bleu verre, bord doré, emblème doré."""
    return svg(f"""<path d="M6 16 Q6 11 11 11 H25 L30 16 H53 Q58 16 58 21 V48 Q58 53 53 53 H11 Q6 53 6 48 Z" fill="url(#dos)"/>
<path d="M6 24 Q6 20 10 20 H54 Q58 20 58 24 V49 Q58 54 53 54 H11 Q6 54 6 49 Z" fill="url(#fond)"/>
<path d="M6.8 24 Q6.8 20.8 10 20.8 H54 Q57.2 20.8 57.2 24" fill="none" stroke="{OR}" stroke-width="1.6"/>
<path d="M7 25 Q7 21 11 21 H53 Q57 21 57 25 V31 Q32 37 7 31 Z" fill="url(#reflet)"/>
<g transform="translate(32 38) scale(0.52) translate(-32 -32)" fill="url(#or)" stroke="url(#or)" stroke-linecap="round" stroke-linejoin="round">{embleme}</g>""")


EMBLEMES = {
    "": "",
    "documents": APPS["bloc-notes"],
    "telechargements": f'<path d="M32 12 V40" {O.replace("3.2", "5")}/><path d="M20 30 L32 42 L44 30" {O.replace("3.2", "5")}/>'
                       f'<path d="M16 50 H48" {O.replace("3.2", "5")}/>',
    "images": APPS["photos"],
    "musique": APPS["musique"],
    "videos": f'<rect x="10" y="16" width="44" height="32" rx="5" {O.replace("3.2", "4")}/><path d="M27 24 L40 32 L27 40 Z" stroke="none"/>',
    "bureau": f'<rect x="10" y="13" width="44" height="30" rx="4" {O.replace("3.2", "4.5")}/><path d="M24 51 H40 M32 43 V51" {O.replace("3.2", "4.5")}/>',
    "modeles": f'<path d="M14 14 H50 V50 H14 Z" {O.replace("3.2", "4.5")} stroke-dasharray="6 5"/>',
    "public": f'<circle cx="24" cy="22" r="7" {O.replace("3.2", "4.5")}/><circle cx="42" cy="26" r="5.5" {O.replace("3.2", "4.5")}/>'
              f'<path d="M10 50 Q10 34 24 34 Q38 34 38 50 M34 50 Q36 38 44 38 Q54 38 54 50" {O.replace("3.2", "4.5")}/>',
    "maison": f'<path d="M12 31 L32 13 L52 31" {O.replace("3.2", "5")}/><path d="M18 27 V50 H46 V27" {O.replace("3.2", "5")}/>'
              '<rect x="28" y="36" width="8" height="14" stroke="none"/>',
}
NOMS_DOSSIERS = {
    "": ["folder", "folder-blue", "folder-open", "inode-directory", "folder-remote", "folder-drag-accept"],
    "documents": ["folder-documents", "folder-text"],
    "telechargements": ["folder-download", "folder-downloads"],
    "images": ["folder-pictures", "folder-images", "folder-image"],
    "musique": ["folder-music", "folder-sound", "folder-audio"],
    "videos": ["folder-videos", "folder-video", "folder-movies"],
    "bureau": ["user-desktop", "folder-desktop", "desktop"],
    "modeles": ["folder-templates"],
    "public": ["folder-publicshare", "folder-public"],
    "maison": ["user-home", "folder-home", "go-home"],
}


def corbeille(pleine):
    papiers = (f'<path d="M24 20 L28 12 L34 18 L40 11 L42 20" fill="{OR_CLAIR}" stroke="{OR_FONCE}" stroke-width="1"/>'
               if pleine else "")
    return svg(f"""{papiers}<path d="M15 21 H49 L45 55 Q44.5 58 41.5 58 H22.5 Q19.5 58 19 55 Z" fill="url(#fond)"/>
<path d="M15.8 21.8 H48.2" stroke="{OR}" stroke-width="1.6"/>
<path d="M16 22 H48 L47 32 Q32 36 17 32 Z" fill="url(#reflet)"/>
<path d="M26 28 L27 51 M32 28 V51 M38 28 L37 51" stroke="{OR}" stroke-width="2.4" stroke-linecap="round"/>
<rect x="11" y="15" width="42" height="6" rx="3" fill="url(#or)"/><rect x="27" y="11" width="10" height="5" rx="2" fill="url(#or)"/>""")


def ecrire(sousdossier, nom, contenu, alias):
    d = os.path.join(DOSSIER, sousdossier)
    os.makedirs(d, exist_ok=True)
    principal = f"protectos-{nom}.svg"
    with open(os.path.join(d, principal), "w", encoding="utf-8") as f:
        f.write(contenu)
    for a in alias:
        lien = os.path.join(d, a + ".svg")
        if os.path.lexists(lien):
            os.remove(lien)
        os.symlink(principal, lien)


def main():
    for nom, motif in APPS.items():
        ecrire("apps", nom, tuile(motif), NOMS_APPS[nom])
    for cle, noms in NOMS_DOSSIERS.items():
        ecrire("places", "dossier" + ("-" + cle if cle else ""), dossier(EMBLEMES[cle]), noms)
    ecrire("places", "corbeille", corbeille(False), ["user-trash", "trashcan_empty"])
    ecrire("places", "corbeille-pleine", corbeille(True), ["user-trash-full", "trashcan_full"])
    # Le thème clair reçoit les mêmes dessins
    for sd in ("apps", "places"):
        src = os.path.join(DOSSIER, sd)
        dst = os.path.join(ICONES, "ProtectOS-Clair", "scalable", sd)
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            lien = os.path.join(dst, f)
            if os.path.lexists(lien):
                continue  # garde les liens déjà présents (logo)
            os.symlink(os.path.join("..", "..", "..", "ProtectOS", "scalable", sd, f), lien)
    print("Icônes protect.OS dessinées dans", DOSSIER)


if __name__ == "__main__":
    main()
