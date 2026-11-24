// Moniteur protect.OS : processeur, carte graphique, mémoire et disque, mis à jour toutes les 2 secondes
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami

PlasmoidItem {
    id: racine
    preferredRepresentation: fullRepresentation
    readonly property string commande: "/usr/lib/protectos/protectos-mesures"
    property var m: ({ cpu: 0, cpuTxt: "", gpu: -1, gpuTxt: "", mem: 0, memTxt: "", disque: 0, disqueTxt: "" })

    P5Support.DataSource {
        id: source
        engine: "executable"
        connectedSources: []
        onNewData: function (nom, donnees) {
            try { racine.m = JSON.parse(donnees["stdout"]) } catch (e) { }
            disconnectSource(nom)
        }
    }
    Timer {
        interval: 2000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: source.connectSource(racine.commande)
    }

    fullRepresentation: GridLayout {
        Layout.minimumWidth: Kirigami.Units.gridUnit * 8
        Layout.minimumHeight: Kirigami.Units.gridUnit * 8
        Layout.preferredWidth: Kirigami.Units.gridUnit * 11
        Layout.preferredHeight: Kirigami.Units.gridUnit * 34
        // En colonne si le gadget est haut, en carré 2×2 sinon
        columns: height > width * 1.8 ? 1 : 2
        rowSpacing: Kirigami.Units.largeSpacing
        columnSpacing: Kirigami.Units.largeSpacing

        Jauge { Layout.fillWidth: true; Layout.fillHeight: true; titre: "Processeur"; valeur: racine.m.cpu; detail: racine.m.cpuTxt }
        Jauge { Layout.fillWidth: true; Layout.fillHeight: true; titre: "Carte graphique"; valeur: racine.m.gpu; detail: racine.m.gpuTxt }
        Jauge { Layout.fillWidth: true; Layout.fillHeight: true; titre: "Mémoire"; valeur: racine.m.mem; detail: racine.m.memTxt }
        Jauge { Layout.fillWidth: true; Layout.fillHeight: true; titre: "Disque"; valeur: racine.m.disque; detail: racine.m.disqueTxt }
    }
}
