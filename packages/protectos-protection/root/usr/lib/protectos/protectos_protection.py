"""Moteur du Centre de protection de protect.OS (sans interface : testable seul).

Chaque vérification renvoie un dict :
  id, titre, etat ("ok" | "attention" | "risque" | "info"), detail, action (texte du bouton ou ""),
  et la façon de corriger : "root:<action>" (via pkexec), "user:<fonction>" ou "lancer:<commande>".
"""
import json
import os
import re
import shutil
import subprocess
import time

HOME = os.path.expanduser("~")
CONFIG = os.environ.get("XDG_CONFIG_HOME", os.path.join(HOME, ".config"))
UFW_CONF = "/etc/ufw/ufw.conf"
TIMESHIFT_JSON = "/etc/timeshift/timeshift.json"
UPDATE_STAMP = "/var/lib/apt/periodic/update-success-stamp"
KSCREEN = os.path.join(CONFIG, "kscreenlockerrc")
ROOT_HELPER = "/usr/lib/protectos/protectos-protection-root"


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None


def installed(pkg):
    r = _run(["dpkg-query", "-W", "-f=${Status}", pkg])
    return bool(r) and "install ok installed" in r.stdout


def _ini(path, group, key):
    """Lit une valeur dans un fichier de réglages KDE (format INI)."""
    try:
        cur = None
        for line in open(path, encoding="utf-8", errors="replace"):
            line = line.strip()
            if line.startswith("["):
                cur = line.strip("[]")
            elif cur == group and line.split("=", 1)[0].strip() == key:
                return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return None


# ------------------------------------------------------------------ vérifications
def check_firewall():
    base = {"id": "pare-feu", "titre": "Pare-feu"}
    if not installed("ufw") and not os.path.exists(UFW_CONF):
        return {**base, "etat": "risque", "detail": "Aucun pare-feu n'est installé.",
                "action": "Installer et activer", "corriger": "root:pare-feu"}
    try:
        enabled = re.search(r"^ENABLED=yes", open(UFW_CONF).read(), re.M) is not None
    except OSError:
        enabled = False
    if enabled:
        return {**base, "etat": "ok", "detail": "Actif : les connexions entrantes non sollicitées sont bloquées.",
                "action": "Réglages", "corriger": "lancer:systemsettings kcm_firewall"}
    return {**base, "etat": "risque", "detail": "Le pare-feu est désactivé.",
            "action": "Activer", "corriger": "root:pare-feu"}


def check_updates(now=None):
    base = {"id": "mises-a-jour", "titre": "Mises à jour de sécurité"}
    now = now or time.time()
    auto = False
    r = _run(["apt-config", "dump"])
    if r:
        auto = re.search(r'APT::Periodic::Unattended-Upgrade "1"', r.stdout) is not None
    if not (installed("unattended-upgrades") and auto):
        return {**base, "etat": "risque", "detail": "Les correctifs de sécurité ne s'installent pas automatiquement.",
                "action": "Activer", "corriger": "root:mises-a-jour"}
    try:
        age_days = (now - os.path.getmtime(UPDATE_STAMP)) / 86400
    except OSError:
        age_days = None
    if age_days is not None and age_days > 7:
        return {**base, "etat": "attention",
                "detail": f"Automatiques, mais la dernière vérification date de {int(age_days)} jours "
                          "(ordinateur hors ligne ?).",
                "action": "Vérifier maintenant", "corriger": "lancer:plasma-discover --mode update"}
    pending = 0
    r = _run(["apt", "list", "--upgradable"])
    if r:
        pending = sum(1 for line in r.stdout.splitlines() if "/" in line and "[" in line)
    if pending:
        return {**base, "etat": "attention",
                "detail": f"Automatiques. {pending} autre{'s' if pending > 1 else ''} mise{'s' if pending > 1 else ''} "
                          f"à jour {'attendent' if pending > 1 else 'attend'} dans Discover.",
                "action": "Ouvrir Discover", "corriger": "lancer:plasma-discover --mode update"}
    return {**base, "etat": "ok", "detail": "Automatiques : les correctifs s'installent chaque jour.",
            "action": "", "corriger": ""}


