"""
data_prep.py
Reconstruit les dataframes exactement comme le fait le notebook P6.
Ce fichier est PARTAGE par les 2 tests (Pandera et Great Expectations)
pour garantir que la comparaison porte bien sur l'outil de validation,
et pas sur des données différentes.
"""

import os
import pandas as pd

# Chemins relatifs à la racine du dépôt (structure : data/, notebook/, scripts/, docs/)
_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_ERP = os.path.join(_RACINE, "data", "erp.xlsx")
CHEMIN_WEB = os.path.join(_RACINE, "data", "web.xlsx")
CHEMIN_LIAISON = os.path.join(_RACINE, "data", "liaison.xlsx")


def charger_donnees_brutes():
    """Charge les 3 fichiers Excel bruts, sans aucun traitement."""
    df_erp = pd.read_excel(CHEMIN_ERP)
    df_web = pd.read_excel(CHEMIN_WEB)
    df_liaison = pd.read_excel(CHEMIN_LIAISON)
    return df_erp, df_web, df_liaison


def nettoyer_web(df_web):
    """
    Reproduit le nettoyage de df_web fait dans le notebook P6 (cellules 37-47) :
    - on ne garde que les colonnes ayant plus d'une valeur unique (colonnes informatives)
    - on retire les lignes sans sku
    - on filtre sur post_type == 'product' (retire les doublons de type 'attachment')
    """
    colonnes_conservees = [c for c in df_web.columns if df_web[c].nunique() > 1]
    df_web_clean = df_web[colonnes_conservees].copy()
    df_web_clean = df_web_clean.dropna(subset=["sku"])
    df_web_clean = df_web_clean.loc[df_web_clean["post_type"] == "product", :]
    return df_web_clean


def construire_df_complet(df_erp, df_web, df_liaison):
    """
    Reproduit la fusion finale du notebook P6 (cellules 56-63) :
    erp + liaison (sur product_id) puis + web (id_web == sku)
    """
    df_web_clean = nettoyer_web(df_web)
    df_erp_liaison = pd.merge(df_erp, df_liaison, on="product_id", how="left")
    df_complet = pd.merge(
        df_erp_liaison, df_web_clean, left_on="id_web", right_on="sku", how="inner"
    )
    return df_complet


if __name__ == "__main__":
    # Petit test manuel pour vérifier que la reconstruction est fidèle au notebook
    df_erp, df_web, df_liaison = charger_donnees_brutes()
    df_web_clean = nettoyer_web(df_web)
    df_complet = construire_df_complet(df_erp, df_web, df_liaison)
    print("df_erp:", df_erp.shape)
    print("df_web (brut):", df_web.shape)
    print("df_web (nettoyé):", df_web_clean.shape)
    print("df_liaison:", df_liaison.shape)
    print("df_complet:", df_complet.shape)
