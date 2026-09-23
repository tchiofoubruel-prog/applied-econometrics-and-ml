"""The acquisition layer is tested only where it does not touch the network."""

import datetime as dt

import pytest

from eo_resilience import fetch


def test_the_chirps_url_template_matches_the_published_layout():
    urls = fetch.chirps_daily_urls("2024-01-30", "2024-02-01")
    assert len(urls) == 3
    assert urls[0].endswith("2024/chirps-v2.0.2024.01.30.tif")
    assert urls[-1].endswith("2024/chirps-v2.0.2024.02.01.tif")


def test_the_range_is_inclusive_on_a_single_day():
    assert len(fetch.chirps_daily_urls(dt.date(2024, 5, 1), dt.date(2024, 5, 1))) == 1


def test_a_reversed_range_is_refused():
    with pytest.raises(ValueError):
        fetch.chirps_daily_urls("2024-02-01", "2024-01-01")


def test_every_band_the_indices_need_is_declared():
    assert {"green", "red", "nir", "swir16", "swir22", "scl"} <= set(fetch.BANDS)


def test_download_skips_a_file_that_is_already_there(tmp_path):
    dest = tmp_path / "already.tif"
    dest.write_bytes(b"x")
    # No network call happens, since the destination is non-empty.
    assert fetch.download("https://example.invalid/x.tif", dest) == dest
    assert dest.read_bytes() == b"x"
