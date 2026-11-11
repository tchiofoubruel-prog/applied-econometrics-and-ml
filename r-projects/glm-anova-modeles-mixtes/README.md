# Modèles linéaires gaussiens: ANOVA, modèles mixtes et sélection de variables

Étude appliquée en R portant sur deux jeux de données, autour des modèles linéaires gaussiens : analyse de variance à facteurs croisés, modèles mixtes, et diagnostic de multicolinéarité en régression multiple.

## Exercice 1: ANOVA à facteurs croisés et modèles mixtes

**Données** : temps de trajet mesuré sur 30 individus, observés à 12 reprises, selon le type de transport (Bus, Vélo, Voiture) et le moment (heure creuse / heure de pointe).

**Démarche** :
- Construction progressive de modèles ANOVA à un facteur, puis à deux facteurs croisés (avec et sans interaction).
- Distinction entre test de Fisher global (effet d'un facteur qualitatif dans son ensemble) et tests de Student par modalité, et interprétation de résultats en apparence contradictoires.
- Sélection de modèle par AIC et R² ajusté, avec application de la règle hiérarchique : conserver toutes les variables impliquées dans une interaction significative.
- Passage à des **modèles linéaires mixtes** (effet aléatoire d'usager, estimation par REML) pour tenir compte de la structure de mesures répétées, et décomposition de la variance en composante inter-individuelle et résiduelle.

**Résultat principal** : le meilleur modèle est un modèle mixte à deux facteurs croisés avec interaction et intercept aléatoire par usager. L'heure de pointe pénalise davantage le temps de trajet en voiture qu'en vélo ou en bus ; en heure creuse, le mode de transport a peu d'effet.

## Exercice 2: Régression multiple, multicolinéarité et sélection de variables

**Données** : capacité respiratoire expliquée par des indicateurs de condition physique, pratique sportive, alimentation, indice de santé, âge et IMC.

**Démarche** :
- Analyse des corrélations pour détecter deux problèmes de multicolinéarité : une redondance parfaite entre deux variables (l'une étant construite à partir de l'autre) et une quasi-colinéarité entre deux autres prédicteurs.
- Diagnostic quantitatif par facteur d'inflation de la variance (VIF).
- Sélection de variables par méthode descendante (AIC), puis simplification manuelle du modèle en retirant les variables non significatives une fois la colinéarité traitée.
- Validation du modèle final par analyse des résidus (linéarité, normalité, homoscédasticité, points influents).

**Résultat principal** : après traitement de la colinéarité, un modèle simple à une seule variable explicative (score d'activité sportive) s'avère le plus stable et interprétable, avec un effet positif et significatif sur la capacité respiratoire, malgré un pouvoir explicatif global modeste.

## Compétences mobilisées

R (car, nlme, knitr) · analyse de variance à facteurs croisés · modèles linéaires mixtes (effets aléatoires, REML) · diagnostic de multicolinéarité (VIF) · sélection de variables par critère d'information · validation de modèle par analyse des résidus · rédaction de rapport reproductible (R Markdown).

## Structure du dépôt

```
glm-anova-modeles-mixtes/
├── modeles_lineaires_gaussiens.Rmd   # rapport R Markdown complet (PDF/HTML)
└── README.md

Données : fichiers des deux exercices (dont datasante.csv), à placer à côté du .Rmd.
```
