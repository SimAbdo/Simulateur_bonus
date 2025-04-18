import pandas as pd
import streamlit as st
import io
import base64
import json

# Systèmes de prime par défaut
SYSTEME_ACTUEL = {
    "nom": "Système Actuel",
    "description": "10 centimes MAD par voyageur",
    "paliers": [{
        "min": 1,
        "max": 999999,
        "taux": 0.10
    }]
}

SYSTEME_NOUVEAU = {
    "nom":
    "Nouveau Système",
    "description":
    "Prime par paliers: 0-249: 0.10 MAD, 250-319: 0.25 MAD, 320-369: 0.50 MAD, 370-419: 0.70 MAD, 420+: 1.00 MAD",
    "paliers": [{
        "min": 0,
        "max": 249,
        "taux": 0.10
    }, {
        "min": 250,
        "max": 319,
        "taux": 0.25
    }, {
        "min": 320,
        "max": 369,
        "taux": 0.50
    }, {
        "min": 370,
        "max": 419,
        "taux": 0.70
    }, {
        "min": 420,
        "max": 999999,
        "taux": 1.00
    }]
}

# Stocker les systèmes par défaut
SYSTEMES_DEFAUT = {
    "systeme_actuel": SYSTEME_ACTUEL,
    "systeme_nouveau": SYSTEME_NOUVEAU
}


def calculer_prime_generique(voyageurs, systeme):
    """
    Calcule la prime selon un système à paliers défini
    
    Args:
        voyageurs (int): Nombre de voyageurs
        systeme (dict): Description du système de prime
        
    Returns:
        float: Montant de la prime en MAD (Dirhams marocains)
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
        float: Montant de la prime en MAD (Dirhams marocains)
    """
    return calculer_prime_generique(voyageurs, SYSTEME_ACTUEL)


def calculer_prime_nouvelle(voyageurs):
    """
    Calcule la prime selon la nouvelle méthode par paliers
    
    Args:
        voyageurs (int): Nombre de voyageurs
        
    Returns:
        float: Montant de la prime en MAD (Dirhams marocains)
    """
    return calculer_prime_generique(voyageurs, SYSTEME_NOUVEAU)


