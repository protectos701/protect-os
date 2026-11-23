#!/usr/bin/env python3
"""Génère toutes les images de protect.OS (fond d'écran, logos, aperçus).

Dépendances (Debian) : sudo apt install python3-pil librsvg2-bin
Usage : python3 tools/render-images.py   (depuis la racine du projet)
"""
import base64
import configparser
import html
import os
import random
import subprocess
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "packages")
TMP = os.path.join(ROOT, "tools", "build")
NOM = "protect.OS"
SLOGAN = "Le système qui vous protège"


def perso(section):
    """Fichier indiqué dans ma-personnalisation.conf (logo ou fond d'écran), ou None."""
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(os.path.join(ROOT, "ma-personnalisation.conf"), encoding="utf-8")
    f = cp.get(section, "fichier", fallback="").strip()
    return os.path.join(ROOT, f) if f else None


def png_data(path):
    return "data:image/png;base64," + base64.b64encode(open(path, "rb").read()).decode()
os.makedirs(TMP, exist_ok=True)


# Chaque image va dans le paquet qui l'installe
OWNER = [
    ("usr/share/plymouth", "protectos-plymouth"),
    ("usr/share/wallpapers", "protectos-wallpapers"),
    ("etc/calamares", "protectos-calamares"),
    ("", "protectos-theme"),
]


def path(*p):
    rel = os.path.join(*p)
    pkg = next(name for prefix, name in OWNER if rel.startswith(prefix))
    full = os.path.join(PKG, pkg, "root", rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    return full


def svg_to_png(svg_file, png_file, w, h):
    subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), "-o", png_file, svg_file], check=True)


