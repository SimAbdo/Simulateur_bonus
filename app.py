import pandas as pd
import streamlit as st
import altair as alt
import io
import base64
import numpy as np
import copy
from utils import (SYSTEMES_DEFAUT, calculer_primes_df, valider_donnees,
                   get_download_link, exporter_systeme_json,
                   importer_systeme_json)
from data_format import obtenir_structure_csv, obtenir_exemple_csv

# Configuration de la page
st.set_page_config(page_title="Simulateur de Primes pour Conducteurs",
                   page_icon="🚌",
                   layout="wide",
                   initial_sidebar_state="expanded")

# Initialiser les variables de session si elles n'existent pas
if 'data' not in st.session_state:
    st.session_state.data = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'username' not in st.session_state:
    st.session_state.username = ""

if 'systemes_personnalises' not in st.session_state:
    st.session_state.systemes_personnalises = {
        "systeme_actuel": copy.deepcopy(SYSTEMES_DEFAUT["systeme_actuel"]),
        "systeme_nouveau": copy.deepcopy(SYSTEMES_DEFAUT["systeme_nouveau"])
    }


# Page de connexion
def page_connexion():
    st.title("🚌 Simulateur de Primes pour Conducteurs")
    st.markdown("### Connexion")

    col1, col2 = st.columns([1, 1])

    with col1:
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")

        if st.button("Se connecter"):
            # Vérification des identifiants spécifiques
            if username == "abdessamad.amoussas" and password == "admin1234":
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Identifiants incorrects. Veuillez réessayer.")

    with col2:
        st.markdown("""
        ### Bienvenue sur le Simulateur de Primes
        
        Cet outil vous permet de calculer et comparer différents systèmes de prime 
        pour les conducteurs de bus en fonction du nombre de voyageurs transportés.
        
        Veuillez vous connecter pour accéder à l'application.
        """)


