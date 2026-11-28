#!/usr/bin/env python3
"""Dessine les décorations de fenêtres protect.OS (thème Aurorae de KWin), façon Windows 11 :

  - barre de titre unie, coins du haut arrondis, ombre douce autour de la fenêtre
  - boutons « — », « ☐ » (ou deux carrés quand la fenêtre est agrandie) et « ✕»,
    larges et plats ; la croix devient rouge au survol

Deux variantes : « protectos » (sombre) et « protectos-clair ».
Sortie : packages/protectos-theme/root/usr/share/aurorae/themes/<nom>/
"""
import json
import os

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIE = os.path.join(ICI, "..", "packages", "protectos-theme", "root", "usr", "share", "aurorae", "themes")

P = 14      # marge réservée à l'ombre
R = 8       # rayon des coins
T = 32      # hauteur de la barre de titre
BW, BH = 46, 32  # taille d'un bouton

VARIANTES = {
    "protectos": {
        "nom": "protect.OS", "fond": "#0c1532", "fond_inactif": "#0a122c", "bord": "#2a3a6e",
        "bord_inactif": "#1c2852", "glyphe": "#e9edf7", "glyphe_inactif": "#7f8bb0",
        "survol": "rgba(255,255,255,0.10)", "appui": "rgba(255,255,255,0.06)",
        "titre": "243,210,122", "titre_inactif": "150,162,196", "ombre": 0.55,
    },
    "protectos-clair": {
        "nom": "protect.OS (clair)", "fond": "#e2e9f8", "fond_inactif": "#eef2fa", "bord": "#b9c4de",
        "bord_inactif": "#d3dbec", "glyphe": "#1b2340", "glyphe_inactif": "#8a93ad",
        "survol": "rgba(0,0,0,0.07)", "appui": "rgba(0,0,0,0.04)",
        "titre": "26,35,64", "titre_inactif": "110,120,150", "ombre": 0.30,
    },
}


def couleur(c):
    """'rgba(r,g,b,a)' → (fill, opacity) compris par Qt SVG (SVG Tiny)."""
    if c.startswith("rgba("):
        r, g, b, a = [x.strip() for x in c[5:-1].split(",")]
        return f"rgb({r},{g},{b})", a
    return c, "1"


def rect(x, y, w, h, c, extra=""):
    f, o = couleur(c)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{f}" fill-opacity="{o}" {extra}/>'


def ombre_lineaire(gid, x1, y1, x2, y2, force):
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'
            f'<stop offset="0" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="0.65" stop-color="#000" stop-opacity="{force * 0.25:.3f}"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="{force * 0.6:.3f}"/></linearGradient>')


def ombre_radiale(gid, cx, cy, force, rayon=0):
    """Ombre d'un coin : opaque au bord de la fenêtre (à « rayon » du centre), transparente P pixels plus loin."""
    debut = rayon / (rayon + P)
    return (f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{rayon + P}">'
            f'<stop offset="{debut:.3f}" stop-color="#000" stop-opacity="{force * 0.6:.3f}"/>'
            f'<stop offset="{debut + (1 - debut) * 0.35:.3f}" stop-color="#000" stop-opacity="{force * 0.25:.3f}"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')


