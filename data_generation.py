import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generer_donnees_synthetiques(nb_conducteurs=10, nb_bus=5, nb_lignes=3, nb_equipes=2, nb_jours=30, nb_voyageurs_min=50, nb_voyageurs_max=500):
    """
    Génère des données synthétiques pour la simulation
    
    Args:
        nb_conducteurs (int): Nombre de conducteurs
        nb_bus (int): Nombre de bus
        nb_lignes (int): Nombre de lignes de service
        nb_equipes (int): Nombre d'équipes
        nb_jours (int): Nombre de jours à simuler
        nb_voyageurs_min (int): Nombre minimum de voyageurs par service
        nb_voyageurs_max (int): Nombre maximum de voyageurs par service
        
    Returns:
        pandas.DataFrame: DataFrame contenant les données synthétiques
    """
    # Créer des listes d'identifiants
    conducteurs = [f"C{i:03d}" for i in range(1, nb_conducteurs + 1)]
    bus = [f"B{i:02d}" for i in range(1, nb_bus + 1)]
    lignes = [f"L{i}" for i in range(1, nb_lignes + 1)]
    equipes = [f"E{i}" for i in range(1, nb_equipes + 1)]
    
    # Générer des dates
    date_debut = datetime.now() - timedelta(days=nb_jours)
    dates = [(date_debut + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(nb_jours)]
    
    # Créer les quarts de travail
    quarts = ["Matin", "Après-midi", "Soir"]
    
    # Générer les données
    data = []
    
    for date in dates:
        for quart in quarts:
            # Chaque conducteur fait un service par jour
            for conducteur in conducteurs:
                # Attribuer un bus, une ligne et une équipe
                bus_id = random.choice(bus)
                ligne = random.choice(lignes)
                equipe = random.choice(equipes)
                
                # Générer un nombre de voyageurs
                # Variation par ligne et par quart pour plus de réalisme
                ligne_index = int(ligne[1:])
                quart_index = quarts.index(quart)
                
                # Facteur de ligne (certaines lignes sont plus fréquentées)
                ligne_facteur = 0.8 + (ligne_index * 0.2)
                
                # Facteur de quart (l'après-midi est généralement plus fréquenté)
                quart_facteur = 0.7 if quart == "Matin" else 1.2 if quart == "Après-midi" else 0.9
                
                # Calculer la base
                base = (nb_voyageurs_min + nb_voyageurs_max) / 2
                
                # Appliquer les facteurs et ajouter de l'aléatoire
                nb_voyageurs = int(base * ligne_facteur * quart_facteur * random.uniform(0.7, 1.3))
                
                # Limiter aux bornes
                nb_voyageurs = max(nb_voyageurs_min, min(nb_voyageurs, nb_voyageurs_max))
                
                # Ajouter l'entrée
                data.append({
                    "date": date,
                    "quart": quart,
                    "conducteur_id": conducteur,
                    "bus_id": bus_id,
                    "ligne_service": ligne,
                    "equipe": equipe,
                    "nb_voyageurs": nb_voyageurs
                })
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    return df

def preparer_exemple_csv():
    """
    Prépare un exemple de fichier CSV pour téléchargement
    
    Returns:
        str: CSV en texte
    """
    df = generer_donnees_synthetiques(nb_conducteurs=3, nb_bus=2, nb_lignes=2, nb_equipes=1, nb_jours=3)
    return df.to_csv(index=False)
