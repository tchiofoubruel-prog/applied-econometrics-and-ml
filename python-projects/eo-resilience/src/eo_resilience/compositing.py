"""Temporal composites over a stack of masked scenes."""

from __future__ import annotations

import warnings

import numpy as np


def _as_stack(stack):
    stack = np.asarray(stack, dtype="float64")
    if stack.ndim != 3:
        raise ValueError("expected a 3-D (time, row, col) stack")
    return stack


def median_composite(stack, min_obs=1):
    """Median over the time axis, ignoring NaN.

    Parameters
    ----------
    stack : array_like
        Shape (time, row, col), already masked, with NaN on discarded pixels.
    min_obs : int
        Pixels with fewer than `min_obs` valid observations come back as NaN
        instead of being composited from too little evidence.
    """
    stack = _as_stack(stack)
    if min_obs < 1:
        raise ValueError("min_obs must be at least 1")
    counts = np.sum(np.isfinite(stack), axis=0)
    # A pixel masked in every scene is a legitimate outcome here, not an
    # anomaly, so the all-NaN warning numpy raises for it is silenced rather
    # than left to clutter the log of a long run.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        out = np.nanmedian(np.where(np.isfinite(stack), stack, np.nan), axis=0)
    return np.where(counts >= min_obs, out, np.nan)


def observation_count(stack):
    """Number of valid observations per pixel."""
    return np.sum(np.isfinite(_as_stack(stack)), axis=0).astype("int32")


def seasonal_composites(stack, months, seasons, min_obs=1):
    """One median composite per season.

    Parameters
    ----------
    stack : array_like
        Shape (time, row, col).
    months : sequence of int
        Calendar month of each slice, same length as the time axis.
    seasons : mapping
        Season name to the months it covers, for example
        ``{"growing": (12, 1, 2, 3), "dry": (6, 7, 8)}``.

    Returns
    -------
    dict
        Season name to composite. A season with no matching slice yields an
        all-NaN array of the spatial shape, so the caller always gets the same
        set of keys whatever the acquisition calendar happens to contain.
    """
    stack = _as_stack(stack)
    months = np.asarray(list(months), dtype=int)
    if months.shape[0] != stack.shape[0]:
        raise ValueError("one month is needed for each slice of the stack")
    out = {}
    for name, wanted in seasons.items():
        keep = np.isin(months, np.asarray(list(wanted), dtype=int))
        if not keep.any():
            out[name] = np.full(stack.shape[1:], np.nan, dtype="float64")
            continue
        out[name] = median_composite(stack[keep], min_obs=min_obs)
    return out
