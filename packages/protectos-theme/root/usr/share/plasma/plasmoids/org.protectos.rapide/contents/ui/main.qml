// Paramètres rapides protect.OS : les icônes réseau, son et batterie dans la barre des tâches ;
// au clic, les tuiles Wi-Fi, Bluetooth, mode avion… et les curseurs de luminosité et de volume (comme Windows 11).
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as P5Support
import org.kde.notificationmanager as NotificationManager
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: racine
    readonly property string outil: "/usr/lib/protectos/protectos-rapide"
    property var e: ({ wifi: null, reseau: "aucun", reseauNom: "", bluetooth: null, avion: false, economie: null,
                       nuit: null, volume: null, muet: false, luminosite: null, batterie: null, charge: false })
    property bool enCours: false

    toolTipMainText: "Paramètres rapides"
    toolTipSubText: (e.reseau === "wifi" ? "Wi-Fi : " + e.reseauNom : e.reseau === "ethernet" ? "Connecté par câble" : "Non connecté")
        + (e.volume !== null ? "\nVolume : " + (e.muet ? "coupé" : e.volume + " %") : "")
        + (e.batterie !== null ? "\nBatterie : " + e.batterie + " %" + (e.charge ? " (branché)" : "") : "")
    Plasmoid.icon: iconeReseau()

    NotificationManager.Settings { id: notifications }
    readonly property bool deranger: notifications.notificationsInhibitedUntil !== undefined
        && notifications.notificationsInhibitedUntil > new Date()

    P5Support.DataSource {
        id: source
        engine: "executable"
        connectedSources: []
        onNewData: function (nom, donnees) {
            try { racine.e = JSON.parse(donnees["stdout"]) } catch (err) { }
            racine.enCours = false
            disconnectSource(nom)
        }
    }
    function lancer(args) {
        enCours = true
        source.connectSource(outil + (args ? " " + args : ""))
    }
    function ouvrir(commande) {
        source.connectSource(commande + " >/dev/null 2>&1 &")
        racine.expanded = false
    }
    Timer {
        interval: racine.expanded ? 3000 : 10000
        running: true; repeat: true; triggeredOnStart: true
        onTriggered: if (!racine.enCours) racine.lancer("")
    }
    onExpandedChanged: if (expanded) lancer("")

    function iconeReseau() {
        if (e.avion) return "network-flightmode-on"
        if (e.reseau === "ethernet") return "network-wired-activated"
        if (e.reseau === "wifi") return "network-wireless-signal-good"
        return "network-wireless-disconnected"
    }
    function iconeVolume() {
        if (e.volume === null) return "audio-volume-high"
        if (e.muet || e.volume === 0) return "audio-volume-muted"
        return e.volume < 34 ? "audio-volume-low" : e.volume < 67 ? "audio-volume-medium" : "audio-volume-high"
    }
    function iconeBatterie() {
        if (e.batterie === null) return ""
        var n = Math.min(100, Math.round(e.batterie / 10) * 10)
        return "battery-" + (n < 100 ? ("00" + n).slice(-3) : "100") + (e.charge ? "-charging" : "")
    }

    compactRepresentation: MouseArea {
        Layout.minimumWidth: rangee.implicitWidth + Kirigami.Units.smallSpacing * 2
        Layout.preferredWidth: Layout.minimumWidth
        hoverEnabled: true
        onClicked: racine.expanded = !racine.expanded
        onWheel: function (w) {
            if (racine.e.volume === null) return
            var v = Math.max(0, Math.min(100, racine.e.volume + (w.angleDelta.y > 0 ? 5 : -5)))
            racine.e.volume = v
            racine.lancer("volume " + v)
        }
        Rectangle {
            anchors.fill: parent
            anchors.margins: 2
            radius: 5
            color: Qt.rgba(1, 1, 1, parent.containsMouse || racine.expanded ? 0.1 : 0)
        }
        RowLayout {
            id: rangee
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing * 1.5
            Kirigami.Icon { source: racine.iconeReseau(); Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth }
            Kirigami.Icon { source: racine.iconeVolume(); Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth }
            Kirigami.Icon {
                visible: racine.e.batterie !== null
                source: racine.iconeBatterie()
                Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth
            }
        }
    }

    fullRepresentation: ColumnLayout {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 22
        Layout.minimumWidth: Kirigami.Units.gridUnit * 20
        Layout.preferredHeight: implicitHeight
        spacing: Kirigami.Units.largeSpacing

        GridLayout {
            Layout.fillWidth: true
            Layout.margins: Kirigami.Units.largeSpacing
            columns: 3
            columnSpacing: Kirigami.Units.largeSpacing
            rowSpacing: Kirigami.Units.smallSpacing

            Tuile {
                titre: "Wi-Fi"
                sousTitre: racine.e.wifi === null ? "Wi-Fi" : (racine.e.reseau === "wifi" ? racine.e.reseauNom : "Wi-Fi")
                icone: racine.e.wifi ? "network-wireless-signal-good" : "network-wireless-disconnected"
                actif: racine.e.wifi === true
                disponible: racine.e.wifi !== null
                avecReglages: true
                onBasculer: racine.lancer("wifi " + (racine.e.wifi ? "off" : "on"))
                onReglages: racine.ouvrir("systemsettings kcm_networkmanagement")
            }
            Tuile {
                titre: "Bluetooth"
                icone: "network-bluetooth"
                actif: racine.e.bluetooth === true
                disponible: racine.e.bluetooth !== null
                avecReglages: true
                onBasculer: racine.lancer("bluetooth " + (racine.e.bluetooth ? "off" : "on"))
                onReglages: racine.ouvrir("systemsettings kcm_bluetooth")
            }
            Tuile {
                titre: "Mode avion"
                icone: "network-flightmode-on"
                actif: racine.e.avion
                onBasculer: racine.lancer("avion " + (racine.e.avion ? "off" : "on"))
            }
            Tuile {
                titre: "Économie d'énergie"
                icone: "battery-profile-powersave"
                actif: racine.e.economie === true
                disponible: racine.e.economie !== null
                onBasculer: racine.lancer("economie " + (racine.e.economie ? "off" : "on"))
            }
            Tuile {
                titre: "Éclairage nocturne"
                icone: "redshift-status-on"
                actif: racine.e.nuit === true
                disponible: racine.e.nuit !== null
                onBasculer: racine.lancer("nuit " + (racine.e.nuit ? "off" : "on"))
            }
            Tuile {
                titre: "Ne pas déranger"
                icone: "notifications-disabled"
                actif: racine.deranger
                onBasculer: {
                    if (racine.deranger) {
                        notifications.notificationsInhibitedUntil = new Date(0)
                        notifications.revokeApplicationInhibitions()
                    } else {
                        notifications.notificationsInhibitedUntil = new Date(2100, 0, 1)
                    }
                    notifications.save()
                }
            }
        }

        // Luminosité (écran de portable) et volume
        RowLayout {
            visible: racine.e.luminosite !== null
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing * 2
            Layout.rightMargin: Kirigami.Units.largeSpacing * 2
            Kirigami.Icon { source: "brightness-high"; Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth }
            PlasmaComponents.Slider {
                id: lumi
                Layout.fillWidth: true
                from: 1; to: 100; stepSize: 1
                value: racine.e.luminosite === null ? 50 : racine.e.luminosite
                onMoved: delaiLumi.restart()
                Timer { id: delaiLumi; interval: 120; onTriggered: racine.lancer("luminosite " + Math.round(lumi.value)) }
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: Kirigami.Units.largeSpacing * 2
            Layout.rightMargin: Kirigami.Units.largeSpacing * 2
            enabled: racine.e.volume !== null
            PlasmaComponents.ToolButton {
                icon.name: racine.iconeVolume()
                onClicked: racine.lancer("muet")
                PlasmaComponents.ToolTip { text: racine.e.muet ? "Réactiver le son" : "Couper le son" }
            }
            PlasmaComponents.Slider {
                id: vol
                Layout.fillWidth: true
                from: 0; to: 100; stepSize: 1
                value: racine.e.volume === null ? 0 : racine.e.volume
                onMoved: delaiVol.restart()
                Timer { id: delaiVol; interval: 120; onTriggered: racine.lancer("volume " + Math.round(vol.value)) }
            }
            PlasmaComponents.Label {
                text: racine.e.volume === null ? "" : Math.round(vol.value) + " %"
                Layout.preferredWidth: Kirigami.Units.gridUnit * 2.2
                horizontalAlignment: Text.AlignRight
            }
        }

        // Barre du bas : batterie et Paramètres
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Kirigami.Units.gridUnit * 2.6
            color: Qt.rgba(0, 0, 0, 0.18)
            radius: 6
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Kirigami.Units.largeSpacing
                anchors.rightMargin: Kirigami.Units.smallSpacing
                Kirigami.Icon {
                    visible: racine.e.batterie !== null
                    source: racine.iconeBatterie()
                    Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth
                }
                PlasmaComponents.Label {
                    text: racine.e.batterie !== null ? racine.e.batterie + " %" + (racine.e.charge ? " · branché" : "")
                        : (racine.e.reseau === "ethernet" ? "Connecté par câble" : racine.e.reseau === "wifi" ? "Connecté au Wi-Fi" : "Non connecté à Internet")
                }
                Item { Layout.fillWidth: true }
                PlasmaComponents.ToolButton {
                    icon.name: "configure"
                    onClicked: racine.ouvrir("protectos-parametres")
                    PlasmaComponents.ToolTip { text: "Tous les paramètres" }
                }
            }
        }
    }
}
