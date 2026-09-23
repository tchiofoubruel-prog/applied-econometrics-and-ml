import numpy as np
import pytest

from eo_resilience import compositing


def test_median_ignores_the_masked_observations():
    stack = np.array([[[1.0]], [[np.nan]], [[3.0]]])
    assert compositing.median_composite(stack)[0, 0] == pytest.approx(2.0)


def test_a_pixel_with_too_few_observations_comes_back_empty():
    stack = np.array([[[1.0]], [[np.nan]], [[np.nan]]])
    assert np.isnan(compositing.median_composite(stack, min_obs=2)[0, 0])
    assert compositing.median_composite(stack, min_obs=1)[0, 0] == 1.0


def test_a_fully_masked_pixel_is_nan_and_raises_no_warning(recwarn):
    stack = np.full((3, 2, 2), np.nan)
    out = compositing.median_composite(stack)
    assert np.isnan(out).all()
    assert not [w for w in recwarn if issubclass(w.category, RuntimeWarning)]


def test_observation_count_matches_the_mask():
    stack = np.array([[[1.0, np.nan]], [[2.0, 5.0]]])
    assert compositing.observation_count(stack).tolist() == [[2, 1]]


def test_seasonal_composites_split_on_the_calendar():
    stack = np.array([[[1.0]], [[3.0]], [[10.0]]])
    out = compositing.seasonal_composites(
        stack, months=[1, 2, 7], seasons={"rains": (1, 2), "dry": (7,)}
    )
    assert out["rains"][0, 0] == pytest.approx(2.0)
    assert out["dry"][0, 0] == pytest.approx(10.0)


def test_a_season_with_no_acquisition_still_yields_a_key():
    stack = np.array([[[1.0]]])
    out = compositing.seasonal_composites(
        stack, months=[1], seasons={"rains": (1,), "dry": (7,)}
    )
    assert set(out) == {"rains", "dry"}
    assert np.isnan(out["dry"]).all()


def test_the_month_list_must_match_the_time_axis():
    with pytest.raises(ValueError):
        compositing.seasonal_composites(
            np.zeros((2, 1, 1)), months=[1], seasons={"a": (1,)}
        )


def test_a_two_dimensional_input_is_refused():
    with pytest.raises(ValueError):
        compositing.median_composite(np.zeros((2, 2)))