def wallpaper_svg(w, h, seed=7):
    """Vitrail bleu nuit : un maillage de verres bleus sertis de plomb doré."""
    rnd = random.Random(seed)
    cols, rows = 14, 8
    pts = []
    for r in range(rows + 1):
        row = []
        for c in range(cols + 1):
            x = c * w / cols
            y = r * h / rows
            if 0 < c < cols:
                x += rnd.uniform(-0.32, 0.32) * w / cols
            if 0 < r < rows:
                y += rnd.uniform(-0.32, 0.32) * h / rows
            row.append((x, y))
        pts.append(row)
    blues = ["#0b1f5c", "#0e2a6b", "#12307a", "#172554", "#1e3a8a", "#1d4ed8", "#0a1a4a", "#153c9c"]
    lead = max(2, w // 900)
    polys = []
    for r in range(rows):
        for c in range(cols):
            a, b, cc, d = pts[r][c], pts[r][c + 1], pts[r + 1][c + 1], pts[r + 1][c]
            tris = [(a, b, cc), (a, cc, d)] if rnd.random() < .5 else [(a, b, d), (b, cc, d)]
            for t in tris:
                col = rnd.choice(blues)
                if rnd.random() < .05:
                    col = rnd.choice(["#c99a24", "#e3b53e", "#a87b10"])
                op = rnd.uniform(.75, 1)
                pts_s = " ".join(f"{x:.1f},{y:.1f}" for x, y in t)
                polys.append(f'<polygon points="{pts_s}" fill="{col}" fill-opacity="{op:.2f}"/>')
    lines = "".join(p.replace("/>", f' fill="none" stroke="url(#lead)" stroke-width="{lead}" stroke-linejoin="round"/>')
                    .replace(' fill="', ' data-f="', 1) for p in polys)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
 <linearGradient id="lead" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="{h}">
  <stop offset="0" stop-color="#f6dc8a"/><stop offset=".5" stop-color="#d4a72c"/><stop offset="1" stop-color="#8a6a0c"/>
 </linearGradient>
 <radialGradient id="glow" cx=".72" cy=".24" r=".45"><stop offset="0" stop-color="#fbe3a0" stop-opacity=".55"/><stop offset="1" stop-color="#fbe3a0" stop-opacity="0"/></radialGradient>
 <radialGradient id="glow2" cx=".12" cy=".88" r=".5"><stop offset="0" stop-color="#5b8cff" stop-opacity=".35"/><stop offset="1" stop-color="#5b8cff" stop-opacity="0"/></radialGradient>
 <radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#020617" stop-opacity=".6"/></radialGradient>
 <linearGradient id="sheen" x1="0" y1="0" x2="1" y2=".55"><stop offset=".38" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff3c4" stop-opacity=".13"/><stop offset=".62" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<rect width="{w}" height="{h}" fill="#0a1a4a"/>
{"".join(polys)}
<g opacity=".7">{lines}</g>
<rect width="{w}" height="{h}" fill="url(#glow)"/>
<rect width="{w}" height="{h}" fill="url(#glow2)"/>
<rect width="{w}" height="{h}" fill="url(#sheen)"/>
<rect width="{w}" height="{h}" fill="url(#vig)"/>
</svg>'''


def main():
    logo = os.path.join(ROOT, "tools", "protectos-logo.svg")
    perso_logo = perso("logo")
    if perso_logo and perso_logo.lower().endswith(".svg"):
        logo = perso_logo
    elif perso_logo:
        # Logo en image : centré dans un carré transparent, puis enveloppé dans un SVG
        im = ImageOps.pad(Image.open(perso_logo).convert("RGBA"), (512, 512), color=(0, 0, 0, 0))
        tmp_png = os.path.join(TMP, "logo-perso.png")
        im.save(tmp_png)
        logo = os.path.join(TMP, "logo-perso.svg")
        with open(logo, "w") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                    'width="512" height="512" viewBox="0 0 512 512">'
                    f'<image width="512" height="512" xlink:href="{png_data(tmp_png)}"/></svg>')

    # Icônes vectorielles (menu Démarrer, installateur)
    for name in ("protectos-logo.svg", "protectos-start.svg"):
        with open(logo) as src, open(path("usr/share/icons/hicolor/scalable/apps", name), "w") as dst:
            dst.write(src.read())

    # Logos PNG
    svg_to_png(logo, path("usr/share/plymouth/themes/protectos/logo.png"), 160, 160)
    svg_to_png(logo, path("usr/share/plasma/look-and-feel/org.protectos.desktop/contents/splash/images/logo.png"), 256, 256)
    svg_to_png(logo, path("etc/calamares/branding/protectos/logo.png"), 256, 256)

    # Barre de progression Plymouth
    Image.new("RGBA", (1, 1), (255, 255, 255, 60)).save(path("usr/share/plymouth/themes/protectos/track.png"))
    Image.new("RGBA", (1, 1), "#d4a72c").save(path("usr/share/plymouth/themes/protectos/fill.png"))

    # Fond d'écran
    big = path("usr/share/wallpapers/ProtectOS/contents/images/3840x2160.png")
    perso_fond = perso("fond_ecran")
    if perso_fond:
        # Votre image, recadrée au format de l'écran (16:9)
        ImageOps.fit(Image.open(perso_fond).convert("RGB"), (3840, 2160), Image.LANCZOS).save(big)
    else:
        wp = os.path.join(TMP, "wallpaper.svg")
        with open(wp, "w") as f:
            f.write(wallpaper_svg(3840, 2160))
        svg_to_png(wp, big, 3840, 2160)
    img = Image.open(big).convert("RGB")
    img.resize((1920, 1080), Image.LANCZOS).save(path("usr/share/wallpapers/ProtectOS/contents/images/1920x1080.png"))
    img.resize((400, 225), Image.LANCZOS).save(path("usr/share/wallpapers/ProtectOS/contents/screenshot.png"))

    # Aperçus du thème global
    lnf = "usr/share/plasma/look-and-feel/org.protectos.desktop/contents/previews"
    prev = img.resize((1920, 1080), Image.LANCZOS)
    mark = Image.open(path("etc/calamares/branding/protectos/logo.png")).convert("RGBA")
    prev.paste(mark, (1920 // 2 - 128, 1080 // 2 - 160), mark)
    prev.save(path(lnf, "fullscreenpreview.jpg"), quality=88)
    prev.resize((600, 338), Image.LANCZOS).save(path(lnf, "preview.png"))

    # Image d'accueil de l'installateur : logo + nom
    welcome_svg = os.path.join(TMP, "welcome.svg")
    logo224 = os.path.join(TMP, "logo224.png")
    svg_to_png(logo, logo224, 224, 224)
    taille = max(28, min(62, int(400 / (0.6 * max(len(NOM), 1)))))  # le nom tient toujours dans l'image
    with open(welcome_svg, "w") as f:
        f.write(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="720" height="300" viewBox="0 0 720 300">
<image x="40" y="38" width="224" height="224" xlink:href="{png_data(logo224)}"/>
<text x="296" y="160" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="{taille}" font-weight="700" fill="#d4a72c">{html.escape(NOM)}</text>
<text x="300" y="206" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="22" fill="#5b6b94">{html.escape(SLOGAN)}</text>
</svg>''')
    svg_to_png(welcome_svg, path("etc/calamares/branding/protectos/welcome.png"), 720, 300)
    print("Images générées.")


if __name__ == "__main__":
    main()
