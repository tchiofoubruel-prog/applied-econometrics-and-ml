import pytest

from eo_resilience import bands


def test_the_four_sources_are_all_present():
    assert set(bands.SOURCE_OF.values()) == {"sentinel1", "sentinel2", "era5", "srtm"}


def test_every_raw_band_is_attributed_to_a_source():
    assert all(b in bands.SOURCE_OF for b in bands.RAW_BANDS)


def test_the_band_count_matches_the_cropharvest_layout():
    # Twelve months of seventeen dynamic bands plus two static ones is the
    # 206-band cube that CropHarvest exports for one location.
    assert bands.expected_band_count(12) == 206


def test_the_month_count_is_recovered_from_the_band_count():
    assert bands.infer_timesteps(206) == 12
    assert bands.infer_timesteps(bands.expected_band_count(24)) == 24


def test_a_band_count_that_does_not_divide_is_refused():
    with pytest.raises(ValueError):
        bands.infer_timesteps(205)


def test_a_cube_shorter_than_one_month_is_refused():
    with pytest.raises(ValueError):
        bands.infer_timesteps(10)
    with pytest.raises(ValueError):
        bands.expected_band_count(0)


def test_band_positions_are_looked_up_by_name():
    assert bands.DYNAMIC_BANDS[bands.band_index("B8")] == "B8"
    assert bands.STATIC_BANDS[bands.static_index("slope")] == "slope"


def test_an_unknown_band_raises_a_key_error():
    with pytest.raises(KeyError):
        bands.band_index("B99")
    with pytest.raises(KeyError):
        bands.static_index("aspect")


def test_the_signal_groups_only_name_bands_that_exist():
    for group in bands.SIGNAL_GROUPS.values():
        assert all(b in bands.RAW_BANDS for b in group)
