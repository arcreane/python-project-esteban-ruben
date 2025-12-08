# Simulation de Contrôle Aérien

Application de simulation de contrôle aérien développée en Python avec PySide6.

## 📋 Description

Cette application simule un système de contrôle aérien où vous devez gérer plusieurs avions dans l'espace aérien, éviter les collisions et assurer l'atterrissage en toute sécurité.

## 🎮 Fonctionnalités

- **Interface graphique PySide6** : Interface moderne avec thème sombre
- **Visualisation radar 2D** : Affichage en temps réel des avions
- **Gestion des avions** : Contrôle de l'altitude, vitesse, et trajectoire
- **Système de gamification** :
  - Score basé sur la performance
  - Difficulté croissante
  - Événements aléatoires (urgences carburant)
  - Vies limitées
- **Détection de collisions** : Prévention des accidents
- **Zone d'atterrissage** : Zone dédiée pour l'atterrissage

## 🚀 Installation

### Prérequis
- Python 3.12 ou supérieur
- PySide6

### Installation des dépendances

```bash
pip install PySide6
```

## ▶️ Lancement

Pour lancer l'application :

```bash
python main.py
```

## 🎯 Comment Jouer

1. **Sélection d'avion** : Cliquez sur un avion dans le radar pour le sélectionner
2. **Contrôles disponibles** :
   - **Monter** : Augmente l'altitude de 2000 ft
   - **Descendre** : Diminue l'altitude de 2000 ft
   - **Atterrir** : Ordonne l'atterrissage (direction zone d'atterrissage)
   - **Attendre** : Met l'avion en pattern d'attente (arrête le mouvement)

3. **Objectifs** :
   - Faire atterrir un maximum d'avions
   - Éviter les collisions
   - Gérer les urgences carburant
   - Maintenir vos 3 vies

## 📊 Système de Score

- **+100 points** : Atterrissage réussi
- **+Bonus** : Carburant économisé
- **+200 points** : Atterrissage d'urgence réussi (carburant < 15%)
- **-50 points** : Avion sort de la zone
- **-150 points** : Crash (manque de carburant)
- **-300 points** : Collision

## 🏗️ Architecture du Projet

```
esteban/
├── models/
│   ├── __init__.py
│   ├── airplane.py          # Classe Airplane avec logique de vol
│   └── game_manager.py      # Gestionnaire du jeu
├── views/
│   ├── __init__.py
│   ├── main_window.py       # Fenêtre principale
│   └── radar_view.py        # Vue radar et graphiques
├── ui/
│   └── mainwindow.ui        # Interface Qt Designer
└── main.py                  # Point d'entrée
```

## 🎨 Codes Couleur

- **Bleu** : Avion normal
- **Or** : Avion sélectionné
- **Rouge** : Urgence (carburant critique)
- **Orange** : En cours d'atterrissage
- **Marron** : En attente
- **Vert** : Zone d'atterrissage

## 📝 Classes Principales

### Airplane
Représente un avion avec ses caractéristiques :
- Position (x, y)
- Altitude
- Vitesse
- Cap (heading)
- Carburant
- État (flying, landing, holding, emergency)

### GameManager
Gère la logique du jeu :
- Spawn des avions
- Détection de collisions
- Calcul du score
- Gestion de la difficulté
- Événements aléatoires

### RadarScene
Affichage graphique :
- Rendu des avions
- Zone d'atterrissage
- Cercles de distance
- Interaction utilisateur

## 🔧 Développement

Le projet utilise la programmation orientée objet (POO) avec :
- Encapsulation des données
- Héritage (Qt classes)
- Composition (GameManager contient des Airplanes)
- Énumérations pour les états

## 📄 Licence

Projet pédagogique - IPSA 2025-2026

## 👥 Auteurs

Développé dans le cadre du projet de simulation de contrôle aérien.
