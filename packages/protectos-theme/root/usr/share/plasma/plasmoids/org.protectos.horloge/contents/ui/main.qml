// Horloge protect.OS : l'heure dans la barre des tâches ; au clic, la météo animée, le calendrier et les notifications.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.extras as PlasmaExtras
import org.kde.plasma.workspace.calendar as PlasmaCalendar
import org.kde.notificationmanager as NotificationManager
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: racine

    property date maintenant: new Date()
    readonly property color or: "#d4a72c"
    readonly property color orClair: "#f3d27a"

    // ---------- Météo (Open-Meteo : gratuit, sans compte, sans pistage)
    property string ville: Plasmoid.configuration.ville || "Paris"
    property real latitude: NaN
    property real longitude: NaN
    property string nomLieu: ""
    property var meteo: null          // { temp, code, jour, vent, min, max }
    property string etatMeteo: "chargement"

    readonly property string condition: Plasmoid.configuration.simulation
        ? Plasmoid.configuration.simulation : (meteo ? conditionDe(meteo.code) : "soleil")

    function conditionDe(code) {
        if (code === 0) return "soleil"
        if (code <= 2) return "peu-nuageux"
        if (code === 3) return "nuageux"
        if (code === 45 || code === 48) return "brouillard"
        if ((code >= 71 && code <= 77) || code === 85 || code === 86) return "neige"
        if (code >= 95) return "orage"
        if (code >= 51) return "pluie"
        return "nuageux"
    }
    function texteDe(code) {
        var t = { 0: "Ciel dégagé", 1: "Plutôt ensoleillé", 2: "Partiellement nuageux", 3: "Couvert",
                  45: "Brouillard", 48: "Brouillard givrant", 51: "Bruine légère", 53: "Bruine", 55: "Bruine forte",
                  56: "Bruine verglaçante", 57: "Bruine verglaçante", 61: "Pluie faible", 63: "Pluie", 65: "Pluie forte",
                  66: "Pluie verglaçante", 67: "Pluie verglaçante", 71: "Neige faible", 73: "Neige", 75: "Neige forte",
                  77: "Grains de neige", 80: "Averses", 81: "Averses", 82: "Fortes averses", 85: "Averses de neige",
                  86: "Averses de neige", 95: "Orage", 96: "Orage et grêle", 99: "Orage et grêle" }
        return t[code] || ""
    }
    function telecharger(url, suite) {
        var x = new XMLHttpRequest()
        x.onreadystatechange = function () {
            if (x.readyState !== XMLHttpRequest.DONE) return
            if (x.status === 200) {
                try { suite(JSON.parse(x.responseText)) } catch (e) { racine.etatMeteo = "erreur" }
            } else {
                racine.etatMeteo = "hors-ligne"
            }
        }
        x.open("GET", url)
        x.send()
    }
    function actualiserMeteo() {
        if (isNaN(latitude)) {
            telecharger("https://geocoding-api.open-meteo.com/v1/search?count=1&language=fr&name="
                        + encodeURIComponent(ville), function (r) {
                if (!r.results || !r.results.length) { racine.etatMeteo = "ville-inconnue"; return }
                racine.latitude = r.results[0].latitude
                racine.longitude = r.results[0].longitude
                racine.nomLieu = r.results[0].name
                actualiserMeteo()
            })
            return
        }
        telecharger("https://api.open-meteo.com/v1/forecast?latitude=" + latitude + "&longitude=" + longitude
                    + "&current=temperature_2m,weather_code,is_day,wind_speed_10m"
                    + "&daily=temperature_2m_max,temperature_2m_min&forecast_days=1&timezone=auto", function (r) {
            racine.meteo = { temp: r.current.temperature_2m, code: r.current.weather_code, jour: r.current.is_day === 1,
                             vent: r.current.wind_speed_10m, min: r.daily.temperature_2m_min[0],
                             max: r.daily.temperature_2m_max[0] }
            racine.etatMeteo = "ok"
        })
    }
    onVilleChanged: { latitude = NaN; actualiserMeteo() }
    Timer { interval: 15 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: racine.actualiserMeteo() }
    Timer { interval: 1000; running: true; repeat: true; onTriggered: racine.maintenant = new Date() }

    // ---------- Notifications (historique)
    NotificationManager.Notifications {
        id: historique
        showExpired: true
        showDismissed: true
        showJobs: false
        groupMode: NotificationManager.Notifications.GroupDisabled
        sortMode: NotificationManager.Notifications.SortByDate
    }

    toolTipMainText: maintenant.toLocaleDateString(Qt.locale(), "dddd d MMMM yyyy")
    toolTipSubText: meteo ? Math.round(meteo.temp) + " °C · " + texteDe(meteo.code) : ""

    // ---------- Dans la barre des tâches
    compactRepresentation: MouseArea {
        Layout.minimumWidth: colonne.implicitWidth + Kirigami.Units.smallSpacing * 2
        Layout.preferredWidth: Layout.minimumWidth
        onClicked: racine.expanded = !racine.expanded
        Column {
            id: colonne
            anchors.centerIn: parent
            PlasmaComponents.Label {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatTime(racine.maintenant, "HH:mm")
                font.bold: true
            }
            PlasmaComponents.Label {
                anchors.horizontalCenter: parent.horizontalCenter
                text: Qt.formatDate(racine.maintenant, "dd/MM/yyyy")
                font.pixelSize: Kirigami.Theme.smallFont.pixelSize
            }
        }
    }

    // ---------- Le panneau
    fullRepresentation: Item {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 24
        Layout.preferredHeight: Kirigami.Units.gridUnit * 40
        Layout.minimumWidth: Kirigami.Units.gridUnit * 20
        Layout.minimumHeight: Kirigami.Units.gridUnit * 30

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Kirigami.Units.smallSpacing
            spacing: Kirigami.Units.largeSpacing

            // Heure et date
            ColumnLayout {
                spacing: 0
                PlasmaComponents.Label {
                    text: Qt.formatTime(racine.maintenant, "HH:mm")
                    color: racine.orClair
                    font.pixelSize: Kirigami.Units.gridUnit * 2.4
                    font.weight: Font.Light
                }
                PlasmaComponents.Label {
                    text: { var t = racine.maintenant.toLocaleDateString(Qt.locale(), "dddd d MMMM yyyy"); return t.charAt(0).toUpperCase() + t.slice(1) }
                    opacity: 0.85
                }
            }

            // Météo animée
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.gridUnit * 9
                Meteo {
                    anchors.fill: parent
                    condition: racine.condition
                    jour: racine.meteo ? racine.meteo.jour : (racine.maintenant.getHours() >= 7 && racine.maintenant.getHours() < 20)
                }
                Rectangle {  // liseré doré
                    anchors.fill: parent; radius: 14; color: "transparent"
                    border.color: Qt.rgba(0.83, 0.65, 0.17, 0.6); border.width: 1
                }
                Column {
                    anchors { right: parent.right; top: parent.top; margins: Kirigami.Units.largeSpacing }
                    spacing: 2
                    Text {
                        anchors.right: parent.right
                        text: racine.meteo ? Math.round(racine.meteo.temp) + " °C" : "—"
                        color: "white"; font.pixelSize: Kirigami.Units.gridUnit * 2.2; font.bold: true
                        style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.35)
                    }
                    Text {
                        anchors.right: parent.right
                        text: racine.meteo ? racine.texteDe(racine.meteo.code)
                              : racine.etatMeteo === "chargement" ? "Chargement de la météo…"
                              : racine.etatMeteo === "ville-inconnue" ? "Ville introuvable : " + racine.ville
                              : "Météo indisponible (pas de connexion)"
                        color: "white"; font.bold: true
                        style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.35)
                    }
                }
                Text {
                    anchors { left: parent.left; bottom: parent.bottom; margins: Kirigami.Units.largeSpacing }
                    text: (racine.nomLieu || racine.ville)
                          + (racine.meteo ? "   ·   min " + Math.round(racine.meteo.min) + "°  max " + Math.round(racine.meteo.max)
                             + "°   ·   vent " + Math.round(racine.meteo.vent) + " km/h" : "")
                    color: "white"
                    style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.4)
                }
            }

            // Calendrier
            PlasmaCalendar.MonthView {
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.gridUnit * 13
                today: racine.maintenant
                showWeekNumbers: false
            }

            // Notifications
            RowLayout {
                Layout.fillWidth: true
                Kirigami.Heading {
                    Layout.fillWidth: true
                    level: 4
                    text: "Notifications"
                    color: racine.orClair
                }
                PlasmaComponents.ToolButton {
                    text: "Tout effacer"
                    icon.name: "edit-clear-history"
                    visible: liste.count > 0
                    onClicked: historique.clear(NotificationManager.Notifications.ClearExpired)
                }
            }
            ListView {
                id: liste
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                spacing: Kirigami.Units.smallSpacing
                model: historique
                delegate: Rectangle {
                    width: ListView.view.width
                    height: contenu.implicitHeight + Kirigami.Units.largeSpacing
                    radius: 10
                    color: Qt.rgba(1, 1, 1, 0.06)
                    border.color: Qt.rgba(0.83, 0.65, 0.17, 0.35)
                    RowLayout {
                        id: contenu
                        anchors { left: parent.left; right: parent.right; verticalCenter: parent.verticalCenter
                                  margins: Kirigami.Units.smallSpacing }
                        Kirigami.Icon {
                            Layout.preferredWidth: Kirigami.Units.iconSizes.medium
                            Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                            Layout.alignment: Qt.AlignTop
                            source: model.applicationIconName || "preferences-desktop-notification"
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 0
                            RowLayout {
                                PlasmaComponents.Label {
                                    Layout.fillWidth: true
                                    text: model.summary || model.applicationName || ""
                                    font.bold: true
                                    elide: Text.ElideRight
                                }
                                PlasmaComponents.Label {
                                    text: model.created ? Qt.formatTime(model.created, "HH:mm") : ""
                                    opacity: 0.6
                                    font.pixelSize: Kirigami.Theme.smallFont.pixelSize
                                }
                            }
                            PlasmaComponents.Label {
                                Layout.fillWidth: true
                                text: model.body || ""
                                textFormat: Text.StyledText
                                wrapMode: Text.Wrap
                                maximumLineCount: 3
                                elide: Text.ElideRight
                                opacity: 0.85
                                visible: text.length > 0
                            }
                        }
                    }
                }
                PlasmaExtras.PlaceholderMessage {
                    anchors.centerIn: parent
                    width: parent.width - Kirigami.Units.gridUnit * 2
                    visible: liste.count === 0
                    iconName: "preferences-desktop-notification"
                    text: "Aucune notification"
                }
            }
        }
    }
}
