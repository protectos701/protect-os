// Disposition par défaut de protect.OS :
// une barre des tâches flottante en bas, avec le menu et les applications au centre (façon Windows 11).

var panel = new Panel;
panel.location = "bottom";
panel.height = 2 * Math.floor(gridUnit * 2.9 / 2);
panel.floating = true;

// Espace extensible à gauche : pousse le menu et les icônes vers le centre (barre centrée)
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

panel.addWidget("org.kde.plasma.systemtray");
var clock = panel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");
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
    var jauges = [
        ["Processeur", "cpu/all/usage", '["cpu/all/averageTemperature","cpu/all/averageFrequency"]'],
        ["Carte graphique", "gpu/gpu0/usage", '["gpu/gpu0/temperature","gpu/gpu0/usedVram"]'],
        ["Mémoire", "memory/physical/usedPercent", '["memory/physical/used","memory/physical/total"]'],
        ["Disque", "disk/all/usedPercent", '["disk/all/free","disk/all/total"]']
    ];
    var largeur = 230, hauteur = 190, marge = 14;
    var x = ecran.width - largeur - 36;
    var y = Math.max(40, Math.floor((ecran.height - 60 - jauges.length * (hauteur + marge)) / 2));
    for (var k = 0; k < jauges.length; k++) {
        var jauge = bureau.addWidget("org.kde.plasma.systemmonitor", x, y + k * (hauteur + marge), largeur, hauteur);
        jauge.currentConfigGroup = ["Appearance"];
        jauge.writeConfig("title", jauges[k][0]);
        jauge.writeConfig("showTitle", "true");
        jauge.writeConfig("chartFace", "org.kde.ksysguard.piechart");
        jauge.currentConfigGroup = ["Sensors"];
        jauge.writeConfig("highPrioritySensorIds", '["' + jauges[k][1] + '"]');
        jauge.writeConfig("totalSensors", '["' + jauges[k][1] + '"]');
        jauge.writeConfig("lowPrioritySensorIds", jauges[k][2]);
        jauge.writeConfig("sensorColors", '{"' + jauges[k][1] + '":"212,167,44"}');
    }
}
