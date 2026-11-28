// Disposition par défaut de protect.OS :
// une barre des tâches flottante en bas, avec le menu et les applications au centre (façon Windows 11).

var panel = new Panel;
panel.location = "bottom";
panel.height = 2 * Math.floor(gridUnit * 2.9 / 2);
panel.floating = true;

// Espace extensible à gauche : pousse le menu et les icônes vers le centre (barre centrée)
// Widgets (Windows+W) : la météo à gauche de la barre des tâches, comme Windows 11
var widgets = panel.addWidget("org.protectos.widgets");
try { widgets.globalShortcut = "Meta+W"; } catch (e) { print("Widgets : " + e); }
panel.addWidget("org.kde.plasma.panelspacer"); // barre-centree

// Menu Démarrer avec le logo protect.OS
var kickoff = panel.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "protectos-start");
kickoff.writeConfig("favoritesPortedToKAstats", "true");
// Menu façon Windows 11 : favoris en grille, toutes les applications en liste, libellés sous les boutons d'arrêt
kickoff.writeConfig("favoritesDisplay", "0");
kickoff.writeConfig("applicationsDisplay", "1");
kickoff.writeConfig("showActionButtonCaptions", "true");
kickoff.writeConfig("highlightNewlyInstalledApps", "true");
kickoff.writeConfig("switchCategoryOnHover", "true");

// Applications épinglées
var tasks = panel.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("iconSpacing", "2");
tasks.writeConfig("maxStripes", "1");
tasks.writeConfig("indicateAudioStreams", "true");
tasks.writeConfig("groupedTaskVisualization", "1");
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:firefox-esr.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:libreoffice-writer.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
]);

// Espace extensible à droite
panel.addWidget("org.kde.plasma.panelspacer");

var zoneNotif = panel.addWidget("org.kde.plasma.systemtray");
// Les icônes réseau, son, batterie, Bluetooth et luminosité sont regroupées dans les Paramètres rapides
// (comme Windows 11) : dans la zone de notification, elles passent sous la petite flèche.
try {
    var idZone = zoneNotif.readConfig("SystrayContainmentId");
    var zone = idZone ? desktopById(idZone) : null;
    if (zone) {
        zone.currentConfigGroup = ["General"];
        zone.writeConfig("hiddenItems", ["org.kde.plasma.networkmanagement", "org.kde.plasma.volume",
            "org.kde.plasma.battery", "org.kde.plasma.bluetooth", "org.kde.plasma.brightness",
            "org.kde.plasma.notifications", "org.kde.plasma.devicenotifier", "org.kde.plasma.clipboard",
            "org.kde.kscreen", "org.kde.plasma.keyboardlayout", "org.kde.plasma.manage-inputmethod"]);
    }
} catch (e) { print("Zone de notification : " + e); }
// Paramètres rapides : Wi-Fi, Bluetooth, mode avion, volume, luminosité, batterie
panel.addWidget("org.protectos.rapide");
// Horloge protect.OS : au clic, météo animée, calendrier et notifications
panel.addWidget("org.protectos.horloge");
panel.addWidget("org.kde.plasma.showdesktop");

// Fond d'écran protect.OS sur tous les bureaux
var desktopsArray = desktopsForActivity(currentActivity());
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image";
    desktopsArray[j].currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    desktopsArray[j].writeConfig("Image", "file:///usr/share/wallpapers/ProtectOS/");
}

// Moniteur du système sur le bureau : processeur, carte graphique, mémoire, disque (jauges dorées en temps réel)
var moniteur = true; // moniteur-bureau
if (moniteur && desktopsArray.length > 0) {
    var bureau = desktopsArray[0];
    var ecran = screenGeometry(bureau.screen);
    // Moniteur protect.OS : un gadget, quatre anneaux dorés (processeur, carte graphique, mémoire, disque)
    var hauteur = Math.min(760, ecran.height - 110);
    var largeur = Math.round(Math.max(170, Math.min(220, hauteur * 0.29)));
    bureau.addWidget("org.protectos.moniteur", ecran.width - largeur - 28, 24, largeur, hauteur);
}
