from PySide6.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsPolygonItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF, QFont
from models.airplane import AirplaneState
import math


class AirplaneGraphicsItem(QGraphicsPolygonItem):
    
    def __init__(self, airplane, game_manager):
        super().__init__()
        self.airplane = airplane
        self.game_manager = game_manager
        self.setZValue(10)
        self.create_airplane_shape()
        
        self.label = QGraphicsTextItem(self)
        self.label.setDefaultTextColor(QColor(255, 255, 255))
        self.label.setPos(-20, -30)
        
        self.update_appearance()
    
    def create_airplane_shape(self):
        """Crée la forme de l'avion (triangle) avec taille selon le niveau"""
        size_multiplier = self.airplane.level * 0.5
        
        base_size = 10
        height = base_size * size_multiplier
        width = 7 * size_multiplier
        
        triangle = QPolygonF([
            QPointF(0, -height),
            QPointF(-width, height),
            QPointF(width, height)
        ])
        self.setPolygon(triangle)
        self.setFlag(QGraphicsPolygonItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
    
    def update_appearance(self):
        airplane = self.airplane
        self.create_airplane_shape()
        
        is_in_danger_zone = False
        if self.game_manager:
            for other in self.game_manager.airplanes:
                if other != airplane and airplane.is_near(other):
                    is_in_danger_zone = True
                    break
        
        if airplane.is_in_danger():
            color = QColor(244, 67, 54)
        elif is_in_danger_zone:
            color = QColor(255, 87, 34)
        elif airplane.state == AirplaneState.LANDING:
            color = QColor(255, 152, 0)
        elif airplane.state == AirplaneState.HOLDING:
            color = QColor(121, 85, 72)
        elif airplane.selected:
            color = QColor(255, 215, 0)
        else:
            color = QColor(33, 150, 243)
        
        self.setBrush(QBrush(color))
        
        if is_in_danger_zone and not airplane.selected:
            self.setPen(QPen(QColor(244, 67, 54), 3))
        else:
            self.setPen(QPen(QColor(255, 255, 255), 2))
        
        self.label.setPlainText(f"{airplane.name}\nN{airplane.level}")
        self.setPos(airplane.x, airplane.y)
        self.setRotation(airplane.heading)
    
    def hoverEnterEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 0), 3))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setPen(QPen(QColor(255, 255, 255), 2))
        super().hoverLeaveEvent(event)


class RadarScene(QGraphicsScene):
    
    def __init__(self, width, height, game_manager):
        super().__init__(0, 0, width, height)
        self.game_manager = game_manager
        self.airplane_items = {}
        self.explosion_items = []
        
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.draw_landing_zone()
        self.draw_distance_circles()
    
    def draw_landing_zone(self):
        x = self.game_manager.landing_zone_x
        y = self.game_manager.landing_zone_y
        radius = self.game_manager.landing_zone_radius
        

        landing_circle = QGraphicsEllipseItem(
            x - radius, y - radius, 
            radius * 2, radius * 2
        )
        landing_circle.setPen(QPen(QColor(76, 175, 80), 3))
        landing_circle.setBrush(QBrush(QColor(76, 175, 80, 50)))
        landing_circle.setZValue(1)
        self.addItem(landing_circle)
        
        # Croix au centre
        cross_size = 20
        line1 = self.addLine(x - cross_size, y, x + cross_size, y,
                            QPen(QColor(255, 255, 255), 2))
        line2 = self.addLine(x, y - cross_size, x, y + cross_size,
                            QPen(QColor(255, 255, 255), 2))
        line1.setZValue(2)
        line2.setZValue(2)
        
        text = QGraphicsTextItem("LANDING ZONE")
        text.setDefaultTextColor(QColor(255, 255, 255))
        text.setPos(x - 50, y + radius + 5)
        text.setZValue(2)
        self.addItem(text)
    
    def draw_distance_circles(self):
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        for i in range(1, 4):
            radius = min(self.width(), self.height()) / 2 * i / 3
            circle = QGraphicsEllipseItem(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2
            )
            circle.setPen(QPen(QColor(90, 90, 90), 1, Qt.DashLine))
            circle.setBrush(Qt.NoBrush)
            circle.setZValue(0)
            self.addItem(circle)
    
    def update_airplanes(self):
        current_ids = set()
        
        for airplane in self.game_manager.airplanes:
            current_ids.add(airplane.id)
            
            if airplane.id not in self.airplane_items:
                item = AirplaneGraphicsItem(airplane, self.game_manager)
                self.airplane_items[airplane.id] = item
                self.addItem(item)
                self.addItem(item.label)
            else:
                item = self.airplane_items[airplane.id]
                item.update_appearance()
        
        # Supprimer les items des avions qui n'existent plus
        to_remove = []
        for airplane_id, item in self.airplane_items.items():
            if airplane_id not in current_ids:
                to_remove.append(airplane_id)
                self.removeItem(item.label)
                self.removeItem(item)
        
        for airplane_id in to_remove:
            del self.airplane_items[airplane_id]
        
        self.update_explosions()
    
    def update_explosions(self):
        """Met à jour l'affichage des explosions"""
        for item in self.explosion_items:
            if item.scene() == self:
                self.removeItem(item)
        self.explosion_items.clear()
        
        for collision in self.game_manager.collision_positions:
            x = collision['x']
            y = collision['y']
            timer = collision['timer']
            
            if timer > 0.5:
                size = (1.0 - timer) * 100
            else:
                size = timer * 100
            
            explosion_circle = QGraphicsEllipseItem(
                x - size/2, y - size/2, size, size
            )
            color = QColor(255, 69, 0)
            color.setAlpha(int(timer * 255))
            explosion_circle.setBrush(QBrush(color))
            explosion_circle.setPen(QPen(QColor(255, 165, 0), 3))
            explosion_circle.setZValue(20)
            self.addItem(explosion_circle)
            self.explosion_items.append(explosion_circle)
            
            if timer > 0.7:
                boom_text = QGraphicsTextItem("💥")
                boom_text.setDefaultTextColor(QColor(255, 255, 0))
                font = QFont("Arial", 24, QFont.Bold)
                boom_text.setFont(font)
                boom_text.setPos(x - 20, y - 30)
                boom_text.setZValue(21)
                self.addItem(boom_text)
                self.explosion_items.append(boom_text)
    
    def get_airplane_at_pos(self, x, y):
        """Trouve l'avion à une position donnée"""
        selected = self.game_manager.select_airplane(x, y)
        
        if selected:
            print(f"✈️ Avion sélectionné: {selected.name} - Niveau: {selected.level}, Fuel: {int(selected.fuel)}%")
        
        return selected
