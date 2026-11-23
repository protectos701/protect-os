#!/usr/bin/python3
"""Dessine la collection de fonds d'écran supplémentaires de protect.OS (bleu nuit et or).

À lancer seulement pour modifier les dessins : les images produites sont enregistrées dans le projet.
Chaque fond devient un fond d'écran KDE (clic droit sur le bureau → Configurer le bureau et le fond d'écran).
"""
import json
import math
import os
import random
import subprocess
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "packages", "protectos-wallpapers", "root", "usr", "share", "wallpapers")
W, H = 3840, 2160

DEFS = """<defs>
 <linearGradient id="or" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6dc8a"/><stop offset=".5" stop-color="#d4a72c"/><stop offset="1" stop-color="#8a6a0c"/></linearGradient>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#020617" stop-opacity=".65"/></radialGradient>
</defs>"""


def vagues():
    """Rubans dorés qui ondulent sur un bleu nuit profond."""
    rnd = random.Random(3)
    lignes = []
    for k in range(26):
        y0 = H * (0.30 + k * 0.018)
        amp = H * (0.07 + 0.002 * k)
        ph = k * 0.22
        pts = []
        for i in range(0, W + 40, 40):
            x = i
            y = y0 + amp * math.sin(i / W * 2.4 * math.pi + ph) + 0.35 * amp * math.sin(i / W * 5.1 * math.pi + ph * 1.7)
            pts.append(f"{x:.0f},{y:.1f}")
        op = 0.10 + 0.55 * math.exp(-((k - 13) / 6.5) ** 2)
        lignes.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="url(#or)" '
                      f'stroke-width="{rnd.uniform(2.5, 5):.1f}" stroke-opacity="{op:.2f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}
<defs><linearGradient id="fond" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1f5c"/><stop offset="1" stop-color="#040b26"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".55" r=".55"><stop offset="0" stop-color="#2a4fb8" stop-opacity=".55"/><stop offset="1" stop-color="#2a4fb8" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#fond)"/><rect width="{W}" height="{H}" fill="url(#halo)"/>
{"".join(lignes)}<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>"""


def nuit():
    """Ciel de nuit : étoiles dorées, constellation en forme de bouclier."""
    rnd = random.Random(11)
    etoiles = []
    for _ in range(900):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        r = rnd.choice([1.2, 1.6, 2, 2.4, 3.2]) * (1.4 if rnd.random() < 0.05 else 1)
        etoiles.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#f3d27a" fill-opacity="{rnd.uniform(.25, .95):.2f}"/>')
    cx, cy, s = W * 0.70, H * 0.38, 330
    bouclier = [(0, -1), (0.85, -0.68), (0.82, 0.18), (0, 1), (-0.82, 0.18), (-0.85, -0.68)]
    pts = [(cx + x * s, cy + y * s) for x, y in bouclier]
    trait = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts + [pts[0]])
    astres = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="#fbe3a0"/><circle cx="{x:.0f}" cy="{y:.0f}" r="26" '
                     f'fill="#fbe3a0" fill-opacity=".15"/>' for x, y in pts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}
<defs><linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#020617"/><stop offset=".7" stop-color="#0a1a52"/><stop offset="1" stop-color="#16307a"/></linearGradient>
<radialGradient id="voie" cx=".3" cy=".6" r=".6"><stop offset="0" stop-color="#5b8cff" stop-opacity=".22"/><stop offset="1" stop-color="#5b8cff" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#ciel)"/><rect width="{W}" height="{H}" fill="url(#voie)"/>
{"".join(etoiles)}<polyline points="{trait}" fill="none" stroke="#f3d27a" stroke-opacity=".45" stroke-width="3" stroke-dasharray="14 12"/>{astres}
<path d="M0 {H} L0 {H * .86:.0f} Q{W * .25:.0f} {H * .80:.0f} {W * .5:.0f} {H * .87:.0f} T{W} {H * .84:.0f} L{W} {H} Z" fill="#020617"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>"""


