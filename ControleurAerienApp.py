from PySide6.QtWidgets import QMainWindow, QApplication, QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtCore import QTimer, Slot, QPointF
from PySide6.QtUiTools import QUiLoader, loadUiType
from Avions import Avion
import sys
import random

class ControleurAerienApp(QMainWindow):


    def __init__(self, ui_file):
        super().__init__()
        loader = QUiLoader()
        loader.registerCustomWidget(ControleurAerienApp)
        self.ui = loader.load(ui_file, self)
        self.avions = []
        self.score = 0
        self.temps_simulation = 0
        self.avion_selectionne = None
        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene) #le widget doit être nommé graphicsView dans l'UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.mise_a_jour_simulation)
        self.timer.start(100)
        self.timer_spawn = QTimer(self)
        self.timer_spawn.timeout.connect(self.creer_nouvel_avion)
        self.timer_spawn.start(5000)
        self.ui.button_climb.clicked.connect(lambda: self.changer_altitude_selectionne(1))
        self.ui.button_descend.clicked.connect(lambda: self.changer_altitude_selectionne(-1))
        self.ui.button_land.clicked.connect(self.demander_atterrissage_selectionne)
        self.creer_nouvel_avion()
        self.creer_nouvel_avion()

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
            self.dessiner_avion(avion)
            self.verifier_toutes_collisions(avion)
        self.mettre_a_jour_interface()

    def dessiner_avion(self, avion):
        taille = 10
        avion_item = QGraphicsEllipseItem(avion.x, avion.y, taille, taille)
        couleur = "red" if avion.est_en_urgence else "green" if avion.atterrissage_demande else "blue"
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
        self.ui.stat_value_score.setText(f"{self.score}")
        self.ui.stat_value_landed.setText(f"{len(self.avions)}")
        '''liste_avions_texte = "\n".join([avion.get_info_texte() for avion in self.avions])
        self.ui.text_avions.setText(liste_avions_texte)'''
        if self.avion_selectionne:
            self.ui.value_airplane_name.setText(self.avion_selectionne.identifiant)

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