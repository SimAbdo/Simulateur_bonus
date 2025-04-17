import pandas as pd
import streamlit as st
import io
import base64
import json

# Systèmes de prime par défaut
SYSTEME_ACTUEL = {
    "nom": "Système Actuel",
    "description": "10 centimes MAD par voyageur",
    "paliers": [
        {"min": 1, "max": 999999, "taux": 0.10}
    ]
}

SYSTEME_NOUVEAU = {
    "nom": "Nouveau Système",
    "description": "Prime par paliers: 0-249: 0.10 MAD, 250-319: 0.25 MAD, 320-369: 0.50 MAD, 370-419: 0.70 MAD, 420+: 1.00 MAD",
    "paliers": [
        {"min": 0, "max": 249, "taux": 0.10},
        {"min": 250, "max": 319, "taux": 0.25},
        {"min": 320, "max": 369, "taux": 0.50},
        {"min": 370, "max": 419, "taux": 0.70},
        {"min": 420, "max": 999999, "taux": 1.00}
    ]
}

SYSTEME_ALTERNATIF1 = {
    "nom": "Alternative 1",
    "description": "Prime progressive: 10c (1-50), 25c (51-200), 50c (201+)",
    "paliers": [
        {"min": 1, "max": 50, "taux": 0.10},
        {"min": 51, "max": 200, "taux": 0.25},
        {"min": 201, "max": 999999, "taux": 0.50}
    ]
}

SYSTEME_ALTERNATIF2 = {
    "nom": "Alternative 2",
    "description": "Prime uniforme de 30 centimes par voyageur",
    "paliers": [
        {"min": 1, "max": 999999, "taux": 0.30}
    ]
}

# Stocker les systèmes par défaut
SYSTEMES_DEFAUT = {
    "systeme_actuel": SYSTEME_ACTUEL,
    "systeme_nouveau": SYSTEME_NOUVEAU,
    "systeme_alternatif1": SYSTEME_ALTERNATIF1,
    "systeme_alternatif2": SYSTEME_ALTERNATIF2
}

def calculer_prime_generique(voyageurs, systeme):
    """
    Calcule la prime selon un système à paliers défini
    
    Args:
        voyageurs (int): Nombre de voyageurs
        systeme (dict): Description du système de prime
        
    Returns:
        float: Montant de la prime en euros
    """
    prime = 0
    for palier in systeme["paliers"]:
        min_voy = palier["min"]
        max_voy = palier["max"]
        taux = palier["taux"]
        
        if voyageurs >= min_voy:
            voy_palier = min(voyageurs, max_voy) - min_voy + 1
            prime += voy_palier * taux
    
    return round(prime, 2)

def calculer_prime_actuelle(voyageurs):
    """
    Calcule la prime selon la méthode actuelle (10 centimes par voyageur)
    
    Args:
        voyageurs (int): Nombre de voyageurs
        
    Returns:
        float: Montant de la prime en euros
    """
    return calculer_prime_generique(voyageurs, SYSTEME_ACTUEL)

def calculer_prime_nouvelle(voyageurs):
    """
    Calcule la prime selon la nouvelle méthode par paliers
    
    Args:
        voyageurs (int): Nombre de voyageurs
        
    Returns:
        float: Montant de la prime en euros
    """
    return calculer_prime_generique(voyageurs, SYSTEME_NOUVEAU)

def calculer_primes_df(df, systemes=None):
    """
    Ajoute les colonnes de primes calculées au DataFrame pour les systèmes définis
    
    Args:
        df (pandas.DataFrame): DataFrame avec une colonne 'nb_voyageurs'
        systemes (list): Liste des systèmes de primes à calculer
        
    Returns:
        pandas.DataFrame: DataFrame avec les colonnes de primes ajoutées
    """
    if systemes is None:
        systemes = [SYSTEME_ACTUEL, SYSTEME_NOUVEAU]
    
    # Ajouter chaque système comme colonne
    for systeme in systemes:
        nom_col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
        df[nom_col] = df['nb_voyageurs'].apply(lambda x: calculer_prime_generique(x, systeme))
    
    # Calculer les différences par rapport au système actuel
    nom_base = f"prime_{systemes[0]['nom'].replace(' ', '_').lower()}"
    for i in range(1, len(systemes)):
        nom_comp = f"prime_{systemes[i]['nom'].replace(' ', '_').lower()}"
        nom_diff = f"diff_{systemes[i]['nom'].replace(' ', '_').lower()}"
        df[nom_diff] = df[nom_comp] - df[nom_base]
    
    return df

def valider_donnees(df):
    """
    Valide le format du DataFrame chargé
    
    Args:
        df (pandas.DataFrame): DataFrame à valider
        
    Returns:
        tuple: (bool, str) - (True, "") si valide, sinon (False, message d'erreur)
    """
    colonnes_requises = ['conducteur_id', 'bus_id', 'ligne_service', 'equipe', 'nb_voyageurs']
    
    # Vérifier les colonnes requises
    colonnes_manquantes = [col for col in colonnes_requises if col not in df.columns]
    if colonnes_manquantes:
        return False, f"Colonnes manquantes: {', '.join(colonnes_manquantes)}"
    
    # Vérifier le type des données
    if not pd.api.types.is_numeric_dtype(df['nb_voyageurs']):
        return False, "La colonne 'nb_voyageurs' doit contenir des valeurs numériques"
    
    return True, ""

def get_download_link(df, filename="resultats_primes.csv"):
    """
    Génère un lien de téléchargement pour un DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame à télécharger
        filename (str): Nom du fichier à télécharger
        
    Returns:
        str: Lien HTML pour télécharger le DataFrame
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Télécharger les résultats (CSV)</a>'
    return href
