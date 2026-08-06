"""
test_great_expectations.py
Implémentation des 13 règles de qualité (les 10 reprises du P6 + 3 ajoutées)
avec Great Expectations (GX), pour comparaison directe avec test_pandera.py.

Fonctionnement de GX (API "moderne" v1.x, dite "Fluent API") :
1. On crée un "contexte" (le projet GX) — ici en mode "ephemeral" (en mémoire,
   pas de fichiers de config générés sur le disque, adapté à un notebook/script).
2. Pour chaque dataframe, on déclare une "source" pandas, puis un "batch"
   (l'ensemble de données à valider).
3. On crée une "suite d'expectations" (Expectation Suite) = la liste des règles.
4. On valide le batch contre la suite -> on obtient un rapport détaillé.

Contrairement à Pandera où une règle "custom" s'écrit en une ligne de lambda,
GX demande soit une Expectation déjà existante dans sa bibliothèque (il y en a
beaucoup), soit de pré-calculer une colonne dérivée en pandas AVANT de valider
si la règle est trop spécifique (voir règle 2 ci-dessous). C'est un point de
comparaison important avec Pandera.
"""

import time
import pandas as pd
import great_expectations as gx
from great_expectations.expectations import (
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToBeInSet,
    ExpectColumnPairValuesAToBeGreaterThanB,
    ExpectColumnValuesToMatchRegex,
)

from data_prep import charger_donnees_brutes, nettoyer_web, construire_df_complet


def construire_contexte():
    """Crée un contexte GX en mémoire (pas de fichiers générés sur le disque)."""
    return gx.get_context(mode="ephemeral")


def valider_dataframe(context, df, nom_source, expectations):
    """
    Fonction utilitaire : enregistre un dataframe comme source GX, construit
    une suite avec la liste d'expectations fournie, et retourne le résultat.
    Cette fonction factorise ce que GX demande de répéter pour chaque dataframe.
    """
    data_source = context.data_sources.add_pandas(nom_source)
    data_asset = data_source.add_dataframe_asset(name=f"{nom_source}_asset")
    batch_definition = data_asset.add_batch_definition_whole_dataframe(
        f"{nom_source}_batch"
    )
    batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

    suite = context.suites.add(gx.ExpectationSuite(name=f"{nom_source}_suite"))
    for expectation in expectations:
        suite.add_expectation(expectation)

    return batch.validate(suite)


def executer_validation_gx():
    resultats = {}
    debut = time.perf_counter()

    context = construire_contexte()
    df_erp, df_web, df_liaison = charger_donnees_brutes()
    df_web_clean = nettoyer_web(df_web)
    df_complet = construire_df_complet(df_erp, df_web, df_liaison)

    # -----------------------------------------------------------------
    # df_erp : règles 1, 3, 4, 5, 6, 11
    # (règle 12 "dtype" : GX n'a pas d'expectation dédiée simple pour ça en
    #  pandas -> on utilise expect_column_values_to_be_of_type)
    # -----------------------------------------------------------------
    from great_expectations.expectations import ExpectColumnValuesToBeOfType

    expectations_erp = [
        ExpectColumnValuesToBeUnique(column="product_id"),  # Règle 1
        ExpectColumnValuesToNotBeNull(column="product_id"),
        ExpectColumnValuesToBeOfType(column="product_id", type_="int64"),  # Règle 12
        ExpectColumnValuesToBeBetween(column="price", min_value=0),  # Règle 3
        ExpectColumnValuesToBeOfType(column="price", type_="float64"),  # Règle 12
        ExpectColumnValuesToBeBetween(column="stock_quantity", min_value=0),  # Règle 4
        ExpectColumnValuesToBeBetween(column="purchase_price", min_value=0),  # Règle 5
        ExpectColumnValuesToBeInSet(column="onsale_web", value_set=[0, 1]),  # Règle 6
        # Règle 11 : marge -> GX a une expectation TOUTE FAITE pour comparer
        # 2 colonnes, contrairement à Pandera qui demandait un lambda "maison"
        ExpectColumnPairValuesAToBeGreaterThanB(
            column_A="price", column_B="purchase_price"
        ),
    ]
    resultats["erp"] = valider_dataframe(context, df_erp, "erp", expectations_erp)

    # -----------------------------------------------------------------
    # Règle 2 (cohérence stock_status / stock_quantity) : règle trop
    # spécifique pour une expectation standard GX. On est OBLIGE de
    # pré-calculer une colonne dérivée en pandas avant de valider.
    # C'est un vrai point faible de GX par rapport à Pandera sur ce cas précis.
    # -----------------------------------------------------------------
    df_erp_coherence = df_erp.copy()
    df_erp_coherence["coherence_stock"] = (
        (df_erp["stock_quantity"] <= 0) == (df_erp["stock_status"] == "outofstock")
    )
    resultats["erp_coherence_stock"] = valider_dataframe(
        context,
        df_erp_coherence,
        "erp_coherence",
        [ExpectColumnValuesToBeInSet(column="coherence_stock", value_set=[True])],
    )

    # -----------------------------------------------------------------
    # df_web (nettoyé) : règles 7, 8
    # -----------------------------------------------------------------
    df_web_clean_str = df_web_clean.copy()
    df_web_clean_str["sku"] = df_web_clean_str["sku"].astype(str)  # même correctif
    # que pour Pandera : la colonne mélange int et str, on uniformise avant test
    expectations_web = [
        ExpectColumnValuesToNotBeNull(column="sku"),  # Règle 8
        ExpectColumnValuesToMatchRegex(column="sku", regex=r"^\d+$"),  # Règle 7
    ]
    resultats["web"] = valider_dataframe(
        context, df_web_clean_str, "web", expectations_web
    )

    # -----------------------------------------------------------------
    # df_liaison : règle 9
    # -----------------------------------------------------------------
    expectations_liaison = [
        ExpectColumnValuesToBeUnique(column="product_id"),
        ExpectColumnValuesToNotBeNull(column="product_id"),
    ]
    resultats["liaison"] = valider_dataframe(
        context, df_liaison, "liaison", expectations_liaison
    )

    # -----------------------------------------------------------------
    # df_complet (post-fusion) : règle 13
    # -----------------------------------------------------------------
    expectations_complet = [
        ExpectColumnValuesToBeUnique(column="product_id"),
    ]
    resultats["complet"] = valider_dataframe(
        context, df_complet, "complet", expectations_complet
    )

    # -----------------------------------------------------------------
    # Règle 10 (cross-dataframe) : comme pour Pandera, GX ne sait pas comparer
    # nativement 2 dataframes -> même solution "maison" que côté Pandera.
    # -----------------------------------------------------------------
    fusion = pd.merge(df_erp, df_liaison, on="product_id", how="outer", indicator=True)
    orphelins = fusion[fusion["_merge"] != "both"]
    resultats["correspondance_erp_liaison"] = len(orphelins) == 0

    duree = time.perf_counter() - debut
    return resultats, duree


if __name__ == "__main__":
    resultats, duree = executer_validation_gx()
    print(f"\n=== RESULTATS GREAT EXPECTATIONS (durée : {duree:.3f}s) ===\n")
    for cle, valeur in resultats.items():
        if isinstance(valeur, bool):
            print(f"[{'OK' if valeur else 'FAIL'}]  {cle}")
        else:
            print(f"[{'OK' if valeur.success else 'FAIL'}]  {cle}")