def decoration(v):
    """SVG à neuf morceaux : coins, bords et centre, pour la fenêtre active, inactive et agrandie."""
    defs, corps = [], []
    for etat, dy in (("", 0), ("inactive-", 200)):
        fond = v["fond_inactif"] if etat else v["fond"]
        bord = v["bord_inactif"] if etat else v["bord"]
        force = v["ombre"] * (0.7 if etat else 1.0)
        k = etat.rstrip("-") or "a"
        x0 = 0
        # Coin haut gauche : ombre + quart de cercle de la barre de titre
        defs.append(ombre_radiale(f"tl{k}", P + R, P + R + dy, force, R))
        corps.append(f'<g id="decoration-{etat}topleft">'
                     f'<rect x="{x0}" y="{dy}" width="{P + R}" height="{P + T}" fill="url(#tl{k})"/>'
                     f'<path d="M {P} {dy + P + T} L {P} {dy + P + R} A {R} {R} 0 0 1 {P + R} {dy + P} L {P + R} {dy + P + T} Z" '
                     f'fill="{fond}"/>'
                     f'<path d="M {P + 0.5} {dy + P + T} L {P + 0.5} {dy + P + R} A {R - 0.5} {R - 0.5} 0 0 1 {P + R} {dy + P + 0.5}" '
                     f'fill="none" stroke="{bord}" stroke-width="1"/></g>')
        # Haut : bande d'ombre puis barre de titre
        x = 40
        defs.append(ombre_lineaire(f"t{k}", 0, dy, 0, dy + P, force))
        corps.append(f'<g id="decoration-{etat}top"><rect x="{x}" y="{dy}" width="1" height="{P}" fill="url(#t{k})"/>'
                     + rect(x, dy + P, 1, T, fond) + rect(x, dy + P, 1, 1, bord) + '</g>')
        # Coin haut droit
        x = 60
        defs.append(ombre_radiale(f"tr{k}", x, P + R + dy, force, R))
        corps.append(f'<g id="decoration-{etat}topright">'
                     f'<rect x="{x}" y="{dy}" width="{P + R}" height="{P + T}" fill="url(#tr{k})"/>'
                     f'<path d="M {x + R} {dy + P + T} L {x + R} {dy + P + R} A {R} {R} 0 0 0 {x} {dy + P} L {x} {dy + P + T} Z" '
                     f'fill="{fond}"/>'
                     f'<path d="M {x + R - 0.5} {dy + P + T} L {x + R - 0.5} {dy + P + R} A {R - 0.5} {R - 0.5} 0 0 0 {x} {dy + P + 0.5}" '
                     f'fill="none" stroke="{bord}" stroke-width="1"/></g>')
        # Bords gauche et droit (ombre + filet), bas et coins du bas
        y = dy + 100
        defs.append(ombre_lineaire(f"l{k}", 0, 0, P, 0, force))
        corps.append(f'<g id="decoration-{etat}left"><rect x="0" y="{y}" width="{P}" height="1" fill="url(#l{k})"/>'
                     + rect(P, y, 1, 1, bord) + '</g>')
        corps.append(f'<g id="decoration-{etat}center">' + rect(40, y, 1, 1, fond) + '</g>')
        defs.append(ombre_lineaire(f"r{k}", 61 + P, 0, 61, 0, force))
        corps.append(f'<g id="decoration-{etat}right">' + rect(60, y, 1, 1, bord)
                     + f'<rect x="61" y="{y}" width="{P}" height="1" fill="url(#r{k})"/></g>')
        y = dy + 140
        defs.append(ombre_radiale(f"bl{k}", P + 1, y, force))
        corps.append(f'<g id="decoration-{etat}bottomleft"><rect x="0" y="{y}" width="{P + 1}" height="{P + 1}" fill="url(#bl{k})"/>'
                     + rect(P, y, 1, 1, bord) + '</g>')
        defs.append(ombre_lineaire(f"b{k}", 0, y + 1 + P, 0, y + 1, force))
        corps.append(f'<g id="decoration-{etat}bottom">' + rect(40, y, 1, 1, bord)
                     + f'<rect x="40" y="{y + 1}" width="1" height="{P}" fill="url(#b{k})"/></g>')
        defs.append(ombre_radiale(f"br{k}", 60, y, force))
        corps.append(f'<g id="decoration-{etat}bottomright"><rect x="60" y="{y}" width="{P + 1}" height="{P + 1}" fill="url(#br{k})"/>'
                     + rect(60, y, 1, 1, bord) + '</g>')
    # Fenêtre agrandie : barre de titre droite, sans ombre ni bord
    for etat, dy in (("", 400), ("inactive-", 450)):
        fond = v["fond_inactif"] if etat else v["fond"]
        for nom, x in (("topleft", 0), ("top", 10), ("topright", 20)):
            corps.append(f'<g id="decoration-maximized-{etat}{nom}">' + rect(x, dy, 1, T, fond) + '</g>')
        for nom, x in (("left", 30), ("center", 40), ("right", 50), ("bottomleft", 60), ("bottom", 70), ("bottomright", 80)):
            corps.append(f'<g id="decoration-maximized-{etat}{nom}">' + rect(x, dy, 1, 1, fond) + '</g>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="120" height="500">'
            f'<defs>{"".join(defs)}</defs>{"".join(corps)}</svg>\n')


