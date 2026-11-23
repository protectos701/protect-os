// Écran affiché pendant l'ouverture de la session Plasma
import QtQuick

Rectangle {
    id: root
    property int stage

    gradient: Gradient {
        GradientStop { position: 0.0; color: "#16307a" }
        GradientStop { position: 1.0; color: "#060f2e" }
    }

    Column {
        anchors.centerIn: parent
        spacing: 26

        Image {
            anchors.horizontalCenter: parent.horizontalCenter
            source: "images/logo.png"
            width: 128
            height: 128
            sourceSize.width: 256
            sourceSize.height: 256
            smooth: true
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: "protect.OS"
            color: "#e8c15a"
            font.pixelSize: 30
            font.weight: Font.DemiBold
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            width: 220
            height: 4
            radius: 2
            color: "#33ffffff"

            Rectangle {
                height: parent.height
                radius: 2
                color: "#d4a72c"
                width: parent.width * Math.min(1, root.stage / 6)
                Behavior on width { NumberAnimation { duration: 450; easing.type: Easing.OutCubic } }
            }
        }
    }
}
