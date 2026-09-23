"""Reading raster values at survey locations, with rasterio and GDAL."""

from __future__ import annotations

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.transform import rowcol
from rasterio.warp import transform as warp_transform
from rasterio.windows import Window


def reproject_points(xs, ys, src_crs, dst_crs):
    """Move coordinates between two coordinate reference systems."""
    src_crs = CRS.from_user_input(src_crs)
    dst_crs = CRS.from_user_input(dst_crs)
    if src_crs == dst_crs:
        return np.asarray(xs, dtype="float64"), np.asarray(ys, dtype="float64")
    out_x, out_y = warp_transform(src_crs, dst_crs, list(xs), list(ys))
    return np.asarray(out_x, dtype="float64"), np.asarray(out_y, dtype="float64")


def sample_points(path, xs, ys, band=1, points_crs="EPSG:4326", buffer_px=0):
    """Read a raster at the given coordinates.

    With `buffer_px` at zero the value of the containing pixel is returned.
    With a positive buffer the mean over the square window of that half-width
    is returned instead, ignoring nodata and NaN, which is the usual way to
    blunt geolocation error on survey coordinates.

    Points falling outside the raster, and windows holding no valid pixel,
    come back as NaN rather than raising, so one stray coordinate does not
    abort the extraction of a whole survey.
    """
    if buffer_px < 0:
        raise ValueError("buffer_px cannot be negative")
    xs = np.asarray(xs, dtype="float64")
    ys = np.asarray(ys, dtype="float64")
    if xs.shape != ys.shape:
        raise ValueError("xs and ys must have the same shape")
    out = np.full(xs.shape, np.nan, dtype="float64")
    with rasterio.open(path) as src:
        px, py = reproject_points(xs, ys, points_crs, src.crs)
        rows, cols = rowcol(src.transform, px, py)
        rows = np.atleast_1d(np.asarray(rows, dtype="int64"))
        cols = np.atleast_1d(np.asarray(cols, dtype="int64"))
        nodata = src.nodata
        for i, (r, c) in enumerate(zip(rows, cols)):
            r0, r1 = r - buffer_px, r + buffer_px + 1
            c0, c1 = c - buffer_px, c + buffer_px + 1
            if r1 <= 0 or c1 <= 0 or r0 >= src.height or c0 >= src.width:
                continue
            r0, c0 = max(r0, 0), max(c0, 0)
            r1, c1 = min(r1, src.height), min(c1, src.width)
            block = src.read(
                band, window=Window(c0, r0, c1 - c0, r1 - r0), masked=False
            ).astype("float64")
            if nodata is not None:
                block = np.where(block == nodata, np.nan, block)
            if np.isfinite(block).any():
                out.reshape(-1)[i] = float(np.nanmean(block))
    return out


def stack_features(path_by_name, xs, ys, points_crs="EPSG:4326", buffer_px=0):
    """Extract several rasters at the same points.

    Returns a dict of feature name to array, in the order of `path_by_name`,
    so the caller can build a design matrix without guessing column order.
    """
    return {
        name: sample_points(
            path, xs, ys, points_crs=points_crs, buffer_px=buffer_px
        )
        for name, path in path_by_name.items()
    }


def write_raster(path, array, transform, crs="EPSG:4326", nodata=None):
    """Write a single-band GeoTIFF, used by the tests and by the fetch layer."""
    array = np.asarray(array)
    if array.ndim != 2:
        raise ValueError("expected a 2-D array")
    profile = {
        "driver": "GTiff",
        "height": array.shape[0],
        "width": array.shape[1],
        "count": 1,
        "dtype": array.dtype.name,
        "crs": CRS.from_user_input(crs),
        "transform": transform,
    }
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array, 1)
    return path
