"""Loading the processed CropHarvest arrays.

Each file holds one labelled location: a monthly array of shape
(time, band) laid out as :data:`eo_resilience.bands.PROCESSED_BANDS`, together
with the coordinates and the crop label in its HDF5 attributes.

The dataset is CC BY-SA 4.0 and is not redistributed with this package. Point
:func:`load_directory` at your own copy of ``features/arrays``.

    Tseng, G., Zvonkov, I., Nakalembe, C. L. and Kerner, H. (2021).
    CropHarvest: a global dataset for crop-type classification.
    NeurIPS Datasets and Benchmarks Track.
"""

from __future__ import annotations

import pathlib
import re

import numpy as np

from . import bands as _bands
from . import phenology as _phenology

#: Source dataset name to the country it samples, for the transferability
#: split. Datasets that mix countries are left out on purpose.
COUNTRY_OF_DATASET = {
    "rwanda-ceo": "Rwanda",
    "kenya": "Kenya",
    "kenya-non-crop": "Kenya",
    "tanzania": "Tanzania",
    "tanzania-ceo": "Tanzania",
    "tanzania-rice-ecaas": "Tanzania",
    "mali": "Mali",
    "mali-non-crop": "Mali",
    "mali-helmets-labelling-crops": "Mali",
    "togo": "Togo",
    "togo-eval": "Togo",
    "ethiopia": "Ethiopia",
    "sudan": "Sudan",
    "uganda": "Uganda",
    "zimbabwe": "Zimbabwe",
}

_NAME = re.compile(r"^(?P<index>\d+)_(?P<dataset>.+)\.h5$")


def parse_filename(name):
    """Split ``1234_togo.h5`` into its index and its source dataset."""
    match = _NAME.match(pathlib.Path(name).name)
    if match is None:
        raise ValueError(f"{name!r} does not follow the index_dataset.h5 pattern")
    return int(match.group("index")), match.group("dataset")


def country_of(dataset):
    """Country sampled by a source dataset, or None when it spans several."""
    return COUNTRY_OF_DATASET.get(dataset)


def load_directory(path, datasets=None, limit=None):
    """Read every array in a directory into one table.

    Parameters
    ----------
    path : path-like
        Directory of ``*.h5`` files.
    datasets : iterable of str, optional
        Keep only these source datasets.
    limit : int, optional
        Stop after this many files, which keeps a smoke run quick.

    Returns
    -------
    dict
        ``X`` of shape (n, time, band), ``y`` of crop labels, ``lat``, ``lon``,
        ``dataset`` and ``country``. Files that cannot be read, or whose array
        has an unexpected shape, are skipped and counted in ``skipped``.
    """
    import h5py

    path = pathlib.Path(path)
    files = sorted(path.glob("*.h5"))
    if not files:
        raise FileNotFoundError(f"no .h5 array under {path}")
    wanted = set(datasets) if datasets is not None else None

    X, y, lat, lon, dataset_name, skipped = [], [], [], [], [], 0
    n_band = len(_bands.PROCESSED_BANDS)
    for file in files:
        try:
            _, name = parse_filename(file.name)
        except ValueError:
            skipped += 1
            continue
        if wanted is not None and name not in wanted:
            continue
        try:
            with h5py.File(file, "r") as handle:
                array = np.asarray(handle["array"], dtype="float64")
                attrs = dict(handle.attrs)
        except (OSError, KeyError):
            skipped += 1
            continue
        if array.ndim != 2 or array.shape[1] != n_band:
            skipped += 1
            continue
        X.append(array)
        y.append(int(attrs.get("is_crop", -1)))
        lat.append(float(attrs.get("instance_lat", np.nan)))
        lon.append(float(attrs.get("instance_lon", np.nan)))
        dataset_name.append(name)
        if limit is not None and len(X) >= limit:
            break

    if not X:
        raise FileNotFoundError(f"no usable array under {path}")
    lengths = {a.shape[0] for a in X}
    if len(lengths) > 1:
        raise ValueError(f"the arrays disagree on their length: {sorted(lengths)}")

    dataset_name = np.array(dataset_name)
    return {
        "X": np.stack(X),
        "y": np.array(y, dtype="int64"),
        "lat": np.array(lat),
        "lon": np.array(lon),
        "dataset": dataset_name,
        "country": np.array([country_of(d) or "unknown" for d in dataset_name]),
        "skipped": skipped,
    }


def band_series(X, name):
    """Monthly series of one band for every location, shape (n, time)."""
    return np.asarray(X)[:, :, _bands.processed_index(name)]


def feature_table(X, extra_bands=("temperature_2m", "total_precipitation", "VV", "VH")):
    """Turn the arrays into named season features, one row per location.

    NDVI comes precomputed in the arrays; NDWI and NDMI are derived from the
    reflectance bands. Terrain is taken from the first time step, since the
    static bands are repeated across months.
    """
    X = np.asarray(X, dtype="float64")
    green, nir, swir = (band_series(X, b) for b in ("B3", "B8", "B11"))
    with np.errstate(invalid="ignore", divide="ignore"):
        ndwi = (green - nir) / (green + nir)
        ndmi = (nir - swir) / (nir + swir)
    series = {
        "ndvi": band_series(X, "NDVI"),
        "ndwi": ndwi,
        "ndmi": ndmi,
    }
    for band in extra_bands:
        series[band] = band_series(X, band)

    rows = []
    for i in range(X.shape[0]):
        features = {}
        for prefix, values in series.items():
            features.update(_phenology.summarise(values[i], prefix=prefix))
        for terrain in ("elevation", "slope"):
            features[terrain] = float(band_series(X, terrain)[i, 0])
        rows.append(features)

    names = sorted(rows[0])
    table = np.array([[row[n] for n in names] for row in rows], dtype="float64")
    return table, names
