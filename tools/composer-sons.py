#!/usr/bin/python3
"""Compose les sons de protect.OS (cloches douces, accord majeur) au format WAV.

À lancer seulement pour modifier les sons : les fichiers produits sont enregistrés dans le projet.
"""
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(ROOT, "packages", "protectos-theme", "root", "usr", "share", "sounds", "protectos")
FREQ = 44100


def note(nom):
    """« C5 », « E5 », « G#4 »… → fréquence en Hz."""
    noms = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440.0 * 2 ** ((noms[nom[:-1]] + 12 * (int(nom[-1]) - 4)) / 12)


def cloche(f, duree, volume=0.5, eclat=1.0):
    """Son de cloche cristalline : fondamentale + harmoniques qui s'éteignent vite."""
    t = np.arange(int(FREQ * duree)) / FREQ
    s = np.zeros_like(t)
    for mult, amp, decroissance in ((1, 1.0, 3.2), (2, 0.45 * eclat, 5.5), (3, 0.22 * eclat, 8.0),
                                    (4.2, 0.10 * eclat, 12.0), (0.5, 0.18, 2.5)):
        s += amp * np.sin(2 * np.pi * f * mult * t) * np.exp(-decroissance * t / max(duree, 0.4) * 2.2)
    attaque = np.minimum(1, t / 0.004)
    return volume * s * attaque


def melodie(notes, duree_totale):
    """notes : liste de (début en s, note, durée, volume)."""
    out = np.zeros(int(FREQ * duree_totale))
    for debut, n, d, v in notes:
        son = cloche(note(n), d, v)
        i = int(debut * FREQ)
        out[i:i + len(son)] += son[:len(out) - i]
    return out


def souffle(duree, de, a, volume=0.35):
    """Bruit filtré qui glisse (corbeille vidée)."""
    n = int(FREQ * duree)
    bruit = np.random.default_rng(7).standard_normal(n)
    t = np.arange(n) / FREQ
    coupure = np.linspace(de, a, n)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):  # passe-bas simple dont la fréquence de coupure glisse
        alpha = 2 * np.pi * coupure[i] / FREQ
        alpha = alpha / (1 + alpha)
        acc += alpha * (bruit[i] - acc)
        y[i] = acc
    enveloppe = np.sin(np.pi * t / duree) ** 1.5
    return volume * y / (np.abs(y).max() + 1e-9) * enveloppe


def ecrire(nom, signal):
    signal = signal / max(1.0, np.abs(signal).max() / 0.89)
    queue = int(FREQ * 0.02)
    signal[-queue:] *= np.linspace(1, 0, queue)
    stereo = np.repeat((signal * 32767).astype(np.int16)[:, None], 2, axis=1)
    os.makedirs(os.path.join(SORTIE, "stereo"), exist_ok=True)
    with wave.open(os.path.join(SORTIE, "stereo", nom + ".wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(FREQ)
        w.writeframes(stereo.tobytes())


SONS = {
    # Démarrage : arpège montant do-mi-sol-do, puis accord tenu
    "desktop-login": melodie([(0.00, "C5", 1.6, 0.45), (0.16, "E5", 1.6, 0.42), (0.32, "G5", 1.6, 0.40),
                              (0.50, "C6", 2.2, 0.42), (0.50, "G4", 2.2, 0.25), (0.50, "E5", 2.2, 0.20)], 2.9),
    # Fermeture de session : la même mélodie, descendante et plus courte
    "desktop-logout": melodie([(0.00, "C6", 1.2, 0.38), (0.14, "G5", 1.2, 0.36), (0.28, "E5", 1.2, 0.34),
                               (0.42, "C5", 1.8, 0.38)], 2.2),
    # Notification : deux notes claires
    "message-new-instant": melodie([(0.00, "G5", 0.7, 0.42), (0.11, "C6", 0.9, 0.42)], 1.0),
    "message": melodie([(0.00, "E5", 0.7, 0.40), (0.11, "A5", 0.9, 0.40)], 1.0),
    "dialog-information": melodie([(0.00, "A5", 0.8, 0.40)], 0.8),
    # Avertissement et erreur : plus graves
    "dialog-warning": melodie([(0.00, "E5", 0.6, 0.45), (0.13, "E5", 0.8, 0.40)], 0.95),
    "dialog-error": melodie([(0.00, "A4", 0.6, 0.50), (0.14, "D#4", 0.9, 0.50)], 1.05),
    "bell": melodie([(0.00, "D5", 0.5, 0.45)], 0.5),
    # Clé USB : montée (branchée) et descente (retirée)
    "device-added": melodie([(0.00, "G4", 0.5, 0.42), (0.09, "D5", 0.7, 0.42)], 0.8),
    "device-removed": melodie([(0.00, "D5", 0.5, 0.42), (0.09, "G4", 0.7, 0.42)], 0.8),
    "power-plug": melodie([(0.00, "C5", 0.5, 0.40), (0.08, "G5", 0.6, 0.40)], 0.7),
    "power-unplug": melodie([(0.00, "G5", 0.5, 0.40), (0.08, "C5", 0.6, 0.40)], 0.7),
    # Tâche terminée : accord brillant
    "complete": melodie([(0.00, "C5", 1.0, 0.35), (0.06, "E5", 1.0, 0.33), (0.12, "G5", 1.1, 0.33),
                         (0.18, "C6", 1.2, 0.30)], 1.4),
    "outcome-success": melodie([(0.00, "E5", 0.8, 0.38), (0.10, "B5", 1.0, 0.38)], 1.1),
    "battery-low": melodie([(0.00, "G5", 0.5, 0.42), (0.18, "E5", 0.5, 0.42), (0.36, "C5", 0.8, 0.42)], 1.2),
    # Corbeille vidée : un souffle qui glisse
    "trash-empty": souffle(0.55, 4500, 400),
}


def main():
    for nom, signal in SONS.items():
        ecrire(nom, signal)
    with open(os.path.join(SORTIE, "index.theme"), "w", encoding="utf-8") as f:
        f.write("[Sound Theme]\nName=protect.OS\nComment=Sons de protect.OS\nInherits=ocean,freedesktop\n"
                "Directories=stereo\n\n[stereo]\nOutputProfile=stereo\n")
    print(f"{len(SONS)} sons composés dans {SORTIE}")


if __name__ == "__main__":
    main()
