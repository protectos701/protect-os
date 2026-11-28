// Widgets protect.OS (Windows+W) : la météo dans la barre des tâches, à gauche, comme Windows 11 ;
// au clic, un grand panneau avec la météo animée et les prévisions, les actualités, l'état de l'ordinateur
// et des raccourcis.
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: racine
    property date maintenant: new Date()
    property string ville: Plasmoid.configuration.ville || "Paris"
    property real latitude: NaN
    property real longitude: NaN
    property string nomLieu: ""
    property var meteo: null
    property var jours: []
    property string etatMeteo: "chargement"
    property var titres: []
    property var mesures: null
    readonly property var nomsJours: ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."]

    switchWidth: Kirigami.Units.gridUnit * 10
    switchHeight: Kirigami.Units.gridUnit * 10
    toolTipMainText: meteo ? Math.round(meteo.temp) + " °C · " + texteDe(meteo.code) : "Widgets"
    toolTipSubText: (nomLieu || ville) + " — Windows+W pour ouvrir les widgets"

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
        var t = { 0: "Ensoleillé", 1: "Plutôt ensoleillé", 2: "Éclaircies", 3: "Nuageux", 45: "Brouillard",
                  48: "Brouillard givrant", 51: "Bruine", 53: "Bruine", 55: "Bruine", 56: "Bruine verglaçante",
                  57: "Bruine verglaçante", 61: "Pluie faible", 63: "Pluie", 65: "Pluie forte", 66: "Pluie verglaçante",
                  67: "Pluie verglaçante", 71: "Neige faible", 73: "Neige", 75: "Neige forte", 77: "Grains de neige",
                  80: "Averses", 81: "Averses", 82: "Fortes averses", 85: "Averses de neige", 86: "Averses de neige",
                  95: "Orage", 96: "Orage et grêle", 99: "Orage et grêle" }
        return t[code] || ""
    }
    function iconeDe(code, jour) {
        var c = conditionDe(code)
        if (c === "soleil") return jour ? "weather-clear" : "weather-clear-night"
        if (c === "peu-nuageux") return jour ? "weather-few-clouds" : "weather-few-clouds-night"
        if (c === "nuageux") return "weather-overcast"
        if (c === "brouillard") return "weather-fog"
        if (c === "neige") return "weather-snow"
        if (c === "orage") return "weather-storm"
        return "weather-showers"
    }
    function telecharger(url, suite, brut) {
        var x = new XMLHttpRequest()
        x.onreadystatechange = function () {
            if (x.readyState !== XMLHttpRequest.DONE) return
            if (x.status === 200) {
                try { suite(brut ? x.responseText : JSON.parse(x.responseText)) } catch (e) { }
            } else if (!brut) {
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
                    + "&current=temperature_2m,apparent_temperature,weather_code,is_day,wind_speed_10m,relative_humidity_2m"
                    + "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
                    + "&forecast_days=5&timezone=auto", function (r) {
            racine.meteo = { temp: r.current.temperature_2m, ressenti: r.current.apparent_temperature,
                             code: r.current.weather_code, jour: r.current.is_day === 1,
                             vent: r.current.wind_speed_10m, humidite: r.current.relative_humidity_2m }
            var j = []
            for (var i = 0; i < r.daily.time.length; i++) {
                var d = new Date(r.daily.time[i] + "T12:00:00")
                j.push({ nom: i === 0 ? "Auj." : racine.nomsJours[d.getDay()], code: r.daily.weather_code[i],
                         max: r.daily.temperature_2m_max[i], min: r.daily.temperature_2m_min[i],
                         pluie: r.daily.precipitation_probability_max ? r.daily.precipitation_probability_max[i] : null })
            }
            racine.jours = j
            racine.etatMeteo = "ok"
        })
    }
    function decoder(t) {
        return t.replace(/<!\[CDATA\[|\]\]>/g, "").replace(/&amp;/g, "&").replace(/&quot;/g, "\"")
                .replace(/&#039;|&#39;|&apos;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
                .replace(/&#8217;/g, "’").replace(/&nbsp;/g, " ").trim()
    }
    function actualiserTitres() {
        var flux = Plasmoid.configuration.actualites
        if (!flux) { titres = []; return }
        telecharger(flux, function (xml) {
            var items = xml.split(/<item[\s>]/).slice(1)
            var liste = []
            for (var i = 0; i < items.length && liste.length < 6; i++) {
                var t = /<title>([\s\S]*?)<\/title>/.exec(items[i])
                var l = /<link>([\s\S]*?)<\/link>/.exec(items[i])
                if (t && l) liste.push({ titre: decoder(t[1]), lien: decoder(l[1]) })
            }
            racine.titres = liste
        }, true)
    }
    onVilleChanged: { latitude = NaN; actualiserMeteo() }
    Timer { interval: 15 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: racine.actualiserMeteo() }
    Timer { interval: 30 * 60 * 1000; running: true; repeat: true; triggeredOnStart: true; onTriggered: racine.actualiserTitres() }
    Timer { interval: 30000; running: true; repeat: true; onTriggered: racine.maintenant = new Date() }

    P5Support.DataSource {
        id: commandes
        engine: "executable"
        connectedSources: []
        onNewData: function (nom, donnees) {
            if (nom.indexOf("protectos-mesures") >= 0) {
                try { racine.mesures = JSON.parse(donnees["stdout"]) } catch (e) { }
            }
            disconnectSource(nom)
        }
    }
    function ouvrir(cmd) {
        commandes.connectSource(cmd + " >/dev/null 2>&1 &")
        racine.expanded = false
    }
    Timer {
        interval: 3000; repeat: true; running: racine.expanded; triggeredOnStart: true
        onTriggered: commandes.connectSource("/usr/lib/protectos/protectos-mesures")
    }
    onExpandedChanged: if (expanded) actualiserTitres()

    // ---------- Dans la barre des tâches : icône et température
    compactRepresentation: MouseArea {
        Layout.minimumWidth: ligne.implicitWidth + Kirigami.Units.largeSpacing * 2
        Layout.preferredWidth: Layout.minimumWidth
        hoverEnabled: true
        onClicked: racine.expanded = !racine.expanded
        Rectangle {
            anchors.fill: parent; anchors.margins: 2; radius: 5
            color: Qt.rgba(1, 1, 1, parent.containsMouse || racine.expanded ? 0.1 : 0)
        }
        RowLayout {
            id: ligne
            anchors.centerIn: parent
            spacing: Kirigami.Units.smallSpacing
            Kirigami.Icon {
                source: racine.meteo ? racine.iconeDe(racine.meteo.code, racine.meteo.jour) : "weather-none-available"
                Layout.preferredWidth: Kirigami.Units.iconSizes.smallMedium; Layout.preferredHeight: Layout.preferredWidth
            }
            ColumnLayout {
                spacing: 0
                PlasmaComponents.Label {
                    text: racine.meteo ? Math.round(racine.meteo.temp) + " °C" : "Widgets"
                    font.bold: true
                }
                PlasmaComponents.Label {
                    visible: racine.meteo !== null
                    text: racine.meteo ? racine.texteDe(racine.meteo.code) : ""
                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                    opacity: 0.8
                }
            }
        }
    }

    // ---------- Le panneau des widgets
    fullRepresentation: Flickable {
        Layout.preferredWidth: Kirigami.Units.gridUnit * 34
        Layout.preferredHeight: Kirigami.Units.gridUnit * 36
        Layout.minimumWidth: Kirigami.Units.gridUnit * 26
        Layout.minimumHeight: Kirigami.Units.gridUnit * 20
        contentHeight: colonne.implicitHeight + Kirigami.Units.largeSpacing * 2
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        ColumnLayout {
            id: colonne
            width: parent.width - Kirigami.Units.largeSpacing * 2
            x: Kirigami.Units.largeSpacing
            y: Kirigami.Units.largeSpacing
            spacing: Kirigami.Units.largeSpacing

            RowLayout {
                PlasmaComponents.Label {
                    text: { var h = racine.maintenant.getHours(); return h < 6 || h >= 18 ? "Bonsoir" : "Bonjour" }
                    font.pointSize: Kirigami.Theme.defaultFont.pointSize * 1.6
                    font.bold: true
                }
                Item { Layout.fillWidth: true }
                PlasmaComponents.Label {
                    text: { var t = racine.maintenant.toLocaleDateString(Qt.locale(), "dddd d MMMM"); return t.charAt(0).toUpperCase() + t.slice(1) }
                    opacity: 0.8
                }
            }

            // Météo
            Carte {
                titre: "Météo · " + (racine.nomLieu || racine.ville)
                icone: "weather-few-clouds"
                ColumnLayout {
                    width: parent.width
                    spacing: Kirigami.Units.largeSpacing
                    Item {
                        Layout.fillWidth: true
                        Layout.preferredHeight: Kirigami.Units.gridUnit * 8
                        Meteo {
                            anchors.fill: parent
                            condition: racine.meteo ? racine.conditionDe(racine.meteo.code) : "soleil"
                            jour: racine.meteo ? racine.meteo.jour : true
                        }
                        Column {
                            anchors { left: parent.left; bottom: parent.bottom; margins: Kirigami.Units.largeSpacing }
                            Text {
                                text: racine.meteo ? Math.round(racine.meteo.temp) + " °C" : "—"
                                color: "white"; font.pixelSize: Kirigami.Units.gridUnit * 2.4; font.bold: true
                                style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.35)
                            }
                            Text {
                                text: racine.meteo ? racine.texteDe(racine.meteo.code) + " · ressenti " + Math.round(racine.meteo.ressenti) + " °C"
                                      : racine.etatMeteo === "chargement" ? "Chargement…"
                                      : racine.etatMeteo === "ville-inconnue" ? "Ville introuvable : " + racine.ville
                                      : "Météo indisponible (pas de connexion)"
                                color: "white"; font.bold: true
                                style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.35)
                            }
                        }
                        Text {
                            visible: racine.meteo !== null
                            anchors { right: parent.right; bottom: parent.bottom; margins: Kirigami.Units.largeSpacing }
                            horizontalAlignment: Text.AlignRight
                            text: racine.meteo ? "Vent " + Math.round(racine.meteo.vent) + " km/h\nHumidité " + racine.meteo.humidite + " %" : ""
                            color: "white"; style: Text.Raised; styleColor: Qt.rgba(0, 0, 0, 0.35)
                        }
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        visible: racine.jours.length > 0
                        Repeater {
                            model: racine.jours
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                PlasmaComponents.Label { Layout.alignment: Qt.AlignHCenter; text: modelData.nom; font.bold: index === 0 }
                                Kirigami.Icon {
                                    Layout.alignment: Qt.AlignHCenter
                                    source: racine.iconeDe(modelData.code, true)
                                    Layout.preferredWidth: Kirigami.Units.iconSizes.medium; Layout.preferredHeight: Layout.preferredWidth
                                }
                                PlasmaComponents.Label { Layout.alignment: Qt.AlignHCenter; text: Math.round(modelData.max) + "° " + Math.round(modelData.min) + "°" }
                                PlasmaComponents.Label {
                                    Layout.alignment: Qt.AlignHCenter
                                    visible: modelData.pluie !== null && modelData.pluie >= 20
                                    text: "💧 " + modelData.pluie + " %"
                                    font.pointSize: Kirigami.Theme.smallFont.pointSize
                                    opacity: 0.8
                                }
                            }
                        }
                    }
                }
            }

            // État de l'ordinateur et raccourcis
            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                Carte {
                    titre: "Mon ordinateur"
                    icone: "computer"
                    Layout.preferredWidth: 1
                    ColumnLayout {
                        width: parent.width
                        Repeater {
                            model: [
                                { nom: "Processeur", cle: "cpu" },
                                { nom: "Mémoire", cle: "mem" },
                                { nom: "Disque", cle: "disque" }
                            ]
                            delegate: ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                RowLayout {
                                    PlasmaComponents.Label { text: modelData.nom; Layout.fillWidth: true }
                                    PlasmaComponents.Label {
                                        text: racine.mesures ? Math.round(racine.mesures[modelData.cle]) + " %" : "…"
                                        opacity: 0.8
                                    }
                                }
                                Rectangle {
                                    Layout.fillWidth: true; height: 6; radius: 3; color: Qt.rgba(1, 1, 1, 0.12)
                                    Rectangle {
                                        height: parent.height; radius: 3
                                        width: parent.width * Math.min(1, (racine.mesures ? racine.mesures[modelData.cle] : 0) / 100)
                                        color: width > parent.width * 0.9 ? "#d9534f" : "#d4a72c"
                                        Behavior on width { NumberAnimation { duration: 400 } }
                                    }
                                }
                            }
                        }
                    }
                }
                Carte {
                    titre: "Raccourcis"
                    icone: "bookmarks"
                    Layout.preferredWidth: 1
                    GridLayout {
                        width: parent.width
                        columns: 2
                        Repeater {
                            model: [
                                { nom: "Ce PC", icone: "computer", cmd: "protectos-ce-pc" },
                                { nom: "Documents", icone: "folder-documents", cmd: "xdg-open \"$(xdg-user-dir DOCUMENTS)\"" },
                                { nom: "Magasin", icone: "plasmadiscover", cmd: "protectos-magasin" },
                                { nom: "Paramètres", icone: "preferences-system", cmd: "protectos-parametres" }
                            ]
                            delegate: PlasmaComponents.ToolButton {
                                Layout.fillWidth: true
                                icon.name: modelData.icone
                                text: modelData.nom
                                display: PlasmaComponents.AbstractButton.TextUnderIcon
                                onClicked: racine.ouvrir(modelData.cmd)
                            }
                        }
                    }
                }
            }

            // Actualités
            Carte {
                visible: racine.titres.length > 0
                titre: "À la une"
                icone: "news-subscribe"
                ColumnLayout {
                    width: parent.width
                    spacing: Kirigami.Units.smallSpacing
                    Repeater {
                        model: racine.titres
                        delegate: PlasmaComponents.ItemDelegate {
                            Layout.fillWidth: true
                            contentItem: PlasmaComponents.Label {
                                text: "• " + modelData.titre
                                wrapMode: Text.WordWrap
                                maximumLineCount: 2
                                elide: Text.ElideRight
                            }
                            onClicked: { Qt.openUrlExternally(modelData.lien); racine.expanded = false }
                        }
                    }
                }
            }
        }
    }
}
