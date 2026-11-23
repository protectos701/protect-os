#!/usr/bin/python3
"""Dessine le style de bureau protect.OS : repères de la barre des tâches (trait doré, verre).

Plasma prend dans ce style les éléments présents (widgets/tasks.svg) et tout le reste dans le style par défaut.
À lancer seulement pour modifier les dessins.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "packages", "protectos-theme", "root", "usr", "share", "plasma", "desktoptheme", "protectos")
OR = "#d4a72c"
C = 6      # taille des coins (marges du cadre)
W = 12     # largeur des morceaux étirables
H = 12     # hauteur des morceaux étirables

# Pour chaque état : fond (couleur, opacité), contour (opacité), trait du bas (couleur, opacité, épaisseur)
ETATS = {
    "normal":    (None, 0.0, 0.0, OR, 0.70, 3),
    "focus":     ("#ffffff", 0.13, 0.16, OR, 1.0, 3),
    "hover":     ("#ffffff", 0.17, 0.20, None, 0, 0),
    "minimized": (None, 0.0, 0.0, OR, 0.35, 3),
    "attention": (OR, 0.28, 0.45, "#ff9a3c", 1.0, 3),
}


def cadre(prefixe, ox, oy, fond, op_fond, op_bord, trait, op_trait, ep):
    w, h = 2 * C + W, 2 * C + H
    remplissage = f'fill="{fond or "#000000"}" fill-opacity="{op_fond}"'
    bord = f'stroke="#ffffff" stroke-opacity="{op_bord}" stroke-width="1"' if op_bord else 'stroke="none"'
    morceaux = {
        "topleft": (0, 0, C, C), "top": (C, 0, W, C), "topright": (C + W, 0, C, C),
        "left": (0, C, C, H), "center": (C, C, W, H), "right": (C + W, C, C, H),
        "bottomleft": (0, C + H, C, C), "bottom": (C, C + H, W, C), "bottomright": (C + W, C + H, C, C),
    }
    out = []
    for nom, (x, y, mw, mh) in morceaux.items():
        X, Y = ox + x, oy + y
        dedans = [f'<rect x="{X}" y="{Y}" width="{mw}" height="{mh}" fill="#000000" fill-opacity="0"/>']
        r = C
        if nom in ("topleft", "topright", "bottomleft", "bottomright"):
            # quart de cercle arrondi, centré sur le coin intérieur
            cx = X + (mw if "left" in nom else 0)
            cy = Y + (mh if "top" in nom else 0)
            sx = -1 if "left" in nom else 1
            sy = -1 if "top" in nom else 1
            d = (f"M{cx} {cy} L{cx + sx * r} {cy} A{r} {r} 0 0 {0 if sx * sy < 0 else 1} {cx} {cy + sy * r} Z")
            dedans.append(f'<path d="{d}" {remplissage}/>')
            if op_bord:
                d2 = f"M{cx + sx * (r - 0.5)} {cy} A{r - 0.5} {r - 0.5} 0 0 {0 if sx * sy < 0 else 1} {cx} {cy + sy * (r - 0.5)}"
                dedans.append(f'<path d="{d2}" fill="none" {bord}/>')
        else:
            dedans.append(f'<rect x="{X}" y="{Y}" width="{mw}" height="{mh}" {remplissage}/>')
            if op_bord and nom != "center":
                if nom == "top":
                    dedans.append(f'<rect x="{X}" y="{Y}" width="{mw}" height="1" fill="#ffffff" fill-opacity="{op_bord}"/>')
                elif nom == "bottom":
                    dedans.append(f'<rect x="{X}" y="{Y + mh - 1}" width="{mw}" height="1" fill="#ffffff" fill-opacity="{op_bord}"/>')
                elif nom == "left":
                    dedans.append(f'<rect x="{X}" y="{Y}" width="1" height="{mh}" fill="#ffffff" fill-opacity="{op_bord}"/>')
                elif nom == "right":
                    dedans.append(f'<rect x="{X + mw - 1}" y="{Y}" width="1" height="{mh}" fill="#ffffff" fill-opacity="{op_bord}"/>')
        if nom == "bottom" and trait:
            # trait doré : seulement sur la partie étirable du bas, donc plus court que le bouton
            dedans.append(f'<rect x="{X}" y="{Y + mh - ep - 1}" width="{mw}" height="{ep}" rx="{ep / 2}" '
                          f'fill="{trait}" fill-opacity="{op_trait}"/>')
        out.append(f'<g id="{prefixe}-{nom}">{"".join(dedans)}</g>')
    return "\n".join(out), w, h


def main():
    morceaux, x = [], 0
    for prefixe, (fond, op_fond, op_bord, trait, op_trait, ep) in ETATS.items():
        svg, w, h = cadre(prefixe, x, 0, fond, op_fond, op_bord, trait, op_trait, ep)
        morceaux.append(svg)
        x += w + 10
    os.makedirs(os.path.join(DEST, "widgets"), exist_ok=True)
    with open(os.path.join(DEST, "widgets", "tasks.svg"), "w", encoding="utf-8") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{x}" height="{2 * C + H}">\n'
                + "\n".join(morceaux) + "\n</svg>\n")
    meta = {"KPlugin": {"Authors": [{"Name": "protect.OS"}], "Id": "protectos", "License": "LGPL-2.1+",
                        "Name": "protect.OS", "Description": "Style de bureau de protect.OS",
                        "Version": "1.0", "Category": ""},
            "X-Plasma-API": "5.0"}
    with open(os.path.join(DEST, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)
        f.write("\n")
    # Les éléments absents de ce style sont pris dans le style par défaut (Brise)
    with open(os.path.join(DEST, "metadata.desktop"), "w", encoding="utf-8") as f:
        f.write("[Desktop Entry]\nName=protect.OS\nX-KDE-PluginInfo-Name=protectos\n\n[Settings]\nFallbackTheme=default\n")
    with open(os.path.join(DEST, "plasmarc"), "w", encoding="utf-8") as f:
        f.write("[Settings]\nFallbackTheme=default\n\n[ContrastEffect]\nenabled=true\ncontrast=0.2\nintensity=2.0\nsaturation=1.7\n\n"
                "[AdaptiveTransparency]\nenabled=true\n")
    print("Style de bureau protect.OS :", DEST)


if __name__ == "__main__":
    main()
