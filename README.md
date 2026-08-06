# Projet 13 — Amélioration du livrable P6 (Bottleneck)

Amélioration critique et documentée du notebook d'analyse stock/ventes du site
Bottleneck (vente de vins en ligne), réalisée dans le cadre du parcours Data
Analyst / Dev IA.

## Contexte

Le service **achats / gestion de catalogue** manque de visibilité fiable sur
la cohérence de son catalogue (prix, stock, marge). Ce projet ajoute une
couche de **nettoyage automatisé** (axe C) au notebook P6 existant, avec un
rapport d'anomalies priorisé directement exploitable, sans compétence Python.

## Structure du dépôt

```
├── notebook/   → le notebook P6 amélioré
├── scripts/    → data_prep.py, schémas de validation (Pandera), génération du rapport
├── docs/       → journal de bord (traçabilité complète des décisions et prompts)
└── data/       → fichiers sources (erp.xlsx, web.xlsx, liaison.xlsx)
```

## Démarche

Voir [`docs/journal_de_bord_p13.md`](docs/journal_de_bord_p13.md) pour la
traçabilité complète : veille technologique (Pandera vs Great Expectations,
testés en conditions réelles), cahier des charges fonctionnel, organisation
projet, et toutes les décisions justifiées au fil de l'eau.

## Utilisation

```bash
cd scripts
python3 rapport_anomalies.py
```

Génère `outputs/rapport_anomalies_bottleneck.xlsx` : rapport d'anomalies
priorisé (🔴 Critique / 🟠 Majeure / 🟡 Mineure), trié par urgence.
