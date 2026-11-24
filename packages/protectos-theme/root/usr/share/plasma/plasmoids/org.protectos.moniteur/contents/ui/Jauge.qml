// Une jauge : anneau doré, pourcentage au centre, titre et détail dessous
import QtQuick
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Item {
    id: jauge
    property string titre: ""
    property real valeur: 0          // 0 à 100, ou -1 si non mesurable
    property string detail: ""
    readonly property color or: "#d4a72c"
    readonly property color orClair: "#f3d27a"

    ColumnLayout {
        anchors.fill: parent
        spacing: 2

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Canvas {
                id: anneau
                anchors.centerIn: parent
                width: Math.min(parent.width, parent.height)
                height: width
                onPaint: {
                    var ctx = getContext("2d");
                    ctx.reset();
                    var r = width / 2 - 6, cx = width / 2, cy = height / 2;
                    ctx.lineWidth = Math.max(5, width * 0.09);
                    ctx.lineCap = "round";
                    ctx.strokeStyle = Qt.rgba(1, 1, 1, 0.14);
                    ctx.beginPath(); ctx.arc(cx, cy, r, 0, 2 * Math.PI); ctx.stroke();
                    if (jauge.valeur >= 0) {
                        var g = ctx.createLinearGradient(0, 0, 0, height);
                        g.addColorStop(0, jauge.orClair); g.addColorStop(1, jauge.or);
                        ctx.strokeStyle = g;
                        ctx.beginPath();
                        ctx.arc(cx, cy, r, -Math.PI / 2, -Math.PI / 2 + 2 * Math.PI * Math.max(0.005, jauge.valeur / 100));
                        ctx.stroke();
                    }
                }
                Connections { target: jauge; function onValeurChanged() { anneau.requestPaint() } }
                onWidthChanged: requestPaint()
            }
            Text {
                anchors.centerIn: anneau
                text: jauge.valeur >= 0 ? Math.round(jauge.valeur) + " %" : "—"
                color: "#eef2fb"
                font.pixelSize: Math.max(11, anneau.width * 0.22)
                font.bold: true
            }
        }
        Text {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            text: jauge.titre
            color: jauge.orClair
            font.pixelSize: Kirigami.Theme.defaultFont.pixelSize * 1.05
            font.bold: true
            elide: Text.ElideRight
        }
        Text {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            text: jauge.detail
            color: Qt.rgba(0.93, 0.95, 0.98, 0.75)
            font.pixelSize: Kirigami.Theme.smallFont.pixelSize
            elide: Text.ElideRight
        }
    }
}
