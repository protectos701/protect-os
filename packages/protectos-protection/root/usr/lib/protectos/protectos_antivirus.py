"""Antivirus de protect.OS (moteur ClamAV) : analyse, quarantaine, surveillance.

Sans interface : utilisé par le Centre de protection, l'Installateur protect.OS et la
surveillance des téléchargements. Les menaces trouvées sont mises en quarantaine : le
fichier est déplacé dans un dossier privé et rendu non exécutable ; on peut le restaurer.
"""
import json
import os
import re
import shutil
import subprocess
import time

HOME = os.path.expanduser("~")
DATA = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(HOME, ".local", "share")), "protectos")
QUARANTAINE = os.path.join(DATA, "quarantaine")
QDB = os.path.join(QUARANTAINE, "index.json")
DB_DIR = "/var/lib/clamav"

# Types de fichiers surveillés à leur arrivée dans Téléchargements
RISQUES = (".exe", ".msi", ".bat", ".cmd", ".com", ".scr", ".pif", ".ps1", ".vbs", ".js", ".jse", ".wsf",
           ".jar", ".dll", ".lnk", ".zip", ".rar", ".7z", ".cab", ".iso", ".img",
           ".docm", ".xlsm", ".pptm", ".doc", ".xls", ".ppt", ".pdf", ".apk", ".sh", ".deb", ".appimage")


def available():
    return shutil.which("clamscan") is not None


def signatures_age_days(now=None):
    """Âge en jours de la base de signatures la plus récente (None si aucune base)."""
    now = now or time.time()
    try:
        files = [os.path.join(DB_DIR, f) for f in os.listdir(DB_DIR)
                 if re.match(r"(daily|main|bytecode)\.(cvd|cld)$", f)]
    except OSError:
        return None
    if not files:
        return None
    return (now - max(os.path.getmtime(f) for f in files)) / 86400


def ready():
    return available() and signatures_age_days() is not None


def user_dir(kind, fallbacks):
    try:
        out = subprocess.run(["xdg-user-dir", kind], capture_output=True, text=True).stdout.strip()
        if out and out != HOME and os.path.isdir(out):
            return out
    except OSError:
        pass
    for name in fallbacks:
        p = os.path.join(HOME, name)
        if os.path.isdir(p):
            return p
    return None


def downloads_dir():
    return user_dir("DOWNLOAD", ("Téléchargements", "Downloads"))


def quick_targets():
    return [p for p in (downloads_dir(), user_dir("DESKTOP", ("Bureau", "Desktop"))) if p]


def is_risky(path):
    return path.lower().endswith(RISQUES)


def scan_command(paths):
    return ["clamscan", "--recursive", "--infected", "--no-summary", "--stdout",
            "--max-filesize=200M", "--max-scansize=400M", "--exclude-dir=" + re.escape(QUARANTAINE), *paths]


def parse(output):
    """Menaces trouvées dans la sortie de clamscan : [(chemin, nom de la menace)]."""
    found = []
    for line in output.splitlines():
        m = re.match(r"^(.*): (.+) FOUND$", line.strip())
        if m:
            found.append((m.group(1), m.group(2)))
    return found


def scan(paths):
    """Analyse des fichiers/dossiers. Renvoie {"menaces": [...], "erreur": texte ou None}."""
    r = subprocess.run(scan_command(paths), capture_output=True, text=True)
    erreur = None
    if r.returncode == 2:
        erreur = (r.stderr.strip().splitlines() or ["erreur inconnue"])[-1]
    return {"menaces": parse(r.stdout), "erreur": erreur}


# ------------------------------------------------------------------ quarantaine
def _load():
    try:
        with open(QDB, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return []


def _save(items):
    os.makedirs(QUARANTAINE, mode=0o700, exist_ok=True)
    tmp = QDB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    os.replace(tmp, QDB)


def list_quarantine():
    return _load()


def quarantine(path, menace):
    """Déplace un fichier infecté en quarantaine. Renvoie l'entrée créée (ou None)."""
    if not os.path.isfile(path):
        return None
    os.makedirs(QUARANTAINE, mode=0o700, exist_ok=True)
    os.chmod(QUARANTAINE, 0o700)
    qid = f"{int(time.time() * 1000)}"
    dest = os.path.join(QUARANTAINE, f"{qid}.quarantaine")
    shutil.move(path, dest)
    os.chmod(dest, 0o400)
    entry = {"id": qid, "nom": os.path.basename(path), "origine": os.path.abspath(path),
             "menace": menace, "date": time.strftime("%Y-%m-%d %H:%M"), "fichier": dest}
    items = _load()
    items.append(entry)
    _save(items)
    return entry


def restore(qid):
    items = _load()
    for e in items:
        if e["id"] == qid:
            target = e["origine"]
            os.makedirs(os.path.dirname(target), exist_ok=True)
            base, ext = os.path.splitext(target)
            n = 2
            while os.path.exists(target):
                target = f"{base} ({n}){ext}"
                n += 1
            os.chmod(e["fichier"], 0o600)
            shutil.move(e["fichier"], target)
            _save([x for x in items if x["id"] != qid])
            return target
    return None


def delete(qid):
    items = _load()
    for e in items:
        if e["id"] == qid:
            try:
                os.chmod(e["fichier"], 0o600)
                os.remove(e["fichier"])
            except OSError:
                pass
    _save([x for x in items if x["id"] != qid])


def scan_and_quarantine(paths):
    """Analyse puis met chaque menace en quarantaine. Renvoie (menaces, erreur)."""
    res = scan(paths)
    out = []
    for path, menace in res["menaces"]:
        e = quarantine(path, menace)
        out.append({"nom": os.path.basename(path), "chemin": path, "menace": menace,
                    "quarantaine": e is not None})
    return out, res["erreur"]
