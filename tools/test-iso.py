#!/usr/bin/env python3
"""Démarre l'ISO de protect.OS dans une machine virtuelle sans écran, prend des captures
d'écran et vérifie que le bureau s'ouvre.

Usage :
  python3 tools/test-iso.py protect-os-amd64.hybrid.iso [-o captures] [--limite 600]

Dépendances (Debian/Ubuntu) : sudo apt install qemu-system-x86 xorriso python3-pil
Avec /dev/kvm (accélération matérielle), le test prend 3 à 5 minutes ; sans, beaucoup plus.

Résultat : des captures PNG, le journal de démarrage (serial.log) et resultat.json dans le
dossier de sortie. Code de sortie 0 si le bureau a démarré, 1 sinon.
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time

APPEND = ("boot=live components splash hostname=protectos username=protect "
          "locales=fr_FR.UTF-8 keyboard-layouts=fr timezone=Europe/Paris "
          "systemd.show_status=1 console=tty1 console=ttyS0,115200")
GRAPHICAL = re.compile(r"Graphical Interface|graphical\.target")
FATAL = re.compile(r"Kernel panic|Unable to find a medium containing a live file system|"
                   r"emergency mode|Failed to start .*Display Manager", re.I)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ------------------------------------------------------------------ ISO
def find_in_iso(iso, pattern):
    r = subprocess.run(["xorriso", "-indev", iso, "-find", "/live", "-name", pattern],
                       capture_output=True, text=True)
    paths = re.findall(r"'?(/live/[^'\s]+)'?", r.stdout)
    return sorted(set(paths), key=len)


def extract_boot_files(iso, dest):
    """Extrait le noyau et l'initrd de l'image d'essai."""
    files = {}
    for key, pattern in (("kernel", "vmlinuz*"), ("initrd", "initrd*")):
        found = find_in_iso(iso, pattern)
        if not found:
            sys.exit(f"Impossible de trouver {pattern} dans /live de l'ISO.")
        out = os.path.join(dest, os.path.basename(found[0]))
        subprocess.run(["xorriso", "-osirrox", "on", "-indev", iso, "-extract", found[0], out],
                       check=True, capture_output=True)
        files[key] = out
    return files


# ------------------------------------------------------------------ QEMU (protocole QMP)
class QMP:
    def __init__(self, path, timeout=60):
        end = time.time() + timeout
        while True:
            try:
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(path)
                break
            except OSError:
                if time.time() > end:
                    raise
                time.sleep(0.5)
        self.sock.settimeout(120)
        self.f = self.sock.makefile("rw", encoding="utf-8")
        self.f.readline()  # message d'accueil
        self.cmd("qmp_capabilities")

    def cmd(self, name, **args):
        msg = {"execute": name}
        if args:
            msg["arguments"] = args
        self.f.write(json.dumps(msg) + "\n")
        self.f.flush()
        while True:
            line = self.f.readline()
            if not line:
                raise ConnectionError("QEMU s'est arrêté")
            obj = json.loads(line)
            if "return" in obj:
                return obj["return"]
            if "error" in obj:
                raise RuntimeError(obj["error"].get("desc", str(obj["error"])))
            # les autres messages sont des événements : on les ignore

    def screenshot(self, png):
        try:
            self.cmd("screendump", filename=png, format="png")
            return png
        except RuntimeError:
            # QEMU ancien : seulement le format PPM
            ppm = png[:-4] + ".ppm"
            self.cmd("screendump", filename=ppm)
            try:
                from PIL import Image
                Image.open(ppm).save(png)
                os.remove(ppm)
                return png
            except Exception:
                return ppm


