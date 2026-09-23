import numpy as np
import pytest
from rasterio.transform import from_origin

from eo_resilience import extraction


def test_a_point_reads_the_value_of_the_pixel_that_contains_it(ramp_raster):
    # Origin 34.0, -13.0 with 0.001 degree pixels: the centre of row 3,
    # column 4 sits at 34.0045, -13.0035, and the ramp stores row * 10 + col.
    got = extraction.sample_points(ramp_raster, [34.0045], [-13.0035])
    assert got[0] == pytest.approx(34.0)


def test_nodata_comes_back_as_nan(ramp_raster):
    got = extraction.sample_points(ramp_raster, [34.0005], [-13.0005])
    assert np.isnan(got[0])


def test_a_point_outside_the_raster_comes_back_as_nan_without_raising(ramp_raster):
    got = extraction.sample_points(ramp_raster, [10.0, 34.0045], [10.0, -13.0035])
    assert np.isnan(got[0])
    assert got[1] == pytest.approx(34.0)


def test_a_buffer_averages_the_window_and_skips_nodata(ramp_raster):
    # Around row 3, column 4 the three by three window holds the values
    # 23, 24, 25, 33, 34, 35, 43, 44, 45, whose mean is 34.
    got = extraction.sample_points(ramp_raster, [34.0045], [-13.0035], buffer_px=1)
    assert got[0] == pytest.approx(34.0)


def test_a_buffer_at_the_corner_is_clipped_rather_than_failing(ramp_raster):
    # The corner pixel is nodata, so the mean covers 1, 10 and 11 only.
    got = extraction.sample_points(ramp_raster, [34.0005], [-13.0005], buffer_px=1)
    assert got[0] == pytest.approx((1 + 10 + 11) / 3)


def test_points_given_in_another_crs_are_reprojected(tmp_path):
    # Same ramp written in UTM 36S, read with coordinates in degrees.
    arr = np.arange(100, dtype="float32").reshape(10, 10)
    transform = from_origin(600000.0, 8560000.0, 10.0, 10.0)
    path = extraction.write_raster(
        tmp_path / "utm.tif", arr, transform, crs="EPSG:32736"
    )
    xs, ys = extraction.reproject_points(
        [600045.0], [8559965.0], "EPSG:32736", "EPSG:4326"
    )
    got = extraction.sample_points(path, xs, ys, points_crs="EPSG:4326")
    assert got[0] == pytest.approx(34.0)


def test_reprojection_is_a_no_op_when_both_systems_agree():
    xs, ys = extraction.reproject_points([1.0], [2.0], "EPSG:4326", "EPSG:4326")
    assert xs[0] == 1.0 and ys[0] == 2.0


def test_stack_features_keeps_the_names_it_was_given(ramp_raster):
    out = extraction.stack_features(
        {"ndvi": ramp_raster, "ndwi": ramp_raster}, [34.0045], [-13.0035]
    )
    assert list(out) == ["ndvi", "ndwi"]
    assert out["ndvi"][0] == pytest.approx(34.0)


def test_a_negative_buffer_is_refused(ramp_raster):
    with pytest.raises(ValueError):
        extraction.sample_points(ramp_raster, [34.0], [-13.0], buffer_px=-1)
