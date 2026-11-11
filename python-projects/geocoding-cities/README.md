# Géocodage et validation de coordonnées de villes

Notebook unique (`geocode_cities_osm.ipynb`) qui géocode une liste de villes lue depuis un fichier Excel, corrige les échecs, valide les coordonnées obtenues, puis les apparie aux enquêtes d'entreprises de la Banque mondiale (WBES) et à des données climatiques.

## Étapes

1. **Géocodage initial** avec geopy et Nominatim (OpenStreetMap), avec gestion des erreurs et des indisponibilités du service.
2. **Seconde passe** ciblée sur les lignes restées sans coordonnées, avec un cache des requêtes déjà résolues.
3. **Standardisation et contrôle qualité** des noms de pays et de villes, détection des erreurs de localisation.
4. **Validation géospatiale** : chaque point doit tomber à l'intérieur des frontières de son pays.
5. **Préparation de la WBES Afrique** : séparation du champ pays/année, éclatement des entrées à plusieurs villes, fusion avec les coordonnées validées, rapport des coordonnées manquantes et corrections ciblées.
6. **Appariement climatique et estimation** : extraction des variables climatiques au point de chaque entreprise, construction de la variable d'investissement et des contrôles, régressions.

## Données

Les fichiers d'entrée (liste de villes en Excel, WBES au format `.dta`, données climatiques) ne sont pas inclus : ils appartiennent à leurs producteurs et ne peuvent pas être redistribués.

## Compétences mobilisées

Python (pandas, geopy, OSMnx, geopandas, shapely, requests) · géocodage automatisé · validation spatiale par frontières · appariement de bases micro et climatiques · nettoyage de données d'enquête.