def calculer_primes_df(df, systemes=None, nb_services_par_jour=5):
    """
    Ajoute les colonnes de primes calculées au DataFrame pour les systèmes définis
    
    Args:
        df (pandas.DataFrame): DataFrame avec une colonne 'VOY/SERVICE/J'
        systemes (list): Liste des systèmes de primes à calculer
        nb_services_par_jour (int): Nombre de services par jour par ligne
        
    Returns:
        pandas.DataFrame: DataFrame avec les colonnes de primes ajoutées
    """
    if systemes is None:
        systemes = [SYSTEME_ACTUEL, SYSTEME_NOUVEAU]

    # Créer une copie du DataFrame pour éviter de modifier l'original
    df_result = df.copy()

    # Ajouter les nouvelles colonnes demandées
    # VOY/MOIS : Nombre de voyageurs par mois dans la ligne (VOY / 12)
    df_result['VOY/MOIS'] = (df_result['VOY'] / 12).astype(int)

    # VOY/BUS : Nombre de voyageurs par bus dans la ligne (VOY / BUS)
    df_result['VOY/BUS'] = (df_result['VOY'] / df_result['BUS']).astype(int)

    # VOY/J : Nombre de voyageurs par jour dans la ligne (VOY / 365)
    df_result['VOY/J'] = (df_result['VOY'] / 365).astype(int)

    # Ajouter chaque système comme colonne
    for systeme in systemes:
        # Créer un nom de base pour ce système pour simplifier la création des noms de colonnes
        base_nom = systeme['nom'].replace(' ', '_').lower()

        # BONUS/SERVICE/J : bonus par service par jour (VOY/SERVICE/J * fonction de calcul de bonus)
        bonus_service_j = f"BONUS/SERVICE/J_{base_nom}"
        df_result[bonus_service_j] = df_result['VOY/SERVICE/J'].apply(
            lambda x: calculer_prime_generique(x, systeme))

        # BONUS/J : bonus par jour (BONUS/SERVICE/J * nombre de services par jour)
        bonus_j = f"BONUS/J_{base_nom}"
        df_result[bonus_j] = df_result[bonus_service_j] * df_result[
            'NBRE CONDUCTEURS ETP']

        # BONUS/CONDUCTEUR/J : bonus par conducteur par jour
        bonus_conducteur_j = f"BONUS/CONDUCTEUR/J_{base_nom}"
        df_result[bonus_conducteur_j] = df_result[bonus_service_j]

        # BONUS/AN : bonus par an (BONUS/J * 365)
        bonus_an = f"BONUS/AN_{base_nom}"
        df_result[bonus_an] = df_result[bonus_j] * 365

        # BONUS/MOIS : bonus par mois (BONUS/J * 30)
        bonus_mois = f"BONUS/MOIS_{base_nom}"
        df_result[bonus_mois] = df_result[bonus_j] * 30

        # BONUS/CONDUCTEUR/MOIS : bonus par conducteur par mois (BONUS/CONDUCTEUR/J * 30)
        bonus_conducteur_mois = f"BONUS/CONDUCTEUR/MOIS_{base_nom}"
        df_result[bonus_conducteur_mois] = df_result[bonus_conducteur_j] * 30

        # BONUS/CONDUCTEUR/AN : bonus par conducteur par an (BONUS/CONDUCTEUR/J * 365)
        bonus_conducteur_an = f"BONUS/CONDUCTEUR/AN_{base_nom}"
        df_result[bonus_conducteur_an] = df_result[bonus_conducteur_j] * 365

        # Ajouter également les noms compatibles avec l'ancien format pour ne pas casser le reste du code
        df_result[f"prime_{base_nom}"] = df_result[bonus_service_j]
        df_result[f"cout_total_{base_nom}"] = df_result[bonus_an]
        df_result[f"cout_total_{base_nom}_mensuel"] = df_result[bonus_mois]

    # Calculer les différences par rapport au système actuel
    if len(systemes) > 1:
        nom_base = systemes[0]['nom'].replace(' ', '_').lower()

        for i in range(1, len(systemes)):
            nom_comp = systemes[i]['nom'].replace(' ', '_').lower()

            # Différence de prime par service
            df_result[f"diff_{nom_comp}"] = df_result[
                f"BONUS/SERVICE/J_{nom_comp}"] - df_result[
                    f"BONUS/SERVICE/J_{nom_base}"]

            # Différence de coût annuel total
            df_result[f"diff_cout_{nom_comp}"] = df_result[
                f"BONUS/AN_{nom_comp}"] - df_result[f"BONUS/AN_{nom_base}"]

            # Différence de coût mensuel total
            df_result[f"diff_cout_mensuel_{nom_comp}"] = df_result[
                f"BONUS/MOIS_{nom_comp}"] - df_result[f"BONUS/MOIS_{nom_base}"]

            # Différence par conducteur par an
            df_result[f"diff_conducteur_an_{nom_comp}"] = df_result[
                f"BONUS/CONDUCTEUR/AN_{nom_comp}"] - df_result[
                    f"BONUS/CONDUCTEUR/AN_{nom_base}"]

    return df_result


def valider_donnees(df):
    """
    Valide le format du DataFrame chargé
    
    Args:
        df (pandas.DataFrame): DataFrame à valider
        
    Returns:
        tuple: (bool, str) - (True, "") si valide, sinon (False, message d'erreur)
    """
    colonnes_requises = [
        'LIGNE', 'VOY', 'BUS', 'VOY/SERVICE/J', 'NBRE CONDUCTEURS ETP'
    ]

    # Vérifier les colonnes requises
    colonnes_manquantes = [
        col for col in colonnes_requises if col not in df.columns
    ]
    if colonnes_manquantes:
        return False, f"Colonnes manquantes: {', '.join(colonnes_manquantes)}"

    # Vérifier le type des données
    for col in ['VOY', 'BUS', 'VOY/SERVICE/J', 'NBRE CONDUCTEURS ETP']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False, f"La colonne '{col}' doit contenir des valeurs numériques"

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


def exporter_systeme_json(systeme):
    """
    Exporte un système de prime au format JSON
    
    Args:
        systeme (dict): Système de prime à exporter
        
    Returns:
        str: Contenu JSON formaté
    """
    return json.dumps(systeme, indent=2)


def importer_systeme_json(json_str):
    """
    Importe un système de prime depuis un format JSON
    
    Args:
        json_str (str): Chaîne JSON à importer
        
    Returns:
        dict: Système de prime importé, ou None si erreur
    """
    try:
        systeme = json.loads(json_str)
        # Vérifier la structure minimale du système
        if "nom" in systeme and "paliers" in systeme and isinstance(
                systeme["paliers"], list):
            return systeme
        return None
    except:
        return None