def hexagones():
    """Maillage d'alvéoles en verre, quelques alvéoles dorées : la protection, en motif."""
    rnd = random.Random(5)
    r = 120
    dx, dy = r * math.sqrt(3), r * 1.5
    cellules = []
    for j in range(-1, int(H / dy) + 2):
        for i in range(-1, int(W / dx) + 2):
            cx = i * dx + (dx / 2 if j % 2 else 0)
            cy = j * dy
            dist = math.hypot((cx - W * 0.5) / W, (cy - H * 0.5) / H)
            pts = " ".join(f"{cx + (r - 6) * math.cos(math.radians(60 * k + 30)):.0f},"
                           f"{cy + (r - 6) * math.sin(math.radians(60 * k + 30)):.0f}" for k in range(6))
            if rnd.random() < 0.045 * (1.4 - dist):
                cellules.append(f'<polygon points="{pts}" fill="url(#or)" fill-opacity="{rnd.uniform(.35, .7):.2f}"/>')
            else:
                bleu = rnd.choice(["#0e2a6b", "#12307a", "#0b1f5c", "#16307a", "#1e3a8a"])
                cellules.append(f'<polygon points="{pts}" fill="{bleu}" fill-opacity="{rnd.uniform(.55, .95):.2f}" '
                                f'stroke="#d4a72c" stroke-opacity="{max(.05, .38 - dist * .45):.2f}" stroke-width="3"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}
<defs><radialGradient id="lum" cx=".5" cy=".42" r=".6"><stop offset="0" stop-color="#5b8cff" stop-opacity=".30"/><stop offset="1" stop-color="#5b8cff" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="#060f2e"/>{"".join(cellules)}<rect width="{W}" height="{H}" fill="url(#lum)"/>
<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>"""


def aube():
    """Lever de soleil doré derrière des collines bleues."""
    collines = []
    for k, (base, amp, couleur) in enumerate([(0.62, 0.05, "#2a4fb8"), (0.70, 0.06, "#1e3a8a"),
                                              (0.78, 0.05, "#12307a"), (0.87, 0.04, "#0a1a52")]):
        pts = [f"0,{H}"]
        for i in range(0, W + 60, 60):
            y = H * (base + amp * math.sin(i / W * (2.2 + k) * math.pi + k * 1.3))
            pts.append(f"{i},{y:.0f}")
        pts.append(f"{W},{H}")
        collines.append(f'<polygon points="{" ".join(pts)}" fill="{couleur}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}
<defs><linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b1f5c"/><stop offset=".45" stop-color="#3a5bb8"/><stop offset=".62" stop-color="#e8c15a"/><stop offset=".75" stop-color="#f6dc8a"/></linearGradient>
<radialGradient id="soleil" cx=".5" cy=".62" r=".35"><stop offset="0" stop-color="#fff3c4"/><stop offset=".12" stop-color="#fbe3a0" stop-opacity=".95"/><stop offset=".4" stop-color="#e3b53e" stop-opacity=".35"/><stop offset="1" stop-color="#e3b53e" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="url(#ciel)"/><rect width="{W}" height="{H}" fill="url(#soleil)"/>
{"".join(collines)}<rect width="{W}" height="{H}" fill="url(#vig)" opacity=".7"/></svg>"""


def epure():
    """Fond épuré : dégradé bleu nuit et un trait doré en diagonale, pour ceux qui aiment la sobriété."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{DEFS}
<defs><linearGradient id="fond" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16307a"/><stop offset=".55" stop-color="#0a1a52"/><stop offset="1" stop-color="#040b26"/></linearGradient>
<linearGradient id="trait" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#d4a72c" stop-opacity="0"/><stop offset=".5" stop-color="#f3d27a"/><stop offset="1" stop-color="#d4a72c" stop-opacity="0"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#fond)"/>
<path d="M{-W * .1:.0f} {H * .95:.0f} Q{W * .45:.0f} {H * .55:.0f} {W * 1.1:.0f} {H * .18:.0f}" fill="none" stroke="url(#trait)" stroke-width="6"/>
<path d="M{-W * .1:.0f} {H * 1.02:.0f} Q{W * .5:.0f} {H * .62:.0f} {W * 1.1:.0f} {H * .3:.0f}" fill="none" stroke="url(#trait)" stroke-width="2" stroke-opacity=".5"/>
<rect width="{W}" height="{H}" fill="url(#vig)" opacity=".6"/></svg>"""


FONDS = [
    ("ProtectOS-Vagues", "protect.OS Vagues d'or", vagues),
    ("ProtectOS-Nuit", "protect.OS Nuit étoilée", nuit),
    ("ProtectOS-Alveoles", "protect.OS Alvéoles", hexagones),
    ("ProtectOS-Aube", "protect.OS Aube dorée", aube),
    ("ProtectOS-Epure", "protect.OS Épuré", epure),
]


def main():
    tmp = tempfile.mkdtemp()
    for ident, nom, dessin in FONDS:
        d = os.path.join(DEST, ident, "contents", "images")
        os.makedirs(d, exist_ok=True)
        svg = os.path.join(tmp, ident + ".svg")
        png = os.path.join(tmp, ident + ".png")
        open(svg, "w").write(dessin())
        subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-o", png, svg], check=True)
        img = Image.open(png).convert("RGB")
        img.save(os.path.join(d, f"{W}x{H}.jpg"), quality=90, optimize=True)
        img.resize((1920, 1080), Image.LANCZOS).save(os.path.join(d, "1920x1080.jpg"), quality=90, optimize=True)
        img.resize((400, 225), Image.LANCZOS).save(os.path.join(DEST, ident, "contents", "screenshot.jpg"), quality=88)
        meta = {"KPlugin": {"Authors": [{"Name": "protect.OS"}], "Id": ident, "License": "CC-BY-SA-4.0",
                            "Name": nom, "Name[fr]": nom}}
        with open(os.path.join(DEST, ident, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=4)
            f.write("\n")
        print("Fond :", nom)


if __name__ == "__main__":
    main()
