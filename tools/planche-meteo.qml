// Planche de test : toutes les météos de l'horloge protect.OS, côte à côte
import QtQuick
import "../packages/protectos-theme/root/usr/share/plasma/plasmoids/org.protectos.horloge/contents/ui"

Rectangle {
    width: 4 * 330 + 50; height: 2 * 210 + 40
    color: "#060f2e"
    Grid {
        x: 10; y: 10; columns: 4; spacing: 10
        Repeater {
            model: [["soleil", true], ["peu-nuageux", true], ["nuageux", true], ["pluie", true],
                    ["orage", true], ["neige", true], ["brouillard", true], ["soleil", false]]
            Item {
                width: 330; height: 210
                Meteo { anchors.fill: parent; condition: modelData[0]; jour: modelData[1] }
                Text { x: 10; y: 186; text: modelData[0] + (modelData[1] ? "" : " (nuit)"); color: "white"; font.bold: true }
            }
        }
    }
}
