# Python Projects

## `data-science/`
Geospatial data construction and machine learning forecasting for a mining production panel. See `data-science/README.md` for the full pipeline description (six notebooks, from geolocation extraction through anomaly integration) and `data-science/MachineLearning/` for the modeling stage (SARIMAX, linear/ridge/lasso, Random Forest, XGBoost, SHAP).

## `geocoding-cities/`
City-name geocoding via Nominatim/OpenStreetMap, cleaning and enriching coordinates for a list of cities read from an Excel file, with a second pass that retries failed lookups. Originally a duplicate file between this repository and `Research-Assistant-Sample-Codes`; kept here as the single copy.

## `bank-marketing-classification/`
Classification of term-deposit subscription on the UCI Bank Marketing data: eight classifiers compared in leakage-free scikit-learn pipelines, bootstrap confidence intervals, Friedman and McNemar tests with Holm correction, and a decision threshold chosen from a gain function rather than fixed at 0.5. README in French.

## `tests-statistiques-performance-rh/`
Parametric and non-parametric tests on an HR dataset (chi-square with Cramér's V, Shapiro-Wilk, Levene, ANOVA, Kruskal-Wallis, Pearson, Spearman), each test chosen from the properties of the data. README in French.

## Requirements

See `requirements.txt` at the repository root. Core dependencies: pandas, numpy, geopandas, rioxarray, xarray, rasterstats, shapely, scikit-learn, statsmodels, scipy, mlxtend, xgboost, shap, matplotlib, seaborn.
