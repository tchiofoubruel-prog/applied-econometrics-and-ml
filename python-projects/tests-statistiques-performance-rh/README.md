# Analyse statistique de la performance et de la satisfaction des employés

Étude appliquée en Python mobilisant une batterie de tests statistiques (paramétriques et non paramétriques) pour explorer les déterminants de la performance et de la satisfaction au travail, à partir d'un jeu de données RH.

## Contexte et objectif

À partir de données individuelles sur des employés (département, score de performance, satisfaction, heures travaillées, heures supplémentaires, salaire...), l'objectif est de tester une série d'hypothèses sur les relations entre variables qualitatives et quantitatives, en choisissant à chaque fois le test le mieux adapté aux propriétés des données (normalité, homogénéité des variances).

## Méthodologie

- **Test du Khi-deux d'indépendance** : relation entre département et niveau de satisfaction, complété par le **V de Cramer** pour mesurer la force de l'association (au-delà de sa seule significativité).
- **Tests de conditions préalables** : test de **Shapiro-Wilk** (normalité des scores de performance par département) et test de **Levene** (homogénéité des variances entre groupes), pour orienter le choix entre test paramétrique et non paramétrique.
- **Comparaison de groupes** : **ANOVA** (`statsmodels`, `ols`) et son équivalent non paramétrique, le test de **Kruskal-Wallis**, pour comparer les scores de performance entre départements.
- **Corrélations** : coefficient de **Pearson** (relation linéaire entre heures travaillées et performance) et coefficient de **Spearman** (relation monotone entre heures supplémentaires et satisfaction).
- **Analyse visuelle complémentaire** : boxplots par groupe, matrice de corrélation, nuages de points, systématiquement mis en regard des résultats des tests formels.

## Principaux résultats

- Le département et le niveau de satisfaction sont **statistiquement liés** (test du Khi-deux significatif), mais l'association est **très faible en intensité** (V de Cramer ≈ 0,01) : la significativité statistique ne traduit pas ici une relation pertinente en pratique.
- Les scores de performance **ne suivent pas une distribution normale** dans les départements (Shapiro-Wilk), mais présentent des **variances homogènes** entre groupes (Levene), ce qui justifie de recourir à un test non paramétrique en complément de l'ANOVA.
- Ni l'ANOVA ni le test de Kruskal-Wallis ne mettent en évidence de **différence significative** de performance entre départements, résultat cohérent entre les deux approches malgré des hypothèses différentes.
- Aucune relation linéaire (Pearson) ou monotone (Spearman) significative n'est détectée entre heures travaillées / heures supplémentaires et performance / satisfaction.
- La seule corrélation notable de l'étude est entre **performance et salaire mensuel** (r ≈ 0,51).

## Compétences mobilisées

Python (pandas, scipy.stats, statsmodels, seaborn/matplotlib) · tests d'indépendance et mesure de force d'association · diagnostic préalable (normalité, homogénéité des variances) · choix entre tests paramétriques et non paramétriques · analyse de corrélation · articulation entre résultats statistiques et visualisation · interprétation métier de résultats statistiques.

## Structure du dépôt

```
tests-statistiques-performance-rh/
├── tests_statistiques_performance_rh.ipynb   # notebook complet (sorties effacées)
└── README.md

Données : Extended_Employee_Performance_and_Productivity_Data.csv (Kaggle), à placer à côté du notebook.
```
