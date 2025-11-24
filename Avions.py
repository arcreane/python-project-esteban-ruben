import random

class Avion:

    COLLISION_DISTANCE = 50

    def __init__(self, identifiant, x, y, altitude, vitesse, cap, carburant):
        self.identifiant = identifiant
        self.x = x
        self.y = y
        self.altitude = altitude
        self.vitesse = vitesse
        self.cap = cap
        self.carburant = carburant
        self.est_en_urgence = False
        self.atterrissage_demande = False

    def mettre_a_jour_position(self, delta_temps_sec):
        distance_parcourue = (self.vitesse / 3600) * delta_temps_sec
        angle_rad = self.cap * (3.14159 / 180.0)
        self.x += distance_parcourue * random.uniform(0.9, 1.1)
        self.y += distance_parcourue * random.uniform(0.9, 1.1)
        self.carburant = max(0, self.carburant - (0.05 * delta_temps_sec))
        if self.carburant <= 5:
            self.est_en_urgence = True

    def verifier_collision(self, autre_avion):
        distance_x = self.x - autre_avion.x
        distance_y = self.y - autre_avion.y
        distance_2d = (distance_x**2 + distance_y**2)**0.5

        return distance_2d < Avion.COLLISION_DISTANCE

    def changer_altitude(self, delta_altitude):
        self.altitude += delta_altitude
        self.altitude = max(0, self.altitude)

    def demander_atterrissage(self):
        self.atterrissage_demande = True

    def get_info_texte(self):
        statut = "URGENCE" if self.est_en_urgence else ("ATTERRISSAGE" if self.atterrissage_demande else "NORMAL")
        return f"{self.identifiant} - Alt: {int(self.altitude)}m, V: {int(self.vitesse)}km/h, Cap: {int(self.cap)}°, Fuel: {int(self.carburant)}%, Statut: {statut}"