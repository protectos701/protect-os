// Écran de connexion de protect.OS (SDDM, Qt 6)
// Uniquement QtQuick de base : aucun module supplémentaire n'est nécessaire.
import QtQuick

Rectangle {
    id: racine
    width: 1920
    height: 1080
    color: "#060f2e"

    readonly property color or: config.accent || "#d4a72c"
    readonly property color orClair: Qt.lighter(or, 1.35)
    readonly property color bleu: config.principale || "#0a1a52"
    readonly property color texte: "#eef2fb"
    readonly property string nomSysteme: config.nom || "protect.OS"
    readonly property real u: Math.max(0.6, Math.min(width / 1920, height / 1080))  // échelle

    property int indexUtilisateur: Math.max(0, userModel.lastIndex)
    property int indexSession: Math.max(0, sessionModel.lastIndex)
    property string erreur: ""

    // ---------- Données des comptes et des sessions
    Repeater {
        id: comptes
        model: userModel
        delegate: Item {
            visible: false
            property string identifiant: model.name
            property string nomAffiche: (model.realName && model.realName.length) ? model.realName : model.name
        }
    }
    Repeater {
        id: sessions
        model: sessionModel
        delegate: Item {
            visible: false
            property string nomSession: model.name
        }
    }
    function compte(i) { return comptes.count > 0 ? comptes.itemAt(Math.min(i, comptes.count - 1)) : null }
    function identifiant() { var c = compte(indexUtilisateur); return c ? c.identifiant : (userModel.lastUser || "") }
    function nomAffiche() { var c = compte(indexUtilisateur); return c ? c.nomAffiche : (userModel.lastUser || "") }
    function initiale() { var n = nomAffiche(); return n.length ? n.charAt(0).toUpperCase() : "?" }
    function nomSession() { var s = sessions.itemAt(indexSession); return s ? s.nomSession : nomSysteme }

    function alimentation(action) {
        if (action === "session") indexSession = (indexSession + 1) % sessions.count
        else if (action === "veille") sddm.suspend()
        else if (action === "redemarrer") sddm.reboot()
        else if (action === "eteindre") sddm.powerOff()
    }

    function seConnecter() {
        if (attente.running) return
        erreur = ""
        attente.start()
        sddm.login(identifiant(), motDePasse.text, indexSession)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            attente.stop()
            motDePasse.text = ""
            erreur = "Mot de passe incorrect. Réessayez."
            secousse.restart()
            motDePasse.forceActiveFocus()
        }
        function onLoginSucceeded() { attente.stop() }
    }
    Timer { id: attente; interval: 30000 }

    // ---------- Fond : image floutée par un voile bleu
    Image {
        anchors.fill: parent
        source: config.background || ""
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        smooth: true
    }
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0.02, 0.06, 0.18, 0.35) }
            GradientStop { position: 1.0; color: Qt.rgba(0.01, 0.03, 0.12, 0.78) }
        }
    }

    // ---------- Logo et nom, en haut à gauche
    Row {
        x: 48 * racine.u; y: 40 * racine.u
        spacing: 14 * racine.u
        Image { source: "logo.png"; width: 46 * racine.u; height: 46 * racine.u; smooth: true; mipmap: true }
        Text {
            anchors.verticalCenter: parent.verticalCenter
            text: nomSysteme; color: racine.orClair
            font.pixelSize: 24 * racine.u; font.bold: true
        }
    }

    // ---------- Horloge
    Column {
        id: horloge
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height * 0.12
        spacing: 2 * racine.u
        property var maintenant: new Date()
        Timer { interval: 1000; running: true; repeat: true; onTriggered: horloge.maintenant = new Date() }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(horloge.maintenant, "HH:mm")
            color: racine.orClair
            font.pixelSize: 112 * racine.u; font.weight: Font.Light
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: { var t = horloge.maintenant.toLocaleDateString(Qt.locale("fr_FR"), "dddd d MMMM"); return t.charAt(0).toUpperCase() + t.slice(1) }
            color: racine.texte
            font.pixelSize: 26 * racine.u
        }
    }

    // ---------- Carte de connexion en verre
    Rectangle {
        id: carte
        width: 420 * racine.u
        height: contenu.height + 56 * racine.u
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: secousse.decalage
        y: parent.height * 0.42
        radius: 22 * racine.u
        color: Qt.rgba(0.05, 0.10, 0.28, 0.55)
        border.color: Qt.rgba(racine.or.r, racine.or.g, racine.or.b, 0.55)
        border.width: 1.5

        Rectangle {  // reflet du verre
            anchors { left: parent.left; right: parent.right; top: parent.top; margins: 1.5 }
            height: parent.height * 0.45
            radius: parent.radius
            gradient: Gradient {
                GradientStop { position: 0.0; color: Qt.rgba(1, 1, 1, 0.10) }
                GradientStop { position: 1.0; color: Qt.rgba(1, 1, 1, 0.0) }
            }
        }

        SequentialAnimation {
            id: secousse
            property real decalage: 0
            NumberAnimation { target: secousse; property: "decalage"; to: -14; duration: 50 }
            NumberAnimation { target: secousse; property: "decalage"; to: 14; duration: 80 }
            NumberAnimation { target: secousse; property: "decalage"; to: -8; duration: 70 }
            NumberAnimation { target: secousse; property: "decalage"; to: 0; duration: 60 }
        }

        Column {
            id: contenu
            anchors.horizontalCenter: parent.horizontalCenter
            y: 28 * racine.u
            width: parent.width - 56 * racine.u
            spacing: 16 * racine.u

            Rectangle {  // avatar : initiale dorée dans un cercle
                anchors.horizontalCenter: parent.horizontalCenter
                width: 104 * racine.u; height: width; radius: width / 2
                gradient: Gradient {
                    GradientStop { position: 0.0; color: "#2a4fb8" }
                    GradientStop { position: 1.0; color: racine.bleu }
                }
                border.color: racine.or; border.width: 3
                Text {
                    anchors.centerIn: parent
                    text: racine.initiale()
                    color: racine.orClair
                    font.pixelSize: 50 * racine.u; font.bold: true
                }
            }
            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: racine.nomAffiche()
                color: racine.texte
                font.pixelSize: 26 * racine.u; font.bold: true
            }

            Rectangle {  // champ du mot de passe
                width: parent.width; height: 52 * racine.u; radius: 26 * racine.u
                color: Qt.rgba(0, 0, 0, 0.30)
                border.color: motDePasse.activeFocus ? racine.or : Qt.rgba(1, 1, 1, 0.22)
                border.width: 1.5
                TextInput {
                    id: motDePasse
                    anchors { left: parent.left; right: bouton.left; verticalCenter: parent.verticalCenter
                              leftMargin: 22 * racine.u; rightMargin: 10 * racine.u }
                    echoMode: TextInput.Password
                    passwordCharacter: "●"
                    color: racine.texte
                    selectionColor: racine.or
                    font.pixelSize: 20 * racine.u
                    clip: true
                    focus: true
                    onAccepted: racine.seConnecter()
                    Keys.onEscapePressed: text = ""
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: motDePasse.text.length === 0
                        text: "Mot de passe"
                        color: Qt.rgba(1, 1, 1, 0.45)
                        font.pixelSize: 19 * racine.u
                    }
                }
                Rectangle {  // bouton flèche doré
                    id: bouton
                    anchors { right: parent.right; verticalCenter: parent.verticalCenter; rightMargin: 5 * racine.u }
                    width: 42 * racine.u; height: width; radius: width / 2
                    color: zoneBouton.containsMouse ? racine.orClair : racine.or
                    Text {
                        anchors.centerIn: parent
                        text: attente.running ? "…" : "→"
                        color: "#1a1405"
                        font.pixelSize: 24 * racine.u; font.bold: true
                    }
                    MouseArea { id: zoneBouton; anchors.fill: parent; hoverEnabled: true; onClicked: racine.seConnecter() }
                }
            }

            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                visible: text.length > 0
                text: racine.erreur.length ? racine.erreur
                      : (keyboard && keyboard.capsLock ? "La touche Verr. Maj est activée." : "")
                color: racine.erreur.length ? "#ff8a80" : racine.orClair
                font.pixelSize: 16 * racine.u
            }
        }
    }

    // ---------- Autres comptes (s'il y en a plusieurs)
    Row {
        anchors { left: parent.left; bottom: parent.bottom; leftMargin: 48 * racine.u; bottomMargin: 40 * racine.u }
        spacing: 10 * racine.u
        visible: comptes.count > 1
        Repeater {
            model: userModel
            delegate: Rectangle {
                height: 44 * racine.u; width: etiquette.implicitWidth + 64 * racine.u; radius: 22 * racine.u
                color: index === racine.indexUtilisateur ? Qt.rgba(racine.or.r, racine.or.g, racine.or.b, 0.25)
                                                         : Qt.rgba(0.05, 0.10, 0.28, 0.55)
                border.color: Qt.rgba(racine.or.r, racine.or.g, racine.or.b, 0.55)
                Rectangle {
                    x: 6 * racine.u; anchors.verticalCenter: parent.verticalCenter
                    width: 32 * racine.u; height: width; radius: width / 2; color: racine.bleu
                    border.color: racine.or
                    Text { anchors.centerIn: parent; color: racine.orClair; font.bold: true; font.pixelSize: 15 * racine.u
                           text: ((model.realName && model.realName.length) ? model.realName : model.name).charAt(0).toUpperCase() }
                }
                Text {
                    id: etiquette
                    x: 46 * racine.u; anchors.verticalCenter: parent.verticalCenter
                    text: (model.realName && model.realName.length) ? model.realName : model.name
                    color: racine.texte; font.pixelSize: 16 * racine.u
                }
                MouseArea {
                    anchors.fill: parent
                    onClicked: { racine.indexUtilisateur = index; racine.erreur = ""; motDePasse.text = ""; motDePasse.forceActiveFocus() }
                }
            }
        }
    }

    // ---------- Session et alimentation, en bas à droite
    Row {
        anchors { right: parent.right; bottom: parent.bottom; rightMargin: 48 * racine.u; bottomMargin: 40 * racine.u }
        spacing: 10 * racine.u

        Repeater {
            model: [
                { libelle: racine.nomSession(), action: "session", visible: sessions.count > 1 },
                { libelle: "Veille", action: "veille", visible: sddm.canSuspend },
                { libelle: "Redémarrer", action: "redemarrer", visible: sddm.canReboot },
                { libelle: "Éteindre", action: "eteindre", visible: sddm.canPowerOff }
            ]
            delegate: Rectangle {
                visible: modelData.visible
                height: 44 * racine.u; width: lib.implicitWidth + 36 * racine.u; radius: 22 * racine.u
                color: zone.containsMouse ? Qt.rgba(racine.or.r, racine.or.g, racine.or.b, 0.30) : Qt.rgba(0.05, 0.10, 0.28, 0.55)
                border.color: Qt.rgba(racine.or.r, racine.or.g, racine.or.b, 0.55)
                Text { id: lib; anchors.centerIn: parent; text: modelData.libelle; color: racine.texte; font.pixelSize: 16 * racine.u }
                MouseArea { id: zone; anchors.fill: parent; hoverEnabled: true; onClicked: racine.alimentation(modelData.action) }
            }
        }
    }

    Component.onCompleted: motDePasse.forceActiveFocus()
}
