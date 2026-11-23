"""Moteur commun de l'installateur et des « Programmes et fonctionnalités » de protect.OS.

Reproduit la façon dont Windows gère les programmes, avec Wine :
- un disque C: par utilisateur (le « préfixe » Wine, ~/.wine par défaut) ;
- la liste des programmes installés lue dans les mêmes clés de registre que Windows
  (...\\CurrentVersion\\Uninstall), avec les mêmes règles d'affichage ;
- la désinstallation par la commande enregistrée par le programme lui-même.

S'y ajoutent les programmes Windows « portables » (un simple .exe) et les applications
protect.OS empaquetées avec protectos-pack (section Debian « protectos »).
Ce module n'utilise pas Qt : il est testable seul.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import time

HOME = os.path.expanduser("~")
DATA = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share")), "protectos")
PORTABLES_DB = os.path.join(DATA, "portables.json")
APPS_DIR = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share")), "applications")
ICONS_DIR = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share")), "icons", "hicolor", "256x256", "apps")

WINDOWS_EXT = (".exe", ".msi", ".bat", ".com")
UNINSTALL_PATHS = (
    r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\",
    r"Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\",
)


# ---------------------------------------------------------------- environnement Windows

def prefix():
    """Dossier du « PC Windows » de l'utilisateur (contient drive_c)."""
    return os.environ.get("WINEPREFIX") or os.path.join(HOME, ".wine")


def drive_c():
    return os.path.join(prefix(), "drive_c")


def prefix_ready():
    return os.path.isfile(os.path.join(prefix(), "system.reg"))


def wine_env():
    env = dict(os.environ)
    env.setdefault("WINEPREFIX", prefix())
    env.setdefault("WINEDEBUG", "-all")
    return env


def wine_available():
    return shutil.which("wine") is not None


def wineserver():
    """Chemin de wineserver (Debian le range parfois hors du PATH)."""
    for c in ("wineserver", "/usr/lib/wine/wineserver64", "/usr/lib/wine/wineserver32",
              "/usr/lib/wine/wineserver"):
        p = shutil.which(c) or (c if os.path.isfile(c) else None)
        if p:
            return p
    return "wineserver"


def support_32bits():
    """Vrai si la partie 32 bits de Wine est installée (nécessaire à beaucoup de programmes)."""
    try:
        r = subprocess.run(["dpkg-query", "-W", "-f=${Status}", "wine32:i386"],
                           capture_output=True, text=True)
        return "install ok installed" in r.stdout
    except OSError:
        return False


def kind_of(path):
    """Type d'un fichier à installer : 'windows', 'msi', 'deb' ou None."""
    low = path.lower()
    if low.endswith(".msi"):
        return "msi"
    if low.endswith(WINDOWS_EXT):
        return "windows"
    if low.endswith(".deb"):
        return "deb"
    try:
        with open(path, "rb") as f:
            head = f.read(8)
        if head[:2] == b"MZ":
            return "windows"
        if head == b"!<arch>\n":
            return "deb"
    except OSError:
        pass
    return None


def install_command(path):
    """Commande qui lance l'installation, comme un double-clic sous Windows."""
    k = kind_of(path)
    if k == "msi":
        return ["wine", "msiexec", "/i", path]
    if k == "windows":
        return ["wine", path]
    if k == "deb":
        return ["pkexec", "apt-get", "install", "-y", "--no-install-recommends", os.path.abspath(path)]
    raise ValueError("type de fichier non pris en charge")


# ---------------------------------------------------------------- registre Windows

