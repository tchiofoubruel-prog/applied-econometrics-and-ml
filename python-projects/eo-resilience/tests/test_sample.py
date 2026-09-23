"""The real-cube test. It needs GitHub, so it is skipped when offline."""

import urllib.error

import numpy as np
import pytest

from eo_resilience import bands, phenology, sample


@pytest.fixture(scope="module")
def togo(tmp_path_factory):
    dest = tmp_path_factory.mktemp("sample") / sample.TOGO_NAME
    try:
        return sample.togo_cube(dest)
    except (urllib.error.URLError, OSError) as exc:
        pytest.skip(f"the Togo cube could not be downloaded: {exc}")


def test_the_real_cube_has_the_layout_the_package_expects(togo):
    assert togo.n_timesteps == 12
    assert togo.dynamic.shape[1] == len(bands.DYNAMIC_BANDS)
    assert togo.static.shape[0] == len(bands.STATIC_BANDS)


def test_the_plot_sits_where_the_sample_says_it_does(togo):
    lon = (togo.bounds.left + togo.bounds.right) / 2
    lat = (togo.bounds.bottom + togo.bounds.top) / 2
    assert lon == pytest.approx(sample.TOGO_APPROX_LONLAT[0], abs=0.01)
    assert lat == pytest.approx(sample.TOGO_APPROX_LONLAT[1], abs=0.01)


def test_the_reflectance_bands_hold_plausible_values(togo):
    red = togo.band("B4")
    assert np.isfinite(red).all()
    assert 0 < np.nanmean(red) < 10000


def test_the_era5_temperature_is_a_plausible_tropical_kelvin(togo):
    celsius = np.nanmean(togo.band("temperature_2m")) - 273.15
    assert 20 < celsius < 35


def test_the_ndvi_season_rises_and_falls_as_a_single_rainy_season(togo):
    series = np.nanmean(togo.ndvi(), axis=(1, 2))
    assert -1 <= series.min() and series.max() <= 1
    assert phenology.amplitude(series) > 0.3
    # The Guinea savanna greens up after the first rains and peaks late in
    # the year, so the greenest month is not the first or the last one.
    assert 2 <= phenology.peak_month(series) <= 10


def test_the_terrain_bands_describe_a_gentle_slope(togo):
    assert 50 < np.nanmean(togo.terrain("elevation")) < 1000
    assert 0 <= np.nanmean(togo.terrain("slope")) < 30


def test_the_summary_produces_the_full_feature_table(togo):
    features = phenology.summarise_cube(togo)
    assert len(features) == 66
    assert all(np.isfinite(v) for v in features.values())
