#!/usr/bin/python3
"""Affiche chaque application protect.OS dans un écran virtuel (sans bureau) et en fait une capture.

Utilisé par le test « Aperçu des applications » sur GitHub : quelques minutes au lieu d'une ISO complète.
  python3 tools/apercu-applis.py [dossier de sortie]
Les captures sont aussi écrites dans le journal (base64) entre APERCU-DEBUT et APERCU-FIN.
"""
import base64
import importlib.machinery
import importlib.util
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PK = os.path.join(ROOT, "packages")
for lib in ("protectos-bienvenue", "protectos-protection", "protectos-parental", "protectos-programmes"):
    sys.path.insert(0, os.path.join(PK, lib, "root", "usr", "lib", "protectos"))

from PyQt6.QtCore import QBuffer, QIODevice, QTimer  # noqa: E402
from PyQt6.QtGui import QColor, QIcon, QPalette  # noqa: E402
from PyQt6.QtWidgets import QApplication  # noqa: E402


def palette_depuis(colors):
    """Construit une palette Qt à partir d'un jeu de couleurs KDE (.colors)."""
    import configparser
    c = configparser.ConfigParser(interpolation=None, strict=False)
    c.optionxform = str
    c.read(colors, encoding="utf-8")

    def col(grp, cle):
        r, g, b = (int(x) for x in c[grp][cle].split(",")[:3])
        return QColor(r, g, b)

    p = QPalette()
    R = QPalette.ColorRole
    p.setColor(R.Window, col("Colors:Window", "BackgroundNormal"))
    p.setColor(R.WindowText, col("Colors:Window", "ForegroundNormal"))
    p.setColor(R.Base, col("Colors:View", "BackgroundNormal"))
    p.setColor(R.AlternateBase, col("Colors:View", "BackgroundAlternate"))
    p.setColor(R.Text, col("Colors:View", "ForegroundNormal"))
    p.setColor(R.Button, col("Colors:Button", "BackgroundNormal"))
    p.setColor(R.ButtonText, col("Colors:Button", "ForegroundNormal"))
    p.setColor(R.Highlight, col("Colors:Selection", "BackgroundNormal"))
    p.setColor(R.HighlightedText, col("Colors:Selection", "ForegroundNormal"))
    p.setColor(R.ToolTipBase, col("Colors:Tooltip", "BackgroundNormal"))
    p.setColor(R.ToolTipText, col("Colors:Tooltip", "ForegroundNormal"))
    p.setColor(R.PlaceholderText, col("Colors:View", "ForegroundInactive"))
    p.setColor(R.Link, col("Colors:View", "ForegroundLink"))
    return p


def charger(chemin, nom):
    l = importlib.machinery.SourceFileLoader(nom, chemin)
    s = importlib.util.spec_from_loader(nom, l)
    m = importlib.util.module_from_spec(s)
    l.exec_module(m)
    return m


def parametres():
    return charger(f"{PK}/protectos-bienvenue/root/usr/bin/protectos-parametres", "pp").Parametres()


def a_propos():
    return charger(f"{PK}/protectos-bienvenue/root/usr/bin/protectos-a-propos", "ap").APropos()


def protection():
    return charger(f"{PK}/protectos-protection/root/usr/bin/protectos-protection", "cp").Centre()


def parental():
    m = charger(f"{PK}/protectos-parental/root/usr/bin/protectos-parental", "par")
    m.pc.comptes = lambda: [{"login": "lea", "uid": 1001, "nom": "Léa", "admin": False},
                            {"login": "tom", "uid": 1002, "nom": "Tom", "admin": False},
                            {"login": "anthony", "uid": 1000, "nom": "Anthony", "admin": True}]
    return m.Parental()


def bienvenue():
    return charger(f"{PK}/protectos-bienvenue/root/usr/bin/protectos-bienvenue", "bv").Bienvenue()


def programmes():
    return charger(f"{PK}/protectos-programmes/root/usr/bin/protectos-programmes", "prg").Programmes()


def magasin():
    return charger(f"{PK}/protectos-programmes/root/usr/bin/protectos-magasin", "mag").Magasin()


APPLIS = [("magasin", magasin, (1100, 780)), ("parametres", parametres, (1100, 760)), ("a-propos", a_propos, (620, 640)),
          ("protection", protection, (900, 700)), ("parental", parental, (760, 640)),
          ("bienvenue", bienvenue, (1000, 700)), ("programmes", programmes, (900, 640))]


def main():
    sortie = sys.argv[1] if len(sys.argv) > 1 else "apercus"
    os.makedirs(sortie, exist_ok=True)
    sys.argv = [sys.argv[0]]
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setPalette(palette_depuis(f"{PK}/protectos-theme/root/usr/share/color-schemes/ProtectBleuOr.colors"))
    QIcon.setThemeSearchPaths([f"{PK}/protectos-theme/root/usr/share/icons", "/usr/share/icons"] + QIcon.themeSearchPaths())
    QIcon.setThemeName("ProtectOS")
    resultats = []
    for nom, fabrique, taille in APPLIS:
        try:
            w = fabrique()
            w.resize(*taille)
            w.show()
            for _ in range(20):
                app.processEvents()
            QTimer.singleShot(0, lambda: None)
            app.processEvents()
            img = w.grab()
            chemin = os.path.join(sortie, f"{nom}.png")
            img.save(chemin)
            buf = QBuffer()
            buf.open(QIODevice.OpenModeFlag.WriteOnly)
            img.scaledToWidth(min(1000, img.width())).save(buf, "JPG", 82)
            d = base64.b64encode(bytes(buf.data())).decode()
            print(f"APERCU-DEBUT {nom}")
            for i in range(0, len(d), 900):
                print(d[i:i + 900])
            print("APERCU-FIN", flush=True)
            w.close()
            resultats.append((nom, "ok"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            resultats.append((nom, f"ERREUR {e}"))
    for nom, r in resultats:
        print(f"{nom:12} {r}")
    return 1 if any(r != "ok" for _n, r in resultats) else 0


if __name__ == "__main__":
    sys.exit(main())
