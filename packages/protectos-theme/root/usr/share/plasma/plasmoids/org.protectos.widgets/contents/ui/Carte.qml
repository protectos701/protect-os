// Carte arrondie des widgets protect.OS
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.components as PlasmaComponents
import org.kde.kirigami as Kirigami

Rectangle {
    id: carte
    property string titre
    property string icone
    default property alias contenu: zone.data
    Layout.fillWidth: true
    implicitHeight: entete.height + zone.childrenRect.height + Kirigami.Units.largeSpacing * 3
    radius: 12
    color: Qt.rgba(1, 1, 1, 0.05)
    border.color: Qt.rgba(0.83, 0.65, 0.17, 0.35)
    RowLayout {
        id: entete
        anchors { left: parent.left; right: parent.right; top: parent.top; margins: Kirigami.Units.largeSpacing }
        Kirigami.Icon { source: carte.icone; Layout.preferredWidth: Kirigami.Units.iconSizes.small; Layout.preferredHeight: Layout.preferredWidth }
        PlasmaComponents.Label { text: carte.titre; font.bold: true; color: "#f3d27a"; Layout.fillWidth: true }
    }
    Item {
        id: zone
        anchors { left: parent.left; right: parent.right; top: entete.bottom; margins: Kirigami.Units.largeSpacing }
        height: childrenRect.height
    }
}
