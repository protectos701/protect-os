"""Contrôle parental de protect.OS (moteur, sans interface : testable seul).

Pour chaque compte enfant :
  - un temps d'écran maximum par jour (en minutes, 0 = sans limite) ;
  - une plage horaire autorisée (par exemple 08:00 → 20:30) ;
  - un filtre des sites inadaptés (les adresses Internet de ce compte passent par un
    service DNS « famille » qui bloque les sites pour adultes et malveillants).

Réglages : /etc/protectos/parental.json   Compteurs : /var/lib/protectos/parental/
"""
import datetime
import json
import os
import pwd
import grp
import re
import subprocess

CONF = os.environ.get("PROTECTOS_PARENTAL_CONF", "/etc/protectos/parental.json")
ETAT = os.environ.get("PROTECTOS_PARENTAL_ETAT", "/var/lib/protectos/parental")
DNS_FAMILLE_V4 = "1.1.1.3"                 # Cloudflare for Families : bloque contenus adultes et logiciels malveillants
DNS_FAMILLE_V6 = "2606:4700:4700::1113"
AVERTISSEMENTS = (10, 5, 1)                # minutes restantes auxquelles l'enfant est prévenu
ADMIN_GROUPS = ("sudo", "admin", "wheel")


# ------------------------------------------------------------------ réglages
def defaut_enfant():
    return {"minutes_par_jour": 120, "debut": "08:00", "fin": "20:30", "filtre": True}


def charger():
    try:
        with open(CONF, encoding="utf-8") as f:
            data = json.load(f)
        return {"enfants": dict(data.get("enfants", {}))}
    except (OSError, ValueError):
        return {"enfants": {}}


def _heure(v):
    if not isinstance(v, str) or not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v):
        raise ValueError(f"heure invalide : {v!r} (format HH:MM)")
    return v


def valider(data, comptes_existants=None, admins=None):
    """Vérifie et nettoie des réglages ; lève ValueError avec un message clair."""
    if not isinstance(data, dict) or not isinstance(data.get("enfants"), dict):
        raise ValueError("format inattendu")
    comptes_existants = set(comptes_existants) if comptes_existants is not None else {u["login"] for u in comptes()}
    admins = set(admins) if admins is not None else admin_users()
    propre = {}
    for login, r in data["enfants"].items():
        if login not in comptes_existants:
            raise ValueError(f"le compte « {login} » n'existe pas")
        if login in admins:
            raise ValueError(f"« {login} » est administrateur : un compte enfant doit être un compte standard")
        m = int(r.get("minutes_par_jour", 0))
        if not 0 <= m <= 1440:
            raise ValueError("le temps par jour doit être entre 0 et 1440 minutes")
        debut, fin = _heure(r.get("debut", "00:00")), _heure(r.get("fin", "23:59"))
        if debut >= fin:
            raise ValueError(f"pour « {login} », l'heure de début doit précéder l'heure de fin")
        propre[login] = {"minutes_par_jour": m, "debut": debut, "fin": fin, "filtre": bool(r.get("filtre", True))}
    return {"enfants": propre}


def enregistrer(data):
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    tmp = CONF + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.chmod(tmp, 0o644)
    os.replace(tmp, CONF)


# ------------------------------------------------------------------ comptes
def admin_users():
    out = set()
    for g in ADMIN_GROUPS:
        try:
            out.update(grp.getgrnam(g).gr_mem)
        except KeyError:
            pass
    return out


def comptes():
    """Comptes de personnes (pas les comptes techniques du système)."""
    admins = admin_users()
    res = []
    for p in pwd.getpwall():
        if 1000 <= p.pw_uid < 60000 and not p.pw_shell.endswith(("nologin", "false")):
            nom = p.pw_gecos.split(",")[0] or p.pw_name
            res.append({"login": p.pw_name, "uid": p.pw_uid, "nom": nom, "admin": p.pw_name in admins})
    return sorted(res, key=lambda u: u["nom"].lower())


# ------------------------------------------------------------------ temps d'écran
def _fichier_jour(login, jour):
    return os.path.join(ETAT, login, jour.isoformat())


