// Diaporama affiché pendant l'installation de protect.OS
import QtQuick
import calamares.slideshow 1.0

Presentation {
    id: presentation

    Timer {
        interval: 7000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }

    component ProtectSlide: Slide {
        property string titre
        property string texte
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#16307a" }
                GradientStop { position: 1.0; color: "#060f2e" }
            }
        }
        Column {
            anchors.centerIn: parent
            width: parent.width * 0.8
            spacing: 18
            Image {
                anchors.horizontalCenter: parent.horizontalCenter
                source: "logo.png"
                width: 96; height: 96
                sourceSize.width: 192; sourceSize.height: 192
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: titre
                color: "#e8c15a"
                font.pixelSize: 26
                font.weight: Font.DemiBold
                wrapMode: Text.WordWrap
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                text: texte
                color: "#eef2fb"
                font.pixelSize: 15
                wrapMode: Text.WordWrap
            }
        }
    }

    ProtectSlide {
        titre: "Bienvenue dans protect.OS"
        texte: "Un système libre et rapide, en bleu et or, construit sur Debian 13 et KDE Plasma 6."
    }
    ProtectSlide {
        titre: "Tout est prêt dès le départ"
        texte: "Firefox, LibreOffice, VLC, un explorateur de fichiers et un terminal sont déjà installés."
    }
    ProtectSlide {
        titre: "Des milliers d'applications"
        texte: "Ouvrez Discover, le magasin d'applications, pour installer jeux, logiciels créatifs et outils."
    }
    ProtectSlide {
        titre: "Toujours à jour"
        texte: "Les mises à jour de sécurité de Debian arrivent automatiquement dans Discover."
    }

    function onActivate() { presentation.currentSlide = 0; }
    function onLeave() { }
}
