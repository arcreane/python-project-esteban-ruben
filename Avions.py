import random
import math  # Nécessaire pour les calculs de trigonométrie et de position


class Avion:
    COLLISION_DISTANCE = 50  # Distance critique pour la collision (en unités de scène)

    def __init__(self, identifiant, x, y, altitude, vitesse, cap, carburant):
        self.identifiant = identifiant
        self.x = x
        self.y = y
        # Altitude est un niveau (1, 2, ou 3) représentant 1000, 2000, 3000 pieds
        self.altitude = altitude
        self.vitesse = vitesse
        self.cap = cap
        self.carburant = carburant
        self.est_en_urgence = False
        self.atterrissage_demande = False

    def mettre_a_jour_position(self, delta_temps_sec):
        """Met à jour la position et le carburant de l'avion."""
        # Conversion du cap en radians
        cap_rad = math.radians(self.cap)

        # Calcul de la distance parcourue
        # (Vitesse en KTS, on assume ici un facteur d'échelle constant pour la scène 500x500)
        distance_parcourue = (self.vitesse / 3600) * delta_temps_sec * 5

        # Mise à jour de la position (sin/cos sont inversés car 0° est Nord/Y-up et Y est inversé dans QGraphicsScene)
        self.x += distance_parcourue * math.sin(cap_rad)
        self.y -= distance_parcourue * math.cos(cap_rad)

        # Gestion du carburant (consommation constante)
        self.carburant = max(0, self.carburant - (0.1 * delta_temps_sec))
        if 0 < self.carburant <= 5:
            self.est_en_urgence = True
        else:
            self.est_en_urgence = False

        # Gestion des bords (réapparition)
        if self.x > 500: self.x = 0
        if self.x < 0: self.x = 500
        if self.y > 500: self.y = 0
        if self.y < 0: self.y = 500

    def verifier_collision(self, autre_avion):
        """Vérifie la distance 2D entre deux avions."""
        distance_x = self.x - autre_avion.x
        distance_y = self.y - autre_avion.y
        distance_2d = (distance_x ** 2 + distance_y ** 2) ** 0.5
        return distance_2d < Avion.COLLISION_DISTANCE

    def changer_altitude(self, delta_altitude):
        """Change le niveau d'altitude (entre 1 et 3)."""
        nouvelle_altitude = self.altitude + delta_altitude
        if 1 <= nouvelle_altitude <= 3:
            self.altitude = nouvelle_altitude

    def demander_atterrissage(self):
        """Passe l'avion en mode 'demande d'atterrissage'."""
        self.atterrissage_demande = True

    def changer_cap(self, delta_cap):
        """Change le cap (direction) de l'avion de delta_cap degrés."""
        self.cap = (self.cap + delta_cap) % 360