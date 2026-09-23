"""Reading a multi-source cube and turning it into named layers."""

from __future__ import annotations

import numpy as np
import rasterio

from . import bands as _bands
from . import indices as _indices


class Cube:
    """A monthly stack of dynamic bands plus the static terrain bands.

    Attributes
    ----------
    dynamic : ndarray
        Shape (time, dynamic_band, row, col).
    static : ndarray
        Shape (static_band, row, col).
    transform, crs, bounds
        Geometry carried over from the source raster.
    """

    def __init__(self, dynamic, static, transform=None, crs=None, bounds=None):
        dynamic = np.asarray(dynamic, dtype="float64")
        static = np.asarray(static, dtype="float64")
        if dynamic.ndim != 4:
            raise ValueError("dynamic must have shape (time, band, row, col)")
        if static.ndim != 3:
            raise ValueError("static must have shape (band, row, col)")
        if dynamic.shape[1] != len(_bands.DYNAMIC_BANDS):
            raise ValueError(
                f"expected {len(_bands.DYNAMIC_BANDS)} dynamic bands, "
                f"got {dynamic.shape[1]}"
            )
        if static.shape[0] != len(_bands.STATIC_BANDS):
            raise ValueError(
                f"expected {len(_bands.STATIC_BANDS)} static bands, "
                f"got {static.shape[0]}"
            )
        if dynamic.shape[2:] != static.shape[1:]:
            raise ValueError("dynamic and static bands must share a grid")
        self.dynamic = dynamic
        self.static = static
        self.transform = transform
        self.crs = crs
        self.bounds = bounds

    @property
    def n_timesteps(self):
        return self.dynamic.shape[0]

    @property
    def shape(self):
        return self.dynamic.shape[2:]

    def band(self, name):
        """Time series of one dynamic band, shape (time, row, col)."""
        return self.dynamic[:, _bands.band_index(name), :, :]

    def terrain(self, name):
        """One static band, shape (row, col)."""
        return self.static[_bands.static_index(name)]

    def ndvi(self):
        return _indices.ndvi(self.band("B8"), self.band("B4"))

    def ndwi(self):
        return _indices.ndwi(self.band("B3"), self.band("B8"))

    def ndmi(self):
        return _indices.ndmi(self.band("B8"), self.band("B11"))

    def nbr(self):
        return _indices.nbr(self.band("B8"), self.band("B12"))

    def __repr__(self):
        rows, cols = self.shape
        return (
            f"<Cube {self.n_timesteps} months, {rows}x{cols} px, "
            f"{len(_bands.DYNAMIC_BANDS)} dynamic + "
            f"{len(_bands.STATIC_BANDS)} static bands>"
        )


def from_array(array):
    """Split a raw (band, row, col) stack into its dynamic and static parts."""
    array = np.asarray(array, dtype="float64")
    if array.ndim != 3:
        raise ValueError("expected a 3-D (band, row, col) stack")
    n_time = _bands.infer_timesteps(array.shape[0])
    n_dyn = len(_bands.DYNAMIC_BANDS)
    dynamic = array[: n_time * n_dyn].reshape(n_time, n_dyn, *array.shape[1:])
    static = array[n_time * n_dyn :]
    return Cube(dynamic, static)


def read(path):
    """Open a cube written in the CropHarvest band layout."""
    with rasterio.open(path) as src:
        array = src.read()
        transform, crs, bounds = src.transform, src.crs, src.bounds
    cube = from_array(array)
    cube.transform, cube.crs, cube.bounds = transform, crs, bounds
    return cube
