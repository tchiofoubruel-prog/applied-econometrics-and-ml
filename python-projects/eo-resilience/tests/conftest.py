import numpy as np
import pytest
from rasterio.transform import from_origin

from eo_resilience.extraction import write_raster


@pytest.fixture
def small_transform():
    """Ten-metre pixels with the origin at 30E, 13S, roughly southern Malawi."""
    return from_origin(34.0, -13.0, 0.001, 0.001)


@pytest.fixture
def ramp_raster(tmp_path, small_transform):
    """A 10 by 10 raster whose value equals row * 10 + col, with nodata."""
    arr = (np.arange(100, dtype="float32").reshape(10, 10))
    arr[0, 0] = -9999.0
    path = tmp_path / "ramp.tif"
    write_raster(path, arr, small_transform, nodata=-9999.0)
    return path
