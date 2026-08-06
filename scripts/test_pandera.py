"""
test_pandera.py
Implémentation des 13 règles de qualité (10 reprises du P6 + 3 ajoutées)
avec la librairie Pandera.

Pandera fonctionne en 2 temps :
1. On déclare un "schéma" (DataFrameSchema) qui décrit les colonnes attendues,
   leur type, et des contraintes (Check) sur chaque colonne.
2. On appelle schema.validate(df) : si une règle est violée, Pandera lève
   une SchemaError (ou SchemaErrors en mode "lazy" pour tout collecter d'un coup).

On utilise le mode lazy=True partout pour récupérer TOUTES les erreurs en une
seule fois, plutôt que de s'arrêter à la première (plus utile pour un audit qualité).
"""

import time
import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check, DataFrameSchema

from data_prep import charger_donnees_brutes, nettoyer_web, construire_df_complet


# ---------------------------------------------------------------------------
# SCHEMA 1 : df_erp
# Règles 1 (doublons), 2 (cohérence stock), 3 (price), 4 (stock_quantity),
# 5 (purchase_price), 6 (onsale_web), 11 (marge), 12 (dtype)
# ---------------------------------------------------------------------------
schema_erp = DataFrameSchema(
    columns={
        # Le simple fait de déclarer le type ici (int, float...) EST le contrôle
        # de dtype demandé par la règle 12 : Pandera refuse une colonne qui
        # n'est pas du bon type.
        "product_id": Column(int, unique=True, nullable=False),  # Règle 1 + 12
        "price": Column(float, Check.ge(0), nullable=False),  # Règle 3 + 12
        "purchase_price": Column(float, Check.ge(0), nullable=False),  # Règle 5 + 12
        "stock_quantity": Column(int, Check.ge(0), nullable=False),  # Règle 4 + 12
        "stock_status": Column(str, Check.isin(["instock", "outofstock"])),
        "onsale_web": Column(int, Check.isin([0, 1])),  # Règle 6
    },
    checks=[
        # Règle 2 : cohérence stock_status / stock_quantity
        # -> si stock_quantity <= 0 alors stock_status doit être "outofstock", sinon "instock"
        Check(
            lambda df: (
                (df["stock_quantity"] <= 0) == (df["stock_status"] == "outofstock")
            ).all(),
            error="Incohérence entre stock_status et stock_quantity",
        ),
        # Règle 11 (nouvelle) : le prix de vente doit être supérieur au prix d'achat
        # -> sinon l'article est vendu à perte, ce qui sent l'erreur de saisie
        Check(
            lambda df: (df["price"] > df["purchase_price"]).all(),
            error="Marge négative détectée : price <= purchase_price",
        ),
    ],
    strict=False,  # on autorise les colonnes non déclarées à rester dans le df
)

# ---------------------------------------------------------------------------
# SCHEMA 2 : df_web (après nettoyage, cf data_prep.nettoyer_web)
# Règles 7 (format sku), 8 (sku non manquant)
# ---------------------------------------------------------------------------
schema_web = DataFrameSchema(
    columns={
        # NB : la colonne sku est déclarée en "object" et non "str" car le test
        # a révélé un mélange de types Python (712 int + 2 str) — voir le
        # commentaire du check ci-dessous, et la note dans le journal de bord.
        "sku": Column(nullable=False),  # Règle 8
    },
    checks=[
        # Règle 7 : le sku doit être un code numérique.
        # DECOUVERTE DU TEST : la colonne sku mélange des int (712 lignes) et
        # des str (2 lignes) suite à la lecture Excel. Un simple .str.isnumeric()
        # échoue silencieusement sur les valeurs int (renvoie NaN -> traité comme
        # False). On convertit donc explicitement en texte avant de tester,
        # ce qui permet d'isoler les VRAIES anomalies de format.
        Check(
            lambda df: df["sku"].astype(str).str.isnumeric().all(),
            error="SKU au format non numérique détecté",
        ),
    ],
    strict=False,
)

# ---------------------------------------------------------------------------
# SCHEMA 3 : df_liaison
# Règle 9 (product_id unique et non manquant)
# ---------------------------------------------------------------------------
schema_liaison = DataFrameSchema(
    columns={
        "product_id": Column(int, unique=True, nullable=False),  # Règle 9
    },
    strict=False,
)

# ---------------------------------------------------------------------------
# SCHEMA 4 : df_complet (post-fusion)
# Règle 13 (nouvelle) : unicité de product_id après la fusion des 3 fichiers
# ---------------------------------------------------------------------------
schema_complet = DataFrameSchema(
    columns={
        "product_id": Column(int, unique=True, nullable=False),  # Règle 13
    },
    strict=False,
)


def verifier_correspondance_erp_liaison(df_erp, df_liaison):
    """
    Règle 10 : correspondance totale entre df_erp et df_liaison (pas d'orphelins).
    Ceci est une règle CROISEE ENTRE 2 DATAFRAMES : ni Pandera ni Great Expectations
    ne savent nativement comparer 2 dataframes dans un seul schéma/suite.
    On l'implémente donc "à la main" avec un merge indicateur, pour les deux outils.
    """
    fusion = pd.merge(df_erp, df_liaison, on="product_id", how="outer", indicator=True)
    orphelins = fusion[fusion["_merge"] != "both"]
    return len(orphelins) == 0, orphelins


def executer_validation_pandera():
    resultats = {}
    debut = time.perf_counter()

    df_erp, df_web, df_liaison = charger_donnees_brutes()
    df_web_clean = nettoyer_web(df_web)
    df_complet = construire_df_complet(df_erp, df_web, df_liaison)

    # --- Validation df_erp ---
    try:
        schema_erp.validate(df_erp, lazy=True)
        resultats["erp"] = "OK"
    except pa.errors.SchemaErrors as e:
        resultats["erp"] = e.failure_cases

    # --- Validation df_web ---
    try:
        schema_web.validate(df_web_clean, lazy=True)
        resultats["web"] = "OK"
    except pa.errors.SchemaErrors as e:
        resultats["web"] = e.failure_cases

    # --- Validation df_liaison ---
    try:
        schema_liaison.validate(df_liaison, lazy=True)
        resultats["liaison"] = "OK"
    except pa.errors.SchemaErrors as e:
        resultats["liaison"] = e.failure_cases

    # --- Validation df_complet ---
    try:
        schema_complet.validate(df_complet, lazy=True)
        resultats["complet"] = "OK"
    except pa.errors.SchemaErrors as e:
        resultats["complet"] = e.failure_cases

    # --- Règle 10 (cross-dataframe) ---
    ok, orphelins = verifier_correspondance_erp_liaison(df_erp, df_liaison)
    resultats["correspondance_erp_liaison"] = "OK" if ok else orphelins

    duree = time.perf_counter() - debut
    return resultats, duree


if __name__ == "__main__":
    resultats, duree = executer_validation_pandera()
    print(f"\n=== RESULTATS PANDERA (durée : {duree:.3f}s) ===\n")
    for cle, valeur in resultats.items():
        if isinstance(valeur, str):
            print(f"[OK]   {cle}")
        else:
            print(f"[FAIL] {cle} -> {len(valeur)} problème(s) détecté(s)")
