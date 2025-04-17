import streamlit as st
import pandas as pd
import numpy as np
import json
import base64
import copy

# Import des modules personnalisés
from utils import calculer_primes_df, valider_donnees, get_download_link, SYSTEMES_DEFAUT
from data_generation import generer_donnees_synthetiques, preparer_exemple_csv
from analysis import analyser_donnees, filtrer_donnees
from visualization import creer_graphiques_comparaison, afficher_detail_conducteur, generer_rapport_impact

# Configuration de la page
st.set_page_config(
    page_title="Simulateur de Primes pour Conducteurs et Contrôleurs",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded")

# Initialisation de la session state si nécessaire
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'data' not in st.session_state:
    st.session_state.data = None
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None
if 'show_details' not in st.session_state:
    st.session_state.show_details = False
if 'selected_conducteur' not in st.session_state:
    st.session_state.selected_conducteur = None
if 'page' not in st.session_state:
    st.session_state.page = "Accueil"
if 'systemes_actifs' not in st.session_state:
    st.session_state.systemes_actifs = [
        SYSTEMES_DEFAUT["systeme_actuel"], SYSTEMES_DEFAUT["systeme_nouveau"]
    ]
if 'parametres_generation' not in st.session_state:
    st.session_state.parametres_generation = {
        "nb_conducteurs": 10,
        "nb_bus": 5,
        "nb_lignes": 3,
        "nb_equipes": 2,
        "nb_jours": 30,
        "nb_voyageurs_min": 50,
        "nb_voyageurs_max": 500
    }
if 'analyses' not in st.session_state:
    st.session_state.analyses = None
if 'source_donnees' not in st.session_state:
    st.session_state.source_donnees = "Génération Synthétique"
if 'filtres' not in st.session_state:
    st.session_state.filtres = {}


# Fonction pour changer de page
def changer_page(page):
    st.session_state.page = page


# Fonctions pour la génération et l'analyse des données
def generer_et_analyser_donnees():
    with st.spinner("Génération des données en cours..."):
        params = st.session_state.parametres_generation
        df = generer_donnees_synthetiques(
            nb_conducteurs=params["nb_conducteurs"],
            nb_bus=params["nb_bus"],
            nb_lignes=params["nb_lignes"],
            nb_equipes=params["nb_equipes"],
            nb_jours=params["nb_jours"],
            nb_voyageurs_min=params["nb_voyageurs_min"],
            nb_voyageurs_max=params["nb_voyageurs_max"])
        df = calculer_primes_df(df, st.session_state.systemes_actifs)
        st.session_state.data = df
        st.session_state.filtered_data = df
        st.session_state.analyses = analyser_donnees(
            df, st.session_state.systemes_actifs)
        st.session_state.page = "Résultats"
        st.success("Données générées avec succès!")
        st.rerun()


def appliquer_filtres():
    if st.session_state.data is not None:
        df_filtre = filtrer_donnees(st.session_state.data,
                                    st.session_state.filtres)
        st.session_state.filtered_data = df_filtre
        if not df_filtre.empty:
            st.session_state.analyses = analyser_donnees(
                df_filtre, st.session_state.systemes_actifs)
            st.success("Filtres appliqués avec succès!")
        else:
            st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
        st.rerun()


# Page de connexion
if not st.session_state.authenticated:
    st.title("Connexion")

    st.markdown("""
    Veuillez vous connecter pour accéder à l'application.
    """)

    col1, col2 = st.columns([1, 1])

    with col1:
        email = st.text_input("Email")
    with col2:
        password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if email == "aas@gmail.com" and password == "admin1234":
            st.session_state.authenticated = True
            st.success("Connexion réussie!")
            st.rerun()
        else:
            st.error("Email ou mot de passe incorrect.")
else:
    # Menu latéral de navigation
    with st.sidebar:
        st.title("Navigation")

        # Options de navigation
        if st.button("🏠 Accueil"):
            changer_page("Accueil")

        if st.button("⚙️ Paramètres"):
            changer_page("Paramètres")

        if st.button("💰 Systèmes de Prime"):
            changer_page("Systèmes")

        if st.session_state.data is not None:
            if st.button("📊 Résultats"):
                changer_page("Résultats")

            if st.button("🔍 Données"):
                changer_page("Données")

            if st.button("⚖️ Filtres"):
                changer_page("Filtres")

        st.markdown("---")

        # Informations sur l'état actuel
        if st.session_state.data is not None:
            st.success("✅ Données chargées")
            st.info(f"📋 {len(st.session_state.data)} enregistrements")
            if st.session_state.filtered_data is not None and len(
                    st.session_state.filtered_data) != len(
                        st.session_state.data):
                st.info(
                    f"🔍 {len(st.session_state.filtered_data)} enregistrements filtrés"
                )
        else:
            st.warning("⚠️ Aucune donnée chargée")

        # Bouton de déconnexion
        if st.button("🚪 Déconnexion"):
            st.session_state.authenticated = False
            st.rerun()

    # Contenu principal basé sur la page active
    if st.session_state.page == "Accueil":
        # Page d'accueil
        st.title("Simulateur de Primes pour Conducteurs et Contrôleurs")

        st.markdown("""
        ## Bienvenue dans le simulateur de primes
        
        Cette application vous permet de comparer différents systèmes de primes pour les conducteurs et contrôleurs de bus.
        
        ### Fonctionnalités
        
        * Générer des données synthétiques ou importer vos propres données
        * Configurer jusqu'à 4 systèmes de primes différents
        * Analyser les coûts à différents niveaux (conducteur, bus, ligne, équipe)
        * Visualiser les comparaisons avec des graphiques côte à côte
        * Filtrer les données pour une analyse plus précise
        
        ### Comment démarrer
        
        1. Allez à la page **Paramètres** pour configurer les données
        2. Visitez **Systèmes de Prime** pour personnaliser les systèmes à comparer
        3. Générez les données pour voir les **Résultats**
        4. Explorez les **Données** détaillées et appliquez des **Filtres** si nécessaire
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Configurer les paramètres",
                         use_container_width=True):
                changer_page("Paramètres")

        with col2:
            if st.session_state.data is None:
                if st.button(
                        "Générer des données avec les paramètres par défaut",
                        use_container_width=True):
                    generer_et_analyser_donnees()
            else:
                if st.button("Voir les résultats", use_container_width=True):
                    changer_page("Résultats")

        # Exemple simple pour comprendre les systèmes
        st.markdown("---")
        st.subheader("Exemple simple de calcul des primes")

        # Créer un exemple avec tous les systèmes actifs
        voyageurs_exemple = [50, 150, 400]
        exemple_data = {}

        for systeme in st.session_state.systemes_actifs:
            nom = systeme["nom"]
            exemple_data[nom] = []
            for v in voyageurs_exemple:
                prime = 0
                for palier in systeme["paliers"]:
                    min_voy = palier["min"]
                    max_voy = palier["max"]
                    taux = palier["taux"]

                    if v >= min_voy:
                        voy_palier = min(v, max_voy) - min_voy + 1
                        prime += voy_palier * taux

                exemple_data[nom].append(round(prime, 2))

        # Créer un DataFrame avec l'exemple
        exemple_cols = ["Nombre de voyageurs"] + [
            s["nom"] for s in st.session_state.systemes_actifs
        ]
        exemple_df = pd.DataFrame(columns=exemple_cols)

        exemple_df["Nombre de voyageurs"] = voyageurs_exemple
        for systeme in st.session_state.systemes_actifs:
            nom = systeme["nom"]
            exemple_df[nom] = exemple_data[nom]

        st.table(exemple_df)

    elif st.session_state.page == "Paramètres":
        # Page des paramètres
        st.title("Paramètres de Génération")

        st.markdown("""
        Configurez les paramètres pour la génération des données synthétiques ou importez vos propres données.
        """)

        # Source des données
        source_donnees = st.radio(
            "Source des données",
            ["Génération Synthétique", "Importation CSV", "Importation Excel"],
            index=0
            if st.session_state.source_donnees == "Génération Synthétique" else
            1 if st.session_state.source_donnees == "Importation CSV" else 2,
            horizontal=True)
        st.session_state.source_donnees = source_donnees

        if source_donnees == "Génération Synthétique":
            st.subheader("Paramètres de la simulation")

            # Utilisation de number_input au lieu de sliders
            col1, col2 = st.columns(2)
            with col1:
                nb_conducteurs = st.number_input(
                    "Nombre de conducteurs",
                    min_value=1,
                    max_value=100,
                    value=st.session_state.
                    parametres_generation["nb_conducteurs"])
                nb_bus = st.number_input(
                    "Nombre de bus",
                    min_value=1,
                    max_value=50,
                    value=st.session_state.parametres_generation["nb_bus"])
                nb_lignes = st.number_input(
                    "Nombre de lignes",
                    min_value=1,
                    max_value=20,
                    value=st.session_state.parametres_generation["nb_lignes"])
                nb_equipes = st.number_input(
                    "Nombre d'équipes",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.parametres_generation["nb_equipes"])

            with col2:
                nb_jours = st.number_input(
                    "Nombre de jours à simuler",
                    min_value=1,
                    max_value=365,
                    value=st.session_state.parametres_generation["nb_jours"])
                nb_voyageurs_min = st.number_input(
                    "Min voyageurs/service",
                    min_value=1,
                    max_value=1000,
                    value=st.session_state.
                    parametres_generation["nb_voyageurs_min"])
                nb_voyageurs_max = st.number_input(
                    "Max voyageurs/service",
                    min_value=nb_voyageurs_min,
                    max_value=2000,
                    value=max(
                        st.session_state.
                        parametres_generation["nb_voyageurs_max"],
                        nb_voyageurs_min))

            # Mettre à jour les paramètres
            st.session_state.parametres_generation = {
                "nb_conducteurs": nb_conducteurs,
                "nb_bus": nb_bus,
                "nb_lignes": nb_lignes,
                "nb_equipes": nb_equipes,
                "nb_jours": nb_jours,
                "nb_voyageurs_min": nb_voyageurs_min,
                "nb_voyageurs_max": nb_voyageurs_max
            }

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Réinitialiser aux valeurs par défaut",
                             use_container_width=True):
                    st.session_state.parametres_generation = {
                        "nb_conducteurs": 10,
                        "nb_bus": 5,
                        "nb_lignes": 3,
                        "nb_equipes": 2,
                        "nb_jours": 30,
                        "nb_voyageurs_min": 50,
                        "nb_voyageurs_max": 500
                    }
                    st.rerun()

            with col2:
                if st.button("Générer les Données", use_container_width=True):
                    generer_et_analyser_donnees()

        elif source_donnees == "Importation CSV":
            st.subheader("Importation de fichier CSV")

            st.markdown("""
            Le fichier CSV doit contenir les colonnes suivantes :
            - `conducteur_id` : Identifiant du conducteur
            - `bus_id` : Identifiant du bus
            - `ligne_service` : Ligne de service
            - `equipe` : Équipe
            - `nb_voyageurs` : Nombre de voyageurs
            
            Les colonnes facultatives :
            - `date` : Date du service (format YYYY-MM-DD)
            - `quart` : Quart de travail (Matin, Après-midi, Soir)
            """)

            # Téléchargement d'un exemple
            csv_exemple = preparer_exemple_csv()
            b64 = base64.b64encode(csv_exemple.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="exemple_donnees.csv">Télécharger un fichier CSV d\'exemple</a>'
            st.markdown(href, unsafe_allow_html=True)

            uploaded_file = st.file_uploader("Importer un fichier CSV",
                                             type=['csv'])

            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    valide, message = valider_donnees(df)

                    if valide:
                        df = calculer_primes_df(
                            df, st.session_state.systemes_actifs)
                        st.session_state.data = df
                        st.session_state.filtered_data = df
                        st.session_state.analyses = analyser_donnees(
                            df, st.session_state.systemes_actifs)
                        st.success("Fichier importé avec succès!")

                        if st.button("Voir les résultats"):
                            changer_page("Résultats")
                            st.rerun()
                    else:
                        st.error(f"Erreur dans le fichier : {message}")
                except Exception as e:
                    st.error(f"Erreur lors de l'importation : {str(e)}")

        elif source_donnees == "Importation Excel":
            st.subheader("Importation de fichier Excel")

            st.markdown("""
            Le fichier Excel doit contenir les colonnes suivantes :
            - `LIGNE` : Identifiant de la ligne de bus
            - `VOY` : Nombre de voyageurs par an
            - `BUS` : Moyenne du nombre de bus par jour
            - `VOY/SERVICE/J` : Nombre de voyageurs par service par jour
            - `NBRE CONDUCTUERS ETP` : Nombre de conducteurs moyen par jour par ligne
            """)

            uploaded_file = st.file_uploader("Importer un fichier Excel",
                                             type=['xlsx', 'xls'])

            if uploaded_file is not None:
                try:
                    df = pd.read_excel(uploaded_file)

                    # Afficher les données brutes
                    st.subheader("Données importées")
                    st.dataframe(df)

                    # Transformer les données au format attendu par l'application
                    transformed_df = pd.DataFrame()

                    for index, row in df.iterrows():
                        ligne = row["LIGNE"]
                        voy_service_jour = row["VOY/SERVICE/J"]
                        nb_conducteurs = row["NBRE CONDUCTUERS ETP"]

                        # Créer des enregistrements pour chaque conducteur
                        for i in range(int(nb_conducteurs)):
                            conducteur_id = f"C{ligne}_{i+1}"
                            bus_id = f"B{ligne}_{i%int(row['BUS'])+1}" if row[
                                'BUS'] > 0 else f"B{ligne}_1"

                            # Ajout d'un enregistrement pour ce conducteur
                            new_row = {
                                'conducteur_id': conducteur_id,
                                'bus_id': bus_id,
                                'ligne_service': f"L{ligne}",
                                'equipe': f"E{i%2+1}",
                                'nb_voyageurs': int(voy_service_jour)
                            }
                            transformed_df = pd.concat(
                                [transformed_df,
                                 pd.DataFrame([new_row])],
                                ignore_index=True)

                    if not transformed_df.empty:
                        # Calculer les primes
                        df = calculer_primes_df(
                            transformed_df, st.session_state.systemes_actifs)
                        st.session_state.data = df
                        st.session_state.filtered_data = df
                        st.session_state.analyses = analyser_donnees(
                            df, st.session_state.systemes_actifs)

                        st.success(
                            "Fichier importé et transformé avec succès!")

                        # Afficher les données transformées
                        st.subheader("Données transformées")
                        st.dataframe(df)

                        if st.button("Voir les résultats"):
                            changer_page("Résultats")
                            st.rerun()
                    else:
                        st.error("Impossible de transformer les données.")
                except Exception as e:
                    st.error(f"Erreur lors de l'importation : {str(e)}")
                    st.error(
                        "Assurez-vous que votre fichier Excel contient les colonnes requises."
                    )

    elif st.session_state.page == "Systèmes":
        # Page de configuration des systèmes de prime
        st.title("Configuration des Systèmes de Prime")

        st.markdown("""
        Configurez jusqu'à 4 systèmes de prime différents à comparer. Pour chaque système, vous pouvez définir:
        
        - Le nom du système
        - Une description
        - Des paliers avec des taux différents selon le nombre de voyageurs
        """)

        # Systèmes actuellement sélectionnés
        st.subheader("Systèmes actifs")

        for i, systeme in enumerate(st.session_state.systemes_actifs):
            with st.expander(f"{systeme['nom']} - {systeme['description']}",
                             expanded=True if i < 2 else False):
                col1, col2, col3 = st.columns([3, 5, 2])

                with col1:
                    nouveau_nom = st.text_input(f"Nom du système",
                                                systeme["nom"],
                                                key=f"nom_{i}")
                with col2:
                    description = st.text_input(f"Description",
                                                systeme["description"],
                                                key=f"desc_{i}")

                # Afficher les paliers
                st.subheader("Paliers")

                for j, palier in enumerate(systeme["paliers"]):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                    with col1:
                        min_val = st.number_input(f"Min voyageurs",
                                                  min_value=0.0,
                                                  max_value=10000,
                                                  value=palier["min"],
                                                  key=f"min_{i}_{j}")
                    with col2:
                        max_val = st.number_input(f"Max voyageurs",
                                                  min_value=min_val,
                                                  max_value=10000,
                                                  value=palier["max"],
                                                  key=f"max_{i}_{j}")
                    with col3:
                        taux = st.number_input(f"Taux (MAD)",
                                               min_value=0.01,
                                               max_value=10.0,
                                               value=palier["taux"],
                                               format="%.2f",
                                               step=0.01,
                                               key=f"taux_{i}_{j}")

                    # Mettre à jour le palier
                    systeme["paliers"][j] = {
                        "min": min_val,
                        "max": max_val,
                        "taux": taux
                    }

                # Bouton pour ajouter un palier
                if st.button("Ajouter un palier", key=f"add_palier_{i}"):
                    dernier_palier = systeme["paliers"][-1]
                    nouveau_min = dernier_palier["max"] + 1
                    systeme["paliers"].append({
                        "min": nouveau_min,
                        "max": nouveau_min + 100,
                        "taux": dernier_palier["taux"]
                    })
                    st.rerun()

                # Bouton pour supprimer le dernier palier
                if len(systeme["paliers"]) > 1 and st.button(
                        "Supprimer le dernier palier", key=f"del_palier_{i}"):
                    systeme["paliers"].pop()
                    st.rerun()

                # Mettre à jour le nom et la description
                systeme["nom"] = nouveau_nom
                systeme["description"] = description

        st.markdown("---")

        # Ajouter/supprimer des systèmes
        if len(st.session_state.systemes_actifs) < 4:
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                nouveau_systeme = st.selectbox("Ajouter un système", [
                    s for s_key, s in SYSTEMES_DEFAUT.items()
                    if not any(sys["nom"] == s["nom"]
                               for sys in st.session_state.systemes_actifs)
                ])

            with col3:
                if st.button("Ajouter"):
                    # Trouver le système dans SYSTEMES_DEFAUT
                    for s_key, s in SYSTEMES_DEFAUT.items():
                        if s["nom"] == nouveau_systeme:
                            st.session_state.systemes_actifs.append(
                                copy.deepcopy(s))
                            st.rerun()
                            break

        if len(st.session_state.systemes_actifs) > 1:
            col1, col2 = st.columns([3, 1])

            with col1:
                systeme_a_supprimer = st.selectbox(
                    "Supprimer un système",
                    [s["nom"] for s in st.session_state.systemes_actifs])

            with col2:
                if st.button("Supprimer"):
                    st.session_state.systemes_actifs = [
                        s for s in st.session_state.systemes_actifs
                        if s["nom"] != systeme_a_supprimer
                    ]
                    st.rerun()

        st.markdown("---")

        # Génération de données avec ces systèmes
        if st.button("Appliquer ces systèmes et générer des données",
                     use_container_width=True):
            # Si des données existent déjà, recalculer les analyses avec les nouveaux systèmes
            if st.session_state.data is not None:
                df = calculer_primes_df(st.session_state.data,
                                        st.session_state.systemes_actifs)
                st.session_state.data = df
                st.session_state.filtered_data = df
                st.session_state.analyses = analyser_donnees(
                    df, st.session_state.systemes_actifs)
                changer_page("Résultats")
                st.rerun()
            else:
                # Sinon, générer de nouvelles données
                generer_et_analyser_donnees()

    elif st.session_state.page == "Filtres":
        # Page de filtres
        st.title("Filtres")

        if st.session_state.data is None:
            st.warning(
                "Aucune donnée disponible. Veuillez d'abord générer ou importer des données."
            )
        else:
            st.markdown("""
            Filtrez les données pour une analyse plus précise. Vous pouvez sélectionner:
            
            - Une période de dates
            - Des quarts de travail spécifiques
            - Des conducteurs, bus, lignes ou équipes particuliers
            """)

            filtres = {}

            # Période
            if 'date' in st.session_state.data.columns:
                st.subheader("Période")
                dates_disponibles = sorted(
                    st.session_state.data['date'].unique())
                date_debut, date_fin = st.select_slider(
                    "Sélectionnez la période",
                    options=dates_disponibles,
                    value=(dates_disponibles[0]
                           if 'date' not in st.session_state.filtres else
                           st.session_state.filtres.get('date', [])[0]
                           if st.session_state.filtres.get('date', []) else
                           dates_disponibles[0], dates_disponibles[-1]
                           if 'date' not in st.session_state.filtres else
                           st.session_state.filtres.get(
                               'date', [])[-1] if st.session_state.filtres.get(
                                   'date', []) else dates_disponibles[-1]))
                start_idx = dates_disponibles.index(date_debut)
                end_idx = dates_disponibles.index(date_fin)
                dates_selectionnees = dates_disponibles[start_idx:end_idx + 1]
                filtres['date'] = dates_selectionnees

            # Quarts
            if 'quart' in st.session_state.data.columns:
                st.subheader("Quarts de travail")
                quarts_disponibles = sorted(
                    st.session_state.data['quart'].unique())
                quarts_selectionnes = st.multiselect(
                    "Sélectionnez les quarts",
                    options=quarts_disponibles,
                    default=st.session_state.filtres.get(
                        'quart', quarts_disponibles))
                if quarts_selectionnes:
                    filtres['quart'] = quarts_selectionnes

            # Parties de filtrage en colonnes
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Conducteurs")
                conducteurs_disponibles = sorted(
                    st.session_state.data['conducteur_id'].unique())
                conducteurs_selectionnes = st.multiselect(
                    "Sélectionnez les conducteurs",
                    options=conducteurs_disponibles,
                    default=st.session_state.filtres.get('conducteur_id', []))
                if conducteurs_selectionnes:
                    filtres['conducteur_id'] = conducteurs_selectionnes

                st.subheader("Bus")
                bus_disponibles = sorted(
                    st.session_state.data['bus_id'].unique())
                bus_selectionnes = st.multiselect(
                    "Sélectionnez les bus",
                    options=bus_disponibles,
                    default=st.session_state.filtres.get('bus_id', []))
                if bus_selectionnes:
                    filtres['bus_id'] = bus_selectionnes

            with col2:
                st.subheader("Lignes")
                lignes_disponibles = sorted(
                    st.session_state.data['ligne_service'].unique())
                lignes_selectionnees = st.multiselect(
                    "Sélectionnez les lignes",
                    options=lignes_disponibles,
                    default=st.session_state.filtres.get('ligne_service', []))
                if lignes_selectionnees:
                    filtres['ligne_service'] = lignes_selectionnees

                st.subheader("Équipes")
                equipes_disponibles = sorted(
                    st.session_state.data['equipe'].unique())
                equipes_selectionnees = st.multiselect(
                    "Sélectionnez les équipes",
                    options=equipes_disponibles,
                    default=st.session_state.filtres.get('equipe', []))
                if equipes_selectionnees:
                    filtres['equipe'] = equipes_selectionnees

            # Filtre sur le nombre de voyageurs
            st.subheader("Nombre de voyageurs")
            min_voy = int(st.session_state.data['nb_voyageurs'].min())
            max_voy = int(st.session_state.data['nb_voyageurs'].max())
            voy_range = st.slider(
                "Plage de voyageurs",
                min_value=min_voy,
                max_value=max_voy,
                value=(st.session_state.filtres.get('nb_voyageurs_min',
                                                    min_voy),
                       st.session_state.filtres.get('nb_voyageurs_max',
                                                    max_voy)))
            filtres['nb_voyageurs_min'] = voy_range[0]
            filtres['nb_voyageurs_max'] = voy_range[1]

            # Actions
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("Réinitialiser les filtres",
                             use_container_width=True):
                    st.session_state.filtres = {}
                    st.session_state.filtered_data = st.session_state.data
                    st.session_state.analyses = analyser_donnees(
                        st.session_state.data,
                        st.session_state.systemes_actifs)
                    st.rerun()

            with col2:
                if st.button("Appliquer les filtres",
                             use_container_width=True):
                    st.session_state.filtres = filtres
                    appliquer_filtres()

    elif st.session_state.page == "Données":
        # Page d'exploration des données
        st.title("Exploration des Données")

        if st.session_state.data is None:
            st.warning(
                "Aucune donnée disponible. Veuillez d'abord générer ou importer des données."
            )
        else:
            # Afficher les statistiques de base
            st.subheader("Statistiques de base")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Nombre total d'enregistrements",
                          len(st.session_state.filtered_data))
            with col2:
                st.metric(
                    "Conducteurs uniques",
                    st.session_state.filtered_data['conducteur_id'].nunique())
            with col3:
                st.metric(
                    "Lignes de service",
                    st.session_state.filtered_data['ligne_service'].nunique())

            # Afficher les statistiques des voyageurs
            st.subheader("Statistiques des voyageurs")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Moyenne voyageurs/service",
                    round(
                        st.session_state.filtered_data['nb_voyageurs'].mean(),
                        1))
            with col2:
                st.metric("Minimum",
                          st.session_state.filtered_data['nb_voyageurs'].min())
            with col3:
                st.metric("Maximum",
                          st.session_state.filtered_data['nb_voyageurs'].max())

            # Tableau des données
            st.subheader("Données")
            st.dataframe(st.session_state.filtered_data)

            # Téléchargement des données
            st.download_button(
                label="Télécharger les données (CSV)",
                data=st.session_state.filtered_data.to_csv(
                    index=False).encode('utf-8'),
                file_name='donnees_filtrees.csv',
                mime='text/csv',
            )

    elif st.session_state.page == "Résultats":
        # Page des résultats
        st.title("Analyse des Résultats")

        if st.session_state.data is None or st.session_state.analyses is None:
            st.warning(
                "Aucune donnée disponible. Veuillez d'abord générer ou importer des données."
            )
        else:
            # Onglets d'analyse
            tab1, tab2, tab3, tab4 = st.tabs([
                "Vue d'ensemble", "Analyse par catégorie",
                "Détails par conducteur", "Rapport d'Impact"
            ])

            with tab1:
                st.header("Vue d'ensemble")

                # Résumé des totaux
                st.subheader("Totaux par système")

                totaux = st.session_state.analyses["totaux_globaux"]

                # Créer un DataFrame pour les totaux
                totaux_df = pd.DataFrame()
                totaux_df["Métrique"] = [
                    "Total des primes", "Moyenne par conducteur",
                    "Moyenne par service"
                ]

                for systeme in st.session_state.systemes_actifs:
                    nom_col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                    nom_affiche = systeme["nom"]
                    # Créer les clés pour les colonnes
                    nom_moy_conducteur = f"moy_conducteur_{systeme['nom'].replace(' ', '_').lower()}"
                    nom_moy_service = f"moy_service_{systeme['nom'].replace(' ', '_').lower()}"

                    # Utiliser les clés pour accéder aux valeurs
                    totaux_df[nom_affiche] = [
                        f"{totaux[nom_col]:.2f} MAD",
                        f"{totaux[nom_moy_conducteur]:.2f} MAD",
                        f"{totaux[nom_moy_service]:.2f} MAD"
                    ]

                st.table(totaux_df)

                # Afficher les différences en pourcentage
                st.subheader("Comparaisons")
                comparaisons_df = pd.DataFrame()
                comparaisons_df["Système"] = [
                    s["nom"] for s in st.session_state.systemes_actifs[1:]
                ]
                # Utiliser des listes par compréhension avec des variables intermédiaires pour éviter les f-strings imbriqués
                diffs = []
                pcts = []
                for s in st.session_state.systemes_actifs[1:]:
                    nom_diff = f"diff_{s['nom'].replace(' ', '_').lower()}"
                    nom_pct = f"pct_{s['nom'].replace(' ', '_').lower()}"
                    diffs.append(f"{totaux[nom_diff]:.2f} MAD")
                    pcts.append(f"{totaux[nom_pct]:.1f}%")

                comparaisons_df["Différence totale"] = diffs
                comparaisons_df["Variation en %"] = pcts

                st.table(comparaisons_df)

                # Créer des graphiques de comparaison
                creer_graphiques_comparaison(st.session_state.analyses,
                                             st.session_state.systemes_actifs)

            with tab2:
                st.header("Analyse par catégorie")

                # Sélection de la catégorie
                categorie = st.selectbox(
                    "Sélectionnez une catégorie",
                    ["Conducteur", "Bus", "Ligne", "Équipe"])

                # Afficher les données agrégées de la catégorie sélectionnée
                if categorie == "Conducteur":
                    data_categorie = st.session_state.analyses[
                        "par_conducteur"]
                    key_col = "conducteur_id"
                elif categorie == "Bus":
                    data_categorie = st.session_state.analyses["par_bus"]
                    key_col = "bus_id"
                elif categorie == "Ligne":
                    data_categorie = st.session_state.analyses["par_ligne"]
                    key_col = "ligne_service"
                else:  # Équipe
                    data_categorie = st.session_state.analyses["par_equipe"]
                    key_col = "equipe"

                # Créer un DataFrame pour l'affichage des primes
                df_display = pd.DataFrame()
                df_display[f"{categorie}"] = data_categorie[key_col]
                df_display["Nombre de services"] = data_categorie[
                    "nb_services"]
                df_display["Voyageurs total"] = data_categorie[
                    "total_voyageurs"]
                df_display["Voyageurs moyen"] = data_categorie[
                    "moy_voyageurs"].round(1)

                # Ajouter les colonnes de prime pour chaque système
                for systeme in st.session_state.systemes_actifs:
                    nom_col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                    df_display[f"Prime {systeme['nom']}"] = data_categorie[
                        nom_col].round(2)

                # Ajouter les colonnes de différence
                for i in range(1, len(st.session_state.systemes_actifs)):
                    systeme = st.session_state.systemes_actifs[i]
                    nom_diff = f"diff_{systeme['nom'].replace(' ', '_').lower()}"
                    df_display[f"Diff. {systeme['nom']}"] = data_categorie[
                        nom_diff].round(2)

                # Afficher le tableau
                st.dataframe(df_display)

                # Graphiques
                st.subheader("Graphiques")

                # Voyageurs par catégorie
                voyageurs_chart = pd.DataFrame({
                    'Catégorie':
                    data_categorie[key_col],
                    'Voyageurs moyen':
                    data_categorie["moy_voyageurs"]
                }).set_index('Catégorie')

                st.bar_chart(voyageurs_chart)

                # Primes par catégorie
                primes_data = {}
                for systeme in st.session_state.systemes_actifs:
                    nom_col = f"prime_{systeme['nom'].replace(' ', '_').lower()}"
                    primes_data[systeme['nom']] = data_categorie[nom_col]

                primes_chart = pd.DataFrame(primes_data).set_index(
                    data_categorie[key_col])
                st.bar_chart(primes_chart)

            with tab3:
                st.header("Détails par Conducteur")

                # Sélection du conducteur
                if st.session_state.filtered_data is not None and 'conducteur_id' in st.session_state.filtered_data.columns:
                    conducteurs = sorted(
                        st.session_state.filtered_data['conducteur_id'].unique(
                        ))
                    conducteur_select = st.selectbox(
                        "Sélectionnez un conducteur", conducteurs)
                else:
                    st.warning(
                        "Aucune donnée disponible pour les conducteurs.")
                    conducteur_select = None

                if st.button("Afficher les détails"):
                    st.session_state.show_details = True
                    st.session_state.selected_conducteur = conducteur_select
                    st.rerun()

                # Affichage des détails du conducteur
                if st.session_state.show_details and st.session_state.selected_conducteur is not None:
                    afficher_detail_conducteur(
                        st.session_state.filtered_data,
                        st.session_state.selected_conducteur,
                        st.session_state.systemes_actifs)

            with tab4:
                st.header("Rapport d'Impact Financier")

                # Génération du rapport d'impact
                generer_rapport_impact(st.session_state.analyses,
                                       st.session_state.systemes_actifs)
    else:
        st.warning("Page inconnue. Retour à l'accueil...")
        changer_page("Accueil")
        st.rerun()