# Fonction pour éditer les systèmes de prime sur une page dédiée
def page_configuration_systemes():
    st.title("Configuration des Systèmes de Prime")
    st.markdown(f"Utilisateur: {st.session_state.username}")

    tab1, tab2 = st.tabs(["Système Actuel", "Nouveau Système"])

    with tab1:
        st.subheader("Modifier le Système Actuel")
        systeme_actuel = st.session_state.systemes_personnalises[
            "systeme_actuel"]

        # Modification du nom et de la description
        systeme_actuel["nom"] = st.text_input("Nom du système",
                                              value=systeme_actuel["nom"],
                                              key="nom_actuel")

        systeme_actuel["description"] = st.text_area(
            "Description",
            value=systeme_actuel["description"],
            key="desc_actuel")

        # Affichage et modification des paliers
        st.subheader("Paliers de prime")

        # Convertir les paliers en DataFrame pour une meilleure manipulation
        paliers_df = pd.DataFrame(
            systeme_actuel["paliers"],
            columns=["min_voyageurs", "max_voyageurs", "taux"])

        # Afficher les paliers existants
        for idx, palier in paliers_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

            with col1:
                # Conversion sécurisée en entier, en gérant les NaN
                min_val = 0
                if not pd.isna(palier["min_voyageurs"]):
                    min_val = int(palier["min_voyageurs"])

                min_v = st.number_input(f"Min Voyageurs (Palier {idx+1})",
                                        value=min_val,
                                        min_value=0,
                                        key=f"min_actuel_{idx}")
                paliers_df.at[idx, "min_voyageurs"] = min_v

            with col2:
                # Conversion sécurisée en entier, en gérant les NaN et Inf
                max_val = 249
                if not pd.isna(palier["max_voyageurs"]
                               ) and palier["max_voyageurs"] != float('inf'):
                    max_val = int(palier["max_voyageurs"])

                max_v = st.number_input(f"Max Voyageurs (Palier {idx+1})",
                                        value=max_val,
                                        min_value=int(min_v),
                                        key=f"max_actuel_{idx}")
                paliers_df.at[
                    idx,
                    "max_voyageurs"] = max_v if max_v < 1000000 else float(
                        'inf')

            with col3:
                # Conversion sécurisée en float, en gérant les NaN
                taux_val = 0.1
                if not pd.isna(palier["taux"]):
                    taux_val = float(palier["taux"])

                taux = st.number_input(f"Taux MAD (Palier {idx+1})",
                                       value=taux_val,
                                       min_value=0.0,
                                       step=0.01,
                                       format="%.2f",
                                       key=f"taux_actuel_{idx}")
                paliers_df.at[idx, "taux"] = taux

            with col4:
                if st.button("🗑️", key=f"suppr_actuel_{idx}"):
                    paliers_df = paliers_df.drop(idx).reset_index(drop=True)
                    st.session_state.systemes_personnalises["systeme_actuel"][
                        "paliers"] = paliers_df.values.tolist()
                    st.rerun()

        # Bouton pour ajouter un nouveau palier
        if st.button("➕ Ajouter un palier", key="add_actuel"):
            # Trouver la valeur maximale actuelle pour le min du nouveau palier
            if not paliers_df.empty:
                dernier_max = paliers_df.iloc[-1]["max_voyageurs"]
                if dernier_max == float('inf'):
                    dernier_max = paliers_df.iloc[-1]["min_voyageurs"] + 100
                nouveau_min = dernier_max + 1
            else:
                nouveau_min = 0

            nouveau_palier = {
                "min_voyageurs": nouveau_min,
                "max_voyageurs": float('inf'),
                "taux": 0.1
            }
            paliers_df = pd.concat(
                [paliers_df, pd.DataFrame([nouveau_palier])],
                ignore_index=True)
            st.session_state.systemes_personnalises["systeme_actuel"][
                "paliers"] = paliers_df.values.tolist()
            st.rerun()

        # Mettre à jour les paliers dans la session
        systeme_actuel["paliers"] = paliers_df.values.tolist()

    with tab2:
        st.subheader("Modifier le Nouveau Système")
        systeme_nouveau = st.session_state.systemes_personnalises[
            "systeme_nouveau"]

        # Modification du nom et de la description
        systeme_nouveau["nom"] = st.text_input("Nom du système",
                                               value=systeme_nouveau["nom"],
                                               key="nom_nouveau")

        systeme_nouveau["description"] = st.text_area(
            "Description",
            value=systeme_nouveau["description"],
            key="desc_nouveau")

        # Affichage et modification des paliers
        st.subheader("Paliers de prime")

        # Convertir les paliers en DataFrame pour une meilleure manipulation
        paliers_df = pd.DataFrame(
            systeme_nouveau["paliers"],
            columns=["min_voyageurs", "max_voyageurs", "taux"])

        # Afficher les paliers existants
        for idx, palier in paliers_df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 3, 3, 1])

            with col1:
                # Conversion sécurisée en entier, en gérant les NaN
                min_val = 0
                if not pd.isna(palier["min_voyageurs"]):
                    min_val = int(palier["min_voyageurs"])

                min_v = st.number_input(f"Min Voyageurs (Palier {idx+1})",
                                        value=min_val,
                                        min_value=0,
                                        key=f"min_nouveau_{idx}")
                paliers_df.at[idx, "min_voyageurs"] = min_v

            with col2:
                # Conversion sécurisée en entier, en gérant les NaN et Inf
                max_val = 249
                if not pd.isna(palier["max_voyageurs"]
                               ) and palier["max_voyageurs"] != float('inf'):
                    max_val = int(palier["max_voyageurs"])

                max_v = st.number_input(f"Max Voyageurs (Palier {idx+1})",
                                        value=max_val,
                                        min_value=int(min_v),
                                        key=f"max_nouveau_{idx}")
                paliers_df.at[
                    idx,
                    "max_voyageurs"] = max_v if max_v < 1000000 else float(
                        'inf')

            with col3:
                # Conversion sécurisée en float, en gérant les NaN
                taux_val = 0.1
                if not pd.isna(palier["taux"]):
                    taux_val = float(palier["taux"])

                taux = st.number_input(f"Taux MAD (Palier {idx+1})",
                                       value=taux_val,
                                       min_value=0.0,
                                       step=0.01,
                                       format="%.2f",
                                       key=f"taux_nouveau_{idx}")
                paliers_df.at[idx, "taux"] = taux

            with col4:
                if st.button("🗑️", key=f"suppr_nouveau_{idx}"):
                    paliers_df = paliers_df.drop(idx).reset_index(drop=True)
                    st.session_state.systemes_personnalises["systeme_nouveau"][
                        "paliers"] = paliers_df.values.tolist()
                    st.rerun()

        # Bouton pour ajouter un nouveau palier
        if st.button("➕ Ajouter un palier", key="add_nouveau"):
            # Trouver la valeur maximale actuelle pour le min du nouveau palier
            if not paliers_df.empty:
                dernier_max = paliers_df.iloc[-1]["max_voyageurs"]
                if dernier_max == float('inf'):
                    dernier_max = paliers_df.iloc[-1]["min_voyageurs"] + 100
                nouveau_min = dernier_max + 1
            else:
                nouveau_min = 0

            nouveau_palier = {
                "min_voyageurs": nouveau_min,
                "max_voyageurs": float(10000),
                "taux": 0.1
            }
            paliers_df = pd.concat(
                [paliers_df, pd.DataFrame([nouveau_palier])],
                ignore_index=True)
            st.session_state.systemes_personnalises["systeme_nouveau"][
                "paliers"] = paliers_df.values.tolist()
            st.rerun()

        # Mettre à jour les paliers dans la session
        systeme_nouveau["paliers"] = paliers_df.values.tolist()

    # Boutons pour la navigation et actions
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Réinitialiser aux valeurs par défaut"):
            st.session_state.systemes_personnalises = {
                "systeme_actuel":
                copy.deepcopy(SYSTEMES_DEFAUT["systeme_actuel"]),
                "systeme_nouveau":
                copy.deepcopy(SYSTEMES_DEFAUT["systeme_nouveau"])
            }
            st.success(
                "Les systèmes ont été réinitialisés aux valeurs par défaut.")
            st.rerun()

    with col2:
        if st.button("Appliquer les modifications"):
            st.success(
                "Les modifications des systèmes de prime ont été appliquées.")

    with col3:
        # Grand bouton pour lancer l'exécution avec les systèmes modifiés
        if st.button("Exécuter avec ces configurations", type="primary"):
            st.session_state.page = "principale"
            st.rerun()

    # Bouton retour
    if st.button("Retour à l'application principale"):
        st.session_state.page = "principale"
        st.rerun()