def glyphe(type_, c, ox, oy):
    """Petit pictogramme de 10 px centré dans le bouton."""
    cx, cy = ox + BW / 2, oy + BH / 2
    trait = f'stroke="{c}" stroke-width="1" fill="none" stroke-linecap="square"'
    if type_ == "minimize":
        return f'<path d="M {cx - 5} {cy + 0.5} H {cx + 5}" {trait}/>'
    if type_ == "maximize":
        return f'<rect x="{cx - 4.5}" y="{cy - 4.5}" width="9" height="9" rx="1" {trait}/>'
    if type_ == "restore":
        return (f'<rect x="{cx - 4.5}" y="{cy - 2.5}" width="7" height="7" rx="1" {trait}/>'
                f'<path d="M {cx - 2.5} {cy - 2.5} V {cy - 4.5} H {cx + 4.5} V {cy + 2.5} H {cx + 2.5}" {trait}/>')
    return f'<path d="M {cx - 5} {cy - 5} L {cx + 5} {cy + 5} M {cx + 5} {cy - 5} L {cx - 5} {cy + 5}" {trait}/>'


def bouton(type_, v):
    """Un SVG par bouton, avec un élément par état (actif, survol, appui, fenêtre inactive…)."""
    etats = [("active", None, v["glyphe"]), ("hover", "survol", v["glyphe"]), ("pressed", "appui", v["glyphe"]),
             ("inactive", None, v["glyphe_inactif"]), ("hover-inactive", "survol", v["glyphe"]),
             ("pressed-inactive", "appui", v["glyphe"]), ("deactivated", None, v["glyphe_inactif"]),
             ("deactivated-inactive", None, v["glyphe_inactif"])]
    corps = []
    for i, (etat, fond, c) in enumerate(etats):
        oy = i * (BH + 4)
        morceau = rect(0, oy, BW, BH, "rgba(0,0,0,0)")
        if fond:
            if type_ == "close":
                rouge = "#c42b1c" if fond == "survol" else "#a8261a"
                morceau += rect(0, oy, BW, BH, rouge)
                c = "#ffffff"
            else:
                morceau += rect(0, oy, BW, BH, v[fond])
        morceau += glyphe(type_, c, 0, oy)
        corps.append(f'<g id="{etat}-center">{morceau}</g>')
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="{BW}" '
            f'height="{len(etats) * (BH + 4)}">{"".join(corps)}</svg>\n')


def config(v):
    return f"""[General]
ActiveTextColor={v['titre']}
InactiveTextColor={v['titre_inactif']}
TitleAlignment=Left
TitleVerticalAlignment=Center
Animation=120
UseTextShadow=false
Shadow=true
HaloActive=false
HaloInactive=false
DecorationPosition=0

[Layout]
BorderLeft=1
BorderRight=1
BorderBottom=1
TitleEdgeTop=0
TitleEdgeBottom=0
TitleEdgeLeft=10
TitleEdgeRight=0
TitleEdgeTopMaximized=0
TitleEdgeBottomMaximized=0
TitleEdgeLeftMaximized=10
TitleEdgeRightMaximized=0
TitleBorderLeft=8
TitleBorderRight=8
TitleHeight={T}
ButtonWidth={BW}
ButtonHeight={BH}
ButtonSpacing=0
ButtonMarginTop=0
ButtonMarginTopMaximized=0
ExplicitButtonSpacer=8
PaddingTop={P}
PaddingBottom={P}
PaddingLeft={P}
PaddingRight={P}
"""


def main():
    for dossier, v in VARIANTES.items():
        d = os.path.join(SORTIE, dossier)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "decoration.svg"), "w") as f:
            f.write(decoration(v))
        for b in ("close", "minimize", "maximize", "restore"):
            with open(os.path.join(d, f"{b}.svg"), "w") as f:
                f.write(bouton(b, v))
        with open(os.path.join(d, f"{dossier}rc"), "w") as f:
            f.write(config(v))
        with open(os.path.join(d, "metadata.desktop"), "w") as f:
            f.write(f"[Desktop Entry]\nName={v['nom']}\nComment=Fenêtres protect.OS\n"
                    f"X-KDE-PluginInfo-Name={dossier}\nX-KDE-PluginInfo-Author=protect.OS\n"
                    "X-KDE-PluginInfo-Version=1.0\nX-KDE-PluginInfo-License=GPL\n")
        with open(os.path.join(d, "metadata.json"), "w") as f:
            json.dump({"KPlugin": {"Id": dossier, "Name": v["nom"], "Description": "Fenêtres protect.OS",
                                   "Authors": [{"Name": "protect.OS"}], "License": "GPL", "Version": "1.0"}},
                      f, ensure_ascii=False, indent=2)
        print("Décoration", dossier)


if __name__ == "__main__":
    main()