# ------------------------------------------------------------------ analyse d'image
def analyse(png):
    """Part de pixels noirs, dorés et bleus d'une capture."""
    try:
        from PIL import Image
    except ImportError:
        return {}
    im = Image.open(png).convert("RGB")
    im.thumbnail((320, 240))
    raw = im.tobytes()
    px = [tuple(raw[i:i + 3]) for i in range(0, len(raw), 3)]
    n = len(px) or 1
    noir = sum(1 for r, g, b in px if r + g + b < 40) / n
    or_ = sum(1 for r, g, b in px if r > 150 and g > 110 and b < 110 and r > b + 60) / n
    bleu = sum(1 for r, g, b in px if b > 70 and b > r + 25) / n
    return {"noir": round(noir, 3), "or": round(or_, 3), "bleu": round(bleu, 3)}


# ------------------------------------------------------------------ test
def touches(qmp, *noms, tenir=None):
    """Appuie sur une combinaison de touches (noms QEMU : meta_l, alt, tab, esc, e…)."""
    args = {"keys": [{"type": "qcode", "data": n} for n in noms]}
    if tenir:
        args["hold-time"] = tenir
    qmp.cmd("send-key", **args)


def clic(qmp, fx, fy, bouton="left"):
    """Clique à une position de l'écran (fractions de la largeur et de la hauteur)."""
    qmp.cmd("input-send-event", events=[
        {"type": "abs", "data": {"axis": "x", "value": int(fx * 32767)}},
        {"type": "abs", "data": {"axis": "y", "value": int(fy * 32767)}}])
    time.sleep(0.3)
    for bas in (True, False):
        qmp.cmd("input-send-event", events=[{"type": "btn", "data": {"down": bas, "button": bouton}}])
        time.sleep(0.1)


def visite(qmp, sortie):
    """Parcourt l'interface comme un utilisateur et capture chaque étape."""
    etapes = []

    def capture(nom, attente):
        time.sleep(attente)
        etapes.append((nom, qmp.screenshot(os.path.join(sortie, f"visite-{nom}.png"))))
        log(f"Capture : visite-{nom}.png")

    for nom, action, attente, apres in [
        ("menu-demarrer", lambda: touches(qmp, "meta_l"), 3, lambda: touches(qmp, "esc")),
        ("explorateur", lambda: touches(qmp, "meta_l", "e"), 7, None),
        ("alt-tab", lambda: touches(qmp, "alt", "tab", tenir=14000), 9, None),
        ("parametres", lambda: touches(qmp, "meta_l", "i"), 9, None),
    ]:
        try:
            action()
            capture(nom, attente)
            if apres:
                time.sleep(0.5)
                apres()
            time.sleep(9 if nom == "alt-tab" else 1.5)  # Alt+Tab : attendre que les touches soient relâchées
        except Exception as e:  # la visite est un bonus : elle ne fait jamais échouer le test
            log(f"Visite « {nom} » impossible : {e}")
    return etapes


