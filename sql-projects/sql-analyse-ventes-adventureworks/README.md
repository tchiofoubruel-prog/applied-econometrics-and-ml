# Analyse des ventes en SQL: Base AdventureWorks

Ensemble de requêtes SQL Server d'analyse commerciale, appliquées à la base de données de démonstration **AdventureWorks** (vente de matériel de cyclisme).

## Contexte et objectif

Ce projet regroupe une série de requêtes répondant à des questions métier classiques d'analyse des ventes : performance par région, par commercial, par produit et par catégorie, segmentation client, évolution temporelle, rentabilité, et qualité de production jusqu'à l'automatisation de rapports via une vue SQL.

## Analyses réalisées

- **Performance commerciale** : total des ventes par région, chiffre d'affaires par commercial, top produits et top clients par revenu généré.
- **Analyse temporelle** : évolution mensuelle des ventes par produit avec cumul progressif, calculé par fonction fenêtre (`SUM() OVER (PARTITION BY ... ORDER BY ...)`).
- **Segmentation client** : classification simplifiée des clients en trois segments de dépense (bas / moyen / élevé), identification des clients ayant commandé récemment, répartition par canal d'achat (en ligne vs magasin).
- **Analyse produit** : top produits par revenu et par volume, ventes détaillées par produit au sein de chaque région, ventes totales par catégorie de produit.
- **Rentabilité** : calcul de la marge unitaire brute par produit (écart entre prix de vente moyen et coût de production standard).
- **Qualité de production** : taux de rejet/retour par produit à partir des ordres de fabrication.
- **Automatisation de rapport** : création d'une **vue SQL** (`vw_RapportPerformanceGlobale`) consolidant ventes, produits, catégories et régions en une seule source interrogeable, pour simplifier les analyses répétées.

## Techniques SQL mobilisées

Jointures multi-tables (`JOIN`), agrégations (`GROUP BY`, `SUM`, `AVG`, `COUNT`), fonctions de fenêtre (`OVER`, `PARTITION BY`), filtrage conditionnel (`CASE WHEN`), classement et limitation de résultats (`TOP`), création de vue (`CREATE VIEW`), gestion des divisions par zéro (`NULLIF`).

## Compétences mobilisées

SQL Server (T-SQL) · modélisation de requêtes analytiques multi-tables · fonctions de fenêtre pour l'analyse de séries temporelles · segmentation client · création de vues pour l'automatisation de rapports · traduction de questions métier en requêtes.

## Structure du dépôt

```
sql-analyse-ventes-adventureworks/
├── analyse_ventes_adventureworks.sql   # requêtes T-SQL et vue vw_RapportPerformanceGlobale
└── README.md

Base : AdventureWorks (base de démonstration Microsoft SQL Server).
```
