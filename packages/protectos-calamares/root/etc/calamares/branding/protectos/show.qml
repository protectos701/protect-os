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
        texte: "Un système rapide et protégé, en bleu et or, pensé pour vous."
    }
    ProtectSlide {
        titre: "Vos programmes Windows"
        texte: "Double-cliquez sur un .exe pour l'installer, ou choisissez parmi les programmes vérifiés du Magasin d'applications."
    }
    ProtectSlide {
        titre: "Protégé dès le premier jour"
        texte: "Antivirus, pare-feu, bloqueur de publicités et de pisteurs : tout se règle dans le Centre de protection."
    }
    ProtectSlide {
        titre: "La météo d'un clic"
        texte: "Cliquez sur l'heure : météo animée, calendrier et toutes vos notifications."
    }
    ProtectSlide {
        titre: "Des réglages simples"
        texte: "Le panneau Paramètres (Windows+I) rassemble le Wi-Fi, le son, l'affichage, le fond d'écran et le thème."
    }
    ProtectSlide {
        titre: "Pour toute la famille"
        texte: "Contrôle parental : temps d'écran, horaires et filtrage des sites pour chaque enfant."
    }
    ProtectSlide {
        titre: "Toujours à jour"
        texte: "Les correctifs de sécurité s'installent tout seuls, chaque jour, sans vous déranger."
    }

    function onActivate() { presentation.currentSlide = 0; }
    function onLeave() { }
}
