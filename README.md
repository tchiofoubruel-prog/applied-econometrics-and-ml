# Applied Econometrics, Geospatial Data and Machine Learning

[![notebook syntax check](https://github.com/tchiofoubruel-prog/applied-econometrics-and-ml/actions/workflows/notebook-check.yml/badge.svg)](https://github.com/tchiofoubruel-prog/applied-econometrics-and-ml/actions/workflows/notebook-check.yml)
[![R Markdown parse check](https://github.com/tchiofoubruel-prog/applied-econometrics-and-ml/actions/workflows/render-check.yml/badge.svg)](https://github.com/tchiofoubruel-prog/applied-econometrics-and-ml/actions/workflows/render-check.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Analysis code written between 2023 and 2025, in Python, Stata and R Markdown. The Python side
builds gridded climate data into analysis panels with xarray, rioxarray, rasterstats, geopandas,
shapely and fiona, geocodes survey locations with geopy and OSMnx, and models the result with
NumPy, pandas, scikit-learn, statsmodels, XGBoost and SHAP. The Stata and R Markdown sides cover
impact evaluation, panel econometrics and household survey measurement, on data from Rwanda, Mali,
Albania and the World Bank indicators.

**Start here:** [`method-demos/`](method-demos/) holds the two notebooks that run from this
repository alone, a Monte Carlo cost-benefit analysis with Sobol sensitivity indices and an
interpretable machine-learning pipeline with its validation design written out in the notebook.
Both generate their own synthetic inputs, which is why their outputs are kept and why the figures
below can be reproduced without any external file. The project of longest reach is
[`python-projects/data-science/`](python-projects/data-science/), a 1901 to 2023 climate and mining
panel assembled from CRU TS4.08 NetCDF grids, and the single largest body of code is
[`python-projects/geocoding-cities/`](python-projects/geocoding-cities/), about 4,300 lines that
resolve and validate city coordinates.

<p align="center">
  <img src="method-demos/figures/ml_shap.png" width="46%"
       alt="SHAP summary plot from the interpretable machine-learning notebook">
  <img src="method-demos/figures/mc_sobol.png" width="46%"
       alt="First-order and total Sobol sensitivity indices from the Monte Carlo notebook">
</p>

<p align="center"><sub>Left, the SHAP summary from the machine-learning notebook. Right, first-order
and total Sobol indices from the Monte Carlo notebook. Both are computed on synthetic inputs.</sub></p>

## Running the method demos

```bash
git clone https://github.com/tchiofoubruel-prog/applied-econometrics-and-ml.git
cd applied-econometrics-and-ml
pip install -r requirements.txt
jupyter lab method-demos/
```

Running the two notebooks end to end reproduces the four figures in `method-demos/figures/`. Every
other folder reads its inputs from a local `./data` path that you supply, described in that folder's
own README.

## Code organisation and checks

The repository is organised as Jupyter notebooks and Stata do-files, one folder per project, each
with its own README covering the data and the method. Two GitHub Actions workflows run on every
push: the Python notebooks are converted with nbconvert and byte-compiled, and the R Markdown files
are purled with knitr and parsed. The checks confirm that the code parses and compiles, and they
stop short of executing anything, since the source data stays outside the repository. Of the
fourteen notebooks, the two in `method-demos/` keep their executed outputs, and the other twelve
have their outputs cleared.

Code volume, counted in code cells and script lines rather than in repository bytes: about 5,900
lines of Python, 4,700 of Stata and 2,600 of R Markdown. GitHub's language bar reports notebooks
under "Jupyter Notebook" and classifies R Markdown as prose, so neither Python nor R appears in it.

## Contents

### `method-demos/`
Two executed notebooks on synthetic data (see the folder README): Monte Carlo cost-benefit with
Sobol indices, and an interpretable ML pipeline with a leakage-free evaluation design.

### `python-projects/`
| Folder | Method | Topic |
|---|---|---|
| `data-science/Extraction/` | 0.1° grid cut from the CRU gridboxes, NetCDF in xarray, raster writing with rioxarray, zonal means with rasterstats | Mine geolocation and ten monthly climate variables, CRU TS4.08, 1901 to 2023, anomalies against a 1901 to 1950 baseline |
| `data-science/MachineLearning/` | SARIMAX, linear/ridge/lasso regression, Random Forest, XGBoost, SHAP | Forecasting mining production from the constructed climate panel |
| `geocoding-cities/` | Geocoding through geopy (Nominatim, Google) and OSMnx, semantic and polygon-inclusion validation | City coordinate lookup, validation and cleanup from an Excel city list |

### `stata-projects/`
Six projects, each in its own folder with a short README describing the data and the method.

| Folder | Method | Topic |
|---|---|---|
| `impact-evaluation-methods/` | RCT, RDD, DiD, PSM, IV | Replication of published impact evaluation methods |
| `panel-data-econometrics/` | Fixed effects, random effects, Hausman test, dynamic panel | Technology and income inequality, World Bank WDI panel (1993 to 2022) |
| `survey-data-analysis/` | Sampling weights, stratification, post-stratification | Household survey methodology, Albania LSMS |
| `household-survey-rwanda/` | Data cleaning, consumption aggregation | Rwanda LWH agricultural household follow-up survey |
| `education-rct-analysis/` | Balance tests, treatment effects, heterogeneity | School-level randomized subsidy program (2010 to 2012) |
| `econometrics-course-2024/` | Applied Stata exercise | CERDI Économétrie 2024 |

### `r-projects/`
| Folder | Method | Topic |
|---|---|---|
| `food-security-mali/` | Descriptive statistics, food insecurity indicators | Food Insecurity Experience Scale, Mali |
| `pca-environment/` | Principal component analysis, dimensionality reduction | Environmental data |
| `analyse-pauvrete/` | FGT, Watts and Chakravarty indices, stochastic dominance | Poverty comparison across Benin, Mali, Burkina Faso and Togo, EHCVM surveys |

## Data

Source data is not included in this repository. Several projects use survey or institutional data
(World Bank WDI, Albania LSMS, Rwanda LWH follow-up survey, EHCVM surveys, CRU climate data) that
belongs to third-party institutions and cannot be redistributed here. Only the analysis code is
shared. Scripts reference a relative `./data` path; point it at your own copy of the source data to
reproduce the analysis.

## Requirements

Python dependencies are pinned to compatible-release ranges in `requirements.txt` at the repository
root: numpy, pandas, xarray, geopandas, shapely, fiona, rioxarray, rasterstats, statsmodels,
scikit-learn, xgboost, shap, SALib, geopy, osmnx, folium, matplotlib and seaborn. Stata scripts were
written for Stata 16 or later, and the R Markdown files list their packages at the top of each file.

## Training

Courses worked through while writing this code, with the materials left in their authors' own
repositories rather than copied here: Biscaye, Pierre (2025 and 2026), *Introduction to Data Science
for Economists*, Université Clermont Auvergne / CERDI, the
[2025 edition](https://github.com/pbiscaye/IntroDataScienceEcon2025) taken for credit in the Master 2
and the [2026 edition](https://github.com/pbiscaye/IntroDataScienceEcon2026) worked through
independently under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), together with his
[Data Science Resources Index](https://github.com/pbiscaye/Teaching/blob/main/DataScienceResourcesIndex.md).

## Citation

Citation metadata is in `CITATION.cff`.

## License

Code is released under the MIT License (see `LICENSE`). The licence covers the analysis code in this
repository only. It does not cover the third-party survey, institutional or climate data referenced
above, none of which is redistributed here.
