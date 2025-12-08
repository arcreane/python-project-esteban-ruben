# Simulation de Contrôle Aérien

Application de simulation de contrôle aérien en Python avec PySide6.

## Description

Gérez plusieurs avions dans l'espace aérien, évitez les collisions et faites-les atterrir en toute sécurité.

## Fonctionnalités

- Interface graphique avec PySide6 et thème sombre
- Radar 2D en temps réel
- Contrôle de l'altitude, vitesse et trajectoire
- Système de score et difficulté croissante
- Événements aléatoires (urgences carburant)
- Détection de collisions

## Installation

Prérequis : Python 3.12+

```bash
pip install PySide6
python main.py
```

## Comment Jouer

1. Sélectionnez un avion dans le radar
2. Contrôles disponibles :
   - Monter / Descendre (+/- 2000 ft)
   - Atterrir (direction zone d'atterrissage)
   - Attendre (pattern d'attente)

3. Objectifs :
   - Faire atterrir un maximum d'avions
   - Éviter les collisions
   - Gérer les urgences carburant
   - Garder vos 3 vies

## Scoring

- Atterrissage réussi : +100 points
- Atterrissage d'urgence : +200 points
- Avion sort de la zone : -50 points
- Crash (carburant) : -150 points
- Collision : -300 points

## Architecture

```
esteban/
├── models/
│   ├── airplane.py
│   └── game_manager.py
├── views/
│   ├── main_window.py
│   └── radar_view.py
└── main.py
```

## Codes Couleur

- Bleu : Normal
- Or : Sélectionné
- Rouge : Urgence
- Orange : En cours d'atterrissage
- Marron : En attente
- Vert : Zone d'atterrissage

## Classes Principales

**Airplane** : Gère un avion (position, altitude, vitesse, carburant)

**GameManager** : Logique du jeu (spawn, collisions, score, difficulté)

**RadarScene** : Affichage graphique et interactions

## Licence

Projet pédagogique - IPSA 2025-2026
