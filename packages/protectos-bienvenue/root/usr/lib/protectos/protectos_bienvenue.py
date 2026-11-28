"""Moteur de « Bienvenue dans protect.OS » (sans interface : testable seul)."""
import os
import re
import shutil
import subprocess

HOME = os.path.expanduser("~")
CONFIG = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config")), "protectos")
DONE_FLAG = os.path.join(CONFIG, "bienvenue-fait")
ROOT_HELPER = "/usr/lib/protectos/protectos-bienvenue-root"

SCHEMES = {"sombre": ("ProtectBleuOr", "ProtectOS"), "clair": ("ProtectBleuOrClair", "ProtectOS-Clair")}

# Applications proposées : (paquets Debian, nom, description, icône).
# La liste des paquets autorisés est répétée dans protectos-bienvenue-root (sécurité).
APPS = [
    (["steam-installer"], "Steam", "Jeux PC, dont beaucoup de jeux Windows grâce à Proton", "steam"),
    (["gimp"], "GIMP", "Retouche photo", "gimp"),
    (["krita"], "Krita", "Dessin et peinture numérique", "krita"),
    (["inkscape"], "Inkscape", "Dessin vectoriel, logos, affiches", "inkscape"),
    (["kdenlive"], "Kdenlive", "Montage vidéo", "kdenlive"),
    (["obs-studio"], "OBS Studio", "Enregistrer l'écran, diffuser en direct", "com.obsproject.Studio"),
    (["audacity"], "Audacity", "Enregistrer et retoucher du son", "audacity"),
    (["thunderbird", "thunderbird-l10n-fr"], "Thunderbird", "Courriel et agenda", "thunderbird"),
]


def is_live():
    try:
        return "boot=live" in open("/proc/cmdline").read().split()
    except OSError:
        return False


def first_run_done():
    return os.path.exists(DONE_FLAG)


def set_show_at_login(show):
    os.makedirs(CONFIG, exist_ok=True)
    if show:
        if os.path.exists(DONE_FLAG):
            os.remove(DONE_FLAG)
    else:
        open(DONE_FLAG, "w").close()


def os_release():
    info = {"PRETTY_NAME": "protect.OS", "VERSION_ID": ""}
    try:
        for line in open("/etc/os-release", encoding="utf-8"):
            m = re.match(r'(\w+)="?([^"\n]*)"?', line)
            if m:
                info[m.group(1)] = m.group(2)
    except OSError:
        pass
    return info


def parse_gpus(lspci_output):
    """Cartes graphiques trouvées dans la sortie de « lspci -nn »."""
    gpus = []
    for line in lspci_output.splitlines():
        if re.search(r"\[(0300|0302|0380)\]", line):
            name = re.sub(r"^\S+\s+[^:]+\[\w{4}\]:\s*", "", line)
            name = re.sub(r"\s*\[[0-9a-f]{4}:[0-9a-f]{4}\].*$", "", name)
            low = name.lower()
            vendor = "nvidia" if "nvidia" in low else "amd" if ("amd" in low or "ati " in low or "radeon" in low) \
                else "intel" if "intel" in low else "autre"
            gpus.append({"nom": name.strip(), "marque": vendor})
    return gpus


def detect_gpus():
    try:
        out = subprocess.run(["lspci", "-nn"], capture_output=True, text=True).stdout
    except OSError:
        return []
    return parse_gpus(out)


def package_installed(name):
    try:
        r = subprocess.run(["dpkg-query", "-W", "-f=${Status}", name], capture_output=True, text=True)
        return "install ok installed" in r.stdout
    except OSError:
        return False


def flathub_enabled():
    """Vrai si le catalogue Flathub est déjà disponible dans Discover."""
    if not shutil.which("flatpak"):
        return False
    try:
        out = subprocess.run(["flatpak", "remotes", "--system", "--columns=name"],
                             capture_output=True, text=True).stdout
        return "flathub" in out.split()
    except OSError:
        return False


def nvidia_installed():
    return package_installed("nvidia-driver")


def secure_boot_enabled():
    try:
        r = subprocess.run(["mokutil", "--sb-state"], capture_output=True, text=True)
        return "enabled" in r.stdout.lower()
    except OSError:
        return False


def apply_scheme(mode):
    """Applique le thème clair ou sombre (couleurs + icônes assorties)."""
    scheme, icons = SCHEMES[mode]
    if shutil.which("plasma-apply-colorscheme"):
        subprocess.run(["plasma-apply-colorscheme", scheme], capture_output=True)
    for tool in ("plasma-changeicons", "/usr/lib/x86_64-linux-gnu/libexec/plasma-changeicons",
                 "/usr/libexec/plasma-changeicons"):
        path = shutil.which(tool) or (tool if os.path.isfile(tool) else None)
        if path:
            subprocess.run([path, icons], capture_output=True)
            break
    # Barres de titre assorties
    subprocess.run(["kwriteconfig6", "--file", "kwinrc", "--group", "org.kde.kdecoration2", "--key", "theme",
                    "__aurorae__svg__protectos" + ("-clair" if mode == "clair" else "")], capture_output=True)
    subprocess.run(["gdbus", "call", "--session", "--dest", "org.kde.KWin", "--object-path", "/KWin",
                    "--method", "org.kde.KWin.reconfigure"], capture_output=True)


def current_scheme():
    path = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config")), "kdeglobals")
    try:
        txt = open(path, encoding="utf-8").read()
        m = re.search(r"^ColorScheme=(.*)$", txt, re.M)
        if m:
            return "clair" if m.group(1).strip() == "ProtectBleuOrClair" else "sombre"
    except OSError:
        pass
    return "sombre"
