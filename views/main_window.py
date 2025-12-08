import os
from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtCore import QTimer, QTime, QEvent, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from models.game_manager import GameManager
from models.airplane import AirplaneState
from views.radar_view import RadarScene


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.load_ui()
        
        radar_width = 800
        radar_height = 600
        self.game_manager = GameManager(radar_width, radar_height)
        
        self.radar_scene = RadarScene(radar_width, radar_height, self.game_manager)
        self.ui.graphicsView.setScene(self.radar_scene)
        
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(50)
        
        self.elapsed_time = QTime(0, 0)
        
        self.connect_signals()
        
        self.ui.graphicsView.viewport().installEventFilter(self)
        
        self.update_ui()
    
    def load_ui(self):
        ui_file_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'mainwindow.ui')
        ui_file = QFile(ui_file_path)
        
        if not ui_file.open(QFile.ReadOnly):
            raise Exception(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
        
        loader = QUiLoader()
        self.ui = loader.load(ui_file, None)
        ui_file.close()
        
        if not self.ui:
            raise Exception(loader.errorString())
        
        self.setWindowTitle("Contrôle Aérien - Tableau de Bord Coloré")
        self.resize(1000, 700)
        
        self.setCentralWidget(self.ui.centralwidget)
        
        self.setStyleSheet("""
/* Style général (Dark Mode) */
QMainWindow {
    background-color: #2e2e2e;
}
QWidget#centralwidget {
    background-color: #2e2e2e;
}
QGroupBox {
    border: 2px solid #5a5a5a;
    border-radius: 5px;
    margin-top: 1ex;
    font-weight: bold;
    color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    background-color: #2e2e2e;
}
QLabel {
    color: #cccccc;
}
QGraphicsView {
    background-color: #1e1e1e;
    border: 1px solid #5a5a5a;
}
QSplitter::handle {
    background-color: #5a5a5a;
}
""")
    
    def connect_signals(self):
        self.ui.button_climb.clicked.connect(self.on_climb)
        self.ui.button_descend.clicked.connect(self.on_descend)
        self.ui.button_land.clicked.connect(self.on_land)
        self.ui.button_hold.clicked.connect(self.on_hold)
    
    def eventFilter(self, obj, event):
        if obj == self.ui.graphicsView.viewport() and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                scene_pos = self.ui.graphicsView.mapToScene(event.pos())
                
                selected = self.radar_scene.get_airplane_at_pos(scene_pos.x(), scene_pos.y())
                
                self.update_selected_airplane_info()
                self.radar_scene.update_airplanes()
                
                return True
        
        return super().eventFilter(obj, event)
    
    def radar_mouse_press(self, event):
        """Gère les clics sur le radar (méthode legacy, remplacée par eventFilter)"""
        scene_pos = self.ui.graphicsView.mapToScene(event.pos())
        
        selected = self.radar_scene.get_airplane_at_pos(scene_pos.x(), scene_pos.y())
        
        self.update_selected_airplane_info()
        self.radar_scene.update_airplanes()
    
    def update_game(self):
        dt = 0.05
        
        if not self.game_manager.game_over:
            self.game_manager.update(dt)
            
            self.radar_scene.update_airplanes()
            self.update_ui()
            
            if self.game_manager.game_over:
                self.show_game_over()
    
    def update_ui(self):
        self.update_stats()
        self.update_selected_airplane_info()
    
    def update_stats(self):
        stats = self.game_manager.get_stats()
        
        self.ui.stat_value_score.setText(str(stats['score']))
        
        minutes = int(stats['time'] // 60)
        seconds = int(stats['time'] % 60)
        self.ui.stat_value_time.setText(f"{minutes:02d}:{seconds:02d}")
        
        self.ui.stat_value_landed.setText(str(stats['landed']))
        
        self.ui.stat_value_lives.setText(str(stats['lives']))
        
        if stats['lives'] <= 1:
            self.ui.stat_value_lives.setStyleSheet("color: #F44336; font-weight: bold;")
        
        status_text = f"Avions actifs: {stats['active_planes']} | Niveau: {stats['difficulty']}"
        if hasattr(self.ui, 'statusbar'):
            self.ui.statusbar.showMessage(status_text)
    
    def update_selected_airplane_info(self):
        airplane = self.game_manager.selected_airplane
        
        if airplane:
            self.ui.button_climb.setEnabled(airplane.level < 3)
            self.ui.button_descend.setEnabled(airplane.level > 1)
            self.ui.button_hold.setEnabled(True)
            
            if airplane.state == AirplaneState.HOLDING:
                self.ui.button_hold.setText("Reprendre Vol")
            else:
                self.ui.button_hold.setText("Attendre (Hold)")
            
            can_land = airplane.level == 1
            in_zone = self.game_manager._is_in_landing_zone(airplane)
            self.ui.button_land.setEnabled(can_land)
            
            if airplane.level != 1:
                self.ui.button_land.setText("Atterrir (Niveau 1 requis)")
            elif airplane.state == AirplaneState.LANDING:
                if in_zone:
                    self.ui.button_land.setText("Annuler Atterrissage")
                else:
                    self.ui.button_land.setText("Annuler Atterrissage")
            elif in_zone:
                self.ui.button_land.setText("Atterrir (Dans zone ✓)")
            else:
                self.ui.button_land.setText("Atterrir (Rejoindre zone)")
            
            self.ui.value_airplane_name.setText(airplane.name)
            self.ui.value_altitude.setText(f"Niveau {airplane.level}")
            self.ui.value_speed.setText(f"{int(airplane.speed)}")
            self.ui.value_fuel.setText(f"{int(airplane.fuel)}%")
            
            if airplane.level == 1:
                level_color = "#4CAF50"  # Vert
            elif airplane.level == 2:
                level_color = "#2196F3"  # Bleu
            else:
                level_color = "#9C27B0"  # Violet
            self.ui.value_altitude.setStyleSheet(f"color: {level_color}; font-weight: bold;")
            
            if airplane.fuel <= 15:
                fuel_color = "#F44336"  # Rouge
            elif airplane.fuel <= 30:
                fuel_color = "#FF9800"  # Orange
            else:
                fuel_color = "#FFC107"  # Jaune
            self.ui.value_fuel.setStyleSheet(f"color: {fuel_color}; font-weight: bold;")
            
            status_msg = f"✈️ {airplane.name} sélectionné - Niveau: {airplane.level} - État: {airplane.state.value}"
            if can_land:
                status_msg += " - 🛬 PRÊT À ATTERRIR"
            if hasattr(self.ui, 'statusbar'):
                self.ui.statusbar.showMessage(status_msg)
        else:
            self.ui.button_climb.setEnabled(False)
            self.ui.button_descend.setEnabled(False)
            self.ui.button_land.setEnabled(False)
            self.ui.button_hold.setEnabled(False)
            
            self.ui.value_airplane_name.setText("Aucun")
            self.ui.value_altitude.setText("---")
            self.ui.value_speed.setText("---")
            self.ui.value_fuel.setText("---")
            
            self.ui.button_land.setText("Atterrir (Land)")
            self.ui.button_hold.setText("Attendre (Hold)")
    
    def on_climb(self):
        if self.game_manager.selected_airplane:
            old_level = self.game_manager.selected_airplane.level
            self.game_manager.selected_airplane.climb()
            new_level = self.game_manager.selected_airplane.level
            if new_level != old_level:
                print(f"⬆️ {self.game_manager.selected_airplane.name} - Monté au niveau {new_level}")
            else:
                print(f"⚠️ {self.game_manager.selected_airplane.name} - Déjà au niveau maximum")
    
    def on_descend(self):
        if self.game_manager.selected_airplane:
            old_level = self.game_manager.selected_airplane.level
            self.game_manager.selected_airplane.descend()
            new_level = self.game_manager.selected_airplane.level
            if new_level != old_level:
                print(f"⬇️ {self.game_manager.selected_airplane.name} - Descendu au niveau {new_level}")
            else:
                print(f"⚠️ {self.game_manager.selected_airplane.name} - Déjà au niveau minimum")
    
    def on_land(self):
        if self.game_manager.selected_airplane:
            airplane = self.game_manager.selected_airplane
            
            landing_x = self.game_manager.landing_zone_x
            landing_y = self.game_manager.landing_zone_y
            
            if airplane.state == AirplaneState.LANDING:
                airplane.land(landing_x, landing_y)
                print(f"❌ {airplane.name} - Atterrissage annulé, retour en vol normal")
            else:
                
                if airplane.land(landing_x, landing_y):
                    print(f"🛬 {airplane.name} - Instruction d'atterrissage donnée, direction zone verte")
                else:
                    print(f"❌ {airplane.name} - Atterrissage impossible! Doit être au niveau 1")
    
    def on_hold(self):
        if self.game_manager.selected_airplane:
            airplane = self.game_manager.selected_airplane
            
            if airplane.state == AirplaneState.HOLDING:
                airplane.hold()
                print(f"▶️ {airplane.name} - Reprise du vol")
            else:
                airplane.hold()
                print(f"⏸️ {airplane.name} - Mis en attente")
    
    def show_collision_warning(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("💥 COLLISION!")
        msg_box.setText("Deux avions sont entrés en collision!")
        msg_box.setInformativeText(f"Vies restantes: {self.game_manager.lives}\nScore: {self.game_manager.score}")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setStyleSheet("QMessageBox { background-color: #2e2e2e; color: white; }")
        
        
        msg_box.show()
        msg_box.raise_()
        msg_box.activateWindow()
        
        
        QTimer.singleShot(2000, msg_box.close)
    
    def show_game_over(self):
        stats = self.game_manager.get_stats()
        
        minutes = int(stats['time'] // 60)
        seconds = int(stats['time'] % 60)
        time_survived = f"{minutes}:{seconds:02d}"
        
        is_new_record = stats['score'] == stats['best_score'] and stats['score'] > 0
        
        message = f"""
<h2 style='color: #FF5252;'>💀 GAME OVER 💀</h2>
<div style='font-size: 14px;'>
<p><b>Score final:</b> <span style='color: #FFEB3B; font-size: 18px;'>{stats['score']}</span></p>
<p><b>Temps de survie:</b> <span style='color: #00BCD4;'>{time_survived}</span></p>
<p><b>Avions atterris:</b> <span style='color: #8BC34A;'>{stats['landed']}</span></p>
<hr>
<p><b>🏆 MEILLEUR SCORE:</b> <span style='color: #FFD700; font-size: 20px;'>{stats['best_score']}</span></p>
"""
        
        if is_new_record:
            message += "<p style='color: #4CAF50; font-size: 16px;'>🎉 NOUVEAU RECORD! 🎉</p>"
        
        message += "</div>"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Over")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Critical)
        
        replay_button = msg_box.addButton("🔄 Rejouer", QMessageBox.ActionRole)
        quit_button = msg_box.addButton("❌ Quitter", QMessageBox.ActionRole)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2e2e2e;
            }
            QMessageBox QLabel {
                color: white;
                min-width: 400px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        
        msg_box.exec()
        
        clicked_button = msg_box.clickedButton()
        if clicked_button == replay_button:
            self.restart_game()
        else:
            self.close()
    
    def restart_game(self):
        self.game_manager.reset()
        
        self.radar_scene.airplane_items.clear()
        self.radar_scene.explosion_items.clear()
        self.radar_scene.clear()
        
        self.radar_scene.draw_landing_zone()
        self.radar_scene.draw_distance_circles()
        
        self.update_ui()
