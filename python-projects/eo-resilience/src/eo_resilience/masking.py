"""Cloud and shadow masking for Sentinel-2 surface reflectance."""

from __future__ import annotations

import numpy as np

# Sentinel-2 Level-2A scene classification, band SCL.
SCL_CLASSES = {
    0: "no_data",
    1: "saturated_or_defective",
    2: "dark_area_pixels",
    3: "cloud_shadow",
    4: "vegetation",
    5: "not_vegetated",
    6: "water",
    7: "unclassified",
    8: "cloud_medium_probability",
    9: "cloud_high_probability",
    10: "thin_cirrus",
    11: "snow_or_ice",
}

#: Classes discarded by :func:`scl_mask` unless the caller overrides them.
DEFAULT_INVALID_SCL = (0, 1, 3, 8, 9, 10, 11)

#: Bits set in the Level-1C QA60 band: 10 for opaque cloud, 11 for cirrus.
QA60_OPAQUE_BIT = 10
QA60_CIRRUS_BIT = 11


def scl_mask(scl, invalid=DEFAULT_INVALID_SCL):
    """Return a boolean array that is True where the pixel is usable.

    Parameters
    ----------
    scl : array_like
        Scene classification band, integer codes described in `SCL_CLASSES`.
    invalid : iterable of int
        Codes to discard. The default drops missing data, defective pixels,
        cloud shadow, both cloud probability classes, thin cirrus, and snow.
    """
    scl = np.asarray(scl)
    if not np.issubdtype(scl.dtype, np.integer):
        raise TypeError("the scene classification band must hold integer codes")
    invalid = np.asarray(sorted(set(int(c) for c in invalid)), dtype=scl.dtype)
    return ~np.isin(scl, invalid)


def qa60_mask(qa60):
    """Return a boolean array that is True where QA60 reports no cloud.

    QA60 is the Level-1C cloud mask band. Bit 10 flags opaque cloud and bit 11
    flags cirrus; a pixel is kept only when both bits are clear.
    """
    qa60 = np.asarray(qa60)
    if not np.issubdtype(qa60.dtype, np.integer):
        raise TypeError("QA60 must hold integer bit flags")
    opaque = (qa60 >> QA60_OPAQUE_BIT) & 1
    cirrus = (qa60 >> QA60_CIRRUS_BIT) & 1
    return (opaque == 0) & (cirrus == 0)


def apply_mask(bands, valid, fill=np.nan):
    """Set invalid pixels to `fill` across every band of a stack.

    `bands` has shape (band, row, col) or (row, col); `valid` has the shape of
    one band. The result is float, since the fill value is normally NaN.
    """
    bands = np.asarray(bands, dtype="float64")
    valid = np.asarray(valid, dtype=bool)
    if bands.ndim == 2:
        if bands.shape != valid.shape:
            raise ValueError("the mask must have the shape of the band")
        return np.where(valid, bands, fill)
    if bands.ndim != 3:
        raise ValueError("expected a 2-D band or a 3-D (band, row, col) stack")
    if bands.shape[1:] != valid.shape:
        raise ValueError("the mask must have the shape of one band")
    return np.where(valid[None, :, :], bands, fill)


def valid_fraction(valid):
    """Share of usable pixels, between 0 and 1."""
    valid = np.asarray(valid, dtype=bool)
    if valid.size == 0:
        return 0.0
    return float(valid.sum()) / float(valid.size)
