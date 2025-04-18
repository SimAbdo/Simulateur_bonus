import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from utils import SYSTEMES_DEFAUT

def creer_graphique_combine(analyses, systemes_actifs, metric_type="BONUS/AN"):
    """
    Crée un graphique unique qui compare les deux systèmes de prime côte à côte
    
    Args:
        analyses (dict): Dictionnaire contenant les analyses des données
        systemes_actifs (list): Liste des systèmes de prime à comparer
        metric_type (str): Type de métrique à visualiser (par défaut "BONUS/AN")
        
    Returns:
        None: Affiche le graphique directement via Streamlit
    """
    couleurs = ['#5B9BD5', '#ED7D31', '#A5A5A5', '#FFC000']
    
    # S'assurer qu'il y a des données à visualiser
    if 'par_ligne' not in analyses or len(analyses['par_ligne']) == 0:
        st.warning("Aucune donnée disponible pour la visualisation")
        return

    df_lignes = analyses['par_ligne']
    
    # Préparer les données pour le graphique
    data = []
    
    # Déterminer la colonne à utiliser selon le type de métrique
    if metric_type == "BONUS/AN":
        cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
        title = "Coût annuel total par ligne"
        y_title = "Montant (MAD)"
    elif metric_type == "BONUS/MOIS":
        cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}_mensuel" for s in systemes_actifs]
        title = "Coût mensuel par ligne"
        y_title = "Montant (MAD)"
    elif metric_type == "BONUS/BUS/AN":
        cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}_bus" for s in systemes_actifs]
        title = "Coût annuel par bus par ligne"
        y_title = "Montant (MAD)"
    elif metric_type == "BONUS/CONDUCTEUR/AN":
        cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}_conducteur" for s in systemes_actifs]
        title = "Coût annuel par conducteur par ligne"
        y_title = "Montant (MAD)"
    elif metric_type == "BONUS/SERVICE/J":
        cols = [f"prime_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
        title = "Prime par service par jour par ligne"
        y_title = "Montant (MAD)"
    else:
        # Type par défaut
        cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
        title = "Comparaison des systèmes par ligne"
        y_title = "Montant (MAD)"
    
    # Vérifier que les colonnes existent
    valid_cols = [col for col in cols if col in df_lignes.columns]
    
    if not valid_cols:
        st.warning(f"Aucune colonne de données trouvée pour {metric_type}")
        return
    
    # Construire le tableau de données pour le graphique
    for i, ligne in df_lignes.iterrows():
        ligne_data = {
            'LIGNE': str(ligne['LIGNE']),
            'VOY': f"{int(ligne['VOY']):,}".replace(',', ' ')
        }
        
        for j, col in enumerate(valid_cols):
            if col in df_lignes.columns:
                systeme_nom = systemes_actifs[j]['nom']
                ligne_data[systeme_nom] = ligne[col]
        
        data.append(ligne_data)
    
    # Créer le DataFrame pour Altair
    df_graph = pd.DataFrame(data)
    
    # Transformer les données pour Altair
    df_melted = pd.melt(
        df_graph, 
        id_vars=['LIGNE', 'VOY'], 
        value_vars=[s['nom'] for s in systemes_actifs if f"cout_total_{s['nom'].replace(' ', '_').lower()}" in valid_cols or 
                    f"prime_{s['nom'].replace(' ', '_').lower()}" in valid_cols],
        var_name='Système',
        value_name='Valeur'
    )
    
    # Créer le graphique avec barres groupées
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('LIGNE:N', title='Ligne de bus', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Valeur:Q', title=y_title),
        color=alt.Color('Système:N', 
                      scale=alt.Scale(range=couleurs[:len(systemes_actifs)]),
                      legend=alt.Legend(orient='top')),
        column=alt.Column('Système:N', title=None),
        tooltip=['LIGNE', 'VOY', 'Système', 'Valeur']
    ).properties(
        title=title,
        width=120
    )
    
    # Afficher le graphique
    st.altair_chart(chart, use_container_width=True)
    
    # Ajouter un graphique combiné pour une comparaison directe
    st.markdown("### Comparaison directe des systèmes")
    
    # Créer un graphique de barres groupées par ligne
    combined_chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('LIGNE:N', title='Ligne de bus', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Valeur:Q', title=y_title),
        color=alt.Color('Système:N', 
                      scale=alt.Scale(range=couleurs[:len(systemes_actifs)]),
                      legend=alt.Legend(orient='top'))
    ).properties(
        title=f"Comparaison directe - {title}",
        width=600
    )
    
    st.altair_chart(combined_chart, use_container_width=True)
    
    # Afficher les données sous forme de tableau
    st.markdown("### Données détaillées")
    st.dataframe(df_graph)

def afficher_metriques_combine(analyses, systemes_actifs):
    """
    Affiche un sélecteur de métrique et le graphique correspondant
    
    Args:
        analyses (dict): Dictionnaire contenant les analyses des données
        systemes_actifs (list): Liste des systèmes de prime à comparer
    """
    # Définir les métriques disponibles
    metrics = [
        "BONUS/AN", 
        "BONUS/MOIS", 
        "BONUS/BUS/AN", 
        "BONUS/CONDUCTEUR/AN",
        "BONUS/SERVICE/J"
    ]
    
    # Sélecteur de métrique
    selected_metric = st.selectbox(
        "Sélectionner la métrique à visualiser",
        options=metrics,
        index=0
    )
    
    # Afficher le graphique
    creer_graphique_combine(analyses, systemes_actifs, selected_metric)
