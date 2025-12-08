"""
Module contenant la classe Airplane pour la simulation de contrôle aérien.
"""
import math
import random
from enum import Enum


class AirplaneState(Enum):
    """États possibles d'un avion"""
    FLYING = "flying"
    LANDING = "landing"
    LANDED = "landed"
    HOLDING = "holding"
    EMERGENCY = "emergency"


class Airplane:
    """Classe représentant un avion dans l'espace aérien"""
    
    # Constantes de classe - Système de niveaux
    LEVEL_1 = 1  # Niveau bas (requis pour atterrir)
    LEVEL_2 = 2  # Niveau moyen
    LEVEL_3 = 3  # Niveau haut
    MIN_LEVEL = 1
    MAX_LEVEL = 3
    
    MIN_SPEED = 150  # kts
    MAX_SPEED = 500  # kts
    FUEL_CONSUMPTION_RATE = 1.43  # % par seconde (100% en ~70 secondes)
    CRITICAL_FUEL_LEVEL = 15  # %
    COLLISION_DISTANCE = 30  # pixels (réduit pour plus de challenge)
    SAFE_DISTANCE = 80  # pixels (zone d'alerte)
    
    _airplane_counter = 0  # Compteur pour générer des IDs uniques
    
    def __init__(self, name=None, x=0, y=0, level=3, speed=250, heading=0, fuel=100):
        """
        Initialise un avion avec ses caractéristiques.
        
        Args:
            name: Nom de l'avion (ex: "AFR123")
            x, y: Position 2D sur le radar
            level: Niveau d'altitude (1, 2 ou 3)
            speed: Vitesse en noeuds
            heading: Cap en degrés (0-360)
            fuel: Carburant restant en %
        """
        Airplane._airplane_counter += 1
        self.id = Airplane._airplane_counter
        self.name = name or self._generate_name()
        self.x = x
        self.y = y
        self.level = max(self.MIN_LEVEL, min(self.MAX_LEVEL, level))  # Niveau 1, 2 ou 3
        self.speed = speed
        self.heading = heading
        self.fuel = fuel
        self.state = AirplaneState.FLYING
        self.selected = False
        self.has_emergency = False
        self.landing_target_x = None
        self.landing_target_y = None
        
    @staticmethod
    def _generate_name():
        """Génère un nom d'avion aléatoire"""
        airlines = ["AFR", "BAW", "LH", "DLH", "UAE", "AAL", "UAL"]
        number = random.randint(100, 999)
        return f"{random.choice(airlines)}{number}"
    
    def update(self, dt):
        """
        Met à jour l'état de l'avion.
        
        Args:
            dt: Delta time en secondes
        """
        if self.state == AirplaneState.LANDED:
            return
        
        # Consommation de carburant
        self.fuel = max(0, self.fuel - self.FUEL_CONSUMPTION_RATE * dt)
        
        # Vérifier le niveau de carburant critique
        if self.fuel <= self.CRITICAL_FUEL_LEVEL and not self.has_emergency:
            self.has_emergency = True
            self.state = AirplaneState.EMERGENCY
        
        # Si plus de carburant, crash
        if self.fuel <= 0:
            self.state = AirplaneState.LANDED
            return
        
        # Mise à jour de la position
        if self.state != AirplaneState.HOLDING:
            # Si en mode atterrissage, se diriger vers la zone
            if self.state == AirplaneState.LANDING and self.landing_target_x is not None:
                # Calculer le cap vers la zone d'atterrissage
                dx = self.landing_target_x - self.x
                dy = self.landing_target_y - self.y
                
                # Calculer l'angle vers la cible
                target_heading = math.degrees(math.atan2(dx, -dy)) % 360
                
                # Ajuster progressivement le cap (virage doux)
                heading_diff = (target_heading - self.heading + 180) % 360 - 180
                turn_rate = 2.0  # Degrés par frame
                if abs(heading_diff) > turn_rate:
                    self.heading += turn_rate if heading_diff > 0 else -turn_rate
                else:
                    self.heading = target_heading
                self.heading = self.heading % 360
            
            # Conversion du cap en radians
            heading_rad = math.radians(self.heading)
            # Déplacement selon le cap
            self.x += math.sin(heading_rad) * self.speed * dt * 0.1
            self.y -= math.cos(heading_rad) * self.speed * dt * 0.1
    
    def climb(self):
        """Ordonne à l'avion de monter d'un niveau"""
        if self.level < self.MAX_LEVEL:
            self.level += 1
        if self.state == AirplaneState.HOLDING:
            self.state = AirplaneState.FLYING
    
    def descend(self):
        """Ordonne à l'avion de descendre d'un niveau"""
        if self.level > self.MIN_LEVEL:
            self.level -= 1
        if self.state == AirplaneState.HOLDING:
            self.state = AirplaneState.FLYING
    
    def land(self, landing_x=None, landing_y=None):
        """Ordonne à l'avion d'atterrir (seulement si niveau 1) ou annule l'atterrissage"""
        if self.level == self.LEVEL_1:
            if self.state == AirplaneState.LANDING:
                # Annuler l'atterrissage
                self.state = AirplaneState.FLYING
                self.landing_target_x = None
                self.landing_target_y = None
            else:
                # Commencer l'atterrissage
                self.state = AirplaneState.LANDING
                self.landing_target_x = landing_x
                self.landing_target_y = landing_y
            return True
        return False
    
    def hold(self):
        """Met l'avion en attente (pattern d'attente) ou annule l'attente"""
        if self.state == AirplaneState.HOLDING:
            # Annuler l'attente
            self.state = AirplaneState.FLYING
        else:
            # Mettre en attente
            self.state = AirplaneState.HOLDING
    
    def change_heading(self, new_heading):
        """Change le cap de l'avion"""
        self.heading = new_heading % 360
        if self.state == AirplaneState.HOLDING:
            self.state = AirplaneState.FLYING
    
    def change_speed(self, new_speed):
        """Change la vitesse de l'avion"""
        self.speed = max(self.MIN_SPEED, min(self.MAX_SPEED, new_speed))
    
    def is_in_danger(self):
        """Vérifie si l'avion est en situation dangereuse"""
        return (self.fuel <= self.CRITICAL_FUEL_LEVEL or 
                self.state == AirplaneState.EMERGENCY)
    
    def distance_to(self, other):
        """Calcule la distance à un autre avion"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx*dx + dy*dy)
    
    def is_too_close(self, other):
        """Vérifie si un autre avion est trop proche (risque de collision)"""
        if self.level != other.level:  # Niveaux différents = sûr
            return False
        return self.distance_to(other) < self.COLLISION_DISTANCE
    
    def is_near(self, other):
        """Vérifie si un autre avion est proche (zone d'alerte)"""
        if self.level != other.level:
            return False
        return self.distance_to(other) < self.SAFE_DISTANCE
    
    def __str__(self):
        return (f"{self.name} - Niveau: {self.level}, "
                f"Speed: {int(self.speed)}kts, "
                f"Fuel: {int(self.fuel)}%, "
                f"State: {self.state.value}")
