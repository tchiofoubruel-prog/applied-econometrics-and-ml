# Classification bancaire Prédiction de souscription à un dépôt à terme

Projet de data mining : modélisation statistique et apprentissage supervisé.

## Contexte et objectif

Ce projet s'appuie sur le jeu de données **Bank Marketing** (UCI Machine Learning Repository), issu de campagnes de marketing direct d'une banque portugaise. L'objectif est de prédire si un client va souscrire un dépôt à terme (variable cible binaire `y`, `yes`/`no`), à partir de ses caractéristiques socio-démographiques et de l'historique de contact.

Au-delà de la performance prédictive brute, le projet cherche à répondre à une problématique métier : **comment choisir un modèle et un seuil de décision pertinents dans un contexte de classes déséquilibrées**, où l'accuracy seule est trompeuse et où chaque contact commercial a un coût.

## Méthodologie

- **Prétraitement** : séparation apprentissage/test, encodage one-hot des variables catégorielles, standardisation des variables numériques, le tout intégré dans un `Pipeline` scikit-learn pour éviter toute fuite de données (*data leakage*).
- **Modèles comparés** : Naive Bayes (variantes Gaussian, Categorical, Bernoulli), arbre de décision (CART), Random Forest, SVM (linéaire et noyau RBF), réseau de neurones (MLP), régression logistique Ridge.
- **Optimisation** : recherche en grille des hyperparamètres (notamment pour le SVM), comparaison `class_weight=None` vs `class_weight="balanced"` pour traiter le déséquilibre de classes.
- **Évaluation** : accuracy, précision, rappel, F1-score, AUC, matrices de confusion ; validation croisée répétée (`RepeatedStratifiedKFold`) pour évaluer la stabilité des résultats.
- **Incertitude et comparaison statistique** : intervalles de confiance bootstrap à 95 % pour les métriques ; test de Friedman puis comparaisons deux à deux par test de McNemar avec correction de Holm pour comparaisons multiples.
- **Analyse complémentaire** : extraction de règles d'association (support, confiance, lift) sur les variables catégorielles ; analyse biais-variance et courbes d'apprentissage.
- **Décision métier** : proposition d'une fonction de gain (`Gain = G × TP − C × (TP + FP)`) pour déterminer le seuil de classification optimal, plutôt que d'utiliser le seuil par défaut de 0,5.

## Principaux résultats

- La **régression logistique Ridge** obtient le meilleur compromis global : meilleur F1-score moyen (≈ 0,58) et meilleure AUC moyenne (≈ 0,935) en validation croisée, avec des performances stables.
- Le test de Friedman rejette l'hypothèse d'égalité parfaite entre modèles ; après correction de Holm, la Ridge Logistic est significativement meilleure que les modèles les moins performants, mais **pas significativement différente** des meilleurs SVM équilibrés  un rappel utile que le "meilleur" modèle statistique n'est pas toujours tranché avec certitude.
- L'accuracy est écartée comme critère de sélection principal en raison du déséquilibre de classes ; le F1-score est privilégié.
- Le seuil de décision optimal dépend des paramètres économiques (gain par souscription, coût par contact) et non d'une convention fixe à 0,5 : **le meilleur modèle statistique n'est pas nécessairement le meilleur modèle économique**.

## Compétences mobilisées

Python (scikit-learn, pandas, scipy) · pipelines de prétraitement · modélisation et comparaison d'algorithmes de classification · recherche d'hyperparamètres · tests statistiques (Friedman, McNemar, correction de Holm) · quantification de l'incertitude par bootstrap · traduction de résultats statistiques en recommandation opérationnelle.

## Structure du dépôt

```
bank-marketing-classification/
├── bank_marketing_classification.ipynb   # notebook complet (sorties effacées)
└── README.md

Données : Bank Marketing (UCI), fichier bank-additional/bank-additional.csv à placer à côté du notebook.
```
