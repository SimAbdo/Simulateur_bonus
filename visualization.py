import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt
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
    
    # Graphique 1: Comparaison des totaux globaux (side by side)
    st.subheader("Comparaison des totaux globaux des primes")
    
    # Préparation des données pour le graphique
    totaux_cols = [f"prime_{s['nom'].replace(' ', '_').lower()}" for s in systemes_actifs]
    data = []
    
    for i, col in enumerate(totaux_cols):
        if col in analyses['totaux_globaux']:
            data.append({
                'Système': noms_systemes[i],
                'Prime Totale (€)': analyses['totaux_globaux'][col]
            })
    
    df_totaux = pd.DataFrame(data)
    
    # Création du graphique avec barres côte à côte
    chart_totaux = alt.Chart(df_totaux).mark_bar().encode(
        x=alt.X('Système', title='Système de prime', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('Prime Totale (€)', title='Montant total (€)'),
        color=alt.Color('Système', legend=alt.Legend(orient="top"), 
                       scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)]))
    ).properties(
        title='Comparaison des montants totaux des primes par système'
    )
    
    st.altair_chart(chart_totaux, use_container_width=True)
    
    # Graphique 2: Comparaison par conducteur (side by side)
    st.subheader("Comparaison des primes par conducteur")
    
    # Transformer les données pour affichage côte à côte
    cols_conducteur = ['conducteur_id', 'nb_voyageurs'] + [col for col in totaux_cols if col in analyses['par_conducteur']]
    par_conducteur = analyses['par_conducteur'][cols_conducteur].copy() if 'par_conducteur' in analyses else None
    
    if par_conducteur is not None and not par_conducteur.empty:
        # Préparer les données pour le graphique
        data_conducteur = pd.melt(
            par_conducteur, 
            id_vars=['conducteur_id', 'nb_voyageurs'],
            value_vars=[col for col in totaux_cols if col in par_conducteur.columns],
            var_name='Système', value_name='Prime'
        )
        
        # Renommer les systèmes pour l'affichage
        mapping_noms = {}
        for s in systemes_actifs:
            mapping_noms[f"prime_{s['nom'].replace(' ', '_').lower()}"] = s['nom']
        data_conducteur['Système'] = data_conducteur['Système'].replace(mapping_noms)
        
        # Créer graphique avec barres côte à côte
        chart_conducteur = alt.Chart(data_conducteur).mark_bar().encode(
            x=alt.X('conducteur_id:N', title='Conducteur'),
            y=alt.Y('Prime:Q', title='Prime (€)'),
            color=alt.Color('Système:N', legend=alt.Legend(orient="top"),
                          scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
            column=alt.Column('Système:N', title=None),
            tooltip=['conducteur_id', 'nb_voyageurs', 'Prime']
        ).properties(
            title='Comparaison des primes par conducteur et par système'
        )
        
        st.altair_chart(chart_conducteur, use_container_width=True)
    
    # Graphique 3: Comparaison par ligne de service (side by side)
    st.subheader("Comparaison par ligne de service")
    
    cols_ligne = ['ligne_service', 'nb_voyageurs'] + [col for col in totaux_cols if col in analyses['par_ligne']]
    par_ligne = analyses['par_ligne'][cols_ligne].copy() if 'par_ligne' in analyses else None
    
    if par_ligne is not None and not par_ligne.empty:
        # Préparer les données
        data_ligne = pd.melt(
            par_ligne, 
            id_vars=['ligne_service', 'nb_voyageurs'],
            value_vars=[col for col in totaux_cols if col in par_ligne.columns],
            var_name='Système', value_name='Prime'
        )
        
        # Renommer les systèmes pour l'affichage
        mapping_noms = {}
        for s in systemes_actifs:
            mapping_noms[f"prime_{s['nom'].replace(' ', '_').lower()}"] = s['nom']
        data_ligne['Système'] = data_ligne['Système'].replace(mapping_noms)
        
        # Création du graphique avec barres côte à côte
        chart_ligne = alt.Chart(data_ligne).mark_bar().encode(
            x=alt.X('ligne_service:N', title='Ligne de service'),
            y=alt.Y('Prime:Q', title='Montant total (€)'),
            color=alt.Color('Système:N', legend=alt.Legend(orient="top"),
                          scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
            column=alt.Column('Système:N', title=None),
            tooltip=['ligne_service', 'nb_voyageurs', 'Prime']
        ).properties(
            title='Comparaison des primes par ligne de service et par système'
        )
        
        st.altair_chart(chart_ligne, use_container_width=True)
    
    # Graphique 4: Distribution des voyageurs dans le temps
    st.subheader("Distribution des voyageurs par service")
    
    if 'analyses_temporelles' in analyses and 'par_date' in analyses['analyses_temporelles']:
        par_date = analyses['analyses_temporelles']['par_date']
        
        # Graphique en ligne simple pour l'évolution des voyageurs
        voyageurs_chart = alt.Chart(par_date).mark_line().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('nb_voyageurs:Q', title='Nombre de voyageurs'),
            tooltip=['date', 'nb_voyageurs']
        ).properties(
            title='Évolution du nombre de voyageurs dans le temps'
        )
        
        st.altair_chart(voyageurs_chart, use_container_width=True)
        
        # Transformation des données pour comparer les primes par date
        cols_date = ['date', 'nb_voyageurs'] + [col for col in totaux_cols if col in par_date]
        data_date = pd.melt(
            par_date[cols_date], 
            id_vars=['date', 'nb_voyageurs'],
            value_vars=[col for col in totaux_cols if col in par_date.columns],
            var_name='Système', value_name='Prime'
        )
        
        # Renommer les systèmes pour l'affichage
        mapping_noms = {}
        for s in systemes_actifs:
            mapping_noms[f"prime_{s['nom'].replace(' ', '_').lower()}"] = s['nom']
        data_date['Système'] = data_date['Système'].replace(mapping_noms)
        
        # Graphique en ligne pour l'évolution des primes par système
        primes_chart = alt.Chart(data_date).mark_line().encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('Prime:Q', title='Prime (€)'),
            color=alt.Color('Système:N', legend=alt.Legend(orient="top"),
                          scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
            tooltip=['date', 'Système', 'Prime', 'nb_voyageurs']
        ).properties(
            title='Évolution des primes dans le temps par système'
        )
        
        st.altair_chart(primes_chart, use_container_width=True)
    
    # Graphique 5: Comparaison par équipe (side by side)
    st.subheader("Comparaison par équipe")
    
    cols_equipe = ['equipe', 'nb_voyageurs'] + [col for col in totaux_cols if col in analyses['par_equipe']]
    par_equipe = analyses['par_equipe'][cols_equipe].copy() if 'par_equipe' in analyses else None
    
    if par_equipe is not None and not par_equipe.empty:
        # Préparer les données
        data_equipe = pd.melt(
            par_equipe, 
            id_vars=['equipe', 'nb_voyageurs'],
            value_vars=[col for col in totaux_cols if col in par_equipe.columns],
            var_name='Système', value_name='Prime'
        )
        
        # Renommer les systèmes pour l'affichage
        mapping_noms = {}
        for s in systemes_actifs:
            mapping_noms[f"prime_{s['nom'].replace(' ', '_').lower()}"] = s['nom']
        data_equipe['Système'] = data_equipe['Système'].replace(mapping_noms)
        
        # Création du graphique avec barres côte à côte
        chart_equipe = alt.Chart(data_equipe).mark_bar().encode(
            x=alt.X('equipe:N', title='Équipe'),
            y=alt.Y('Prime:Q', title='Montant total (€)'),
            color=alt.Color('Système:N', legend=alt.Legend(orient="top"),
                          scale=alt.Scale(domain=noms_systemes, range=couleurs[:len(noms_systemes)])),
            column=alt.Column('Système:N', title=None),
            tooltip=['equipe', 'nb_voyageurs', 'Prime']
        ).properties(
            title='Comparaison des primes par équipe et par système'
        )
        
        st.altair_chart(chart_equipe, use_container_width=True)

def afficher_detail_conducteur(df, conducteur_id, systemes_actifs=None):
    """
    Affiche les détails pour un conducteur spécifique
    
    Args:
        df (pandas.DataFrame): DataFrame contenant les données
        conducteur_id (str): Identifiant du conducteur à analyser
        systemes_actifs (list): Liste des systèmes de prime actifs
        
    Returns:
        None: Affiche les détails directement via Streamlit
    """
    import matplotlib.pyplot as plt
    
    # Filtrer les données pour le conducteur spécifique
    df_conducteur = df[df['conducteur_id'] == conducteur_id].copy()
    
    # Statistiques globales du conducteur
    total_voyageurs = df_conducteur['nb_voyageurs'].sum()

    # Rechercher les colonnes de prime correspondant aux systèmes actifs
    colonnes_primes = []
    for col in df_conducteur.columns:
        if col.startswith('prime_'):
            colonnes_primes.append(col)
    
    # Afficher les métriques pour chaque système
    st.subheader(f"Statistiques pour {conducteur_id}")
    
    # Afficher d'abord le nombre total de voyageurs
    st.metric("Total voyageurs", total_voyageurs)
    
    # Ensuite, afficher les montants de prime
    cols = st.columns(min(3, len(colonnes_primes)))
    
    for i, col in enumerate(colonnes_primes):
        prime = df_conducteur[col].sum()
        # Extraire le nom du système à partir du nom de colonne
        nom_systeme = col.replace('prime_', '').replace('_', ' ').title()
        
        # Si c'est une colonne de différence, l'afficher avec delta
        if i == 0:  # Système de référence
            cols[i % 3].metric(nom_systeme, f"{prime:.2f} €")
        else:
            # Calculer la différence avec le système de référence
            prime_ref = df_conducteur[colonnes_primes[0]].sum()
            diff = prime - prime_ref
            pct = (prime / prime_ref - 1) * 100 if prime_ref > 0 else 0
            cols[i % 3].metric(nom_systeme, f"{prime:.2f} €", f"{diff:.2f} € ({pct:.1f}%)")
    
    # Distribution des voyageurs par service pour ce conducteur
    st.subheader(f"Distribution des voyageurs par service pour {conducteur_id}")
    
    hist_values = np.histogram(
        df_conducteur['nb_voyageurs'], 
        bins=20, 
        range=(df_conducteur['nb_voyageurs'].min(), df_conducteur['nb_voyageurs'].max())
    )[0]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(df_conducteur['nb_voyageurs'], bins=20)
    ax.set_xlabel('Nombre de voyageurs')
    ax.set_ylabel('Nombre de services')
    
    # Ajouter les seuils des différents systèmes si disponibles
    if systemes_actifs:
        couleurs = ['r', 'g', 'b', 'm']
        for i, systeme in enumerate(systemes_actifs):
            for j, palier in enumerate(systeme["paliers"][1:], 1):  # Commencer au deuxième palier
                ax.axvline(
                    x=palier["min"], 
                    color=couleurs[i % len(couleurs)], 
                    linestyle='--', 
                    alpha=0.7, 
                    label=f"{systeme['nom']} - Seuil {palier['min']} voyageurs"
                )
    else:
        # Afficher les seuils par défaut si aucun système n'est fourni
        ax.axvline(x=100, color='r', linestyle='--', alpha=0.7, label='Seuil 100 voyageurs')
        ax.axvline(x=350, color='g', linestyle='--', alpha=0.7, label='Seuil 350 voyageurs')
    
    ax.legend()
    st.pyplot(fig)
    
    # Afficher les détails de chaque service
    st.subheader(f"Détails des services pour {conducteur_id}")
    
    # Trier par date si disponible, sinon par nombre de voyageurs
    df_details = df_conducteur.sort_values('date' if 'date' in df_conducteur.columns else 'nb_voyageurs', ascending=False)
    
    # Sélectionner les colonnes à afficher
    colonnes_affichage = []
    
    if 'date' in df_details.columns:
        colonnes_affichage.append('date')
    
    if 'quart' in df_details.columns:
        colonnes_affichage.append('quart')
    
    colonnes_affichage.extend(['ligne_service', 'bus_id', 'nb_voyageurs'])
    colonnes_affichage.extend(colonnes_primes)
    
    # Ajouter les colonnes de différence si elles existent
    for col in df_details.columns:
        if col.startswith('diff_'):
            colonnes_affichage.append(col)
    
    # S'assurer que toutes les colonnes sélectionnées existent
    colonnes_affichage = [col for col in colonnes_affichage if col in df_details.columns]
    
    # Afficher le dataframe
    st.dataframe(df_details[colonnes_affichage])

def generer_rapport_impact(analyses, systemes_actifs=None):
    """
    Génère un rapport d'impact financier des systèmes de primes
    
    Args:
        analyses (dict): Dictionnaire contenant les analyses des données
        systemes_actifs (list): Liste des systèmes de prime actifs
        
    Returns:
        None: Affiche le rapport directement via Streamlit
    """
    # Récupérer les statistiques globales
    totaux = analyses['totaux_globaux']
    
    # Vérifier que nous avons au moins deux systèmes pour comparer
    if systemes_actifs and len(systemes_actifs) > 1:
        systeme_ref = systemes_actifs[0]
        systeme_comp = systemes_actifs[1]
        
        # Noms des colonnes pour les systèmes
        col_ref = f"prime_{systeme_ref['nom'].replace(' ', '_').lower()}"
        col_comp = f"prime_{systeme_comp['nom'].replace(' ', '_').lower()}"
        col_diff = f"diff_{systeme_comp['nom'].replace(' ', '_').lower()}"
        col_pct = f"pct_{systeme_comp['nom'].replace(' ', '_').lower()}"
        
        # S'assurer que toutes les colonnes existent
        if col_ref in totaux and col_comp in totaux and col_diff in totaux and col_pct in totaux:
            difference_totale = totaux[col_diff]
            pourcentage_global = totaux[col_pct]
            
            # Créer le rapport
            st.subheader("Rapport d'impact financier")
            
            # Impact global
            st.markdown(f"""
            ### Impact global
            
            Le passage de "{systeme_ref['nom']}" à "{systeme_comp['nom']}" entraînerait une 
            **{'+' if difference_totale > 0 else ''}{difference_totale:.2f} €** ({pourcentage_global:.2f}%) 
            sur le montant total des primes.
            
            * Prime totale avec {systeme_ref['nom']}: **{totaux[col_ref]:.2f} €**
            * Prime totale avec {systeme_comp['nom']}: **{totaux[col_comp]:.2f} €**
            * Nombre total de voyageurs: **{totaux['nb_voyageurs']}**
            """)
            
            # Analyse des gagnants et perdants
            if 'gagnants' in analyses and 'perdants' in analyses:
                st.markdown("### Analyse des conducteurs les plus impactés")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"#### Top 5 des conducteurs gagnants avec {systeme_comp['nom']}")
                    gagnants = analyses['gagnants']
                    if not gagnants.empty:
                        for _, row in gagnants.iterrows():
                            diff_col = next((col for col in row.index if col.startswith('diff_')), None)
                            pct_col = next((col for col in row.index if col.startswith('pct_')), None)
                            
                            if diff_col and pct_col:
                                st.markdown(f"""
                                **{row['conducteur_id']}**: +{row[diff_col]:.2f} € ({row[pct_col]:.1f}%)  
                                """)
                    else:
                        st.info("Aucun conducteur ne bénéficie significativement de ce changement.")
                
                with col2:
                    st.markdown(f"#### Top 5 des conducteurs perdants avec {systeme_comp['nom']}")
                    perdants = analyses['perdants']
                    if not perdants.empty:
                        for _, row in perdants.iterrows():
                            diff_col = next((col for col in row.index if col.startswith('diff_')), None)
                            pct_col = next((col for col in row.index if col.startswith('pct_')), None)
                            
                            if diff_col and pct_col:
                                st.markdown(f"""
                                **{row['conducteur_id']}**: {row[diff_col]:.2f} € ({row[pct_col]:.1f}%)  
                                """)
                    else:
                        st.info("Aucun conducteur n'est défavorisé par ce changement.")
            
            # Seuils de rentabilité
            st.markdown("### Analyse des seuils de rentabilité")
            
            # Récupérer les seuils des deux systèmes
            seuils_ref = [p["min"] for p in systeme_ref["paliers"][1:]]
            seuils_comp = [p["min"] for p in systeme_comp["paliers"][1:]]
            taux_ref = [p["taux"] for p in systeme_ref["paliers"]]
            taux_comp = [p["taux"] for p in systeme_comp["paliers"]]
            
            # Déterminer les points où le système comparé devient avantageux
            points_avantage = []
            
            # Cas simple : comparer deux systèmes à paliers
            if len(seuils_comp) > 0:
                for seuil in seuils_comp:
                    # Calculer un exemple avec 20 voyageurs de plus que le seuil
                    voyageurs = seuil + 20
                    
                    # Calculer les primes pour les deux systèmes
                    prime_ref = 0
                    for i, p in enumerate(systeme_ref["paliers"]):
                        min_voy = p["min"]
                        max_voy = p["max"]
                        if i < len(systeme_ref["paliers"]) - 1:
                            max_voy = systeme_ref["paliers"][i+1]["min"] - 1
                        
                        if voyageurs >= min_voy:
                            voy_dans_palier = min(voyageurs, max_voy) - min_voy + 1
                            prime_ref += voy_dans_palier * p["taux"]
                    
                    prime_comp = 0
                    for i, p in enumerate(systeme_comp["paliers"]):
                        min_voy = p["min"]
                        max_voy = p["max"]
                        if i < len(systeme_comp["paliers"]) - 1:
                            max_voy = systeme_comp["paliers"][i+1]["min"] - 1
                        
                        if voyageurs >= min_voy:
                            voy_dans_palier = min(voyageurs, max_voy) - min_voy + 1
                            prime_comp += voy_dans_palier * p["taux"]
                    
                    if prime_comp > prime_ref:
                        points_avantage.append((seuil, voyageurs, prime_comp - prime_ref))
            
            if points_avantage:
                st.markdown(f"""
                Le système "{systeme_comp['nom']}" devient avantageux par rapport à "{systeme_ref['nom']}":
                """)
                
                for seuil, exemple, diff in points_avantage:
                    st.markdown(f"""
                    * À partir de **{seuil} voyageurs** par service (exemple : avec {exemple} voyageurs, 
                      la différence est de +{diff:.2f}€)
                    """)
            else:
                # Comparaison simple des premiers taux
                if taux_comp[0] > taux_ref[0]:
                    st.markdown(f"""
                    Le système "{systeme_comp['nom']}" est **toujours avantageux** par rapport à "{systeme_ref['nom']}" 
                    car le taux de base est plus élevé ({taux_comp[0]:.2f}€ contre {taux_ref[0]:.2f}€).
                    """)
                else:
                    st.markdown(f"""
                    Le système "{systeme_comp['nom']}" n'est **jamais avantageux** par rapport à "{systeme_ref['nom']}" 
                    dans la plage des données analysées.
                    """)
            
            # Conclusion et recommandation
            st.markdown("### Conclusion")
            
            if difference_totale > 0:
                st.markdown(f"""
                Le système "{systeme_comp['nom']}" représente un **coût supplémentaire** de {difference_totale:.2f} € 
                ({pourcentage_global:.1f}%) par rapport au système "{systeme_ref['nom']}". Ce surcoût doit être évalué 
                en fonction des bénéfices attendus en termes de motivation et de performance des conducteurs.
                """)
            else:
                st.markdown(f"""
                Le système "{systeme_comp['nom']}" représente une **économie** de {-difference_totale:.2f} € 
                ({-pourcentage_global:.1f}%) par rapport au système "{systeme_ref['nom']}". Cette économie doit être 
                évaluée en fonction des risques potentiels sur la motivation des conducteurs.
                """)
            
            # Recommandations générales
            st.markdown("""
            ### Recommandations générales
            
            1. **Équité entre conducteurs** : Vérifiez que le nouveau système ne crée pas de disparités trop importantes.
            
            2. **Motivation** : Les systèmes à paliers peuvent motiver les conducteurs à atteindre les seuils supérieurs.
            
            3. **Prévisibilité budgétaire** : Évaluez l'impact budgétaire à long terme de ce changement.
            
            4. **Communication** : Préparez une communication claire expliquant les avantages du système choisi.
            """)
        else:
            st.warning("Données insuffisantes pour générer un rapport d'impact complet.")
    else:
        st.warning("Au moins deux systèmes de prime sont nécessaires pour générer un rapport d'impact comparatif.")
