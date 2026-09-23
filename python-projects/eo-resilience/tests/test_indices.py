import numpy as np
import pytest

from eo_resilience import indices


def test_ndvi_matches_the_hand_computed_value():
    got = indices.ndvi(np.array([[0.4]]), np.array([[0.1]]))
    assert got[0, 0] == pytest.approx((0.4 - 0.1) / (0.4 + 0.1))


def test_ndvi_stays_inside_minus_one_and_one():
    rng = np.random.default_rng(0)
    nir = rng.uniform(0.01, 1.0, size=(20, 20))
    red = rng.uniform(0.01, 1.0, size=(20, 20))
    out = indices.ndvi(nir, red)
    assert np.nanmin(out) >= -1.0 and np.nanmax(out) <= 1.0


def test_a_vanishing_denominator_gives_nan_rather_than_a_huge_value():
    out = indices.normalised_difference(np.array([[0.0]]), np.array([[0.0]]))
    assert np.isnan(out[0, 0])


def test_nan_inputs_propagate():
    out = indices.ndvi(np.array([[np.nan]]), np.array([[0.1]]))
    assert np.isnan(out[0, 0])


def test_ndwi_and_ndmi_use_the_bands_in_the_documented_order():
    green, nir, swir1 = np.array([[0.3]]), np.array([[0.1]]), np.array([[0.2]])
    assert indices.ndwi(green, nir)[0, 0] == pytest.approx(0.5)
    assert indices.ndmi(nir, swir1)[0, 0] == pytest.approx(-1 / 3)


def test_mismatched_shapes_are_refused():
    with pytest.raises(ValueError):
        indices.normalised_difference(np.zeros((2, 2)), np.zeros((3, 3)))


def test_local_std_is_zero_on_a_flat_field_and_positive_on_a_ramp():
    flat = np.ones((5, 5))
    assert indices.local_std(flat)[2, 2] == pytest.approx(0.0)
    ramp = np.tile(np.arange(5, dtype="float64"), (5, 1))
    assert indices.local_std(ramp)[2, 2] > 0.0


def test_local_std_leaves_the_border_and_masked_windows_empty():
    arr = np.ones((5, 5))
    arr[2, 2] = np.nan
    out = indices.local_std(arr)
    assert np.isnan(out[0, 0])
    assert np.isnan(out[2, 2])


def test_local_std_refuses_an_even_window():
    with pytest.raises(ValueError):
        indices.local_std(np.ones((5, 5)), window=4)
