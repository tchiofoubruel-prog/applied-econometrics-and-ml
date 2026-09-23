"""Normalised difference indices used as resilience proxies.

Each index stands for one of the three signal families the call describes:
NDVI and NDMI for vegetation state and water dynamics, NDWI for open water,
NBR and the texture helper for landscape structure.
"""

from __future__ import annotations

import numpy as np


def normalised_difference(a, b, eps=1e-10):
    """Return (a - b) / (a + b), with NaN where the denominator vanishes.

    `eps` guards the division; pixels whose denominator falls below it in
    absolute value come back as NaN rather than as a large spurious value.
    """
    a = np.asarray(a, dtype="float64")
    b = np.asarray(b, dtype="float64")
    if a.shape != b.shape:
        raise ValueError("both bands must have the same shape")
    denom = a + b
    out = np.full(a.shape, np.nan, dtype="float64")
    usable = np.isfinite(denom) & (np.abs(denom) > eps)
    np.divide(a - b, denom, out=out, where=usable)
    out[~usable] = np.nan
    return out


def ndvi(nir, red):
    """Normalised difference vegetation index, Sentinel-2 B08 and B04."""
    return normalised_difference(nir, red)


def ndwi(green, nir):
    """McFeeters normalised difference water index, B03 and B08."""
    return normalised_difference(green, nir)


def ndmi(nir, swir1):
    """Normalised difference moisture index, B08 and B11.

    Sensitive to vegetation water content, which is the water dynamics signal
    the topic asks for at the scale of a field.
    """
    return normalised_difference(nir, swir1)


def nbr(nir, swir2):
    """Normalised burn ratio, B08 and B12."""
    return normalised_difference(nir, swir2)


def local_std(arr, window=3):
    """Standard deviation in a square window, a plain texture measure.

    Landscape structure is approximated here by local heterogeneity. Pixels
    whose window falls outside the array come back as NaN, and NaN inputs
    propagate, so a masked scene does not leak fabricated texture.
    """
    arr = np.asarray(arr, dtype="float64")
    if arr.ndim != 2:
        raise ValueError("expected a 2-D array")
    if window < 2 or window % 2 == 0:
        raise ValueError("window must be an odd integer of at least 3")
    pad = window // 2
    rows, cols = arr.shape
    out = np.full(arr.shape, np.nan, dtype="float64")
    for i in range(pad, rows - pad):
        for j in range(pad, cols - pad):
            block = arr[i - pad : i + pad + 1, j - pad : j + pad + 1]
            if np.isnan(block).any():
                continue
            out[i, j] = block.std(ddof=0)
    return out
