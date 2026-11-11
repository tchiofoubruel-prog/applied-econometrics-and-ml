# Manipulation de données bancaires et transactionnelles avec SAS

Projet de manipulation, nettoyage et croisement de données multi-sources en SAS, portant sur des données bancaires, clients et transactions.

## Contexte et objectif

Ce projet part de plusieurs fichiers sources bruts (banques, clients, transactions, référentiel géographique) et construit, étape par étape, un pipeline complet de préparation de données : import, nettoyage, déduplication, enrichissement, agrégation, jointures et export, jusqu'à la production de tables et de fichiers exploitables pour l'analyse.

## Étapes du pipeline

1. **Import multi-format** : lecture de fichiers texte délimités (tabulation, `*`, virgule) via `proc import`.
2. **Déduplication** : détection et isolement des lignes strictement dupliquées (`proc sort ... noduprecs / dupout`).
3. **Nettoyage et transformation de variables texte** : construction de champs dérivés par concaténation et extraction de sous-chaînes (numéro de téléphone formaté, adresse e-mail reconstituée à partir du nom).
4. **Gestion des valeurs manquantes** : filtrage sur complétude de variables clés, et réaffectation de valeurs manquantes par report de la dernière valeur connue (instruction `RETAIN`).
5. **Création de variables dérivées métier** : génération d'une variable de génération démographique à partir de l'année de naissance, extraction d'un code d'État depuis une adresse.
6. **Simulation itérative** : boucle `do while` calculant, pour chaque client, le nombre d'années nécessaires pour atteindre un seuil de solde donné un taux d'intérêt annuel.
7. **Concaténation et agrégation temporelles** : fusion de plusieurs fichiers de transactions, extraction de la date à partir d'un horodatage, agrégation journalière (nombre et montant total de transactions par jour) via `proc means`.
8. **Jointures internes** : rapprochement des tables clients/banques puis clients/transactions par clé (`BankID`, `AccountID`), avec isolement des observations sans correspondance.
9. **Formats utilisateurs** : création de formats personnalisés pour recoder des variables catégorielles (statut marital), discrétiser une variable continue en classes (à partir de ses quartiles), et mapper des codes vers des libellés à partir d'une table de référence (`proc format cntlin`).
10. **Paramétrage par macro-variables** : généralisation du code d'export via des macro-variables (`%let`) pour rendre la table source, le chemin de sortie et le délimiteur configurables sans dupliquer le code.

## Compétences mobilisées

SAS (data step, `proc import`/`export`, `proc sort`, `proc means`, `proc univariate`, `proc format`) · nettoyage et déduplication de données · gestion des valeurs manquantes · création de variables dérivées · jointures et agrégation de données · formats utilisateurs · macro-programmation SAS (`%let`).

## Structure du dépôt

```
sas-data-pipeline-bancaire/
├── pipeline_donnees_bancaires.sas   # pipeline complet, étapes 1 à 10
└── README.md

Données : bank.txt, supercustomer.txt, TransactionFull_1.csv, TransactionFull_2.csv, StateCode.csv,
à placer dans le dossier pointé par la macro-variable &chemin (./data par défaut).
```
