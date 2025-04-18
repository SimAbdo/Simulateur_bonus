import pandas as pd

def obtenir_structure_csv():
    """
    Fournit une structure d'exemple pour le fichier CSV attendu
    
    Returns:
        str: Description de la structure CSV attendue
    """
    structure = """
    Le fichier CSV doit contenir les colonnes suivantes:
    
    - LIGNE : Identification de la ligne de bus
    - VOY : Nombre de voyageurs par an dans la ligne
    - BUS : Moyenne du nombre de bus affectés à une ligne par jour sur une année
    - VOY/SERVICE/J : Nombre de voyageurs par service par jour
    - NBRE CONDUCTEURS ETP : Nombre de conducteurs moyen par jour par ligne
    
    Exemple de contenu:
    
    LIGNE,VOY,BUS,VOY/SERVICE/J,NBRE CONDUCTEURS ETP
    L1,2500000,10,250,15
    L2,1800000,8,180,12
    L3,3200000,14,320,20
    L4,1200000,5,120,8
    """
    return structure

def obtenir_exemple_csv():
    """
    Fournit un exemple de fichier CSV à télécharger
    
    Returns:
        str: Contenu CSV d'exemple
    """
    exemple = """LIGNE,VOY,BUS,VOY/SERVICE/J,NBRE CONDUCTEURS ETP
L1,2500000,10,250,15
L2,1800000,8,180,12
L3,3200000,14,320,20
L4,1200000,5,120,8
L5,950000,4,95,6
L6,2300000,9,230,14
L7,1500000,6,150,10"""
    return exemple