def _unescape(s):
    """Décode une chaîne du registre Wine ("\\\\", "\\"", "\\n", "\\x00e9"…)."""
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            n = s[i + 1]
            if n == "x":
                m = re.match(r"[0-9a-fA-F]{1,4}", s[i + 2:])
                if m:
                    out.append(chr(int(m.group(0), 16)))
                    i += 2 + len(m.group(0))
                    continue
            out.append({"n": "\n", "t": "\t", "r": "\r", "0": "\0"}.get(n, n))
            i += 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def parse_reg(path):
    """Lit un fichier de registre Wine (system.reg / user.reg) : {clé: {valeur: donnée}}."""
    keys, cur = {}, None
    try:
        f = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return keys
    with f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("["):
                m = re.match(r"\[(.*)\]", line)
                cur = keys.setdefault(m.group(1), {}) if m else None
            elif cur is not None and line.startswith('"'):
                m = re.match(r'"((?:[^"\\]|\\.)*)"=(.*)$', line)
                if not m:
                    continue
                name, raw = _unescape(m.group(1)), m.group(2)
                if raw.startswith('"') and raw.endswith('"'):
                    cur[name] = _unescape(raw[1:-1])
                elif raw.startswith("str(2):"):
                    cur[name] = _unescape(raw[8:-1])
                elif raw.startswith("dword:"):
                    cur[name] = int(raw[6:], 16)
                else:
                    cur[name] = raw
    return keys


def windows_programs():
    """Programmes Windows installés, avec les règles de « Programmes et fonctionnalités » :
    une clé Uninstall avec un DisplayName, ni SystemComponent=1, ni rattachée à un parent."""
    if not prefix_ready():
        return []
    found = {}
    for regfile in ("system.reg", "user.reg"):
        for key, vals in parse_reg(os.path.join(prefix(), regfile)).items():
            for base in UNINSTALL_PATHS:
                if key.startswith(base) and "\\\\" not in key[len(base):]:
                    sub = key[len(base):].replace("\\\\", "\\")
                    name = vals.get("DisplayName")
                    if not name or vals.get("SystemComponent") == 1 or vals.get("ParentKeyName"):
                        continue
                    if not (vals.get("UninstallString") or vals.get("WindowsInstaller") == 1):
                        continue
                    found[sub] = {
                        "type": "windows", "id": sub, "nom": name,
                        "editeur": vals.get("Publisher", ""),
                        "version": vals.get("DisplayVersion", ""),
                        "icone": vals.get("DisplayIcon", ""),
                    }
    return sorted(found.values(), key=lambda p: p["nom"].lower())


def uninstall_windows_command(key):
    return ["wine", "uninstaller", "--remove", key]


# ---------------------------------------------------------------- informations d'un .exe

def exe_info(path):
    """Nom du produit, éditeur et version d'un .exe (si python3-pefile est installé)."""
    info = {"nom": "", "editeur": "", "version": "", "description": ""}
    try:
        import pefile  # facultatif
        pe = pefile.PE(path, fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
        for fi in getattr(pe, "FileInfo", []) or []:
            for entry in fi:
                for st in getattr(entry, "StringTable", []) or []:
                    t = {k.decode(errors="ignore"): v.decode(errors="ignore") for k, v in st.entries.items()}
                    info["nom"] = info["nom"] or t.get("ProductName", "")
                    info["editeur"] = info["editeur"] or t.get("CompanyName", "")
                    info["version"] = info["version"] or t.get("ProductVersion", "") or t.get("FileVersion", "")
                    info["description"] = info["description"] or t.get("FileDescription", "")
    except Exception:
        pass
    if not info["nom"]:
        info["nom"] = info["description"] or os.path.splitext(os.path.basename(path))[0]
    return info


def extract_icon(exe, dest_png):
    """Extrait la plus grande icône d'un .exe (outils wrestool/icotool du paquet icoutils)."""
    if not (shutil.which("wrestool") and shutil.which("icotool")):
        return False
    with tempfile.TemporaryDirectory() as tmp:
        ico = os.path.join(tmp, "icone.ico")
        r = subprocess.run(["wrestool", "-x", "-t", "14", "-o", ico, exe], capture_output=True)
        if r.returncode != 0 or not os.path.isfile(ico):
            return False
        subprocess.run(["icotool", "-x", "-o", tmp, ico], capture_output=True)
        pngs = [os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".png")]
        if not pngs:
            return False
        def score(p):
            m = re.search(r"_(\d+)x(\d+)x(\d+)\.png$", p)
            return (int(m.group(1)), int(m.group(3))) if m else (0, 0)
        os.makedirs(os.path.dirname(dest_png), exist_ok=True)
        shutil.copy(max(pngs, key=score), dest_png)
        return True


