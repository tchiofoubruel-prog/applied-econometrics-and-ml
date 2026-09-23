"""Season-level summaries of a monthly index series.

A resilience proxy is rarely the reflectance of one date. What carries
information about a farming system is the shape of its season: how green it
gets, how long it stays green, when it greens up, and how much the signal
varies from month to month. These summaries are the features the model sees,
and each one is meant to stand for something a SHARP+ question asks about.
"""

from __future__ import annotations

import numpy as np


def _series(values):
    values = np.asarray(values, dtype="float64")
    if values.ndim != 1:
        raise ValueError("expected a one-dimensional monthly series")
    if values.size == 0:
        raise ValueError("the series is empty")
    return values


def peak(values):
    """Highest value of the season, NaN when nothing is observed."""
    values = _series(values)
    return float(np.nanmax(values)) if np.isfinite(values).any() else np.nan


def trough(values):
    values = _series(values)
    return float(np.nanmin(values)) if np.isfinite(values).any() else np.nan


def amplitude(values):
    """Peak minus trough, the depth of the seasonal cycle.

    A flat series means either bare ground or perennial cover; a deep cycle
    means an annual crop. The distinction is what separates the cropping
    system indicators from the tree cover ones.
    """
    hi, lo = peak(values), trough(values)
    return hi - lo if np.isfinite(hi) and np.isfinite(lo) else np.nan


def integral(values):
    """Sum over the observed months, a proxy for cumulative productivity.

    Missing months are skipped rather than treated as zero, and the result is
    rescaled to the full length of the series so that two locations with
    different cloud cover stay comparable.
    """
    values = _series(values)
    finite = np.isfinite(values)
    if not finite.any():
        return np.nan
    return float(np.nansum(values) * values.size / finite.sum())


def peak_month(values):
    """Index of the greenest month, NaN when nothing is observed.

    Timing separates a single rainy season from a bimodal one, and a shift in
    timing between neighbouring farms is often the first visible sign of a
    change in planting date.
    """
    values = _series(values)
    if not np.isfinite(values).any():
        return np.nan
    return float(np.nanargmax(values))


def greenup_month(values, fraction=0.5):
    """First month where the series crosses `fraction` of its amplitude.

    Returns NaN when the season never reaches that level, which is itself
    informative: a plot that does not green up is either fallow or failed.
    """
    values = _series(values)
    lo, hi = trough(values), peak(values)
    if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
        return np.nan
    threshold = lo + fraction * (hi - lo)
    above = np.flatnonzero(np.isfinite(values) & (values >= threshold))
    return float(above[0]) if above.size else np.nan


def season_length(values, fraction=0.5):
    """Number of months spent above `fraction` of the amplitude."""
    values = _series(values)
    lo, hi = trough(values), peak(values)
    if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
        return np.nan
    threshold = lo + fraction * (hi - lo)
    return float(np.sum(np.isfinite(values) & (values >= threshold)))


def variability(values):
    """Standard deviation across months, ignoring the missing ones."""
    values = _series(values)
    finite = values[np.isfinite(values)]
    return float(finite.std(ddof=0)) if finite.size else np.nan


def summarise(values, prefix=""):
    """Every summary above, as a dict ready to become feature columns."""
    stats = {
        "peak": peak(values),
        "trough": trough(values),
        "amplitude": amplitude(values),
        "integral": integral(values),
        "peak_month": peak_month(values),
        "greenup_month": greenup_month(values),
        "season_length": season_length(values),
        "variability": variability(values),
    }
    if prefix:
        stats = {f"{prefix}_{k}": v for k, v in stats.items()}
    return stats


def summarise_cube(cube, reducer=np.nanmean):
    """Feature table for one cube, from its four indices and its terrain.

    `reducer` collapses the spatial extent of the cube to a single series per
    month, so the result describes the location rather than each pixel.
    """
    features = {}
    for name, grid in (
        ("ndvi", cube.ndvi()),
        ("ndwi", cube.ndwi()),
        ("ndmi", cube.ndmi()),
        ("nbr", cube.nbr()),
    ):
        series = reducer(grid, axis=(1, 2))
        features.update(summarise(series, prefix=name))
    for band in ("temperature_2m", "total_precipitation", "VV", "VH"):
        series = reducer(cube.band(band), axis=(1, 2))
        features.update(summarise(series, prefix=band))
    for terrain in ("elevation", "slope"):
        features[terrain] = float(reducer(cube.terrain(terrain)))
    return features