def check_backups():
    base = {"id": "sauvegardes", "titre": "Sauvegardes du système"}
    if not installed("timeshift"):
        return {**base, "etat": "attention", "detail": "Aucun outil de sauvegarde n'est installé.",
                "action": "Installer Timeshift", "corriger": "root:sauvegardes"}
    try:
        cfg = json.load(open(TIMESHIFT_JSON))
    except (OSError, ValueError):
        cfg = {}
    scheduled = any(str(cfg.get(k, "false")).lower() == "true"
                    for k in ("schedule_monthly", "schedule_weekly", "schedule_daily", "schedule_hourly", "schedule_boot"))
    if scheduled:
        return {**base, "etat": "ok", "detail": "Des sauvegardes automatiques sont programmées.",
                "action": "Ouvrir Timeshift", "corriger": "lancer:timeshift-launcher"}
    return {**base, "etat": "attention", "detail": "Timeshift est installé, mais aucune sauvegarde n'est programmée.",
            "action": "Configurer", "corriger": "lancer:timeshift-launcher"}


def root_is_encrypted():
    r = _run(["findmnt", "-no", "SOURCE", "/"])
    if not r or not r.stdout.strip():
        return None
    src = r.stdout.strip().split("[")[0]
    r = _run(["lsblk", "-s", "-no", "TYPE", src])
    if not r:
        return None
    return "crypt" in r.stdout.split()


def check_encryption():
    base = {"id": "chiffrement", "titre": "Chiffrement du disque"}
    enc = root_is_encrypted()
    if enc:
        return {**base, "etat": "ok", "detail": "Le disque est chiffré : vos fichiers sont illisibles sans votre mot de passe.",
                "action": "", "corriger": ""}
    if enc is None:
        return {**base, "etat": "info", "detail": "Impossible de déterminer si le disque est chiffré.",
                "action": "", "corriger": ""}
    return {**base, "etat": "attention",
            "detail": "Le disque n'est pas chiffré : en cas de vol de l'ordinateur, vos fichiers seraient lisibles. "
                      "Le chiffrement se choisit à l'installation (case « Chiffrer le système »).",
            "action": "", "corriger": ""}


def check_secure_boot():
    base = {"id": "secure-boot", "titre": "Démarrage sécurisé"}
    if not os.path.isdir("/sys/firmware/efi"):
        return {**base, "etat": "info", "detail": "Ordinateur en mode BIOS ancien : le démarrage sécurisé n'existe pas ici.",
                "action": "", "corriger": ""}
    r = _run(["mokutil", "--sb-state"])
    if r and "enabled" in r.stdout.lower():
        return {**base, "etat": "ok", "detail": "Actif : seul un système de démarrage signé peut se lancer.",
                "action": "", "corriger": ""}
    if r and "disabled" in r.stdout.lower():
        return {**base, "etat": "attention",
                "detail": "Désactivé. Vous pouvez l'activer dans les réglages du BIOS/UEFI de l'ordinateur "
                          "(protect.OS le prend en charge).", "action": "", "corriger": ""}
    return {**base, "etat": "info", "detail": "État inconnu (outil mokutil absent).", "action": "", "corriger": ""}


def check_screen_lock():
    base = {"id": "verrouillage", "titre": "Verrouillage de l'écran"}
    autolock = (_ini(KSCREEN, "Daemon", "Autolock") or "true").lower() != "false"
    on_resume = (_ini(KSCREEN, "Daemon", "LockOnResume") or "true").lower() != "false"
    if autolock and on_resume:
        return {**base, "etat": "ok", "detail": "L'écran se verrouille en cas d'absence et au réveil.",
                "action": "", "corriger": ""}
    return {**base, "etat": "attention",
            "detail": "L'écran ne se verrouille pas automatiquement : quelqu'un pourrait utiliser votre session.",
            "action": "Activer", "corriger": "user:enable_screen_lock"}


