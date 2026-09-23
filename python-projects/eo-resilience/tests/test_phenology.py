import numpy as np
import pytest

from eo_resilience import bands, cube, phenology

# A single rainy season: low, rising, peak in the middle, falling back.
SEASON = np.array([0.10, 0.12, 0.20, 0.35, 0.55, 0.70, 0.65, 0.45, 0.25, 0.15, 0.11, 0.10])


def test_the_peak_and_the_trough_are_read_off_the_series():
    assert phenology.peak(SEASON) == pytest.approx(0.70)
    assert phenology.trough(SEASON) == pytest.approx(0.10)
    assert phenology.amplitude(SEASON) == pytest.approx(0.60)


def test_the_peak_month_is_the_greenest_one():
    assert phenology.peak_month(SEASON) == 5


def test_greenup_is_the_first_crossing_of_half_the_amplitude():
    # Half of the amplitude sits at 0.40, first reached at index 4.
    assert phenology.greenup_month(SEASON) == 4


def test_the_season_length_counts_the_months_above_the_threshold():
    assert phenology.season_length(SEASON) == 4


def test_a_flat_series_has_no_season():
    flat = np.full(12, 0.3)
    assert phenology.amplitude(flat) == pytest.approx(0.0)
    assert np.isnan(phenology.greenup_month(flat))
    assert np.isnan(phenology.season_length(flat))


def test_the_integral_is_rescaled_when_months_are_missing():
    full = np.array([1.0, 1.0, 1.0, 1.0])
    gappy = np.array([1.0, np.nan, 1.0, np.nan])
    assert phenology.integral(full) == pytest.approx(4.0)
    assert phenology.integral(gappy) == pytest.approx(4.0)


def test_an_entirely_missing_series_yields_nan_everywhere():
    empty = np.full(6, np.nan)
    stats = phenology.summarise(empty)
    assert all(np.isnan(v) for v in stats.values())


def test_summarise_prefixes_the_keys():
    stats = phenology.summarise(SEASON, prefix="ndvi")
    assert "ndvi_peak" in stats and "peak" not in stats


def test_an_empty_or_two_dimensional_series_is_refused():
    with pytest.raises(ValueError):
        phenology.peak(np.array([]))
    with pytest.raises(ValueError):
        phenology.peak(np.zeros((2, 2)))


def test_summarise_cube_covers_every_source():
    rng = np.random.default_rng(3)
    arr = rng.uniform(0.05, 0.6, size=(bands.expected_band_count(6), 3, 3))
    features = phenology.summarise_cube(cube.from_array(arr))
    assert any(k.startswith("ndvi_") for k in features)          # Sentinel-2
    assert any(k.startswith("VV_") for k in features)            # Sentinel-1
    assert any(k.startswith("temperature_2m_") for k in features)  # ERA5
    assert "elevation" in features and "slope" in features        # SRTM
    assert len(features) == 66