def deb_info(path):
    info = {"nom": os.path.basename(path), "editeur": "", "version": "", "description": "", "paquet": ""}
    try:
        out = subprocess.run(["dpkg-deb", "-f", path, "Package", "Version", "Maintainer", "Description"],
                             capture_output=True, text=True, check=True).stdout
        f = dict(re.findall(r"^(\w+): (.*)$", out, re.M))
        info.update(paquet=f.get("Package", ""), nom=f.get("Description", f.get("Package", "")),
                    version=f.get("Version", ""), editeur=re.sub(r"\s*<.*>", "", f.get("Maintainer", "")))
    except (OSError, subprocess.CalledProcessError):
        pass
    return info


# ---------------------------------------------------------------- composants Windows

# Briques que beaucoup de programmes Windows attendent (installées avec winetricks).
COMPONENTS = [
    ("dotnet48", ".NET Framework 4.8", "Pour les programmes créés avec .NET (beaucoup d'utilitaires)"),
    ("vcrun2022", "Visual C++ 2015-2022", "Bibliothèques utilisées par la plupart des programmes récents"),
    ("d3dx9", "DirectX 9", "Pour les jeux et logiciels 3D plus anciens"),
    ("corefonts", "Polices Windows", "Arial, Times New Roman, Verdana… pour un affichage fidèle"),
]
COMPONENT_NAMES = {verb: name for verb, name, _ in COMPONENTS}

# Indices cherchés dans le fichier : nom de DLL → composant
_HINTS = [
    (re.compile(rb"vcruntime140|msvcp140|vcomp140|concrt140", re.I), "vcrun2022"),
    (re.compile(rb"d3dx9_\d\d\.dll", re.I), "d3dx9"),
    (re.compile(rb"mscoree\.dll", re.I), "dotnet48"),
]


def is_dotnet(path):
    """Vrai si le .exe est un programme .NET (en-tête PE avec un répertoire CLR non vide)."""
    import struct
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
    except OSError:
        return False
    if head[:2] != b"MZ" or len(head) < 64:
        return False
    pe = struct.unpack_from("<I", head, 0x3C)[0]
    if pe + 24 > len(head) or head[pe:pe + 4] != b"PE\0\0":
        return False
    opt = pe + 24
    magic = struct.unpack_from("<H", head, opt)[0]
    if magic == 0x10B:      # PE32
        count_off, dirs = opt + 92, opt + 96
    elif magic == 0x20B:    # PE32+ (64 bits)
        count_off, dirs = opt + 108, opt + 112
    else:
        return False
    if dirs + 15 * 8 > len(head):
        return False
    count = struct.unpack_from("<I", head, count_off)[0]
    if count <= 14:
        return False
    rva, size = struct.unpack_from("<II", head, dirs + 14 * 8)
    return rva != 0 and size != 0


def needed_components(path, limit=64 * 1024 * 1024):
    """Composants dont le programme semble avoir besoin (lecture des 64 premiers Mo)."""
    found = set()
    if is_dotnet(path):
        found.add("dotnet48")
    try:
        with open(path, "rb") as f:
            tail, read = b"", 0
            while read < limit and len(found) < len(_HINTS):
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                read += len(chunk)
                data = tail + chunk
                for rx, verb in _HINTS:
                    if verb not in found and rx.search(data):
                        found.add(verb)
                tail = chunk[-32:]
    except OSError:
        pass
    return [verb for verb, _, _ in COMPONENTS if verb in found]


def installed_components():
    try:
        with open(os.path.join(prefix(), "winetricks.log"), encoding="utf-8", errors="replace") as f:
            return {line.strip() for line in f if line.strip()}
    except OSError:
        return set()