def check_antivirus():
    import protectos_antivirus as av
    base = {"id": "antivirus", "titre": "Antivirus"}
    if not av.available():
        return {**base, "etat": "attention",
                "detail": "Aucun antivirus installé. Utile surtout pour les fichiers Windows et les clés USB.",
                "action": "Installer l'antivirus", "corriger": "root:antivirus"}
    age = av.signatures_age_days()
    q = len(av.list_quarantine())
    quar = f" {q} fichier{'s' if q > 1 else ''} en quarantaine." if q else ""
    if age is None:
        return {**base, "etat": "attention",
                "detail": "Installé, mais les signatures de virus ne sont pas encore téléchargées "
                          "(il faut une connexion Internet)." + quar,
                "action": "Télécharger", "corriger": "root:antivirus"}
    if age > 3:
        return {**base, "etat": "attention",
                "detail": f"Les signatures de virus datent de {int(age)} jours." + quar,
                "action": "Mettre à jour", "corriger": "root:antivirus"}
    return {**base, "etat": "ok",
            "detail": "Actif : signatures à jour, téléchargements surveillés, programmes Windows analysés "
                      "avant installation." + quar,
            "action": "Analyser…", "corriger": "ui:analyse"}


def check_privacy():
    base = {"id": "vie-privee", "titre": "Vie privée"}
    r = _run(["/usr/lib/protectos/protectos-bloqueur", "etat"])
    etat = r.stdout.strip() if r else ""
    firefox = any(os.path.isfile(f"/etc/{d}/policies/policies.json") for d in ("firefox-esr", "firefox"))
    ff = " Firefox est réglé pour limiter le pistage." if firefox else ""
    if etat.startswith("actif"):
        n = etat.split()[1] if len(etat.split()) > 1 else "?"
        try:
            n = f"{int(n):,}".replace(",", " ")
        except ValueError:
            pass
        return {**base, "etat": "ok",
                "detail": f"Publicités et traqueurs bloqués dans tout le système ({n} domaines).{ff}",
                "action": "", "corriger": ""}
    if etat == "en-attente":
        return {**base, "etat": "attention",
                "detail": "Le bloqueur de publicités attend sa liste (connexion Internet nécessaire)." + ff,
                "action": "Mettre à jour", "corriger": "root:vie-privee"}
    return {**base, "etat": "attention",
            "detail": "Le bloqueur de publicités et de traqueurs est désactivé." + ff,
            "action": "Activer", "corriger": "root:vie-privee"}


def check_parental():
    base = {"id": "parental", "titre": "Contrôle parental"}
    try:
        import protectos_parental as pc
    except ImportError:
        return {**base, "etat": "info", "detail": "Non installé.", "action": "", "corriger": ""}
    qui = pc.statut_texte()
    if qui:
        return {**base, "etat": "ok", "detail": f"Actif pour : {qui}.", "action": "Régler",
                "corriger": "lancer:protectos-parental"}
    return {**base, "etat": "info",
            "detail": "Aucun compte enfant n'est protégé. Utile si des enfants utilisent cet ordinateur.",
            "action": "Configurer", "corriger": "lancer:protectos-parental"}


CHECKS = [check_antivirus, check_privacy, check_firewall, check_updates, check_backups, check_encryption, check_secure_boot,
          check_screen_lock, check_parental]


def run_all():
    results = []
    for chk in CHECKS:
        try:
            results.append(chk())
        except Exception as e:  # une vérification ne doit jamais empêcher les autres
            results.append({"id": chk.__name__, "titre": chk.__name__, "etat": "info",
                            "detail": f"Vérification impossible : {e}", "action": "", "corriger": ""})
    return results


def summary(results):
    risques = sum(1 for r in results if r["etat"] == "risque")
    attentions = sum(1 for r in results if r["etat"] == "attention")
    if risques:
        return "risque", f"{risques} problème{'s' if risques > 1 else ''} de sécurité à corriger"
    if attentions:
        return "attention", f"Protégé, avec {attentions} point{'s' if attentions > 1 else ''} à améliorer"
    return "ok", "Votre ordinateur est protégé"


# ------------------------------------------------------------------ corrections côté utilisateur
def enable_screen_lock():
    tool = shutil.which("kwriteconfig6") or shutil.which("kwriteconfig5")
    if tool:
        for key in ("Autolock", "LockOnResume"):
            subprocess.run([tool, "--file", "kscreenlockerrc", "--group", "Daemon", "--key", key, "true"])
        return True
    return False
