#!/usr/bin/python3
"""Démarre l'ISO comme un vrai PC UEFI (firmware → menu → écran protect.OS → bureau) et capture l'écran
toutes les 2 secondes. Les captures sont assemblées en une planche, écrite dans le journal (base64).

  python3 tools/demarrage-reel.py protect-os.iso [dossier]
"""
import base64
import io
import json
import os
import socket
import subprocess
import sys
import time

from PIL import Image, ImageDraw


class Qmp:
    def __init__(self, chemin):
        for _ in range(100):
            try:
                self.s = socket.socket(socket.AF_UNIX)
                self.s.connect(chemin)
                break
            except OSError:
                time.sleep(0.1)
        self.f = self.s.makefile("rw")
        self.f.readline()
        self.cmd("qmp_capabilities")

    def cmd(self, nom, **args):
        self.f.write(json.dumps({"execute": nom, "arguments": args}) + "\n")
        self.f.flush()
        while True:
            r = json.loads(self.f.readline())
            if "return" in r or "error" in r:
                return r


def main():
    iso = sys.argv[1]
    sortie = sys.argv[2] if len(sys.argv) > 2 else "demarrage"
    os.makedirs(sortie, exist_ok=True)
    ovmf = next((p for p in ("/usr/share/ovmf/OVMF.fd", "/usr/share/OVMF/OVMF_CODE.fd", "/usr/share/qemu/OVMF.fd")
                 if os.path.exists(p)), None)
    if not ovmf:
        print("Firmware UEFI (OVMF) introuvable : test ignoré")
        return 0
    qmp_sock = os.path.join(sortie, "qmp.sock")
    kvm = ["-enable-kvm", "-cpu", "host"] if os.access("/dev/kvm", os.W_OK) else []
    vm = subprocess.Popen(["qemu-system-x86_64", *kvm, "-m", "4096", "-smp", "2", "-bios", ovmf,
                           "-cdrom", iso, "-vga", "virtio", "-display", "none", "-usb", "-device", "usb-tablet",
                           "-qmp", f"unix:{qmp_sock},server,nowait"])
    try:
        qmp = Qmp(qmp_sock)
        images = []
        for k in range(26):
            t = 2 * k
            chemin = os.path.join(sortie, f"t{t:02d}.ppm")
            qmp.cmd("screendump", filename=os.path.abspath(chemin))
            time.sleep(0.3)
            try:
                images.append((t, Image.open(chemin).convert("RGB")))
            except Exception:
                pass
            time.sleep(1.7)
        # Planche : 6 colonnes de vignettes 320×200, avec le temps écoulé
        col, w, h = 6, 320, 200
        lignes = (len(images) + col - 1) // col
        planche = Image.new("RGB", (col * w, lignes * (h + 22)), (0, 0, 0))
        d = ImageDraw.Draw(planche)
        for i, (t, im) in enumerate(images):
            x, y = (i % col) * w, (i // col) * (h + 22)
            planche.paste(im.resize((w, h)), (x, y + 22))
            d.text((x + 6, y + 4), f"{t} s", fill=(243, 210, 122))
        planche.save(os.path.join(sortie, "planche.png"))
        b = io.BytesIO()
        planche.save(b, "JPEG", quality=78)
        donnees = base64.b64encode(b.getvalue()).decode()
        print("APERCU-DEBUT demarrage-reel")
        for i in range(0, len(donnees), 900):
            print(donnees[i:i + 900])
        print("APERCU-FIN", flush=True)
    finally:
        vm.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