def minutes_utilisees(login, jour=None):
    jour = jour or datetime.date.today()
    try:
        return int(open(_fichier_jour(login, jour)).read().strip() or 0)
    except (OSError, ValueError):
        return 0


def ajouter_minute(login, jour=None):
    jour = jour or datetime.date.today()
    path = _fichier_jour(login, jour)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = minutes_utilisees(login, jour) + 1
    with open(path, "w") as f:
        f.write(str(n))
    return n


def decision(regle, maintenant, utilisees):
    """Que faire pour un enfant connecté ? Renvoie (action, minutes_restantes, raison).

    action : "ok", "avertir" (il reste peu de temps) ou "fin" (temps écoulé ou hors des heures).
    """
    hm = maintenant.strftime("%H:%M")
    if not (regle["debut"] <= hm < regle["fin"]):
        return "fin", 0, f"l'ordinateur est autorisé de {regle['debut']} à {regle['fin']}"
    restantes_horaire = _minutes_jusqua(maintenant, regle["fin"])
    if regle["minutes_par_jour"]:
        restantes_quota = regle["minutes_par_jour"] - utilisees
        if restantes_quota <= 0:
            return "fin", 0, f"le temps d'écran du jour ({_duree(regle['minutes_par_jour'])}) est écoulé"
        restantes = min(restantes_quota, restantes_horaire)
    else:
        restantes = restantes_horaire
    if restantes in AVERTISSEMENTS:
        return "avertir", restantes, ""
    return "ok", restantes, ""


def _minutes_jusqua(maintenant, hhmm):
    h, m = map(int, hhmm.split(":"))
    fin = maintenant.replace(hour=h, minute=m, second=0, microsecond=0)
    return max(0, int((fin - maintenant).total_seconds() // 60))


def _duree(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} h {m:02d}" if h else f"{m} min"


# ------------------------------------------------------------------ filtrage des sites
def regles_nftables(data, uid_de=None):
    """Règles nftables : les requêtes DNS des comptes enfants filtrés passent par le DNS « famille »."""
    uid_de = uid_de or (lambda login: pwd.getpwnam(login).pw_uid)
    uids = []
    for login, r in sorted(data["enfants"].items()):
        if r.get("filtre"):
            try:
                uids.append(uid_de(login))
            except KeyError:
                pass
    lignes = ["table inet protectos_parental {"]
    if uids:
        ens = ", ".join(str(u) for u in uids)
        lignes += [
            "\tchain dns_famille {",
            "\t\ttype nat hook output priority -100; policy accept;",
            f"\t\tmeta skuid {{ {ens} }} meta nfproto ipv4 udp dport 53 dnat ip to {DNS_FAMILLE_V4}",
            f"\t\tmeta skuid {{ {ens} }} meta nfproto ipv4 tcp dport 53 dnat ip to {DNS_FAMILLE_V4}",
            f"\t\tmeta skuid {{ {ens} }} meta nfproto ipv6 udp dport 53 dnat ip6 to {DNS_FAMILLE_V6}",
            f"\t\tmeta skuid {{ {ens} }} meta nfproto ipv6 tcp dport 53 dnat ip6 to {DNS_FAMILLE_V6}",
            "\t}",
            "\tchain contournements {",
            "\t\ttype filter hook output priority 0; policy accept;",
            "\t\t# DNS chiffré (DoT) : empêcherait le filtre de fonctionner",
            f"\t\tmeta skuid {{ {ens} }} tcp dport 853 reject",
            "\t}",
        ]
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def statut_texte(data=None):
    data = data or charger()
    enfants = data["enfants"]
    if not enfants:
        return None
    noms = {u["login"]: u["nom"] for u in comptes()}
    return ", ".join(noms.get(k, k) for k in sorted(enfants))


def utilisateurs_connectes():
    """Comptes ayant une session ouverte (via loginctl)."""
    try:
        out = subprocess.run(["loginctl", "list-users", "--no-legend"], capture_output=True, text=True).stdout
    except OSError:
        return set()
    return {ligne.split()[1] for ligne in out.splitlines() if len(ligne.split()) >= 2}
