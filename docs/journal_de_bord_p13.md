# Journal de bord — Projet 13 (Amélioration P6 + Portfolio)

**Chef de mission** : Quentin Chiniard
**Assistant / rédacteur** : Claude

Ce document trace les décisions prises, les options comparées, et les justifications, au fil du projet. Il sert de base à la documentation finale (livrable 2) et à la préparation de la soutenance.

---

## Contexte du projet

- **Base de travail** : notebook P6 "Analyse du stock et des ventes du site Bottleneck" (`notebook_p6_ameliore.ipynb`)
- **Nature des données** : 3 fichiers Excel (erp.xlsx, web.xlsx, liaison.xlsx) — vente de vins en ligne
- **Dataset final après jointure** : 714 lignes, 24 colonnes (`df_complet`)
- **Contenu existant du notebook P6** :
  - Import et exploration des 3 fichiers (doublons, cohérence, valeurs manquantes)
  - Jointure des 3 fichiers
  - Analyse univariée des prix + détection d'outliers (Z-score et IQR)
  - Analyse du CA, quantités vendues, stocks, marge
  - Analyse de corrélations (heatmap)
  - Export du dataset final en Excel

---

## Décision 1 — Plan d'action général (Phase 0 à Phase 6)

**Date** : début de mission

**Décision** : structurer le travail en 7 phases :
0. Cadrage (lecture du notebook, identification des axes)
1. Veille métier et technologique
2. Cahier des charges fonctionnel
3. Organisation projet (Kanban, planning, risques)
4. Exécution technique (tests comparatifs, documentation au fil de l'eau)
5. Documentation finale
6. Portfolio (Mission 2)

**Justification** : la mission exige explicitement une démarche comparative et documentée. Commencer par le cadrage et la veille avant de coder évite de "faire du ML pour faire du ML" — chaque choix technique doit répondre à un besoin identifié en amont.

---

## Décision 2 — Axes d'amélioration priorisés

**Date** : après analyse du notebook P6

**Options envisagées** :
| Axe | Description | Retenu ? |
|---|---|---|
| A | Détection d'anomalies plus robuste (Isolation Forest / LOF vs Z-score/IQR existant) | ✅ |
| B | Ajout de Machine Learning (clustering ou prédiction) | ✅ (voir Décision 3) |
| C | Nettoyage automatisé (Great Expectations vs Pandera) | ✅ |
| D | Visualisation interactive (Dash / Streamlit) | ❌ (non retenu pour l'instant) |

**Ordre de traitement retenu** : **C → A → B**

**Justification** : logique de dépendance — sécuriser la qualité des données (C) avant d'affiner la détection d'anomalies (A), avant de construire un modèle ML (B) sur une base fiabilisée. Éviter le principe "garbage in, garbage out".

---

## Décision 3 — Pertinence du Machine Learning (axe B) — en cours d'arbitrage

**Date** : après analyse critique des données

**Constat chiffré (issu du notebook P6, Étape 5.5)** :
- Corrélation prix ↔ ventes : **-0,52** (négative modérée)
- Corrélation prix ↔ stock : **-0,11** (quasi nulle)
- Corrélation ventes ↔ stock : **0,44** (positive modérée)
- Taille du dataset : 714 lignes, très peu de variables numériques exploitables, catalogue quasi mono-catégorie ("Vin" ~99%)

**Analyse** :
- **Régression prédictive** (prédire les ventes à partir du prix) : écartée comme solution principale. Avec une corrélation de -0,52, un modèle linéaire plafonnerait à un R² ≈ 0,27 — insuffisant pour un usage métier fiable.
- **Clustering** (segmentation du catalogue) : retenu comme piste principale. Ne dépend pas de fortes corrélations, répond à un besoin métier concret (identifier produits stars / stock dormant / niche premium), exploitable pour la gestion de catalogue.

**Décision finale** : **Clustering pur** (K-means vs DBSCAN), pas de test de régression.

**Justification** : dans un contexte de travail individuel, chaque test technique doit être choisi avec un fort niveau de confiance a priori — une équipe pourrait se permettre d'explorer une piste à faible probabilité de succès en parallèle d'autres pistes, ce n'est pas le cas en solo. L'analyse critique (R² prévisible ≈ 0,27) montre que le résultat de la régression est déjà anticipable et n'apporterait pas de valeur métier suffisante pour justifier un test dédié. Le clustering, lui, ne dépend pas de la force des corrélations et répond à un vrai besoin métier (segmentation du catalogue).

---

## Décision 4 — Périmètre technique du projet (relecture de la mission)

**Date** : après relecture attentive de la consigne mission 1

**Constat** : la mission demande explicitement "au moins 2 options" comparées sur **une** amélioration, pas un nombre minimum d'axes. La liste (nettoyage / visualisation / ML / formation) est introduite par "Exemples" — illustrative, non obligatoire dans son intégralité. Les 4 étapes obligatoires (veille, cahier des charges, organisation projet, documentation) portent sur la démarche, pas sur le nombre d'axes techniques.

**Décision** : recentrage du périmètre technique sur l'axe C en priorité, A et B en complément si possible.

**Justification** : dans un contexte de travail **individuel** (pas d'équipe à coordonner, pas de parallélisation possible des axes), mieux vaut traiter un axe avec une vraie profondeur comparative qu'en disperser plusieurs superficiellement. Un axe traité en profondeur est plus défendable en soutenance (critère "qualité" de la mission) et plus proche d'une vraie démarche professionnelle solo que d'une dispersion. Dans un contexte d'équipe, les 3-4 axes auraient pu être répartis entre plusieurs personnes en parallèle — ce n'est pas le cas ici.

---

## Annexe — Prompts utilisés

Traçabilité des échanges IA : outil, prompt, contexte, résultat retenu.

| # | Outil | Contexte / Objectif | Prompt (reconstitué ou original) | Résultat / Décision liée |
|---|---|---|---|---|
| 1 | Claude (claude.ai) | Challenger la pertinence du ML sur le dataset P6 avant de s'engager sur l'axe B | *"Voici les corrélations calculées dans mon notebook P6 (prix/ventes -0,52, prix/stock -0,11, ventes/stock 0,44) sur un dataset de 714 lignes majoritairement mono-catégorie. Est-ce que le Machine Learning est pertinent sur ces données ? Compare l'intérêt d'une régression prédictive des ventes vs un clustering de segmentation du catalogue, en argumentant avec des critères objectifs (puissance explicative, besoin métier, complexité)."* | → Décision 3 : abandon de la régression, clustering retenu comme piste ML si le temps le permet |

---

## Décision 5 — Liste des règles de validation retenues (axe C)

**Date** : après relecture du détail du notebook P6 (étapes 1-2)

**Méthode** : reprise exhaustive des vérifications manuelles déjà faites dans le P6 + ajout de règles complémentaires à valeur métier, proposées par l'assistant IA et validées par le chef de mission.

**Règles reprises du P6 (10)** :
1. Pas de doublons sur `product_id` (df_erp)
2. Cohérence `stock_status` / `stock_quantity`
3. `price` non négatif et non manquant
4. `stock_quantity` non négatif et non manquant
5. `purchase_price` non négatif et non manquant
6. `onsale_web` limité aux valeurs 0/1
7. `sku` (df_web) au format numérique attendu
8. `sku` non manquant
9. `product_id` unique et non manquant (df_liaison)
10. Correspondance totale entre `df_erp` et `df_liaison` (pas d'orphelins)

**Règles ajoutées (3)** — proposées par l'IA pour renforcer l'EDA, validées par Quentin :
11. Cohérence marge : `price` > `purchase_price` (détection d'articles potentiellement vendus à perte)
12. Contrôle des types de données (dtype) sur les colonnes clés
13. Unicité de `product_id` après fusion des 3 fichiers (`df_complet`) — non vérifié dans le P6 original

**Écarté** : cohérence des dates (`post_date`) — non retenu par Quentin, probablement pour limiter le périmètre vu la contrainte de temps.

## Décision 6 — Résultat du test comparatif Pandera vs Great Expectations

**Date** : test réel exécuté sur les 3 fichiers de données (erp.xlsx, web.xlsx, liaison.xlsx), 13 règles implémentées avec les deux outils.

**Méthode** : implémentation identique des 13 règles avec chaque outil, sur les mêmes dataframes (reconstruits fidèlement au P6 via `data_prep.py`), mesure du temps d'exécution et du volume de code.

**Résultats mesurés** :

| Critère | Pandera | Great Expectations |
|---|---|---|
| Temps d'exécution | 0,81s | 1,35s (+65%) |
| Lignes de code utile | ~108 | ~110 |
| Setup par dataframe | Direct (déclaration de schéma) | Lourd (contexte + source + batch + suite) |
| Règle cross-colonnes simple (marge) | Lambda à écrire | Expectation native disponible |
| Règle cross-colonnes complexe (cohérence stock) | Lambda direct sur le df | Contournement obligatoire (colonne dérivée pré-calculée) |
| Règle cross-dataframe (correspondance erp/liaison) | Non géré nativement | Non géré nativement (même contournement des 2 côtés) |
| Dépendances | Légères | Lourdes (confirmé : bien plus de dépendances installées) |

**Anomalies réelles découvertes sur les données** (convergence des 2 outils) :
- 3 prix négatifs (`df_erp`, non détectés dans le P6 original)
- 2 stocks négatifs (`df_erp`)
- Mélange de types (int/str) dans la colonne `sku` suite à la lecture Excel — risque de faux négatif si le check n'est pas écrit avec précaution

**Décision finale** : **Pandera retenu** pour intégrer le nettoyage automatisé au notebook final.

**Justification** : à volume de code équivalent, la différence se joue sur la **gouvernance**. Great Expectations est conçu pour des pipelines multi-outils partagés par une équipe : suites d'expectations centralisées, checkpoints, documentation générée pour plusieurs consommateurs — cette lourdeur (contexte + source + batch + suite à recréer pour chaque dataframe, dépendances nombreuses) se justifie quand plusieurs personnes doivent appliquer les mêmes règles sur plusieurs pipelines. Pandera, plus léger et sans couche de gouvernance, correspond à un contexte de **travail individuel sur un notebook unique** — ce qui est le cas ici. Ce n'est donc pas un choix "par manque de temps", mais un choix **adapté au contexte projet (solo vs équipe)**, cohérent avec les critères "reproductibilité" et "maintenabilité" de la mission. Si ce projet impliquait une équipe data partageant plusieurs pipelines, Great Expectations deviendrait le choix pertinent.

**Fichiers produits** : `data_prep.py`, `test_pandera.py`, `test_great_expectations.py` — conservés comme preuve de la démarche comparative testée (et non uniquement théorique).

---

## Décision 7 — Parties prenantes du cahier des charges

**Date** : après challenge du chef de mission sur la proposition initiale de l'assistant

**Contexte** : l'assistant avait initialement proposé de traiter 2 parties prenantes distinctes (marketing ET achats), en argumentant à tort que la mission exigeait plusieurs parties prenantes au pluriel. **Correction** : relecture du texte exact de la mission — *"Contexte & parties prenantes : qui utilise l'analyse, pour décider quoi ?"* — le pluriel est une convention de rédaction du terme, pas une exigence d'en citer plusieurs. Point relevé et challengé par Quentin, à raison.

**Risque identifié** : viser 2 parties prenantes (marketing + achats) aurait obligé à livrer un travail solide pour chacune (nettoyage ET clustering), recréant la dispersion qu'on cherchait justement à éviter (cf. Décision 4).

**Décision finale** : une seule partie prenante décisionnaire, avec un effet de **cascade de qualité** vers d'autres bénéficiaires (proposition de Quentin) :

| Rôle | Acteur | Usage |
|---|---|---|
| **Décideur principal** | Service achats / gestion de catalogue | Utilise directement l'analyse fiabilisée pour décider des réapprovisionnements et renégocier les prix d'achat sur les produits à faible marge |
| **Bénéficiaire indirect** | Marketing | Profite d'un catalogue fiabilisé (sans prix/stocks aberrants) pour toute segmentation ou action commerciale future, sans être décideur sur ce livrable |
| **Bénéficiaire indirect** | CODIR | Profite d'indicateurs consolidés (CA, marge) plus fiables pour le reporting stratégique |

**Justification** : garde un périmètre technique resserré et déjà réalisé (nettoyage = axe C) comme preuve pour le décideur principal, tout en démontrant une vision métier plus large sans développement technique supplémentaire. Pattern classique de gouvernance de la donnée (décideur direct vs bénéficiaires en aval).

---

## Annexe — Prompts utilisés

Traçabilité des échanges IA : outil, prompt, contexte, résultat retenu.

| # | Outil | Contexte / Objectif | Prompt (reconstitué ou original) | Résultat / Décision liée |
|---|---|---|---|---|
| 1 | Claude (claude.ai) | Challenger la pertinence du ML sur le dataset P6 avant de s'engager sur l'axe B | *"Voici les corrélations calculées dans mon notebook P6 (prix/ventes -0,52, prix/stock -0,11, ventes/stock 0,44) sur un dataset de 714 lignes majoritairement mono-catégorie. Est-ce que le Machine Learning est pertinent sur ces données ? Compare l'intérêt d'une régression prédictive des ventes vs un clustering de segmentation du catalogue, en argumentant avec des critères objectifs (puissance explicative, besoin métier, complexité)."* | → Décision 3 : abandon de la régression, clustering retenu comme piste ML si le temps le permet |
| 2 | Claude (claude.ai) | Définir la/les partie(s) prenante(s) du cahier des charges fonctionnel | *"Je pars sur un positionnement service marketing comme destinataire de l'outil (analyse prix/stock). Est-ce cohérent ? Challenge mon idée pour voir si je ne peux pas faire mieux, en vérifiant si la mission impose plusieurs parties prenantes."* | → Décision 7 : recentrage sur une seule partie prenante décisionnaire (achats), avec effet de cascade vers marketing et CODIR comme bénéficiaires indirects |

---

## Décision 8 — Problématique métier reformulée (validée)

**Date** : validation finale par le chef de mission, avec ajout du risque en cascade sur les analyses futures

**Problématique retenue** :
> Le service achats de Bottleneck manque aujourd'hui de visibilité fiable sur la cohérence de son catalogue (prix, stock, marge). Des anomalies de saisie (prix négatifs, stocks négatifs, incohérences de statut) faussent silencieusement les décisions de réapprovisionnement et de négociation fournisseur. Au-delà de l'usage direct par les achats, ces anomalies non corrigées représentent un risque en cascade pour toute analyse future construite sur ce catalogue — segmentation marketing, reporting CODIR — qui hériterait des mêmes biais sans le savoir. Comment fiabiliser automatiquement la qualité des données catalogue pour sécuriser ces décisions, présentes et futures ?

**Justification** : reprend les 5 anomalies réelles découvertes lors du test comparatif (Décision 6) comme preuve concrète, et intègre l'effet de cascade de qualité identifié en Décision 7 (bénéficiaires indirects), pour ancrer la problématique dans une vision à la fois opérationnelle (achats) et stratégique (marketing, CODIR) sans élargir le périmètre technique.

---

## Décision 9 — Rapport d'anomalies exploitable (complément au périmètre)

**Date** : identifié par le chef de mission en réaction à la limite "l'outil détecte mais ne corrige pas"

**Constat** : sans format de sortie exploitable, la détection d'anomalies (axe C) reste cantonnée au notebook technique — inutilisable en l'état par le service achats (partie prenante définie en Décision 7).

**Décision** : ajout au périmètre d'un **export automatique des anomalies détectées** (CSV/Excel), structuré pour permettre une correction humaine ciblée et rapide :
- Dataframe source, index de ligne, colonne concernée, règle violée, valeur observée, action recommandée

**Justification** : répond au critère KPI "opérationnel" de la mission (clarté du rendu, gain de temps de traitement). Transforme un outil de détection technique en livrable réellement actionnable par une personne non-technique du service achats — cohérent avec le rôle de "décideur principal" attribué à ce service (Décision 7).

**Statut** : ajouté au backlog technique (à développer après le cahier des charges et l'organisation projet, cf. consigne du chef de mission sur l'ordre des étapes).

**Mise à jour du périmètre — "Couvre"** (ajout) : export automatique d'un rapport d'anomalies exploitable (CSV/Excel) pour correction humaine ciblée.

---

## Décision 10 — Contraintes du projet (en cours)

**RGPD** : **confirmé par le chef de mission** — dataset 100% catalogue produit (prix, stock, sku, marge). Les seules données hors "produit pur" sont des URLs vers le site web (images) — ressource catalogue, pas donnée personnelle. Aucune contrainte RGPD identifiée sur ce projet.

**Autres contraintes identifiées** :
- **Dépendance au format source** : l'outil de nettoyage (Pandera) suppose une structure stable des fichiers erp/web/liaison — toute évolution du format d'export nécessiterait une mise à jour des schémas de validation
- **Volumétrie actuelle** : 714 à 825 lignes selon le fichier — l'outil doit rester pertinent si le catalogue grossit (pas de contrainte de performance identifiée à ce stade vu le volume)
- **Outillage imposé** : Python/pandas déjà en place (héritage du notebook P6), pas de contrainte d'infrastructure supplémentaire identifiée

## Décision 11 — Critères de réussite / KPI (finalisés)

**Date** : après double challenge du chef de mission (nombre de catégories obligatoires, puis pertinence de forcer 3 catégories)

**Contexte** : l'assistant avait proposé 3 catégories de KPI en interprétant à tort la liste "data / modèle-insights / opérationnel" de la mission comme obligatoire dans son intégralité. Relecture : les "ex." devant chaque catégorie indiquent des exemples, pas une obligation de remplissage systématique. Erreur de classement corrigée au passage (reproductibilité et clarté du rendu relèvent d'"opérationnel", pas d'"insights").

**KPI retenus** :

*Data* :
- Taux d'anomalies détectées : 5 sur 714 lignes (0,7%) — baseline mesurée
- 13 règles de qualité couvertes (10 reprises du P6 + 3 ajoutées)

*Opérationnel* :
- Temps d'exécution < 1s (mesuré : 0,81s avec Pandera)
- Reproductibilité : résultat identique à chaque exécution (règles déterministes)
- Clarté du rendu : rapport d'anomalies exploitable sans compétence Python (Décision 9)

*Modèle/Insights* : **non applicable**, justifié — aucun modèle prédictif dans le périmètre retenu (régression écartée en Décision 3, clustering non développé en Décision 4)

**Justification** : chaque action mise en place a un critère mesurable associé, sans indicateur artificiel ajouté pour "cocher" une catégorie non pertinente. Démarche plus honnête et défendable en soutenance qu'un remplissage systématique des 3 catégories.

---

## Décision 12 — Priorisation des anomalies + simplification du plan de formation

**Date** : après retour du chef de mission (pas de disponibilité pour une session de 30 min)

**Constat** : plutôt que former le service achats à prioriser les anomalies, l'outil priorise directement à leur place — réduit le besoin de formation à un simple one-pager.

**Décision** : ajout d'une colonne "Priorité" au rapport d'anomalies (Décision 9), avec 3 niveaux appliqués aux 13 règles :

| Priorité | Règles concernées | Logique métier |
|---|---|---|
| 🔴 Critique | Prix négatif (3), stock négatif (4), marge négative price≤purchase_price (11) | Bloque une décision commerciale immédiate (vente à perte, rupture mal signalée) |
| 🟠 Majeure | Doublons product_id erp (1), cohérence stock_status/quantity (2), purchase_price négatif (5), product_id liaison unique/non-null (9), correspondance erp/liaison (10), unicité post-fusion (13) | Fausse l'analyse ou fiabilise la jointure, sans urgence commerciale immédiate |
| 🟡 Mineure | onsale_web hors {0,1} (6), format sku non numérique (7), sku manquant (8), contrôle dtype (12) | Défaut structurel, sans impact business direct |

**Mini-plan de formation (révisé)** : abandon de la session de 30 min, remplacée par un **one-pager** glissé avec le rapport d'anomalies : "Rouge = aujourd'hui, orange = cette semaine, jaune = quand vous avez le temps." Auto-explicatif, ~5 min de lecture, zéro session à planifier.

**Justification** : adapté à la disponibilité réelle du chef de mission et du service achats (contrainte réaliste, pas artificielle) ; démarche cohérente avec la posture "consultant professionnel" attendue en soutenance — trouver la solution la plus efficace, pas la plus lourde.

**Statut** : cahier des charges fonctionnel **complet** (parties prenantes, problématique, périmètre, contraintes, KPI, plan de formation).

---

## Décision 13 — Calage du planning réel

**Date** : 6 août 2026

**Point de vigilance soulevé par l'assistant** : le chef de mission a d'abord évoqué un planning "sur 3 semaines" non retrouvé dans les documents de mission, puis proposé de décaler artificiellement la date de démarrage pour raconter une histoire différente en soutenance. L'assistant a refusé de construire un planning sur une date fictive, en expliquant le risque de crédibilité (traces réelles : Git, dates du journal de bord).

**Date de démarrage réelle confirmée** : lundi 3 août 2026 (cadrage, veille axe C, une bonne partie du cahier des charges réalisés ce jour-là et le lendemain).

**Deadline** : 20 août 2026.

**Durée réelle du projet** : 18 jours (3 → 20 août).

**Justification de la démarche** : un planning honnête, même resserré, est plus défendable en soutenance qu'un planning théorique décorrélé des faits réels et potentiellement contredit par l'historique Git ou les dates du journal de bord.

**Note sur la nature du planning** : outil de pilotage indicatif, pas un engagement figé — ajusté lot par lot selon l'avancement réel, avec un objectif de clôture avant le 20 août plutôt qu'au 20 août pile.

---

## Décision 14 — Implémentation finale du rapport d'anomalies (avec correction de fiabilité)

**Date** : implémentation technique du Lot 4

**Problème découvert en cours de build** : la première version du rapport laissait la colonne "Ligne concernée" à `NaN` pour les 3 règles multi-colonnes (marge, cohérence stock, format sku), car Pandera ne remonte qu'un résultat agrégé pour les `Check` au niveau dataframe, pas le détail ligne par ligne. Corrigé en recalculant les masques booléens directement pour identifier précisément chaque ligne fautive.

**Résultat final** : **16 anomalies détectées avec précision** (contre 8 lignes agrégées dans la première version) :
- 🔴 Critique : 12 (dont 4 nouveaux cas de vente à perte non détectés par le simple contrôle "prix négatif" — prix positif mais inférieur au prix d'achat, lignes 210, 391, 724, 817)
- 🟠 Majeure : 2 (incohérences stock_status/stock_quantity)
- 🟡 Mineure : 2 (dont un cas particulier : ligne 1387 = un bon cadeau, pas un vrai produit vin — à exclure des futures analyses catalogue plutôt qu'à "corriger")

**Livrable produit** : `rapport_anomalies.py` + export `rapport_anomalies_bottleneck.xlsx` (police Arial, priorités colorées, en-tête figé, tri par criticité) — directement lisible par le service achats sans compétence Python, conforme à la Décision 9.

**Traçabilité technique** : Git initialisé, 2 commits réalisés (data_prep + tests comparatifs ; rapport d'anomalies priorisé).

**Correction post-relecture (chef de mission)** : le rapport initial affichait la même ligne produit 2 fois quand elle violait plusieurs règles simultanément (ex : prix négatif ET marge négative, logiquement liées mais redondantes pour un lecteur métier). Corrigé par un regroupement `(source, ligne)` : une ligne produit = une entrée dans le rapport, avec toutes ses règles violées listées et un compteur "Nb règles violées". **Résultat final : 13 anomalies uniques** (9 critiques, 2 majeures, 2 mineures), sans doublon visible.

**Statut** : reste à intégrer ces scripts dans le notebook P6 final (remplacement des checks manuels par les schémas Pandera + génération automatique du rapport).

---

## Décision 15 — Structuration du dépôt Git définitif

**Date** : après retour du chef de mission

**Constat** : le Git initialisé plus tôt (Décision 6bis, dossier `axe_c_nettoyage`) n'était qu'un espace de travail technique brouillon, pas une structure présentable. Vu que ce dépôt alimentera le portfolio GitHub (Mission 2), restructuration en amont de la suite de l'implémentation.

**Structure retenue** :
```
notebook/   → notebook P6 amélioré
scripts/    → data_prep.py, schémas Pandera, génération du rapport
docs/       → journal de bord (traçabilité)
data/       → fichiers sources
```

**Correctifs de portabilité** : les chemins codés en dur (`/mnt/user-data/...`) dans `data_prep.py` et `rapport_anomalies.py` ont été remplacés par des chemins relatifs à la racine du dépôt — nécessaire pour que le projet fonctionne une fois cloné depuis GitHub par un tiers (recruteur, évaluateur).

**Justification** : structurer le dépôt avant d'ajouter la dernière pièce technique (intégration notebook) évite de devoir tout réorganiser après coup, et anticipe l'usage final (portfolio public sur GitHub, cf. échange sur la Mission 2).

**Statut** : dépôt initialisé, 1 commit ("Init dépôt projet 13"). Prêt pour la suite de l'implémentation.

---

## Décision 16 — Nettoyage des identifiants techniques du dépôt

**Date** : après remarque du chef de mission sur l'apparition de son nom dans le repo public

**Analyse du risque** (réalisée avant correction) : le nom du chef de mission apparaissant sur un repo GitHub public n'est **pas un risque réel** — c'est la norme professionnelle d'attribution du travail, et l'objectif même d'un portfolio est de permettre l'identification de l'auteur par un recruteur. Aucune donnée personnelle sensible, aucune donnée client tierce, aucun email réel n'était exposé.

**Décision finale** : le nom du chef de mission est **conservé** dans le README et le journal de bord (cohérent avec l'usage portfolio). En revanche, deux éléments techniques "administratifs" sans valeur pour un lecteur externe sont nettoyés :
- Nom de fichier du notebook : `Chiniard_Quentin_1_notebook_P6_ameliore.ipynb` (convention de dépôt plateforme école, avec ID d'upload résiduel) → renommé `notebook_p6_ameliore.ipynb`
- Email d'auteur Git : remplacé par l'adresse "no-reply" fournie par GitHub (protège l'email réel tout en gardant l'attribution du nom)

**Justification** : distinction entre exposition **intentionnelle** (nom, dans un contexte où c'est la norme et l'objectif) et résidu **technique non maîtrisé** (nom de fichier avec ID d'upload, email inventé non conforme aux bonnes pratiques Git/GitHub).

---

## Décision 17 — Intégration finale dans le notebook P6 (Lot 4 terminé)

**Date** : intégration technique complète, validée par exécution de bout en bout

**Travail réalisé** :
- Correction des chemins de lecture des fichiers (`data/erp.xlsx` etc. au lieu de chemins absolus temporaires) pour la portabilité du dépôt
- Ajout d'une nouvelle section "Étape 6 - Nettoyage automatisé du catalogue (Axe C)" avec : les 4 schémas Pandera (13 règles), la génération du rapport d'anomalies priorisé, l'export Excel formaté
- **Validation de bout en bout** : le notebook complet (117 cellules) a été exécuté intégralement via `jupyter nbconvert --execute`, sans aucune erreur

**Bug découvert et corrigé** (indépendant de l'axe C) : la cellule calculant la courbe de Lorenz / indice de Gini utilisait la colonne `ca_article` avant sa création (bug d'ordre d'exécution du P6 original, invisible tant que le notebook n'était exécuté que cellule par cellule dans le désordre). Corrigé en déplaçant la cellule après la création de `ca_article`. Ce type de bug renforce l'argument de la Décision 14 (fiabilité des vérifications manuelles vs automatisées) à l'échelle de tout le notebook, pas seulement du nettoyage.

**Résultat de la validation en conditions réelles (dans le notebook, après les corrections manuelles déjà présentes dans le P6)** : **11 anomalies uniques** (9 critiques, 0 majeure, 2 mineures) — la catégorie "incohérence stock_status" (majeure) disparaît, ce qui **valide que la correction manuelle de la cellule 20 du P6 original fonctionnait correctement**. Le script standalone (`scripts/rapport_anomalies.py`), lui, tourne sur données brutes sans cette correction préalable et trouve 13 anomalies (2 majeures en plus) — différence normale et documentée, pas une incohérence.

**Statut Lot 4** : **terminé**. Les 3 étapes de la mission (veille, cahier des charges, organisation projet) + l'implémentation technique (nettoyage automatisé intégré et validé) sont bouclées.

---

## Décision 18 — Relecture critique du livrable de documentation par le chef de mission

**Date** : après remise d'une première version du document Word (Mission 1, livrable 2)

**Contexte** : le chef de mission a systématiquement relu le document avant acceptation, conformément à sa posture de validation à chaque étape du projet. 15 points de correction identifiés, tous pertinents :

| # | Correction demandée | Nature |
|---|---|---|
| 1 | Retirer la mention "périmètre du machine learning" dans le résumé exécutif (aucun ML dans le livrable final) | Exactitude |
| 2 | Préciser "LLM (Claude)" plutôt que "l'IA" de façon générique | Précision terminologique |
| 3 | Retirer toute mention de "contrainte de temps" dans la justification du périmètre, recentrer sur l'arbitrage métier | Cohérence avec posture professionnelle (cf. Décisions 3, 4, 6) |
| 4 | Préciser qu'une action humaine reste nécessaire pour la correction des anomalies (ex : vérification physique de stock) | Complétude |
| 5 | Simplifier le titre "Critères de réussite / KPI" en "Critères de réussite" | Clarté |
| 6 | Retirer les emojis de priorité (rendu incohérent selon les lecteurs/imprimantes, lisibilité) | Forme |
| 7 | Remplacer le tableau de dates fixes du planning par un Gantt visuel basé sur le statut réel (moins figé, plus lisible) | Forme + exactitude (le planning à dates fixes était déjà dépassé) |
| 8 | Renommer la colonne "Mitigation" en "Comment on y répond", ajouter le point de vérification avec le mentor/formateur | Accessibilité du vocabulaire + complétude |
| 9 | Simplifier le point "versioning" en retirant la référence à la soutenance | Sobriété |
| 10 | Expliciter pourquoi la validation porte sur chaque dataframe séparément plutôt que sur le seul dataframe fusionné (risque de perte d'anomalies via la jointure "inner") | Rigueur technique — argument non explicité jusqu'ici |
| 11 | Remplacer "viole" par "déroge à" (registre de langue) | Forme |
| 12 | Retirer la mention spécifique de l'outil "Jupyter nbconvert" (détail d'implémentation non représentatif si le chef de mission avait codé lui-même) | Neutralité |
| 13 | Retirer les emojis du tableau de résultats (cohérence avec le point 6) | Forme |
| 14 | Ajouter des estimations de temps de développement pour les prochaines pistes (crédibilité du scoping) | Complétude |
| 15 | Ajouter le prompt de lancement du projet en tête de l'annexe traçabilité, retirer la mention "(reconstitué)" du titre de colonne | Traçabilité |

**Corrections transverses effectuées suite au point 11** : le terme "Règle(s) violée(s)" a été remplacé par "Règle(s) non respectée(s)" dans `scripts/rapport_anomalies.py` et dans le notebook, pour une cohérence terminologique entre tous les livrables (pas seulement le document Word).

**Justification de la démarche** : cette relecture illustre concrètement la méthodologie de contrôle qualité appliquée tout au long du projet — aucun livrable, y compris généré par IA, n'est accepté sans vérification critique par le chef de mission. Bon matériau pour la soutenance sur la question de la "rigueur de la documentation".

---

## Décision 19 — Annexe hypothèses + reproductibilité (requirements.txt)

**Date** : complément suite à la revue des attendus de la Mission 1

**Hypothèses** : le point "hypothèses" de la documentation (attendu explicite de la mission) était jusqu'ici implicite dans les décisions successives, jamais formalisé. Une première proposition de positionnement avant le cahier des charges a été challengée par le chef de mission : sur les 5 hypothèses identifiées, seules 3 (ML peu pertinent, Pandera > Great Expectations, absence de RGPD) ont réellement précédé et informé le cahier des charges ; les 2 autres (angles morts du P6, fiabilité de la correction stock) n'ont été découvertes qu'en cours d'implémentation. Positionner les 5 avant le CDC aurait reconstruit une chronologie inexacte. **Décision finale** : les 5 hypothèses sont regroupées dans une annexe dédiée (§8), avec une colonne "Impact sur le projet" ajoutée pour expliciter la conséquence concrète de chaque hypothèse vérifiée — le format annexe s'affranchit de la contrainte chronologique tout en gardant la démarche traçable.

**Reproductibilité** : ajout d'un `requirements.txt` à la racine du dépôt, listant les dépendances réellement utilisées par le notebook (pandas, numpy, matplotlib, seaborn, plotly, scipy, statsmodels, openpyxl, pandera), avec versions figées. Great Expectations volontairement exclu (non retenu dans la solution finale), avec une note explicative pour permettre de rejouer `scripts/test_great_expectations.py` séparément si besoin.

**Statut Mission 1** : livrables 1 et 2 complets. Reste la Mission 2 (portfolio).

---

## Décisions à venir
- [ ] Portfolio (Mission 2 — GitHub)
