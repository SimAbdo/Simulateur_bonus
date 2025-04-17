import pandas as pd
import streamlit as st
from utils import calculer_primes_df, SYSTEMES_DEFAUT

def analyser_donnees(df, systemes_actifs=None):
    """
    Analyse les données et calcule les statistiques à différents niveaux
    
    Args:
        df (pandas.DataFrame): DataFrame avec les données et primes calculées
        systemes_actifs (list): Liste des systèmes de prime à analyser
        
    Returns:
        dict: Dictionnaire contenant les différentes analyses
    """
    # Utiliser les systèmes par défaut si aucun n'est fourni
    if systemes_actifs is None:
        systemes_actifs = [SYSTEMES_DEFAUT['systeme_actuel'], SYSTEMES_DEFAUT['systeme_nouveau']]
        
    # Préparer les noms de colonnes pour les systèmes
    noms_cols = [f"prime_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
    noms_diff = [f"diff_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs[1:]]
    
    # S'assurer que les primes sont calculées pour tous les systèmes
    colonnes_existantes = set(df.columns)
    colonnes_requises = set(noms_cols)
    
    if not colonnes_requises.issubset(colonnes_existantes):
        df = calculer_primes_df(df, systemes_actifs)
    
    # Calculer les totaux globaux
    totaux_globaux = {'nb_voyageurs': df['nb_voyageurs'].sum()}
    
    # Ajouter chaque système
    for col in noms_cols:
        if col in df.columns:
            totaux_globaux[col] = df[col].sum()
    
    # Ajouter les différences
    for col in noms_diff:
        if col in df.columns:
            totaux_globaux[col] = df[col].sum()
    
    # Calculer les pourcentages d'écart par rapport au système de référence
    if len(noms_cols) > 1 and noms_cols[0] in totaux_globaux:
        base_val = totaux_globaux[noms_cols[0]]
        for i in range(1, len(noms_cols)):
            if noms_cols[i] in totaux_globaux and base_val > 0:
                totaux_globaux[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                    (totaux_globaux[noms_cols[i]] / base_val - 1) * 100
                )
    
    # Analyse par conducteur
    agg_dict = {'nb_voyageurs': 'sum'}
    for col in noms_cols + noms_diff:
        if col in df.columns:
            agg_dict[col] = 'sum'
    
    par_conducteur = df.groupby('conducteur_id').agg(agg_dict).reset_index()
    
    # Ajouter les pourcentages
    if len(noms_cols) > 1 and noms_cols[0] in par_conducteur:
        for i in range(1, len(noms_cols)):
            if noms_cols[i] in par_conducteur:
                par_conducteur[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                    (par_conducteur[noms_cols[i]] / par_conducteur[noms_cols[0]] - 1) * 100
                )
    
    # Analyse par bus
    par_bus = df.groupby('bus_id').agg(agg_dict).reset_index()
    
    # Ajouter les pourcentages
    if len(noms_cols) > 1 and noms_cols[0] in par_bus:
        for i in range(1, len(noms_cols)):
            if noms_cols[i] in par_bus:
                par_bus[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                    (par_bus[noms_cols[i]] / par_bus[noms_cols[0]] - 1) * 100
                )
    
    # Analyse par ligne de service
    par_ligne = df.groupby('ligne_service').agg(agg_dict).reset_index()
    
    # Ajouter les pourcentages
    if len(noms_cols) > 1 and noms_cols[0] in par_ligne:
        for i in range(1, len(noms_cols)):
            if noms_cols[i] in par_ligne:
                par_ligne[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                    (par_ligne[noms_cols[i]] / par_ligne[noms_cols[0]] - 1) * 100
                )
    
    # Analyse par équipe
    par_equipe = df.groupby('equipe').agg(agg_dict).reset_index()
    
    # Ajouter les pourcentages
    if len(noms_cols) > 1 and noms_cols[0] in par_equipe:
        for i in range(1, len(noms_cols)):
            if noms_cols[i] in par_equipe:
                par_equipe[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                    (par_equipe[noms_cols[i]] / par_equipe[noms_cols[0]] - 1) * 100
                )
    
    # Analyse temporelle (par date si disponible)
    analyses_temporelles = {}
    if 'date' in df.columns:
        par_date = df.groupby('date').agg(agg_dict).reset_index()
        
        # Ajouter les pourcentages
        if len(noms_cols) > 1 and noms_cols[0] in par_date:
            for i in range(1, len(noms_cols)):
                if noms_cols[i] in par_date:
                    par_date[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                        (par_date[noms_cols[i]] / par_date[noms_cols[0]] - 1) * 100
                    )
        
        analyses_temporelles['par_date'] = par_date
    
    # Analyse par quart si disponible
    if 'quart' in df.columns:
        par_quart = df.groupby('quart').agg(agg_dict).reset_index()
        
        # Ajouter les pourcentages
        if len(noms_cols) > 1 and noms_cols[0] in par_quart:
            for i in range(1, len(noms_cols)):
                if noms_cols[i] in par_quart:
                    par_quart[f"pct_{systemes_actifs[i]['nom'].replace(' ', '_').lower()}"] = (
                        (par_quart[noms_cols[i]] / par_quart[noms_cols[0]] - 1) * 100
                    )
        
        analyses_temporelles['par_quart'] = par_quart
    
    # Analyse des conducteurs qui gagnent/perdent le plus avec le premier système alternatif
    gagnants = None
    perdants = None
    
    if len(noms_diff) > 0 and noms_diff[0] in par_conducteur.columns:
        gagnants = par_conducteur.sort_values(noms_diff[0], ascending=False).head(5)
        perdants = par_conducteur.sort_values(noms_diff[0], ascending=True).head(5)
    
    # Distribution des voyageurs par service
    distribution_voyageurs = df['nb_voyageurs'].describe()
    
    # Retourner toutes les analyses
    return {
        'totaux_globaux': totaux_globaux,
        'par_conducteur': par_conducteur,
        'par_bus': par_bus,
        'par_ligne': par_ligne,
        'par_equipe': par_equipe,
        'analyses_temporelles': analyses_temporelles,
        'gagnants': gagnants,
        'perdants': perdants,
        'distribution_voyageurs': distribution_voyageurs
    }

def filtrer_donnees(df, filtres):
    """
    Filtre les données en fonction des critères sélectionnés
    
    Args:
        df (pandas.DataFrame): DataFrame à filtrer
        filtres (dict): Dictionnaire des filtres à appliquer
        
    Returns:
        pandas.DataFrame: DataFrame filtré
    """
    df_filtre = df.copy()
    
    # Appliquer les filtres
    for colonne, valeurs in filtres.items():
        if valeurs and colonne in df.columns:
            if isinstance(valeurs, list) and len(valeurs) > 0:
                df_filtre = df_filtre[df_filtre[colonne].isin(valeurs)]
            elif not isinstance(valeurs, list):
                df_filtre = df_filtre[df_filtre[colonne] == valeurs]
    
    return df_filtre