def missing_components(path):
    have = installed_components()
    return [v for v in needed_components(path) if v not in have]


def winetricks_available():
    return shutil.which("winetricks") is not None


def winetricks_command(verbs):
    return ["winetricks", "--unattended"] + list(verbs)


# ---------------------------------------------------------------- programmes portables

def _slug(text):
    import unicodedata
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return s or "programme"


def load_portables():
    try:
        with open(PORTABLES_DB, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def _save_portables(items):
    os.makedirs(DATA, exist_ok=True)
    tmp = PORTABLES_DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, PORTABLES_DB)


def add_portable(exe, nom, editeur="", version=""):
    """Range un .exe portable dans C:\\Program Files\\<nom> et l'ajoute au menu Démarrer."""
    items = load_portables()
    pid = _slug(nom)
    base = pid
    n = 2
    while any(p["id"] == pid for p in items):
        pid = f"{base}-{n}"
        n += 1
    folder = os.path.join(drive_c(), "Program Files", nom if n == 2 else f"{nom} ({n - 1})")
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, os.path.basename(exe))
    if os.path.abspath(exe) != os.path.abspath(target):
        shutil.copy2(exe, target)
    icon = os.path.join(ICONS_DIR, f"protectos-win-{pid}.png")
    icon_name = f"protectos-win-{pid}" if extract_icon(target, icon) else "wine"
    desktop = os.path.join(APPS_DIR, f"protectos-win-{pid}.desktop")
    os.makedirs(APPS_DIR, exist_ok=True)
    with open(desktop, "w", encoding="utf-8") as f:
        f.write("[Desktop Entry]\nType=Application\n"
                f"Name={nom}\nComment=Programme Windows\n"
                f"Exec=env WINEDEBUG=-all wine \"{target}\"\n"
                f"Path={folder}\nIcon={icon_name}\nCategories=Wine;\n")
    os.chmod(desktop, 0o755)
    entry = {"type": "portable", "id": pid, "nom": nom, "editeur": editeur, "version": version,
             "dossier": folder, "desktop": desktop, "icone": icon if icon_name != "wine" else "",
             "ajoute": time.strftime("%Y-%m-%d")}
    items.append(entry)
    _save_portables(items)
    return entry


def remove_portable(pid):
    items = load_portables()
    keep = []
    for p in items:
        if p["id"] != pid:
            keep.append(p)
            continue
        for path in (p.get("desktop"), p.get("icone")):
            if path and os.path.isfile(path):
                os.remove(path)
        folder = p.get("dossier", "")
        # Sécurité : on ne supprime qu'un dossier situé dans le disque C:
        if folder and os.path.realpath(folder).startswith(os.path.realpath(drive_c()) + os.sep):
            shutil.rmtree(folder, ignore_errors=True)
    _save_portables(keep)


# ---------------------------------------------------------------- applications protect.OS (.deb)

def protectos_apps():
    """Applications empaquetées avec protectos-pack (section Debian « protectos »)."""
    try:
        out = subprocess.run(
            ["dpkg-query", "-W", "-f=${Package}\t${Version}\t${Section}\t${db:Status-Abbrev}\t${Maintainer}\t${binary:Summary}\n"],
            capture_output=True, text=True).stdout
    except OSError:
        return []
    apps = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 6 or parts[2] != "protectos" or not parts[3].startswith("ii"):
            continue
        apps.append({"type": "protectos", "id": parts[0], "nom": parts[5] or parts[0],
                     "version": parts[1], "editeur": re.sub(r"\s*<.*>", "", parts[4])})
    return sorted(apps, key=lambda p: p["nom"].lower())


def uninstall_protectos_command(package):
    return ["pkexec", "apt-get", "remove", "-y", package]


def all_programs():
    return windows_programs() + load_portables() + protectos_apps()


def refresh_menu():
    """Demande à Plasma de relire les raccourcis du menu Démarrer."""
    for tool in ("kbuildsycoca6", "kbuildsycoca5"):
        if shutil.which(tool):
            subprocess.Popen([tool], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
