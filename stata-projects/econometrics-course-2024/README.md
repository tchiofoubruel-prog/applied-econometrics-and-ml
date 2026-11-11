# Exercices d'économétrie appliquée en Stata (2024)

Do-file unique (`econometrics_course_2024.do`, environ 1 850 lignes) écrit pendant le cours d'économétrie du CERDI en 2024. Il couvre deux types de travail.

## Construction d'un panel macroéconomique

- Import des indicateurs de la Banque mondiale avec `wbopendata` : PIB par habitant en PPA, ouverture commerciale, dépenses de R&D, crédit au secteur privé, éducation de la population active, impôts sur le revenu, importations de biens TIC, indice de capital humain, inflation.
- Renommage et étiquetage des variables, suppression des agrégats régionaux pour ne garder que les pays.
- Calcul de moyennes sur six périodes de cinq ans.
- Fusion avec l'ICRG (International Country Risk Guide), les indices de développement financier du FMI et des données de brevets.

## Analyse de la pauvreté sur enquête ménages

- Déclaration du plan de sondage et estimations pondérées (`svy`).
- Taux de pauvreté selon l'éducation du chef de ménage, pour les enfants de moins de 15 ans et selon la taille du ménage.

## Données

Les données sources ne sont pas incluses. Les chemins pointent vers `./data` et `./output`, à adapter à votre copie locale.

## Compétences mobilisées

Stata · import de données par API (`wbopendata`) · construction de panel pays · fusion de bases · estimations pondérées sur données d'enquête.
