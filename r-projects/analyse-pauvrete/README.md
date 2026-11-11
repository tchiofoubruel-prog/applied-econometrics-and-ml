# Analyse comparative de la pauvreté en Afrique de l'Ouest (EHCVM)

Script R Markdown (`poverty_analysis_report.Rmd`) qui mesure et compare la pauvreté dans quatre pays couverts par les enquêtes EHCVM 2018 : Bénin, Burkina Faso, Niger et Togo. Travail de groupe réalisé en troisième année de licence (2022/2023).

## Démarche

- Fusion des fichiers ménages (bien-être) et individus pour chaque pays.
- Écriture de fonctions pour les indices FGT (incidence, profondeur, sévérité), de Watts et de Chakravarty.
- Calcul des indices par sous-groupe de population.
- Comparaison des pays par des tests de dominance stochastique sur une plage de seuils de pauvreté.

## Données

Les fichiers EHCVM (`.dta`) ne sont pas inclus. Ils sont diffusés par les instituts nationaux de statistique et la Banque mondiale.

## Compétences mobilisées

R (haven) · mesure de la pauvreté (FGT, Watts, Chakravarty) · dominance stochastique · comparaison internationale sur données d'enquête harmonisées.