# Fonction pour afficher la page principale de l'application
def page_principale():
    # Titre principal
    st.title(f"🚌 Simulateur de Primes pour Conducteurs")
    st.markdown(f"Utilisateur: {st.session_state.username}")
    st.markdown("""
    Cet outil vous permet de calculer et comparer différents systèmes de prime pour les conducteurs de bus
    en fonction du nombre de voyageurs transportés.
    """)

    # Barre latérale pour le chargement des données et les paramètres
    with st.sidebar:
        st.header("Données et Paramètres")

        # Section d'import de données
        st.subheader("Importer des données")

        uploaded_file = st.file_uploader(
            "Choisir un fichier Excel",
            type=["xlsx", "xls"],
            help=
            "Fichier Excel avec les colonnes: LIGNE, VOY, BUS, VOY/SERVICE/J, NBRE CONDUCTEURS ETP"
        )

        if uploaded_file is not None:
            try:
                data = pd.read_excel(uploaded_file)
                valide, message = valider_donnees(data)

                if valide:
                    st.session_state.data = data
                    st.success("Données chargées avec succès !")
                else:
                    st.error(f"Erreur dans le format des données: {message}")
            except Exception as e:
                st.error(f"Erreur lors du chargement du fichier: {str(e)}")
                st.info("Vérifiez le format attendu:")
                st.code(obtenir_structure_csv())

        # Informations sur la structure du CSV
        with st.expander("Structure du fichier attendu"):
            st.code(obtenir_structure_csv())

        # Section des paramètres de calcul
        st.subheader("Paramètres de calcul")

        nb_services_par_jour = st.number_input(
            "Nombre de services par jour",
            min_value=1,
            max_value=20,
            value=2,  
            help=
            "Nombre moyen de services (trajets) par jour pour chaque conducteur"
        )

        # Bouton pour accéder à la page de configuration des systèmes
        if st.button("Configurer les Systèmes de Prime"):
            st.session_state.page = "configurer_systemes"
            st.rerun()

        # Afficher un résumé des systèmes de prime actifs
        st.subheader("Systèmes de prime actifs")

        systemes_actifs = [
            st.session_state.systemes_personnalises["systeme_actuel"],
            st.session_state.systemes_personnalises["systeme_nouveau"]
        ]

        # Afficher les systèmes actifs
        for systeme in systemes_actifs:
            with st.expander(f"Détails: {systeme['nom']}"):
                st.write(f"**Description**: {systeme['description']}")

                # Afficher les paliers sous forme de tableau
                paliers_df = pd.DataFrame(systeme['paliers'])
                paliers_df.columns = [
                    "Min Voyageurs", "Max Voyageurs", "Taux (MAD)"
                ]
                st.dataframe(paliers_df)

        # Option de déconnexion
        if st.button("Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

    # Contenu principal
    if st.session_state.data is not None:
        # Effectuer les calculs sur les données
        # Utiliser les systèmes personnalisés
        systemes_actifs = [
            st.session_state.systemes_personnalises["systeme_actuel"],
            st.session_state.systemes_personnalises["systeme_nouveau"]
        ]

        # Calcul des primes avec le nombre de services par jour donné
        df_resultat = calculer_primes_df(st.session_state.data,
                                         systemes_actifs, nb_services_par_jour)

        # Analyses par catégorie
        analyses = {}

        # Calcul des totaux globaux (somme pour toutes les lignes)
        analyses['totaux_globaux'] = {}

        # VOY total (somme de VOY pour toutes les lignes)
        analyses['totaux_globaux']['VOY_TOTAL'] = df_resultat['VOY'].sum()

        # Calculer les sommes pour chaque système
        systeme_base = systemes_actifs[0]['nom'].replace(' ', '_').lower()
        systeme_comp = systemes_actifs[1]['nom'].replace(' ', '_').lower()

        # Coût total annuel pour chaque système (somme pour toutes les lignes)
        analyses['totaux_globaux'][f"cout_total_{systeme_base}"] = df_resultat[
            f"cout_total_{systeme_base}"].sum()
        analyses['totaux_globaux'][f"cout_total_{systeme_comp}"] = df_resultat[
            f"cout_total_{systeme_comp}"].sum()

        # Bonus moyen pondéré par conducteur pour chaque système
        total_conducteurs = df_resultat['NBRE CONDUCTEURS ETP'].sum()

        # Par jour
        analyses['totaux_globaux'][f"bonus_cond_jour_{systeme_base}"] = (
            df_resultat[f"BONUS/CONDUCTEUR/J_{systeme_base}"] *
            df_resultat['NBRE CONDUCTEURS ETP']).sum() / total_conducteurs
        analyses['totaux_globaux'][f"bonus_cond_jour_{systeme_comp}"] = (
            df_resultat[f"BONUS/CONDUCTEUR/J_{systeme_comp}"] *
            df_resultat['NBRE CONDUCTEURS ETP']).sum() / total_conducteurs

        # Par mois (jour * 30)
        analyses['totaux_globaux'][
            f"bonus_cond_mois_{systeme_base}"] = analyses['totaux_globaux'][
                f"bonus_cond_jour_{systeme_base}"] * 30
        analyses['totaux_globaux'][
            f"bonus_cond_mois_{systeme_comp}"] = analyses['totaux_globaux'][
                f"bonus_cond_jour_{systeme_comp}"] * 30

        # Par an (jour * 365)
        analyses['totaux_globaux'][f"bonus_cond_an_{systeme_base}"] = analyses[
            'totaux_globaux'][f"bonus_cond_jour_{systeme_base}"] * 365
        analyses['totaux_globaux'][f"bonus_cond_an_{systeme_comp}"] = analyses[
            'totaux_globaux'][f"bonus_cond_jour_{systeme_comp}"] * 365

        # Calculer les différences
        diff_cout_total = analyses['totaux_globaux'][
            f"cout_total_{systeme_comp}"] - analyses['totaux_globaux'][
                f"cout_total_{systeme_base}"]
        diff_cout_total_pct = (
            diff_cout_total /
            analyses['totaux_globaux'][f"cout_total_{systeme_base}"] *
            100 if analyses['totaux_globaux'][f"cout_total_{systeme_base}"]
            != 0 else 0)

        # Affichage des KPIs principaux
        st.subheader("KPIs Principaux")

        # Utiliser des colonnes pour afficher les KPIs (au lieu d'un tableau)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Nombre de lignes", f"{len(df_resultat)}")
            st.metric("Nombre total de voyageurs par an",
                      f"{int(analyses['totaux_globaux']['VOY_TOTAL']):,}")

        with col2:
            st.metric(
                f"Somme totale des bonus - {systemes_actifs[0]['nom']}",
                f"{analyses['totaux_globaux'][f'cout_total_{systeme_base}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/jour - {systemes_actifs[0]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_jour_{systeme_base}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/mois - {systemes_actifs[0]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_mois_{systeme_base}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/an - {systemes_actifs[0]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_an_{systeme_base}']:,.2f} MAD"
            )

        with col3:
            st.metric(
                f"Somme totale des bonus - {systemes_actifs[1]['nom']}",
                f"{analyses['totaux_globaux'][f'cout_total_{systeme_comp}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/jour - {systemes_actifs[1]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_jour_{systeme_comp}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/mois - {systemes_actifs[1]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_mois_{systeme_comp}']:,.2f} MAD"
            )
            st.metric(
                f"Bonus moyen par conducteur/an - {systemes_actifs[1]['nom']}",
                f"{analyses['totaux_globaux'][f'bonus_cond_an_{systeme_comp}']:,.2f} MAD"
            )

        # Afficher la différence en pourcentage
        st.info(
            f"**Différence entre les systèmes**: {diff_cout_total:,.2f} MAD ({diff_cout_total_pct:.2f}%)"
        )

        # Visualisation sous forme de graphique à barres
        st.subheader("Comparaison des systèmes de bonus")

        # Créer des données pour le graphique
        chart_data = {
            'Système': [systemes_actifs[0]['nom'], systemes_actifs[1]['nom']],
            'Bonus total (MAD)': [
                analyses['totaux_globaux'][f"cout_total_{systeme_base}"],
                analyses['totaux_globaux'][f"cout_total_{systeme_comp}"]
            ]
        }

        df_chart = pd.DataFrame(chart_data)

        # Créer le graphique
        chart = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X('Système:N', title='Système de prime'),
            y=alt.Y('Bonus total (MAD):Q', title='Bonus total (MAD)'),
            color=alt.Color('Système:N', legend=None),
            tooltip=['Système', 'Bonus total (MAD)']).properties(
                title='Comparaison des bonus totaux entre les systèmes',
                width=600,
                height=400)

        st.altair_chart(chart, use_container_width=True)

        # Graphique des bonus moyens par conducteur
        st.subheader("Comparaison des bonus moyens par conducteur")

        # Créer des données pour le graphique des bonus moyens
        chart_data_cond = pd.DataFrame({
            'Période': ['Par Jour', 'Par Mois', 'Par An'] * 2,
            'Système':
            [systemes_actifs[0]['nom']] * 3 + [systemes_actifs[1]['nom']] * 3,
            'Bonus moyen (MAD)': [
                analyses['totaux_globaux'][f"bonus_cond_jour_{systeme_base}"],
                analyses['totaux_globaux'][f"bonus_cond_mois_{systeme_base}"],
                analyses['totaux_globaux'][f"bonus_cond_an_{systeme_base}"],
                analyses['totaux_globaux'][f"bonus_cond_jour_{systeme_comp}"],
                analyses['totaux_globaux'][f"bonus_cond_mois_{systeme_comp}"],
                analyses['totaux_globaux'][f"bonus_cond_an_{systeme_comp}"]
            ]
        })

        # Créer le graphique pour les bonus moyens
        chart_cond = alt.Chart(chart_data_cond).mark_bar().encode(
            x=alt.X('Période:N', title='Période'),
            y=alt.Y('Bonus moyen (MAD):Q', title='Bonus moyen (MAD)'),
            color=alt.Color('Système:N', legend=alt.Legend(orient="top")),
            column=alt.Column('Période:N', title=None),
            tooltip=['Système', 'Période', 'Bonus moyen (MAD)']).properties(
                title='Comparaison des bonus moyens par conducteur', width=150)

        st.altair_chart(chart_cond, use_container_width=True)

        # Option pour télécharger les résultats
        st.subheader("Données détaillées par ligne")

        # Sélectionner les colonnes pertinentes
        colonnes_affichage = ["LIGNE", "VOY", "BUS", "NBRE CONDUCTEURS ETP"]

        # Ajouter les colonnes des primes pour chaque système
        for systeme in systemes_actifs:
            nom_col = systeme['nom'].replace(' ', '_').lower()
            colonnes_affichage.extend([
                f"prime_{nom_col}", f"cout_total_{nom_col}",
                f"BONUS/CONDUCTEUR/J_{nom_col}",
                f"BONUS/CONDUCTEUR/AN_{nom_col}"
            ])

        st.dataframe(df_resultat[colonnes_affichage])

        # Option pour télécharger les résultats en Excel
        st.markdown("### 💾 Exporter les résultats")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_resultat[colonnes_affichage].to_excel(writer,
                                                     sheet_name='Resultats',
                                                     index=False)

            # Créer un onglet pour les KPIs
            kpi_df = pd.DataFrame({
                'Métrique': [
                    "Nombre de lignes", "Nombre total de voyageurs par an",
                    f"Somme totale des bonus - {systemes_actifs[0]['nom']}",
                    f"Somme totale des bonus - {systemes_actifs[1]['nom']}",
                    "Différence entre les systèmes",
                    "Différence en pourcentage",
                    f"Bonus moyen par conducteur/jour - {systemes_actifs[0]['nom']}",
                    f"Bonus moyen par conducteur/mois - {systemes_actifs[0]['nom']}",
                    f"Bonus moyen par conducteur/an - {systemes_actifs[0]['nom']}",
                    f"Bonus moyen par conducteur/jour - {systemes_actifs[1]['nom']}",
                    f"Bonus moyen par conducteur/mois - {systemes_actifs[1]['nom']}",
                    f"Bonus moyen par conducteur/an - {systemes_actifs[1]['nom']}"
                ],
                'Valeur': [
                    len(df_resultat),
                    f"{analyses['totaux_globaux']['VOY_TOTAL']}",
                    f"{analyses['totaux_globaux'][f'cout_total_{systeme_base}']}",
                    f"{analyses['totaux_globaux'][f'cout_total_{systeme_comp}']}",
                    f"{diff_cout_total}", f"{diff_cout_total_pct}%",
                    f"{analyses['totaux_globaux'][f'bonus_cond_jour_{systeme_base}']}",
                    f"{analyses['totaux_globaux'][f'bonus_cond_mois_{systeme_base}']}",
                    f"{analyses['totaux_globaux'][f'bonus_cond_an_{systeme_base}']}",
                    f"{analyses['totaux_globaux'][f'bonus_cond_jour_{systeme_comp}']}",
                    f"{analyses['totaux_globaux'][f'bonus_cond_mois_{systeme_comp}']}",
                    f"{analyses['totaux_globaux'][f'bonus_cond_an_{systeme_comp}']}"
                ]
            })
            kpi_df.to_excel(writer, sheet_name='KPIs', index=False)

            # Ajouter les détails des systèmes de prime
            sys_actuel_df = pd.DataFrame(
                systemes_actifs[0]['paliers'],
                columns=["Min Voyageurs", "Max Voyageurs", "Taux (MAD)"])
            sys_actuel_df.to_excel(
                writer,
                sheet_name=f'Système {systemes_actifs[0]["nom"]}',
                index=False)

            sys_nouveau_df = pd.DataFrame(
                systemes_actifs[1]['paliers'],
                columns=["Min Voyageurs", "Max Voyageurs", "Taux (MAD)"])
            sys_nouveau_df.to_excel(
                writer,
                sheet_name=f'Système {systemes_actifs[1]["nom"]}',
                index=False)

        excel_data = buffer.getvalue()

        # Créer un lien de téléchargement pour le fichier Excel
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="resultats_primes.xlsx">Télécharger les résultats (Excel)</a>'
        st.markdown(href, unsafe_allow_html=True)

    else:
        st.info("Veuillez charger des données pour commencer l'analyse.")

        # Afficher une description des systèmes de prime
        st.subheader("Systèmes de Prime Disponibles")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"### {st.session_state.systemes_personnalises['systeme_actuel']['nom']}"
            )
            st.write(st.session_state.systemes_personnalises["systeme_actuel"]
                     ["description"])

            # Afficher les paliers sous forme de tableau
            paliers_df = pd.DataFrame(
                st.session_state.systemes_personnalises["systeme_actuel"]
                ["paliers"])
            paliers_df.columns = [
                "Min Voyageurs", "Max Voyageurs", "Taux (MAD)"
            ]
            st.dataframe(paliers_df)

        with col2:
            st.markdown(
                f"### {st.session_state.systemes_personnalises['systeme_nouveau']['nom']}"
            )
            st.write(st.session_state.systemes_personnalises["systeme_nouveau"]
                     ["description"])

            # Afficher les paliers sous forme de tableau
            paliers_df = pd.DataFrame(
                st.session_state.systemes_personnalises["systeme_nouveau"]
                ["paliers"])
            paliers_df.columns = [
                "Min Voyageurs", "Max Voyageurs", "Taux (MAD)"
            ]
            st.dataframe(paliers_df)

    # Pied de page
    st.markdown("---")
    st.markdown("🚌 Simulateur de Primes pour Conducteurs - Version 1.0")


# Gestion de la navigation entre les pages
if 'page' not in st.session_state:
    st.session_state.page = "accueil"

# Afficher la bonne page en fonction de l'état d'authentification et de la page actuelle
if not st.session_state.authenticated:
    page_connexion()
elif st.session_state.page == "configurer_systemes":
    page_configuration_systemes()
else:
    page_principale()
