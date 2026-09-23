import numpy as np
import pytest

from eo_resilience import bands, cube


def make_array(n_time=3, rows=4, cols=5, seed=0):
    rng = np.random.default_rng(seed)
    return rng.uniform(0.05, 0.6, size=(bands.expected_band_count(n_time), rows, cols))


def test_a_raw_stack_splits_into_the_two_blocks():
    c = cube.from_array(make_array(n_time=3))
    assert c.n_timesteps == 3
    assert c.dynamic.shape == (3, len(bands.DYNAMIC_BANDS), 4, 5)
    assert c.static.shape == (len(bands.STATIC_BANDS), 4, 5)


def test_the_static_block_is_the_tail_of_the_stack():
    arr = make_array(n_time=2)
    c = cube.from_array(arr)
    assert np.array_equal(c.static, arr[-len(bands.STATIC_BANDS):])


def test_a_band_is_retrieved_by_name_in_the_documented_order():
    arr = make_array(n_time=2)
    c = cube.from_array(arr)
    position = bands.band_index("B4")
    assert np.array_equal(c.band("B4")[0], arr[position])


def test_terrain_bands_are_retrieved_by_name():
    c = cube.from_array(make_array())
    assert c.terrain("elevation").shape == c.shape


def test_ndvi_uses_b8_and_b4():
    arr = np.zeros((bands.expected_band_count(1), 1, 1))
    arr[bands.band_index("B8")] = 0.4
    arr[bands.band_index("B4")] = 0.1
    c = cube.from_array(arr)
    assert c.ndvi()[0, 0, 0] == pytest.approx(0.6)


def test_the_four_indices_all_return_the_shape_of_the_series():
    c = cube.from_array(make_array(n_time=3))
    for grid in (c.ndvi(), c.ndwi(), c.ndmi(), c.nbr()):
        assert grid.shape == (3, 4, 5)


def test_a_stack_with_the_wrong_band_count_is_refused():
    with pytest.raises(ValueError):
        cube.from_array(np.zeros((205, 2, 2)))


def test_mismatched_grids_are_refused():
    dynamic = np.zeros((2, len(bands.DYNAMIC_BANDS), 4, 4))
    static = np.zeros((len(bands.STATIC_BANDS), 3, 3))
    with pytest.raises(ValueError):
        cube.Cube(dynamic, static)


def test_a_dynamic_block_with_too_few_bands_is_refused():
    with pytest.raises(ValueError):
        cube.Cube(np.zeros((2, 5, 4, 4)), np.zeros((len(bands.STATIC_BANDS), 4, 4)))


def test_the_repr_states_the_shape():
    text = repr(cube.from_array(make_array(n_time=3)))
    assert "3 months" in text and "4x5" in text