def apercu(nom, png):
    """Écrit une capture réduite dans le journal (lisible sans télécharger les artefacts)."""
    try:
        import base64
        import io
        from PIL import Image
        b = io.BytesIO()
        Image.open(png).convert("RGB").resize((960, 540)).save(b, "JPEG", quality=80)
        d = base64.b64encode(b.getvalue()).decode()
        print(f"APERCU-DEBUT {nom}")
        for i in range(0, len(d), 900):
            print(d[i:i + 900])
        print("APERCU-FIN", flush=True)
    except Exception as e:
        print("Aperçu impossible :", e)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("iso")
    ap.add_argument("-o", "--sortie", default="captures")
    ap.add_argument("--limite", type=int, default=600, help="durée maximale en secondes (défaut 600)")
    ap.add_argument("--apres-bureau", type=int, default=75,
                    help="secondes d'attente après l'ouverture de la session graphique (défaut 75)")
    ap.add_argument("--qemu", default="qemu-system-x86_64")
    a = ap.parse_args()

    os.makedirs(a.sortie, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="protectos-test-")
    boot = extract_boot_files(a.iso, tmp)
    serial = os.path.join(a.sortie, "serial.log")
    qmp_path = os.path.join(tmp, "qmp.sock")
    kvm = os.access("/dev/kvm", os.R_OK | os.W_OK)
    cmd = [a.qemu, "-m", "4096", "-smp", "2",
           *(["-enable-kvm", "-cpu", "host"] if kvm else ["-cpu", "max"]),
           "-cdrom", a.iso, "-kernel", boot["kernel"], "-initrd", boot["initrd"], "-append", APPEND,
           "-vga", "virtio", "-display", "none", "-usb", "-device", "usb-tablet", "-serial", f"file:{serial}",
           "-qmp", f"unix:{qmp_path},server=on,wait=off", "-no-reboot"]
    log(f"Démarrage de la machine virtuelle ({'KVM' if kvm else 'sans accélération, ce sera lent'})")
    vm = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    qmp = QMP(qmp_path)

    start = time.time()
    shots, graphical_at, fatal = [], None, None
    etapes = []
    plan = [20, 45, 90]          # captures pendant le démarrage
    deadline = start + a.limite
    while time.time() < deadline and vm.poll() is None:
        t = time.time() - start
        try:
            text = open(serial, encoding="utf-8", errors="replace").read()
        except OSError:
            text = ""
        if graphical_at is None and GRAPHICAL.search(text):
            graphical_at = round(t)
            log(f"Session graphique atteinte en {graphical_at} s")
            plan = sorted({t + min(25, a.apres_bureau // 2), t + a.apres_bureau})
        m = FATAL.search(text)
        if m:
            fatal = m.group(0)
            log(f"Erreur au démarrage : {fatal}")
            shots.append(qmp.screenshot(os.path.join(a.sortie, f"erreur-{round(t):03d}s.png")))
            break
        if plan and t >= plan[0]:
            plan.pop(0)
            name = ("bureau" if graphical_at is not None else "demarrage") + f"-{round(t):03d}s.png"
            shots.append(qmp.screenshot(os.path.join(a.sortie, name)))
            log(f"Capture : {name}")
            if graphical_at is not None and not plan:
                break
        time.sleep(2)

    # Capture finale, puis arrêt
    if vm.poll() is None:
        final = qmp.screenshot(os.path.join(a.sortie, "final.png"))
        shots.append(final)
        etapes = visite(qmp, a.sortie) if graphical_at is not None else []
        try:
            qmp.cmd("quit")
        except Exception:
            pass
    try:
        vm.wait(timeout=30)
    except subprocess.TimeoutExpired:
        vm.kill()
    shutil.rmtree(tmp, ignore_errors=True)

    last = analyse(shots[-1]) if shots and shots[-1].endswith(".png") else {}
    # Aperçus dans le journal : bureau, puis chaque étape de la visite
    if shots and shots[-1].endswith(".png") and os.path.exists(shots[-1]):
        apercu("bureau", shots[-1])
    for nom, png in etapes:
        if png and png.endswith(".png") and os.path.exists(png):
            apercu(nom, png)
    ok = graphical_at is not None and fatal is None and last.get("noir", 0) < 0.9
    result = {
        "bureau_demarre": ok,
        "session_graphique_en_secondes": graphical_at,
        "erreur": fatal,
        "kvm": kvm,
        "captures": [os.path.basename(s) for s in shots],
        "derniere_capture": last,
    }
    with open(os.path.join(a.sortie, "resultat.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    verdict = ("✅ protect.OS démarre jusqu'au bureau" if ok else "❌ protect.OS n'a pas atteint le bureau")
    detail = (f"Session graphique en {graphical_at} s. " if graphical_at else "") + \
             (f"Erreur : {fatal}. " if fatal else "") + \
             (f"Dernière capture : {round(last.get('bleu', 0) * 100)} % de bleu, "
              f"{round(last.get('or', 0) * 100)} % d'or, {round(last.get('noir', 0) * 100)} % de noir."
              if last else "")
    log(f"{verdict}. {detail}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(f"## {verdict}\n\n{detail}\n\nCaptures : {', '.join(result['captures'])} "
                    "(artefact « captures-ecran »).\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
