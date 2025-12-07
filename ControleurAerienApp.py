from PySide6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, \
    QGraphicsPixmapItem
from PySide6.QtCore import QTimer, Slot, QPointF
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap, QTransform, QColor
from Avions import Avion
import sys
import random


class ControleurAerienApp(QMainWindow):

    def __init__(self, ui_file):
        super().__init__()
        loader = QUiLoader()
        loader.registerCustomWidget(ControleurAerienApp)

        # 1. Charger l'UI sur un objet distinct (self.ui)
        self.ui = loader.load(ui_file)

        # 2. Définir self.ui comme le widget central de la QMainWindow (garantit l'affichage)
        self.setCentralWidget(self.ui)

        # --- Initialisation des données de simulation ---

        self.avions = []
        self.score = 0
        self.temps_simulation = 0
        self.avion_selectionne = None
        self.scene = QGraphicsScene(self)

        # 3. Accès aux widgets via self.ui.nom_du_widget
        self.ui.graphicsView.setScene(self.scene)

        # Configuration des Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mise_a_jour_simulation)
        self.timer.start(100)

        self.timer_spawn = QTimer(self)
        self.timer_spawn.timeout.connect(self.creer_nouvel_avion)
        self.timer_spawn.start(5000)

        # Connexion des boutons
        self.ui.button_climb.clicked.connect(lambda: self.changer_altitude_selectionne(1))
        self.ui.button_descend.clicked.connect(lambda: self.changer_altitude_selectionne(-1))
        self.ui.button_land.clicked.connect(self.demander_atterrissage_selectionne)

        self.creer_nouvel_avion()
        self.creer_nouvel_avion()

    # --- Les méthodes de la classe (mise_a_jour_simulation, dessiner_avion, etc.) suivent ici ---

    # NOTE: Pour que les boutons et le mouvement fonctionnent, assurez-vous que :
    # 1. La méthode dessiner_avion est robuste et utilise la logique directionnelle.
    # 2. La méthode __init__ inclut : self.ui.graphicsView.setSceneRect(0, 0, 500, 500)
    # 3. La méthode __init__ inclut : self.selectionner_avion(self.avions[0].identifiant)

    # ... (Ajoutez le reste de vos méthodes ici) ...
    # Je vais réinsérer les méthodes corrigées pour que tout fonctionne.

    @Slot()
    def creer_nouvel_avion(self):
        identifiant = f"{random.choice(['AF', 'LH', 'BA'])}{random.randint(1000, 9999)}"
        x = random.randint(50, 450)
        y = random.randint(50, 450)
        altitude = random.randint(1, 3)
        vitesse = random.randint(300, 500)
        cap = random.randint(0, 360)
        carburant = random.randint(60, 100)
        nouvel_avion = Avion(identifiant, x, y, altitude, vitesse, cap, carburant)
        self.avions.append(nouvel_avion)

    @Slot()
    def mise_a_jour_simulation(self):
        delta_temps_sec = 0.1
        self.temps_simulation += delta_temps_sec
        self.scene.clear()
        for avion in self.avions:
            avion.mettre_a_jour_position(delta_temps_sec)
            # self.dessiner_avion(avion) # Laissez cette ligne commentée pour l'instant si vous ne voulez pas d'image
            # Utiliser la version du cercle pour la robustesse:
            self.dessiner_cercle_avion(avion)
            self.verifier_toutes_collisions(avion)
        self.mettre_a_jour_interface()

    def dessiner_cercle_avion(self, avion):
        taille = 10
        avion_item = QGraphicsEllipseItem(avion.x, avion.y, taille, taille)
        couleur = QColor("red") if avion.est_en_urgence else QColor("green") if avion.atterrissage_demande else QColor(
            "blue")
        avion_item.setBrush(couleur)
        self.scene.addItem(avion_item)
        info_item = QGraphicsTextItem(avion.identifiant)
        info_item.setPos(avion.x + taille, avion.y - taille)
        self.scene.addItem(info_item)

    def verifier_toutes_collisions(self, avion):
        for autre_avion in self.avions:
            if avion is not autre_avion and avion.verifier_collision(autre_avion):
                print(f"!!! COLLISION entre {avion.identifiant} et {autre_avion.identifiant} !!!")
                self.score -= 500

    def mettre_a_jour_interface(self):
        # Utilisation de self.ui.xxx
        self.ui.stat_value_score.setText(f"{self.score}")
        self.ui.stat_value_landed.setText(f"{len(self.avions)}")

        if self.avion_selectionne:
            self.ui.value_airplane_name.setText(self.avion_selectionne.identifiant)
            # Ajout des champs Altitude, Vitesse, Carburant pour le feedback
            if hasattr(self.ui, 'value_altitude'):
                self.ui.value_altitude.setText(f"{self.avion_selectionne.altitude * 1000:,} ft")
            if hasattr(self.ui, 'value_speed'):
                self.ui.value_speed.setText(f"{self.avion_selectionne.vitesse} kts")
            if hasattr(self.ui, 'value_fuel'):
                self.ui.value_fuel.setText(f"{int(self.avion_selectionne.carburant)}%")
        else:
            self.ui.value_airplane_name.setText("-")
            if hasattr(self.ui, 'value_altitude'):
                self.ui.value_altitude.setText("-")
            if hasattr(self.ui, 'value_speed'):
                self.ui.value_speed.setText("-")
            if hasattr(self.ui, 'value_fuel'):
                self.ui.value_fuel.setText("-")

    def selectionner_avion(self, identifiant):
        self.avion_selectionne = next((a for a in self.avions if a.identifiant == identifiant), None)

    @Slot()
    def changer_altitude_selectionne(self, delta):
        if self.avion_selectionne:
            self.avion_selectionne.changer_altitude(delta)

    @Slot()
    def demander_atterrissage_selectionne(self):
        if self.avion_selectionne:
            self.avion_selectionne.demander_atterrissage()