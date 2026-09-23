"""Prediction intervals with split conformal prediction.

The call asks for confidence bounds on predictions rather than a single
accuracy figure. Split conformal gives finite-sample marginal coverage under
exchangeability, without assuming anything about the model that produced the
point predictions.
"""

from __future__ import annotations

import numpy as np


def conformal_quantile(residuals, alpha=0.1):
    """Return the conformal width for a target coverage of 1 - alpha.

    The quantile level is ceil((n + 1) * (1 - alpha)) / n, which is what gives
    the finite-sample guarantee; with small calibration sets it can exceed 1,
    in which case no finite width is justified and the function says so by
    returning infinity.
    """
    residuals = np.asarray(residuals, dtype="float64")
    residuals = residuals[np.isfinite(residuals)]
    n = residuals.size
    if n == 0:
        raise ValueError("no finite residual to calibrate on")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between 0 and 1")
    level = np.ceil((n + 1) * (1 - alpha)) / n
    if level > 1:
        return float("inf")
    return float(np.quantile(np.abs(residuals), level, method="higher"))


def split_conformal_intervals(cal_true, cal_pred, test_pred, alpha=0.1):
    """Symmetric prediction intervals around `test_pred`.

    `cal_true` and `cal_pred` come from a calibration set the model never saw.
    Returns (lower, upper).
    """
    cal_true = np.asarray(cal_true, dtype="float64")
    cal_pred = np.asarray(cal_pred, dtype="float64")
    if cal_true.shape != cal_pred.shape:
        raise ValueError("calibration arrays must have the same shape")
    width = conformal_quantile(cal_true - cal_pred, alpha=alpha)
    test_pred = np.asarray(test_pred, dtype="float64")
    return test_pred - width, test_pred + width


def empirical_coverage(y_true, lower, upper):
    """Share of observations falling inside their interval."""
    y_true = np.asarray(y_true, dtype="float64")
    lower = np.asarray(lower, dtype="float64")
    upper = np.asarray(upper, dtype="float64")
    if not (y_true.shape == lower.shape == upper.shape):
        raise ValueError("all three arrays must have the same shape")
    inside = (y_true >= lower) & (y_true <= upper)
    finite = np.isfinite(y_true) & np.isfinite(lower) & np.isfinite(upper)
    if not finite.any():
        return float("nan")
    return float(inside[finite].mean())


def mean_interval_width(lower, upper):
    """Average width, the price paid for the coverage above."""
    lower = np.asarray(lower, dtype="float64")
    upper = np.asarray(upper, dtype="float64")
    width = upper - lower
    finite = np.isfinite(width)
    if not finite.any():
        return float("nan")
    return float(width[finite].mean())


def conformal_label_sets(cal_true, cal_proba, test_proba, alpha=0.1):
    """Prediction sets for a classifier, with marginal coverage 1 - alpha.

    The nonconformity score is one minus the probability the model gave to the
    observed class. A test point receives every label whose score falls below
    the calibrated threshold, so the set is a singleton where the model is
    confident and holds both labels where it is not. An empty set means no
    label was plausible enough, which is worth surfacing rather than hiding.

    Parameters
    ----------
    cal_true : array_like of int
        Observed classes on the calibration set.
    cal_proba, test_proba : array_like
        Predicted probabilities, shape (n, n_classes).

    Returns
    -------
    ndarray of bool
        Shape (n_test, n_classes), True where the label is in the set.
    """
    cal_true = np.asarray(cal_true, dtype="int64")
    cal_proba = np.asarray(cal_proba, dtype="float64")
    test_proba = np.asarray(test_proba, dtype="float64")
    if cal_proba.ndim != 2 or test_proba.ndim != 2:
        raise ValueError("probabilities must have shape (n, n_classes)")
    if cal_proba.shape[1] != test_proba.shape[1]:
        raise ValueError("calibration and test must share the class axis")
    if cal_true.shape[0] != cal_proba.shape[0]:
        raise ValueError("one observed class is needed per calibration row")
    scores = 1.0 - cal_proba[np.arange(cal_true.size), cal_true]
    threshold = conformal_quantile(scores, alpha=alpha)
    if not np.isfinite(threshold):
        return np.ones_like(test_proba, dtype=bool)
    return (1.0 - test_proba) <= threshold


def set_coverage(y_true, label_sets):
    """Share of points whose observed class is inside the prediction set."""
    y_true = np.asarray(y_true, dtype="int64")
    label_sets = np.asarray(label_sets, dtype=bool)
    if y_true.shape[0] != label_sets.shape[0]:
        raise ValueError("one row of the set matrix is needed per observation")
    return float(label_sets[np.arange(y_true.size), y_true].mean())


def mean_set_size(label_sets):
    """Average number of labels retained, the price of the coverage above.

    A value near one means the model commits to a single label almost
    everywhere; a value near the number of classes means it abstains.
    """
    return float(np.asarray(label_sets, dtype=bool).sum(axis=1).mean())
