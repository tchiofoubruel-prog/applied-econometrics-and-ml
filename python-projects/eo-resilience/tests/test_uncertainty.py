import numpy as np
import pytest

from eo_resilience import uncertainty


def test_coverage_reaches_the_target_on_exchangeable_data():
    rng = np.random.default_rng(0)
    cal_true = rng.normal(size=2000)
    cal_pred = np.zeros_like(cal_true)
    test_true = rng.normal(size=2000)
    test_pred = np.zeros_like(test_true)
    lo, hi = uncertainty.split_conformal_intervals(
        cal_true, cal_pred, test_pred, alpha=0.1
    )
    assert uncertainty.empirical_coverage(test_true, lo, hi) > 0.88


def test_a_tighter_alpha_widens_the_interval():
    rng = np.random.default_rng(1)
    cal_true = rng.normal(size=500)
    cal_pred = np.zeros_like(cal_true)
    narrow = uncertainty.conformal_quantile(cal_true - cal_pred, alpha=0.2)
    wide = uncertainty.conformal_quantile(cal_true - cal_pred, alpha=0.05)
    assert wide > narrow


def test_a_calibration_set_too_small_for_the_target_gives_no_finite_width():
    assert uncertainty.conformal_quantile(np.zeros(5), alpha=0.01) == float("inf")


def test_the_width_is_the_absolute_residual_quantile():
    residuals = np.array([-3.0, 1.0, 2.0, -0.5, 0.25])
    width = uncertainty.conformal_quantile(residuals, alpha=0.5)
    assert width in set(np.abs(residuals).tolist())


def test_an_empty_calibration_set_is_refused():
    with pytest.raises(ValueError):
        uncertainty.conformal_quantile(np.array([np.nan, np.nan]))


def test_alpha_outside_the_unit_interval_is_refused():
    with pytest.raises(ValueError):
        uncertainty.conformal_quantile(np.zeros(10), alpha=1.5)


def test_coverage_and_width_report_the_expected_numbers():
    y = np.array([0.0, 5.0, 1.0])
    lo = np.array([-1.0, -1.0, -1.0])
    hi = np.array([1.0, 1.0, 1.0])
    assert uncertainty.empirical_coverage(y, lo, hi) == pytest.approx(2 / 3)
    assert uncertainty.mean_interval_width(lo, hi) == pytest.approx(2.0)


def test_nan_observations_are_left_out_of_the_coverage():
    y = np.array([0.0, np.nan])
    lo, hi = np.array([-1.0, -1.0]), np.array([1.0, 1.0])
    assert uncertainty.empirical_coverage(y, lo, hi) == pytest.approx(1.0)


def test_mismatched_shapes_are_refused():
    with pytest.raises(ValueError):
        uncertainty.empirical_coverage(np.zeros(3), np.zeros(2), np.zeros(3))


def test_label_sets_cover_the_true_class_at_the_target_rate():
    rng = np.random.default_rng(4)
    n = 3000
    y_cal = rng.integers(0, 2, size=n)
    # A model that is right most of the time but not always.
    p_cal = np.zeros((n, 2))
    confident = rng.random(n) < 0.8
    p_cal[np.arange(n), y_cal] = np.where(confident, 0.9, 0.4)
    p_cal[np.arange(n), 1 - y_cal] = 1 - p_cal[np.arange(n), y_cal]
    y_test = rng.integers(0, 2, size=n)
    p_test = np.zeros((n, 2))
    confident_t = rng.random(n) < 0.8
    p_test[np.arange(n), y_test] = np.where(confident_t, 0.9, 0.4)
    p_test[np.arange(n), 1 - y_test] = 1 - p_test[np.arange(n), y_test]
    sets = uncertainty.conformal_label_sets(y_cal, p_cal, p_test, alpha=0.1)
    assert uncertainty.set_coverage(y_test, sets) > 0.88


def test_a_confident_model_returns_singletons_and_a_vague_one_abstains():
    y_cal = np.array([0, 1, 0, 1] * 50)
    sharp = np.tile([[0.99, 0.01], [0.01, 0.99]], (100, 1))
    sets = uncertainty.conformal_label_sets(y_cal, sharp, np.array([[0.99, 0.01]]))
    assert uncertainty.mean_set_size(sets) == pytest.approx(1.0)
    vague = np.tile([[0.5, 0.5]], (200, 1))
    wide = uncertainty.conformal_label_sets(y_cal, vague, np.array([[0.5, 0.5]]))
    assert uncertainty.mean_set_size(wide) == pytest.approx(2.0)


def test_mismatched_class_axes_are_refused():
    with pytest.raises(ValueError):
        uncertainty.conformal_label_sets(
            np.array([0, 1]), np.zeros((2, 2)), np.zeros((2, 3))
        )
