// Tuile des Paramètres rapides : dorée quand le réglage est activé, comme Windows 11
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Item {
    id: tuile
    property string titre
    property string sousTitre: ""
    property string icone
    property bool actif: false
    property bool disponible: true
    property bool avecReglages: false
    signal basculer()
    signal reglages()

    Layout.fillWidth: true
    Layout.preferredHeight: Kirigami.Units.gridUnit * 3.6
    opacity: disponible ? 1 : 0.45

    Rectangle {
        id: fond
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Kirigami.Units.gridUnit * 2.4
        radius: 7
        color: tuile.actif ? "#d4a72c" : (zone.containsMouse ? Qt.rgba(1, 1, 1, 0.14) : Qt.rgba(1, 1, 1, 0.08))
        border.color: tuile.actif ? "#f3d27a" : Qt.rgba(1, 1, 1, 0.18)
        Behavior on color { ColorAnimation { duration: 150 } }

        Kirigami.Icon {
            anchors.verticalCenter: parent.verticalCenter
            x: tuile.avecReglages ? (parent.width * 0.6 - width) / 2 : (parent.width - width) / 2
            width: Kirigami.Units.iconSizes.smallMedium
            height: width
            source: tuile.icone
            color: tuile.actif ? "#0a1a52" : Kirigami.Theme.textColor
            isMask: true
        }
        MouseArea {
            id: zone
            anchors.fill: parent
            anchors.rightMargin: tuile.avecReglages ? parent.width * 0.4 : 0
            hoverEnabled: true
            enabled: tuile.disponible
            cursorShape: Qt.PointingHandCursor
            onClicked: tuile.basculer()
        }
        Rectangle {
            visible: tuile.avecReglages
            x: parent.width * 0.6
            width: 1
            height: parent.height * 0.6
            anchors.verticalCenter: parent.verticalCenter
            color: tuile.actif ? Qt.rgba(0.04, 0.1, 0.32, 0.35) : Qt.rgba(1, 1, 1, 0.2)
        }
        Kirigami.Icon {
            visible: tuile.avecReglages
            anchors.verticalCenter: parent.verticalCenter
            x: parent.width * 0.8 - width / 2
            width: Kirigami.Units.iconSizes.small
            height: width
            source: "go-next"
            color: tuile.actif ? "#0a1a52" : Kirigami.Theme.textColor
            isMask: true
            MouseArea {
                anchors.fill: parent
                anchors.margins: -8
                cursorShape: Qt.PointingHandCursor
                onClicked: tuile.reglages()
            }
        }
    }
    PlasmaComponents.Label {
        anchors.top: fond.bottom
        anchors.topMargin: 3
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        horizontalAlignment: Text.AlignHCenter
        elide: Text.ElideRight
        font.pointSize: Kirigami.Theme.smallFont.pointSize
        text: tuile.sousTitre || tuile.titre
    }
}
