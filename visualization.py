import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from utils import SYSTEMES_DEFAUT

def creer_graphiques_comparaison(analyses, systemes_actifs):
    """
    Crée des graphiques comparant les méthodes de prime sélectionnées
    
    Args:
        analyses (dict): Dictionnaire contenant les analyses des données
        systemes_actifs (list): Liste des systèmes de prime à comparer
        
    Returns:
        None: Affiche les graphiques directement via Streamlit
    """
    couleurs = ['#5B9BD5', '#ED7D31', '#A5A5A5', '#FFC000']
    noms_systemes = [s["nom"] for s in systemes_actifs]
    
    # Section des onglets pour différentes vues
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Vue globale", 
        "Par ligne", 
        "Par mois", 
        "Par granularité",
        "Distribution"
    ])
    
    with tab1:
        st.subheader("Comparaison globale des systèmes de prime")
        
        # Graphique 1: Comparaison des coûts totaux annuels (side by side)
        st.markdown("#### Comparaison des coûts totaux annuels des primes")
        
        # Préparation des données pour le graphique
        totaux_cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
        data = []
        
        for i, col in enumerate(totaux_cols):
            if col in analyses['totaux_globaux']:
                data.append({
                    'Système': noms_systemes[i],
                    'Coût Total Annuel (MAD)': analyses['totaux_globaux'][col]
                })
        
        df_totaux = pd.DataFrame(data)
        
        # Création du graphique avec barres côte à côte
        chart_totaux = alt.Chart(df_totaux).mark_bar().encode(
            x=alt.X('Système', title='Système de prime', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Coût Total Annuel (MAD)', title='Montant total annuel (MAD)'),
            color=alt.Color('Système', legend=alt.Legend(orient="top"), 
                           scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)]))
        ).properties(
            title='Comparaison des coûts totaux annuels des primes par système'
        )
        
        st.altair_chart(chart_totaux, use_container_width=True)
        
        # Graphique 2: Comparaison des primes moyennes par service (side by side)
        st.markdown("#### Comparaison des primes moyennes par service")
        
        # Préparation des données pour le graphique
        primes_cols = [f"prime_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
        data = []
        
        for i, col in enumerate(primes_cols):
            if col in analyses['totaux_globaux']:
                data.append({
                    'Système': noms_systemes[i],
                    'Prime Moyenne (MAD)': analyses['totaux_globaux'][col]
                })
        
        df_primes = pd.DataFrame(data)
        
        # Création du graphique avec barres côte à côte
        chart_primes = alt.Chart(df_primes).mark_bar().encode(
            x=alt.X('Système', title='Système de prime', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Prime Moyenne (MAD)', title='Prime moyenne par service (MAD)'),
            color=alt.Color('Système', legend=alt.Legend(orient="top"), 
                           scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)]))
        ).properties(
            title='Comparaison des primes moyennes par service pour chaque système'
        )
        
        st.altair_chart(chart_primes, use_container_width=True)
    
    with tab2:
        st.subheader("Comparaison par ligne de bus")
        
        if 'par_ligne' in analyses and len(analyses['par_ligne']) > 0:
            df_lignes = analyses['par_ligne']
            
            # Création de la visualisation par ligne
            st.markdown("#### Primes moyennes par service par ligne")
            
            # Préparation des données pour le graphique
            data_lignes = []
            
            for i, ligne in df_lignes.iterrows():
                for j, systeme in enumerate(systemes_actifs):
                    col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                    if col in df_lignes.columns:
                        data_lignes.append({
                            'LIGNE': ligne['LIGNE'],
                            'Système': systeme['nom'],
                            'Prime (MAD)': ligne[col]
                        })
            
            if data_lignes:
                df_data_lignes = pd.DataFrame(data_lignes)
                
                # Création du graphique côte à côte par ligne
                chart_lignes = alt.Chart(df_data_lignes).mark_bar().encode(
                    x=alt.X('LIGNE', title='Ligne de bus'),
                    y=alt.Y('Prime (MAD)', title='Prime moyenne par service (MAD)'),
                    color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                   scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                    column=alt.Column('Système', title='')
                ).properties(
                    width=120
                )
                
                st.altair_chart(chart_lignes, use_container_width=True)
            
            # Graphique des coûts totaux par ligne
            st.markdown("#### Coûts totaux annuels par ligne")
            
            # Préparation des données pour le graphique de coûts
            data_couts = []
            
            for i, ligne in df_lignes.iterrows():
                for j, systeme in enumerate(systemes_actifs):
                    col = f"cout_total_{systeme['nom'].replace(' ', '_').lower()}"
                    if col in df_lignes.columns:
                        data_couts.append({
                            'LIGNE': ligne['LIGNE'],
                            'Système': systeme['nom'],
                            'Coût (MAD)': ligne[col]
                        })
            
            if data_couts:
                df_data_couts = pd.DataFrame(data_couts)
                
                # Création du graphique côte à côte par ligne
                chart_couts = alt.Chart(df_data_couts).mark_bar().encode(
                    x=alt.X('LIGNE', title='Ligne de bus'),
                    y=alt.Y('Coût (MAD)', title='Coût total annuel (MAD)'),
                    color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                   scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                    column=alt.Column('Système', title='')
                ).properties(
                    width=120
                )
                
                st.altair_chart(chart_couts, use_container_width=True)
    
    with tab3:
        st.subheader("Analyse mensuelle")
        
        # Graphique des coûts mensuels moyens
        st.markdown("#### Coûts mensuels moyens")
        
        # Préparation des données pour le graphique mensuel
        mensuel_cols = [f"cout_total_{s['nom'].replace(' ', '_').lower()}_mensuel" for s in systemes_actifs]
        data_mensuel = []
        
        for i, col in enumerate(mensuel_cols):
            if col in analyses['totaux_globaux']:
                data_mensuel.append({
                    'Système': noms_systemes[i],
                    'Coût Mensuel (MAD)': analyses['totaux_globaux'][col]
                })
        
        if data_mensuel:
            df_mensuel = pd.DataFrame(data_mensuel)
            
            # Création du graphique avec barres côte à côte
            chart_mensuel = alt.Chart(df_mensuel).mark_bar().encode(
                x=alt.X('Système', title='Système de prime', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Coût Mensuel (MAD)', title='Coût mensuel moyen (MAD)'),
                color=alt.Color('Système', legend=alt.Legend(orient="top"), 
                               scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)]))
            ).properties(
                title='Comparaison des coûts mensuels moyens par système'
            )
            
            st.altair_chart(chart_mensuel, use_container_width=True)
        
        # Graphique des voyageurs mensuels moyens
        if 'VOY_MENSUEL' in analyses['totaux_globaux']:
            st.markdown("#### Voyageurs mensuels moyens")
            voy_mensuel = analyses['totaux_globaux']['VOY_MENSUEL']
            
            # Affichage en métrique
            st.metric("Nombre de voyageurs mensuel moyen", f"{voy_mensuel:,.0f}")
            
            # Si nous avons des données par mois
            if 'par_mois' in analyses and len(analyses['par_mois']) > 0:
                df_par_mois = analyses['par_mois']
                
                # Préparation des données par ligne et par mois
                data_mensuel_ligne = []
                
                for i, ligne in df_par_mois.iterrows():
                    data_mensuel_ligne.append({
                        'LIGNE': ligne['LIGNE'],
                        'Voyageurs mensuels': ligne['VOY_MENSUEL']
                    })
                
                if data_mensuel_ligne:
                    df_mensuel_ligne = pd.DataFrame(data_mensuel_ligne)
                    
                    # Création du graphique
                    chart_mensuel_ligne = alt.Chart(df_mensuel_ligne).mark_bar().encode(
                        x=alt.X('LIGNE', title='Ligne de bus'),
                        y=alt.Y('Voyageurs mensuels', title='Voyageurs mensuels moyens'),
                        color=alt.Color('LIGNE', legend=None)
                    ).properties(
                        title='Voyageurs mensuels moyens par ligne'
                    )
                    
                    st.altair_chart(chart_mensuel_ligne, use_container_width=True)
    
    with tab4:
        st.subheader("Analyse par granularité")
        
        # Création d'onglets pour chaque granularité
        subtab1, subtab2, subtab3, subtab4 = st.tabs([
            "Par ligne", 
            "Par bus", 
            "Par conducteur", 
            "Par service"
        ])
        
        with subtab1:
            st.markdown("#### Analyse par ligne de bus")
            
            if 'par_ligne' in analyses and len(analyses['par_ligne']) > 0:
                df_lignes = analyses['par_ligne']
                
                # Tableau récapitulatif des données par ligne
                st.dataframe(df_lignes[['LIGNE', 'VOY', 'BUS', 'VOY/SERVICE/J', 'NBRE CONDUCTEURS ETP'] + 
                                     [f"prime_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs] +
                                     [f"cout_total_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]])
        
        with subtab2:
            st.markdown("#### Analyse par bus")
            
            if 'par_bus' in analyses and len(analyses['par_bus']) > 0:
                df_bus = analyses['par_bus']
                
                # Préparation des données pour le graphique
                data_bus = []
                
                for i, ligne in df_bus.iterrows():
                    for j, systeme in enumerate(systemes_actifs):
                        col = f"cout_total_{systeme['nom'].replace(' ', '_').lower()}_bus"
                        if col in df_bus.columns:
                            data_bus.append({
                                'LIGNE': ligne['LIGNE'],
                                'Système': systeme['nom'],
                                'Coût par bus (MAD)': ligne[col]
                            })
                
                if data_bus:
                    df_data_bus = pd.DataFrame(data_bus)
                    
                    # Création du graphique côte à côte
                    chart_bus = alt.Chart(df_data_bus).mark_bar().encode(
                        x=alt.X('LIGNE', title='Ligne de bus'),
                        y=alt.Y('Coût par bus (MAD)', title='Coût annuel par bus (MAD)'),
                        color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                       scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                        column=alt.Column('Système', title='')
                    ).properties(
                        width=120,
                        title='Coût annuel par bus par ligne et par système'
                    )
                    
                    st.altair_chart(chart_bus, use_container_width=True)
        
        with subtab3:
            st.markdown("#### Analyse par conducteur")
            
            if 'par_conducteur' in analyses and len(analyses['par_conducteur']) > 0:
                df_conducteur = analyses['par_conducteur']
                
                # Préparation des données pour le graphique
                data_conducteur = []
                
                for i, ligne in df_conducteur.iterrows():
                    for j, systeme in enumerate(systemes_actifs):
                        col = f"cout_total_{systeme['nom'].replace(' ', '_').lower()}_conducteur"
                        if col in df_conducteur.columns:
                            data_conducteur.append({
                                'LIGNE': ligne['LIGNE'],
                                'Système': systeme['nom'],
                                'Coût par conducteur (MAD)': ligne[col]
                            })
                
                if data_conducteur:
                    df_data_conducteur = pd.DataFrame(data_conducteur)
                    
                    # Création du graphique côte à côte
                    chart_conducteur = alt.Chart(df_data_conducteur).mark_bar().encode(
                        x=alt.X('LIGNE', title='Ligne de bus'),
                        y=alt.Y('Coût par conducteur (MAD)', title='Coût annuel par conducteur (MAD)'),
                        color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                       scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                        column=alt.Column('Système', title='')
                    ).properties(
                        width=120,
                        title='Coût annuel par conducteur par ligne et par système'
                    )
                    
                    st.altair_chart(chart_conducteur, use_container_width=True)
        
        with subtab4:
            st.markdown("#### Analyse par service")
            
            if 'par_ligne' in analyses and len(analyses['par_ligne']) > 0:
                df_service = analyses['par_ligne']
                
                # Préparation des données pour le graphique
                data_service = []
                
                for i, ligne in df_service.iterrows():
                    for j, systeme in enumerate(systemes_actifs):
                        col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                        if col in df_service.columns:
                            data_service.append({
                                'LIGNE': ligne['LIGNE'],
                                'Système': systeme['nom'],
                                'Prime par service (MAD)': ligne[col]
                            })
                
                if data_service:
                    df_data_service = pd.DataFrame(data_service)
                    
                    # Création du graphique
                    chart_service = alt.Chart(df_data_service).mark_bar().encode(
                        x=alt.X('LIGNE', title='Ligne de bus'),
                        y=alt.Y('Prime par service (MAD)', title='Prime par service (MAD)'),
                        color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                       scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                    ).properties(
                        title='Prime par service par ligne et par système'
                    )
                    
                    st.altair_chart(chart_service, use_container_width=True)
    
    with tab5:
        st.subheader("Distribution des primes")
        
        if 'par_ligne' in analyses and len(analyses['par_ligne']) > 0:
            df_lignes = analyses['par_ligne']
            
            # Création de la visualisation de distribution
            st.markdown("#### Distribution des primes par service")
            
            # Préparation des données pour le graphique
            data_dist = []
            
            for i, ligne in df_lignes.iterrows():
                for j, systeme in enumerate(systemes_actifs):
                    col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                    if col in df_lignes.columns:
                        data_dist.append({
                            'Système': systeme['nom'],
                            'Prime (MAD)': ligne[col],
                            'Voyageurs': ligne['VOY/SERVICE/J']
                        })
            
            if data_dist:
                df_data_dist = pd.DataFrame(data_dist)
                
                # Création du graphique de dispersion
                chart_dist = alt.Chart(df_data_dist).mark_circle(size=60).encode(
                    x=alt.X('Voyageurs', title='Voyageurs par service'),
                    y=alt.Y('Prime (MAD)', title='Prime par service (MAD)'),
                    color=alt.Color('Système', legend=alt.Legend(orient="top"),
                                   scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
                    tooltip=['Système', 'Voyageurs', 'Prime (MAD)']
                ).properties(
                    title='Distribution des primes par nombre de voyageurs',
                    width=600,
                    height=400
                )
                
                st.altair_chart(chart_dist, use_container_width=True)
