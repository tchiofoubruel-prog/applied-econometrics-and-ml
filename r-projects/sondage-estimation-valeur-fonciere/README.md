# Estimation de la valeur foncière totale par sondage

Étude appliquée en R de théorie des sondages, sur des données réelles de transactions immobilières françaises (DVF 2019), comparant huit stratégies d'échantillonnage pour l'estimation d'un total de population.

## Contexte et objectif

À partir d'une population de travail de plus de 258 000 locaux vendus, l'objectif est d'estimer le total de la valeur foncière en mettant en œuvre puis en comparant plusieurs plans de sondage : aléatoire simple, stratifié, en grappes, à deux degrés, et estimation par le ratio, puis de départager ces stratégies par simulation.

Le total exact étant connu sur la population de travail (calcul exhaustif possible ici à des fins pédagogiques), chaque stratégie peut être confrontée à la vérité, ce qui permet de quantifier précisément son biais et son erreur.

## Méthodologie

- **Exploration des données** : description de la variable d'intérêt (fortement asymétrique), identification de variables auxiliaires pertinentes pour la stratification (type de local) et pour l'estimation par ratio (surface bâtie, corrélée à la valeur foncière).
- **Plan aléatoire simple (SI)** : estimateur de Horvitz-Thompson, calcul et estimation de la variance.
- **Plan stratifié (STSI)** : comparaison des répartitions proportionnelle et de Neyman entre strates.
- **Plans en grappes et à deux degrés** : sondage par unités primaires (communes, départements), avec évaluation de l'effet de plan.
- **Estimation par le ratio** : exploitation d'une variable auxiliaire corrélée pour réduire la variance, combinée aux différents plans de base.
- **Simulation Monte Carlo (500 répétitions)** : comparaison empirique des huit estimateurs sur la base du biais, de la variance et de l'erreur quadratique moyenne (EQM), avec classement final des stratégies.

## Principaux résultats

- Le plan **stratifié avec affectation de Neyman** s'impose comme la stratégie la plus performante (EQM la plus faible, biais minimal, variance divisée par deux par rapport au plan aléatoire simple).
- Le plan aléatoire simple se classe second, confirmant sa robustesse malgré l'absence d'information auxiliaire exploitée.
- L'estimation par ratio (plan simple) est pénalisée par une corrélation globale modérée entre la variable auxiliaire et la variable d'intérêt à l'échelle de toute la population.
- Les plans en grappes affichent les moins bonnes performances, illustrant l'effet de plan négatif lié à l'hétérogénéité de taille des unités primaires.

## Compétences mobilisées

R (survey, sampling, dplyr, ggplot2) · plans de sondage (SI, STSI, grappes, deux degrés) · estimateur de Horvitz-Thompson · estimation par le ratio · affectation de Neyman · simulation Monte Carlo · comparaison d'estimateurs par biais, variance et EQM · rapport reproductible (R Markdown).

## Structure du dépôt

```
sondage-estimation-valeur-fonciere/
├── rapport_sondage.Rmd   # rapport R Markdown complet (PDF)
└── README.md

Données : extraction DVF 2019 (base8.csv), à placer à côté du .Rmd.
```
