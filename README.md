# protect.OS

**protect.OS, le système qui vous protège.** C'est un système d'exploitation complet, en bleu et or, avec un bouclier en vitrail pour logo, construit sur **Debian 13 « trixie »** et le bureau **KDE Plasma 6**. Il fonctionne comme une vraie distribution :

- tout ce qui fait protect.OS est rangé dans **ses propres paquets** (`protectos-theme`, `protectos-base`…) ;
- un **dépôt de mises à jour signé** livre les nouvelles versions à tous les ordinateurs installés ;
- **GitHub construit tout seul** les paquets, le dépôt et l'image ISO.

## Ce que contient protect.OS

- **Antivirus** (moteur ClamAV) : les fichiers à risque sont analysés dès qu'ils arrivent dans Téléchargements, chaque programme Windows est vérifié avant d'être installé ou ouvert, et on peut analyser un dossier ou une clé USB par clic droit (« Analyser avec l'antivirus »). Les menaces sont mises en **quarantaine** (restaurables), et les signatures se mettent à jour chaque jour.
- **Vie privée** : un bloqueur de publicités et de pisteurs pour tout l'ordinateur (liste mise à jour chaque semaine), et Firefox réglé pour protéger votre vie privée (protection renforcée contre le pistage, pas de télémétrie, pas d'études ni de publicités sur la page d'accueil).
- **Contrôle parental** : pour chaque compte enfant, un temps d'écran par jour, des horaires autorisés et le filtrage des sites pour adultes ou malveillants. L'enfant est prévenu 10, 5 et 1 minute avant la fin, puis sa session se ferme. Seul un administrateur peut changer les réglages.
- **Chiffrement conseillé** : avant l'installation, une fenêtre rappelle de sauvegarder ses fichiers et conseille de cocher « Chiffrer le système » : en cas de vol, personne ne peut lire vos fichiers.
- **Centre de protection** : l'état de sécurité de l'ordinateur d'un coup d'œil (antivirus, vie privée, pare-feu, correctifs automatiques, sauvegardes, chiffrement du disque, démarrage sécurisé, verrouillage de l'écran, contrôle parental), avec correction en un clic et « Tout corriger ». Une vérification discrète a lieu à chaque ouverture de session : une notification prévient seulement en cas de problème.
- **Bureau façon Windows** : barre des tâches flottante, menu Démarrer et applications au centre, boutons Réduire / Agrandir / Fermer à droite.
- **Thème bleu et or, effet verre** : couleurs bleu nuit et sélection dorée (thème sombre ou clair), fond d'écran en vitrail, écrans de connexion et de verrouillage assortis. Le terminal est en verre bleu nuit transparent et flouté, les menus sont translucides, et les fenêtres en arrière-plan ou en déplacement deviennent légèrement transparentes.
- **Démarrage aux couleurs de protect.OS** : logo et barre de progression dorée, écran de chargement de session, menu GRUB au fond protectos. Le système s'appelle « protect.OS » partout (paramètres, menu de démarrage, `os-release`).
- **Installateur graphique** (Calamares) habillé en protect.OS, avec diaporama.
- **Logiciels** : Firefox, LibreOffice, VLC, Dolphin, Konsole, Kate, Discover (magasin d'applications), visionneuses, calculatrice, gestionnaire de partitions.
- **« Bienvenue dans protect.OS »** au premier démarrage : thème sombre ou clair, pilote NVIDIA, sauvegardes Timeshift, applications populaires (Steam, GIMP, Krita, OBS…) en quelques cases à cocher. Dans la session d'essai, il propose aussi d'installer protect.OS.
- **Programmes Windows, comme sous Windows** : double-clic sur un `.exe` ou un `.msi` pour l'installer, disque C: et « Program Files », raccourcis dans le menu Démarrer, désinstallation depuis « Programmes et fonctionnalités ».
- **Vos propres programmes** : l'outil `protectos-pack` les transforme en paquets installables d'un double-clic, avec raccourci et icône. Ça marche pour un programme Linux comme pour un `.exe` Windows.
- **Le quotidien, sans réglage** : impression et numérisation (pilotes HP, Epson et génériques), Flathub dans Discover pour des milliers d'applications de plus, pare-feu activé, correctifs de sécurité installés automatiquement chaque jour (sans redémarrage forcé), mémoire compressée (zram) pour rester fluide sur les petits PC, profils d'énergie pour les portables.
- **Raccourcis clavier familiers** : Windows+E (fichiers), Ctrl+Maj+Échap (gestionnaire des tâches), Windows+I (paramètres), Windows+R (exécuter), Windows+Maj+S (capture d'une zone), Ctrl+Alt+T (terminal), Windows+Maj+P (Centre de protection). Tous modifiables.
- **En français** : langue, clavier AZERTY, heure de Paris. Pilotes Wi-Fi, Bluetooth et graphiques courants.

## Organisation du projet

```
ma-personnalisation.conf  ← VOTRE FICHIER : nom, logo, couleurs, fond, bureau, noms, raccourcis, logiciels, langue
personnalisation/       vos images (logo, fond d'écran)
VERSION                 numéro de version de protect.OS (ex. 1.0.0)
protectos.conf            adresse du dépôt, version de Debian, responsable
packages/               les paquets protect.OS (un dossier par paquet)
  protectos-base/           identité « protect.OS », réglages GRUB, icône d'installation
  protectos-theme/          couleurs, thème global Plasma, barre des tâches, logo
  protectos-wallpapers/     fonds d'écran
  protectos-plymouth/       écran de démarrage
  protectos-calamares/      habillage de l'installateur
  protectos-programmes/     installateur .exe/.msi/.deb, « Programmes et fonctionnalités », protectos-pack
  protectos-bienvenue/      assistant du premier démarrage
  protectos-protection/     Centre de protection, antivirus, vie privée
  protectos-parental/       contrôle parental
  protectos-archive-keyring/ adresse et clé du dépôt de mises à jour
  protectos-desktop/        métapaquet : installe tout protect.OS + les applications
keys/                   clé PUBLIQUE du dépôt (protectos-archive.asc)
apps/                   vos programmes .deb (faits avec protectos-pack) à publier dans le dépôt
site/                   le site web de protect.OS (page d'accueil, aperçus, téléchargement)
tools/
  build-debs.sh           construit les paquets .deb dans build/debs/
  personnaliser.py        applique ma-personnalisation.conf à tout le projet (automatique sur GitHub)
  test-iso.py             démarre l'ISO dans une machine virtuelle et prend des captures
  make-repo.py            crée le dépôt APT signé dans repo/
  render-images.py        régénère fond d'écran, logos et aperçus
config/, auto/          configuration live-build de l'ISO
build.sh                construit les paquets puis l'ISO
.github/workflows/      construction automatique sur GitHub
```

Dans chaque paquet, `root/` contient les fichiers tels qu'ils seront installés (par exemple `root/usr/share/wallpapers/…`), et `DEBIAN/` la description du paquet et ses scripts d'installation.


## Personnaliser votre système (un seul fichier)

Tout ce qui fait l'identité du système se règle dans **`ma-personnalisation.conf`**, sans toucher au reste :

| Section | Ce que vous choisissez |
|---|---|
| `[identite]` | le **nom** affiché partout (démarrage, connexion, menus, installateur, site) et le **slogan** |
| `[couleurs]` | la teinte **principale** (fonds, fenêtres, fond d'écran) et la couleur d'**accent** (boutons, sélections, logo) |
| `[logo]` | votre **logo** (.svg ou .png carré) ; vide = le bouclier en vitrail, recoloré avec vos couleurs |
| `[fond_ecran]` | votre **image de fond** ; vide = le vitrail généré avec vos couleurs |
| `[bureau]` | thème **sombre** ou **clair**, barre des tâches **centrée** ou à **gauche**, en **bas** ou en **haut**, effet **verre**, assistant **Bienvenue** au premier démarrage |
| `[noms_applications]` | **vos noms** pour les applications du menu (« Explorateur de fichiers », « Bloc-notes »… ou ce que vous voulez) |
| `[raccourcis]` | les **raccourcis clavier** (`Meta` = touche Windows, par exemple `Meta+E`) |
| `[protection]` | le **bloqueur de publicités** et le réglage **Firefox confidentiel** (oui / non) |
| `[logiciels]` | les logiciels à **ajouter** ou **retirer**, et les applications **épinglées** dans la barre des tâches |
| `[langue]` | la **langue**, le **clavier** (et sa variante) et le **fuseau horaire** |

**Depuis le site de GitHub, sans rien installer sur votre PC :**

1. Ouvrez `ma-personnalisation.conf` sur la page de votre dépôt, cliquez sur le crayon ✎, modifiez les valeurs, puis **Commit changes**.
2. Pour un logo ou un fond d'écran : ouvrez le dossier `personnalisation`, cliquez sur **Add file → Upload files**, déposez votre image, puis indiquez son nom dans le fichier (par exemple `fichier = personnalisation/mon-logo.png`).
3. Lancez **Actions → Image ISO**. GitHub applique vos choix à tout le système, construit l'ISO et la teste.

Vous pouvez changer d'avis autant de fois que vous voulez : remettre les valeurs notées « origine » ramène exactement le système d'origine. Sur une machine Linux, `python3 tools/personnaliser.py` applique le fichier tout de suite. Les programmes propres au système (Centre de protection, Installateur, Bienvenue…) restent en français, quelle que soit la langue choisie.

## 1. Construire l'ISO sur votre machine

Il vous faut une machine (ou une VM VirtualBox) sous **Debian 13**, avec 30 Go libres, 8 Go de mémoire si possible, et Internet.

```sh
sudo apt update
sudo apt install live-build
cd protect-os
sudo ./build.sh
```

Le script construit d'abord les paquets protect.OS, puis l'ISO. Comptez 30 à 60 minutes. Vous obtenez **`protect-os-amd64.hybrid.iso`**.

Pour l'essayer dans une machine virtuelle :

```sh
sudo apt install qemu-system-x86
qemu-system-x86_64 -enable-kvm -m 4096 -smp 2 -cdrom protect-os-amd64.hybrid.iso
```

La session d'essai s'ouvre toute seule (utilisateur `protect`, mot de passe `live`).

## 2. Clé USB et installation

- **Clé USB** : balenaEtcher (choisir l'ISO, la clé, « Flash ») ou Ventoy (copier l'ISO sur la clé). Sous Linux : `sudo dd if=protect-os-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress oflag=sync` (vérifiez `sdX` avec `lsblk` : la clé est effacée).
- **Démarrer sur la clé** : touche F12, F11, F8 ou Échap au démarrage selon la marque du PC.
- **Installer** : double-cliquez sur « Installer protect.OS » sur le bureau. Une fenêtre rappelle d'abord les deux précautions :
  1. **Sauvegardez vos fichiers** sur une clé ou un disque externe : pour remplacer Windows, choisissez « Effacer le disque », ce qui efface tout.
  2. **Cochez « Chiffrer le système »** à l'étape Partitions et notez la phrase secrète en lieu sûr : elle sera demandée à chaque démarrage, et sans elle les fichiers sont perdus.

  L'installation peut aussi se faire à côté de Windows (« Installer à côté »), pour garder les deux au choix au démarrage.
- **Contrôle parental** (après l'installation) : créez un compte **Standard** pour chaque enfant (Paramètres → Utilisateurs), puis ouvrez « Contrôle parental » dans le menu, cochez « Compte enfant » et réglez temps, horaires et filtrage.

## 3. Installer des programmes Windows et vos propres programmes

### Comment protect.OS reproduit Windows

Le code de Windows appartient à Microsoft : on ne peut pas le reprendre. protect.OS reproduit donc sa *façon de faire* avec **Wine**, une réimplémentation libre de Windows :

| Sous Windows | Sous protect.OS |
|---|---|
| Double-clic sur `setup.exe` ou `.msi` | Double-clic : l'**Installateur protect.OS** demande confirmation, puis lance l'installateur du programme, exactement le même |
| Disque `C:` et dossier `C:\Program Files` | Un disque C: par utilisateur, dans `~/.wine/drive_c` (bouton « Disque C: ») |
| Raccourci dans le menu Démarrer | Raccourci dans le menu Démarrer de protect.OS, rubrique « Wine » |
| « Programmes et fonctionnalités » | Même nom, même liste : protect.OS lit les clés de registre `Uninstall` comme Windows, et masque comme lui les composants système et les mises à jour |
| Désinstaller | Lance le désinstallateur fourni par le programme, comme Windows. Le double-clic sur une ligne désinstalle aussi |
| Installer .NET, Visual C++ ou DirectX avant un programme qui en a besoin | L'Installateur protect.OS **repère** ces besoins dans le `.exe` et propose « Ajouter puis continuer ». « Programmes et fonctionnalités » → Plus → **Composants Windows** permet aussi de les ajouter à la main |
| Programme « portable » (un `.exe` sans installation) | « Ouvrir sans installer », ou « Ajouter au menu Démarrer » : protect.OS le range dans `C:\Program Files` et récupère son icône |

L'image ISO contient Wine en 64 et 32 bits. Sur un Debian où il manquerait la partie 32 bits, « Programmes et fonctionnalités » → **Plus → Activer les programmes Windows 32 bits**.

**Ce qui fonctionne bien** : la plupart des logiciels classiques (utilitaires, éditeurs, anciens Office, beaucoup de jeux via Steam/Proton). **Ce qui fonctionne mal ou pas** : les pilotes de matériel, les jeux avec anti-triche noyau, et certaines suites très récentes (Adobe Creative Cloud, Microsoft 365). Les composants proposés sont .NET Framework 4.8, Visual C++ 2015-2022, DirectX 9 et les polices Windows. La détection lit le `.exe` lui-même : elle est fiable pour un programme .NET ou un `.exe` direct, mais pas toujours pour un installateur compressé (`setup.exe`). Si un programme installé ne démarre pas, ajoutez les composants à la main. Pour d'autres briques, `winetricks` en propose des centaines (`winetricks list-all`).

### Vos propres programmes : `protectos-pack`

`protectos-pack` transforme le dossier de votre programme en paquet `.deb`. Ce paquet s'installe d'un double-clic, crée son raccourci et son icône dans le menu Démarrer, se met à jour en installant la version suivante par-dessus, et apparaît dans « Programmes et fonctionnalités » sous le type « Application protect.OS ».

```sh
protectos-pack nouveau MonApp              # projet d'exemple pour un programme Linux
protectos-pack nouveau MonJeu --windows    # projet pour un programme Windows (.exe)
protectos-pack nouveau MesTaches --python  # application Python avec fenêtre bleu et or, prête à modifier
# … mettez vos fichiers dans le dossier et complétez protectos-app.json …
protectos-pack MonApp                      # produit monapp_1.0.0_all.deb
```

Le modèle `--python` contient une vraie petite application (une liste de tâches enregistrée dans le dossier personnel) avec le bandeau bleu nuit, les boutons dorés et le style de protect.OS. Remplacez la classe `Fenetre` par votre programme : la mise en forme est déjà là.

Le fichier `protectos-app.json` décrit le programme :

```json
{
  "id": "monapp",
  "nom": "Mon application",
  "version": "1.0.0",
  "auteur": "Votre nom <vous@exemple.fr>",
  "description": "Ce que fait votre application, en une phrase.",
  "lancer": "monapp.sh",
  "icone": "icone.svg",
  "categories": ["Utility"],
  "dependances": ["python3"],
  "terminal": false
}
```

- `lancer` : le fichier à exécuter. S'il se termine par `.exe`, protect.OS le lance avec la compatibilité Windows et ajoute Wine aux dépendances. Sans `icone`, il reprend celle du `.exe`.
- `dependances` : les paquets Debian dont votre programme a besoin. Ils s'installent automatiquement avec lui.
- `categories` : la rubrique du menu (`Utility`, `Office`, `Game`, `Graphics`, `Development`, `Education`, `Network`, `AudioVideo`…).

Pour distribuer vos programmes à tous les utilisateurs de protect.OS, placez leurs `.deb` dans le dossier `apps/` du projet et envoyez-les sur GitHub. Ils sont alors publiés dans le dépôt protect.OS (section 4) : les utilisateurs les installent avec `sudo apt install monapp` ou depuis Discover, et reçoivent vos nouvelles versions automatiquement.

## 4. Mettre en place le dépôt de mises à jour (une seule fois)

Le dépôt permet d'envoyer les nouvelles versions de protect.OS à tous les ordinateurs déjà installés. Il est hébergé gratuitement par **GitHub Pages** et signé par une clé GPG, pour que personne ne puisse se faire passer pour vous.

**a. Mettre le projet sur GitHub.** Créez un dépôt GitHub (par exemple `protect-os`, public), puis envoyez-y ce dossier :

```sh
cd protect-os
git init -b main
git add .
git commit -m "protect.OS 1.0.0"
git remote add origin https://github.com/protectos701/protect-os.git
git push -u origin main
```

Le premier lancement automatique de « Paquets et dépôt » dans l'onglet Actions échouera : c'est normal, la clé de signature n'est pas encore en place. Il réussira à l'étape f.

**b. Créer la clé de signature** (sur votre machine) :

```sh
gpg --batch --passphrase '' --quick-gen-key "protect.OS (dépôt) <votre@email>" rsa4096 sign 3y
mkdir -p keys
gpg --armor --export "protect.OS (dépôt)" > keys/protectos-archive.asc
gpg --armor --export-secret-keys "protect.OS (dépôt)" > /tmp/cle-privee.asc
```

**c. Donner la clé privée à GitHub, et à personne d'autre.** Sur GitHub, ouvrez **Settings → Secrets and variables → Actions → New repository secret**. Nommez le secret `PROTECTOS_GPG_PRIVATE_KEY`, collez-y tout le contenu de `/tmp/cle-privee.asc`, enregistrez, puis supprimez le fichier : `shred -u /tmp/cle-privee.asc`. Gardez une sauvegarde de la clé privée sur une clé USB rangée en lieu sûr : si vous la perdez, vous ne pourrez plus signer de mises à jour.

**d. Activer GitHub Pages.** Ouvrez **Settings → Pages → Source : GitHub Actions**.

**e. Régler l'adresse du dépôt.** Dans `protectos.conf`, remplacez `REPO_URL` par `https://protectos701.github.io/protect-os`. Sur GitHub, l'adresse est calculée automatiquement, mais elle sert pour vos constructions locales.

**f. Envoyer la clé publique** (elle n'a rien de secret) :

```sh
git add keys/protectos-archive.asc protectos.conf
git commit -m "Clé du dépôt protect.OS"
git push
```

L'onglet **Actions** lance « Paquets, dépôt et site ». Quelques minutes plus tard, tout est en ligne à l'adresse `https://protectos701.github.io/protect-os` : le **site de protect.OS** en page d'accueil, le dépôt de mises à jour au même endroit, et la liste des paquets sur la page `depot.html`. Sur le site, le bouton « Télécharger l'ISO » mène automatiquement à la dernière version publiée (section 6). À partir de là, chaque ISO contient le paquet `protectos-archive-keyring` : les ordinateurs installés savent où chercher les mises à jour protect.OS.

## 5. Construire l'ISO sur GitHub (sans machine Debian)

Dans l'onglet **Actions**, choisissez **Image ISO → Run workflow**. Environ une heure plus tard, l'ISO est téléchargeable dans les **artefacts** du workflow, pendant 7 jours.

**Test automatique.** Juste après la construction, GitHub démarre l'ISO dans une machine virtuelle sans écran. Il vérifie que protect.OS va jusqu'au bureau et prend de **vraies captures d'écran** : démarrage, bureau, assistant de bienvenue. Le résultat s'affiche en haut de la page du workflow (« ✅ protect.OS démarre jusqu'au bureau »), et les captures sont dans l'artefact **captures-ecran**, gardé 30 jours, avec le journal de démarrage `serial.log`. Si le bureau ne démarre pas, la version n'est pas publiée : envoyez-moi `serial.log` et les captures, c'est exactement ce qu'il faut pour corriger.

Pour lancer ce test sur votre propre machine Linux :

```sh
sudo apt install qemu-system-x86 xorriso python3-pil
python3 tools/test-iso.py protect-os-amd64.hybrid.iso -o captures
```

Ces captures réelles peuvent remplacer les aperçus du site : copiez-les dans `site/images/` sous les mêmes noms.

## 6. Publier une nouvelle version

1. Faites vos modifications (thème, fond d'écran, liste de logiciels…).
2. Augmentez le numéro dans `VERSION` : `1.0.1` pour une correction, `1.1.0` pour des nouveautés, `2.0.0` pour un changement majeur.
3. Envoyez le tout et posez une étiquette de version :

```sh
git add .
git commit -m "protect.OS 1.1.0 : nouveau fond d'écran"
git push
git tag v1.1.0
git push origin v1.1.0
```

Ce qui se passe ensuite :
- le **dépôt** est mis à jour : les ordinateurs installés reçoivent la nouvelle version dans **Discover**, ou avec `sudo apt update && sudo apt full-upgrade` ;
- l'ISO est **testée automatiquement**. Si elle démarre jusqu'au bureau, une **Release GitHub** « protect.OS v1.1.0 » est créée avec l'ISO, ses sommes de contrôle et une capture du bureau. GitHub limite chaque fichier à 2 Go : si l'ISO est plus grosse, elle est découpée en morceaux, et le fichier `LISEZMOI-ISO.txt` explique comment la reconstituer.

Les mises à jour de Debian elle-même (sécurité, Firefox, noyau…) continuent d'arriver directement depuis les dépôts Debian.

## 7. Personnaliser : où se trouve quoi

| À modifier | Fichier |
|---|---|
| Logiciels installés avec le bureau | `packages/protectos-desktop/DEBIAN/control` (lignes `Depends` et `Recommends`) |
| Logiciels de l'image d'essai uniquement | `config/package-lists/protectos.list.chroot` |
| Langue, clavier, fuseau, nom de l'ISO | `auto/config` |
| Couleurs | `packages/protectos-theme/root/usr/share/color-schemes/ProtectBleuOr.colors` (sombre) et `ProtectBleuOrClair.colors` (clair) |
| Assistant de bienvenue (pages, applications proposées) | `packages/protectos-bienvenue/root/usr/lib/protectos/protectos_bienvenue.py` (liste `APPS`) et `usr/bin/protectos-bienvenue` ; tout paquet ajouté à `APPS` doit aussi être autorisé dans `usr/lib/protectos/protectos-bienvenue-root` |
| Barre des tâches et applications épinglées | `packages/protectos-theme/root/usr/share/plasma/look-and-feel/org.protectos.desktop/contents/layouts/org.kde.plasma.desktop-layout.js` |
| Écran de chargement de session | `…/org.protectos.desktop/contents/splash/Splash.qml` |
| Boutons des fenêtres, flou, transparence des fenêtres | `packages/protectos-theme/root/etc/xdg/kwinrc` (section `Effect-translucency`) |
| Transparence des menus | `packages/protectos-theme/root/etc/xdg/breezerc` (`MenuOpacity`, de 0 à 100) |
| Terminal en verre (couleurs, opacité, flou) | `packages/protectos-theme/root/usr/share/konsole/ProtectOS.colorscheme` |
| Nom et version affichés du système | `packages/protectos-base/root/usr/lib/os-release` (la version vient de `VERSION`) |
| Centre de protection (vérifications, textes, corrections) | `packages/protectos-protection/root/usr/lib/protectos/protectos_protection.py` (fonctions `check_…`) ; les corrections administrateur sont dans `usr/lib/protectos/protectos-protection-root` |
| Antivirus (types de fichiers surveillés, options d'analyse, quarantaine) | `packages/protectos-protection/root/usr/lib/protectos/protectos_antivirus.py` (liste `RISQUES`, fonction `scan_command`) |
| Mises à jour automatiques | `packages/protectos-base/root/etc/apt/apt.conf.d/` (`21protectos-mises-a-jour`, `52protectos-unattended-upgrades`) |
| Mémoire compressée (zram) | `packages/protectos-base/root/etc/systemd/zram-generator.conf` |
| Pare-feu (activé une seule fois, puis au choix de l'utilisateur) | `packages/protectos-base/DEBIAN/postinst` ; réglages ensuite dans Paramètres → Pare-feu |
| Menu GRUB | `packages/protectos-base/root/etc/default/grub.d/protectos.cfg` |
| Programmes Windows, installateur, « Programmes et fonctionnalités », protectos-pack | `packages/protectos-programmes/root/usr/bin/` et `usr/lib/protectos/` |
| Écran de démarrage | `packages/protectos-plymouth/root/usr/share/plymouth/themes/protectos/` |
| Installateur et diaporama | `packages/protectos-calamares/root/etc/calamares/branding/protectos/` |
| Site web (textes, sections, questions fréquentes) | `site/index.html` ; les images sont dans `site/images/` |
| Logo | `tools/protectos-logo.svg`, puis `python3 tools/render-images.py` |
| Fond d'écran | `tools/render-images.py` (fonction `wallpaper_svg`), puis relancer le script |

Pour régénérer les images : `sudo apt install python3-pil librsvg2-bin` puis `python3 tools/render-images.py`.

Pour tester vos paquets sans construire d'ISO : `./tools/build-debs.sh`, puis sur un Debian 13 avec KDE, `sudo apt install ./build/debs/*.deb`.

## 8. Aller plus loin

- **Une boutique protect.OS** : publier vos applications `protectos-pack` dans le dépôt pour qu'elles apparaissent dans Discover.
- **Verre sur tout l'intérieur des fenêtres** : aujourd'hui, le verre concerne le terminal, les menus, la barre des tâches et les fenêtres inactives. Pour l'étendre à toutes les applications, il faudrait un thème Kvantum translucide bleu et or, dans un nouveau paquet `protectos-kvantum`.
- **Nom et licences** : vérifiez que « protect.OS » n'est pas une marque déposée avant de diffuser. protect.OS reprend des logiciels libres (GPL et autres) : si vous distribuez l'ISO, rendez aussi leurs sources disponibles. Le plus simple est de renvoyer aux dépôts Debian, ou d'ajouter `--source true` dans `auto/config` pour produire une image des sources.

## 9. En cas de problème

- **« lb : commande introuvable »** : `sudo apt install live-build`.
- **Un paquet Debian est introuvable** pendant la construction : son nom a pu changer. Cherchez-le sur packages.debian.org et corrigez la liste ou le `control` de `protectos-desktop`.
- **« protectos-archive-keyring ignoré »** : normal tant que `keys/protectos-archive.asc` n'existe pas (section 4). L'ISO fonctionne, mais ne recevra pas les mises à jour protect.OS.
- **Le workflow « Paquets et dépôt » échoue sur la clé** : le secret `PROTECTOS_GPG_PRIVATE_KEY` manque ou est incomplet. Recollez tout le bloc, lignes `BEGIN` et `END` comprises.
- **`apt update` refuse le dépôt (NO_PUBKEY)** : la clé de `keys/` n'est pas celle qui a signé le dépôt. Réexportez la clé publique de la même clé que le secret.
- **Un programme Windows ne démarre pas** : ajoutez d'abord .NET et Visual C++ (« Programmes et fonctionnalités » → Plus → Composants Windows), c'est la cause la plus fréquente. Vérifiez aussi que les programmes 32 bits sont activés (« Programmes et fonctionnalités » → Plus). Si vous venez de les activer, réinitialisez le disque C: au même endroit : un disque C: créé sans la partie 32 bits ne la prend pas en compte. Pour .NET ou Visual C++, utilisez `winetricks`.
- **Le double-clic sur un .exe ouvre autre chose** : clic droit sur le fichier → « Installer avec protect.OS », ou Propriétés → Ouvrir avec → Installateur protect.OS.
- **L'assistant de bienvenue ne s'ouvre plus** : c'est voulu après la première fois. Rouvrez-le depuis le menu Démarrer (« Bienvenue dans protect.OS »), et cochez « Afficher au démarrage » pour le revoir à chaque ouverture de session.
- **Le pilote NVIDIA ne se charge pas après redémarrage** : si le démarrage sécurisé est actif, il faut accepter la clé à l'écran bleu « MOK management » (Enroll MOK), avec le mot de passe choisi pendant l'installation.
- **Une imprimante n'est pas détectée** : Paramètres du système → Imprimantes → Ajouter. Pour certaines imprimantes Canon ou Brother, il faut le pilote du fabricant (fichier .deb, qui s'installe d'un double-clic).
- **Un appareil du réseau local ne voit pas l'ordinateur** (partage de fichiers, KDE Connect) : le pare-feu bloque les connexions entrantes. Autorisez le service voulu dans Paramètres → Pare-feu.
- **L'antivirus indique « signatures pas encore téléchargées »** : la base de virus (environ 300 Mo) se télécharge au premier branchement à Internet. Cliquez sur « Télécharger » dans le Centre de protection pour le faire tout de suite.
- **Une analyse est lente ou l'ordinateur ralentit pendant l'analyse** : c'est normal, une analyse charge la base de virus en mémoire (environ 1 Go). Préférez l'analyse rapide ; la surveillance des téléchargements ne traite que les fichiers à risque.
- **L'antivirus bloque un fichier que vous savez sain** : Centre de protection → Antivirus… → sélectionnez-le dans la quarantaine → Restaurer.
- **Le Centre de protection signale le chiffrement du disque** : le chiffrement se choisit à l'installation (case « Chiffrer le système » dans l'installateur) et ne s'ajoute pas facilement ensuite. Pour un portable, c'est fortement conseillé.
- **Le thème n'apparaît pas** sur un compte existant : Configuration du système → Thème global → « protect.OS Bleu et Or ». Il s'applique d'office seulement aux nouveaux comptes.
- **Écran noir au démarrage dans une VM** : activez l'accélération 3D, ou choisissez « fail-safe mode » dans le menu de démarrage.
- **Logiciel tiers qui refuse « protect.OS »** : protect.OS se déclare `ID=protectos` et `ID_LIKE=debian`. Presque tous les logiciels l'acceptent comme un Debian. Pour un installateur trop strict, choisissez « Debian 13 » s'il le demande.
- **Un site ne s'affiche plus correctement** (bloqueur de publicités) : Centre de protection → Vie privée → désactivez le bloqueur, ou en terminal `sudo /usr/lib/protectos/protectos-bloqueur desactiver`. Pour le remettre : `sudo /usr/lib/protectos/protectos-bloqueur activer`.
- **Un enfant a besoin de plus de temps aujourd'hui** : ouvrez « Contrôle parental » avec votre compte, augmentez son temps et enregistrez : c'est pris en compte dans la minute. L'enfant peut voir son temps restant avec `protectos-parental --temps`.
- **Phrase de chiffrement oubliée** : il n'existe aucun moyen de la contourner, c'est le principe. Il faut réinstaller (les fichiers sont perdus), d'où l'importance de la noter et de faire des sauvegardes.
