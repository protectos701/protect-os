// Scène météo animée de protect.OS (uniquement dans le panneau de l'horloge).
// condition : "soleil", "peu-nuageux", "nuageux", "brouillard", "pluie", "neige", "orage"
// Les changements sont animés : quand le ciel se couvre, les nuages glissent devant le soleil.
import QtQuick

Item {
    id: scene
    property string condition: "soleil"
    property bool jour: true
    clip: true

    readonly property bool nuages: condition !== "soleil"
    readonly property real couverture: ({ "soleil": 0, "peu-nuageux": 0.45, "nuageux": 1, "brouillard": 1,
                                          "pluie": 1, "neige": 1, "orage": 1 })[condition] || 0
    readonly property bool sombre: condition === "pluie" || condition === "orage"

    // ---------- Ciel
    Rectangle {
        anchors.fill: parent
        radius: 14
        gradient: Gradient {
            GradientStop {
                position: 0
                color: !scene.jour ? "#050b24" : scene.sombre ? "#33415e" : scene.couverture > 0.8 ? "#5b6f96" : "#2f6fd6"
                Behavior on color { ColorAnimation { duration: 1500 } }
            }
            GradientStop {
                position: 1
                color: !scene.jour ? "#16307a" : scene.sombre ? "#5d6b86" : scene.couverture > 0.8 ? "#9aaacb" : "#8cc1ff"
                Behavior on color { ColorAnimation { duration: 1500 } }
            }
        }
    }

    // ---------- Étoiles (nuit)
    Repeater {
        model: 26
        Rectangle {
            readonly property real hasard: (index * 7919 % 100) / 100
            x: (index * 53 % 97) / 97 * scene.width
            y: (index * 37 % 61) / 61 * scene.height * 0.6
            width: 2 + hasard * 2; height: width; radius: width / 2
            color: "#fbe3a0"
            opacity: scene.jour ? 0 : 0.35 + hasard * 0.6
            Behavior on opacity { NumberAnimation { duration: 1500 } }
            SequentialAnimation on scale {
                loops: Animation.Infinite
                running: !scene.jour
                NumberAnimation { to: 0.4; duration: 900 + index * 90 }
                NumberAnimation { to: 1; duration: 900 + index * 90 }
            }
        }
    }

    // ---------- Soleil (jour) ou lune (nuit)
    Item {
        id: astre
        width: scene.height * 0.5; height: width
        x: scene.width * 0.16; y: scene.height * 0.14
        // Par ciel couvert, pluie, neige ou orage, le soleil (ou la lune) est presque caché
        opacity: scene.condition === "brouillard" ? 0.35 : scene.couverture >= 1 ? 0.28 : 1
        Behavior on opacity { NumberAnimation { duration: 1500 } }

        Item {  // rayons qui tournent
            anchors.fill: parent
            visible: scene.jour
            RotationAnimation on rotation { from: 0; to: 360; duration: 24000; loops: Animation.Infinite }
            Repeater {
                model: 12
                Rectangle {
                    x: astre.width / 2 - width / 2; y: -astre.width * 0.16
                    width: astre.width * 0.06; height: astre.width * 0.22; radius: width / 2
                    color: "#f6c945"; antialiasing: true
                    transform: Rotation { origin.x: width / 2; origin.y: astre.width * 0.66; angle: index * 30 }
                }
            }
        }
        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.68; height: width; radius: width / 2
            gradient: Gradient {
                GradientStop { position: 0; color: scene.jour ? "#ffe27a" : "#f4f1e3" }
                GradientStop { position: 1; color: scene.jour ? "#f0a92a" : "#c9c4ae" }
            }
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { to: 1.05; duration: 2200; easing.type: Easing.InOutSine }
                NumberAnimation { to: 1.0; duration: 2200; easing.type: Easing.InOutSine }
            }
            Rectangle {  // ombre de la lune
                visible: !scene.jour
                width: parent.width * 0.85; height: width; radius: width / 2
                x: parent.width * 0.32; y: -parent.width * 0.12
                color: "#0a1640"
            }
        }
    }

    // ---------- Nuages : ils arrivent de la droite et passent devant le soleil quand le ciel se couvre
    // (composant sans accès direct à « scene » : tout lui est transmis par propriétés)
    component Nuage: Item {
        id: n
        property real taille: 1
        property real vitesse: 30000
        property real hauteur: 0.2
        property bool visibleNuage: true
        property real largeurScene: 300
        property real hauteurScene: 160
        property color teinte: "#ffffff"
        width: largeurScene * 0.42 * taille; height: width * 0.5
        y: hauteurScene * hauteur
        opacity: visibleNuage ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 2500 } }
        property real deplacement: largeurScene
        x: deplacement
        NumberAnimation on deplacement {
            from: n.largeurScene + 10; to: -n.width - 10
            duration: n.vitesse; loops: Animation.Infinite; running: true
        }
        Rectangle { x: n.width * 0.05; y: n.height * 0.45; width: n.width * 0.9; height: n.height * 0.5; radius: height / 2; color: n.teinte }
        Rectangle { x: n.width * 0.18; y: n.height * 0.18; width: n.width * 0.38; height: width; radius: width / 2; color: n.teinte }
        Rectangle { x: n.width * 0.42; y: n.height * 0.02; width: n.width * 0.44; height: width; radius: width / 2; color: n.teinte }
    }
    readonly property color teinteNuage: sombre ? "#8b95aa" : jour ? "#ffffff" : "#56628a"

    Nuage { taille: 1.15; vitesse: 26000; hauteur: 0.16; visibleNuage: scene.couverture > 0.3; largeurScene: scene.width; hauteurScene: scene.height; teinte: scene.teinteNuage }
    Nuage { taille: 0.85; vitesse: 34000; hauteur: 0.36; visibleNuage: scene.couverture > 0.6; largeurScene: scene.width; hauteurScene: scene.height; teinte: scene.teinteNuage }
    Nuage { taille: 1.3; vitesse: 21000; hauteur: 0.02; visibleNuage: scene.couverture > 0.8; largeurScene: scene.width; hauteurScene: scene.height; teinte: scene.teinteNuage }
    Nuage { taille: 0.7; vitesse: 40000; hauteur: 0.48; visibleNuage: scene.couverture > 0.9; largeurScene: scene.width; hauteurScene: scene.height; teinte: scene.teinteNuage }

    // ---------- Brouillard
    Repeater {
        model: 3
        Rectangle {
            width: scene.width * 1.4; height: scene.height * 0.09; radius: height / 2
            y: scene.height * (0.45 + index * 0.15)
            color: "#dfe6f2"
            opacity: scene.condition === "brouillard" ? 0.55 : 0
            Behavior on opacity { NumberAnimation { duration: 1500 } }
            SequentialAnimation on x {
                loops: Animation.Infinite
                NumberAnimation { from: -scene.width * 0.3; to: -scene.width * 0.05; duration: 7000 + index * 1500; easing.type: Easing.InOutSine }
                NumberAnimation { from: -scene.width * 0.05; to: -scene.width * 0.3; duration: 7000 + index * 1500; easing.type: Easing.InOutSine }
            }
        }
    }

    // ---------- Pluie / neige
    Repeater {
        model: 34
        Rectangle {
            id: goutte
            readonly property bool neige: scene.condition === "neige"
            readonly property bool actif: scene.condition === "pluie" || scene.condition === "orage" || neige
            x: (index * 41 % 100) / 100 * scene.width
            width: neige ? 5 : 2; height: neige ? 5 : 11; radius: neige ? 2.5 : 1
            color: neige ? "#ffffff" : "#bcd6ff"
            rotation: neige ? 0 : 12
            opacity: actif ? 0.85 : 0
            Behavior on opacity { NumberAnimation { duration: 1200 } }
            NumberAnimation on y {
                from: -20 - (index * 13 % 60); to: scene.height + 10
                duration: goutte.neige ? 4200 + index * 60 : 850 + (index * 23 % 400)
                loops: Animation.Infinite; running: goutte.actif
            }
        }
    }

    // ---------- Éclairs (orage)
    Rectangle {
        anchors.fill: parent
        radius: 14
        color: "#ffffff"
        opacity: 0
        SequentialAnimation on opacity {
            loops: Animation.Infinite
            running: scene.condition === "orage"
            PauseAnimation { duration: 2600 }
            NumberAnimation { to: 0.75; duration: 60 }
            NumberAnimation { to: 0; duration: 120 }
            NumberAnimation { to: 0.5; duration: 50 }
            NumberAnimation { to: 0; duration: 260 }
        }
    }
}
