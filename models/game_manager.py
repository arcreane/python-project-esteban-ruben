"""
Module contenant la classe GameManager pour gérer la logique du jeu.
"""
import random
from models.airplane import Airplane, AirplaneState


class GameManager:
    """Gestionnaire principal du jeu de contrôle aérien"""
    
    def __init__(self, radar_width=800, radar_height=600):
        """
        Initialise le gestionnaire de jeu.
        
        Args:
            radar_width: Largeur de la zone radar
            radar_height: Hauteur de la zone radar
        """
        self.radar_width = radar_width
        self.radar_height = radar_height
        self.airplanes = []
        self.score = 0
        self.best_score = 0  # Meilleur score
        self.lives = 3
        self.planes_landed = 0
        self.collisions_avoided = 0
        self.game_time = 0
        self.difficulty_level = 1
        self.spawn_timer = 8  # Commencer avec un timer déjà avancé
        self.spawn_interval = 5  # Secondes entre chaque spawn (réduit)
        self.game_over = False
        self.selected_airplane = None
        self.collision_positions = []  # Stocker les positions des collisions pour animation
        
        # Spawn initial d'avions (8 pour commencer)
        for _ in range(8):
            self.spawn_airplane()
        
        # Zone d'atterrissage (au centre en bas)
        self.landing_zone_x = radar_width / 2
        self.landing_zone_y = radar_height - 50
        self.landing_zone_radius = 80
        
    def update(self, dt):
        """
        Met à jour l'état du jeu.
        
        Args:
            dt: Delta time en secondes
        """
        if self.game_over:
            return
        
        self.game_time += dt
        self.spawn_timer += dt
        
        # Augmenter la difficulté avec le temps
        new_difficulty = 1 + int(self.game_time / 30)  # +1 niveau toutes les 30 secondes (encore plus rapide)
        if new_difficulty > self.difficulty_level:
            self.difficulty_level = new_difficulty
            self.spawn_interval = max(2.5, 7 - self.difficulty_level * 0.7)  # Plus difficile = spawn beaucoup plus rapide
        
        # Spawn de nouveaux avions
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_airplane()
            self.spawn_timer = 0
        
        # Mise à jour de tous les avions
        for airplane in self.airplanes[:]:  # Copie pour modification safe
            airplane.update(dt)
            
            # Vérifier si l'avion a crashé (plus de carburant)
            if airplane.fuel <= 0:
                self.handle_crash(airplane)
                continue
            
            # Vérifier si l'avion est dans la zone d'atterrissage
            if airplane.state == AirplaneState.LANDING:
                in_zone = self._is_in_landing_zone(airplane)
                at_level_1 = (airplane.level == 1)
                
                print(f"🛬 {airplane.name} en approche - Dans zone: {in_zone}, Niveau 1: {at_level_1}")
                
                # Vérifier que l'avion est bien au niveau 1 ET dans la zone
                if in_zone and at_level_1:
                    self.handle_landing(airplane)
                    continue
                elif not in_zone and not at_level_1:
                    # Si plus au niveau 1, annuler l'atterrissage
                    airplane.state = AirplaneState.FLYING
                    airplane.landing_target_x = None
                    airplane.landing_target_y = None
            
            # Vérifier si l'avion est sorti de la zone (ricochet)
            if self._is_out_of_bounds(airplane):
                self._bounce_airplane(airplane)
                continue
        
        # Détection de collisions
        self._check_collisions()
        
        # Mettre à jour les animations d'explosion
        self.collision_positions = [
            {'x': pos['x'], 'y': pos['y'], 'timer': pos['timer'] - dt}
            for pos in self.collision_positions
            if pos['timer'] > 0
        ]
        
        # Vérifier game over
        if self.lives <= 0:
            self.game_over = True
    
    def spawn_airplane(self):
        """Fait apparaître un nouvel avion"""
        max_attempts = 10  # Nombre maximum de tentatives pour éviter les collisions
        
        for attempt in range(max_attempts):
            # Position aléatoire plus près du centre (sur un cercle autour du radar)
            edge = random.randint(0, 3)  # 0=haut, 1=droite, 2=bas, 3=gauche
            margin = 100  # Distance du bord
            
            if edge == 0:  # Haut
                x = random.uniform(margin, self.radar_width - margin)
                y = margin
                heading = random.uniform(135, 225)  # Vers le bas
            elif edge == 1:  # Droite
                x = self.radar_width - margin
                y = random.uniform(margin, self.radar_height - margin)
                heading = random.uniform(225, 315)  # Vers la gauche
            elif edge == 2:  # Bas
                x = random.uniform(margin, self.radar_width - margin)
                y = self.radar_height - margin
                heading = random.uniform(315, 405) % 360  # Vers le haut
            else:  # Gauche
                x = margin
                y = random.uniform(margin, self.radar_height - margin)
                heading = random.uniform(45, 135)  # Vers la droite
            
            level = random.randint(1, 3)  # Niveau aléatoire 1, 2 ou 3
            speed = random.randint(200, 400)
            fuel = random.randint(60, 100)
            
            # Événement aléatoire: avion en urgence
            if random.random() < 0.1 * self.difficulty_level / 10:  # Probabilité augmente avec difficulté
                fuel = random.randint(5, 20)
            
            # Créer un avion temporaire pour vérifier les collisions
            temp_airplane = Airplane(x=x, y=y, level=level, speed=speed, 
                              heading=heading, fuel=fuel)
            
            # Vérifier si trop proche d'autres avions
            too_close = False
            for existing in self.airplanes:
                if existing.level == temp_airplane.level:
                    distance = temp_airplane.distance_to(existing)
                    if distance < 150:  # Distance minimale au spawn (plus grande que collision)
                        too_close = True
                        break
            
            # Si pas trop proche, ajouter l'avion
            if not too_close:
                self.airplanes.append(temp_airplane)
                return
        
        # Si après 10 tentatives on n'a pas trouvé de place, ajouter quand même (rare)
        airplane = Airplane(x=x, y=y, level=level, speed=speed, 
                          heading=heading, fuel=fuel)
        self.airplanes.append(airplane)
    
    def _is_in_landing_zone(self, airplane):
        """Vérifie si un avion est dans la zone d'atterrissage"""
        dx = airplane.x - self.landing_zone_x
        dy = airplane.y - self.landing_zone_y
        distance = (dx*dx + dy*dy) ** 0.5
        return distance <= self.landing_zone_radius
    
    def _is_out_of_bounds(self, airplane):
        """Vérifie si un avion est sorti de la zone radar"""
        margin = 50
        return (airplane.x < -margin or airplane.x > self.radar_width + margin or
                airplane.y < -margin or airplane.y > self.radar_height + margin)
    
    def _bounce_airplane(self, airplane):
        """Fait rebondir un avion qui sort de la zone en le redirigeant vers le centre"""
        import math
        margin = 50
        
        # Replacer l'avion dans les limites
        if airplane.x < -margin:
            airplane.x = -margin + 10
        elif airplane.x > self.radar_width + margin:
            airplane.x = self.radar_width + margin - 10
        
        if airplane.y < -margin:
            airplane.y = -margin + 10
        elif airplane.y > self.radar_height + margin:
            airplane.y = self.radar_height + margin - 10
        
        # Calculer la direction vers le centre du radar
        center_x = self.radar_width / 2
        center_y = self.radar_height / 2
        
        dx = center_x - airplane.x
        dy = center_y - airplane.y
        
        # Calculer le nouveau cap vers le centre
        new_heading = math.degrees(math.atan2(dx, -dy)) % 360
        airplane.heading = new_heading
        
        # Annuler l'atterrissage si en cours
        if airplane.state == AirplaneState.LANDING:
            airplane.state = AirplaneState.FLYING
            airplane.landing_target_x = None
            airplane.landing_target_y = None
    
    def _check_collisions(self):
        """Détecte les collisions entre avions"""
        collided_pairs = []
        
        for i, airplane1 in enumerate(self.airplanes):
            for airplane2 in self.airplanes[i+1:]:
                if airplane1.is_too_close(airplane2):
                    collided_pairs.append((airplane1, airplane2))
        
        # Traiter toutes les collisions détectées
        for airplane1, airplane2 in collided_pairs:
            self.handle_collision(airplane1, airplane2)
            break  # Une seule collision par frame pour éviter les problèmes
    
    def handle_landing(self, airplane):
        """Gère l'atterrissage réussi d'un avion"""
        self.airplanes.remove(airplane)
        self.planes_landed += 1
        
        # Calcul du score basé sur le carburant restant
        base_score = 100
        fuel_bonus = int(airplane.fuel * 2)  # Bonus pour carburant économisé
        
        if airplane.fuel <= 15:
            fuel_bonus += 200  # Gros bonus pour atterrissage d'urgence réussi
        
        total_points = base_score + fuel_bonus
        self.score += total_points
        
        print(f"✅ ATTERRISSAGE RÉUSSI! {airplane.name} - +{total_points} points (Score: {self.score})")
        
        if airplane == self.selected_airplane:
            self.selected_airplane = None
    
    def handle_crash(self, airplane):
        """Gère le crash d'un avion (manque de carburant)"""
        print(f"⛽ CRASH CARBURANT! {airplane.name} est tombé en panne de carburant!")
        self.airplanes.remove(airplane)
        self.lives -= 1
        self.score = max(0, self.score - 150)
        
        if airplane == self.selected_airplane:
            self.selected_airplane = None
    
    def handle_collision(self, airplane1, airplane2):
        """Gère une collision entre deux avions"""
        print(f"💥 COLLISION! {airplane1.name} et {airplane2.name} se sont heurtés au niveau {airplane1.level}!")
        
        # Stocker la position de la collision pour l'animation
        collision_x = (airplane1.x + airplane2.x) / 2
        collision_y = (airplane1.y + airplane2.y) / 2
        self.collision_positions.append({'x': collision_x, 'y': collision_y, 'timer': 1.0})
        
        if airplane1 in self.airplanes:
            self.airplanes.remove(airplane1)
        if airplane2 in self.airplanes:
            self.airplanes.remove(airplane2)
        
        self.lives -= 1
        self.score = max(0, self.score - 300)
        
        if airplane1 == self.selected_airplane or airplane2 == self.selected_airplane:
            self.selected_airplane = None
    
    def select_airplane(self, x, y):
        """
        Sélectionne un avion en cliquant dessus.
        
        Args:
            x, y: Coordonnées du clic
        
        Returns:
            L'avion sélectionné ou None
        """
        # Désélectionner tous les avions
        for airplane in self.airplanes:
            airplane.selected = False
        
        # Trouver l'avion le plus proche du clic
        closest = None
        min_dist = 30  # Distance maximale pour la sélection
        
        for airplane in self.airplanes:
            dx = airplane.x - x
            dy = airplane.y - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = airplane
        
        if closest:
            closest.selected = True
            self.selected_airplane = closest
        else:
            self.selected_airplane = None
        
        return self.selected_airplane
    
    def get_stats(self):
        """Retourne les statistiques du jeu"""
        # Mettre à jour le meilleur score
        if self.score > self.best_score:
            self.best_score = self.score
        
        return {
            'score': self.score,
            'best_score': self.best_score,
            'time': self.game_time,
            'landed': self.planes_landed,
            'lives': self.lives,
            'active_planes': len(self.airplanes),
            'difficulty': self.difficulty_level
        }
    
    def reset(self):
        """Réinitialise le jeu"""
        self.airplanes.clear()
        self.collision_positions.clear()
        # Ne pas réinitialiser best_score
        self.score = 0
        self.lives = 3
        self.planes_landed = 0
        self.collisions_avoided = 0
        self.game_time = 0
        self.difficulty_level = 1
        self.spawn_timer = 8
        self.spawn_interval = 5
        self.game_over = False
        self.selected_airplane = None
        
        # Respawn des avions initiaux
        for _ in range(8):
            self.spawn_airplane()
