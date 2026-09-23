"""Spatial validation, so that accuracy is not read off neighbouring pixels.

Random k-fold splits put pixels from the same field, and often from the same
village, on both sides of the split, which flatters any model built on
spatially autocorrelated predictors. The splitters here keep whole blocks, or
whole regions, on one side at a time.
"""

from __future__ import annotations

import numpy as np


def spatial_blocks(xs, ys, block_size):
    """Label each point with the square block of side `block_size` holding it.

    Labels are integers assigned in a stable order, so two runs on the same
    coordinates give the same folds.
    """
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    xs = np.asarray(xs, dtype="float64")
    ys = np.asarray(ys, dtype="float64")
    if xs.shape != ys.shape:
        raise ValueError("xs and ys must have the same shape")
    ix = np.floor(xs / block_size).astype("int64")
    iy = np.floor(ys / block_size).astype("int64")
    keys = np.stack([ix, iy], axis=1)
    uniq, labels = np.unique(keys, axis=0, return_inverse=True)
    return labels.astype("int64"), uniq


def block_folds(labels, n_splits=5, seed=0):
    """Group blocks into folds, yielding (train_index, test_index).

    Blocks are shuffled once with `seed` and dealt round robin, so folds hold
    a comparable number of blocks even when block sizes differ.
    """
    labels = np.asarray(labels)
    blocks = np.unique(labels)
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    if blocks.size < n_splits:
        raise ValueError(
            f"{blocks.size} blocks cannot be split into {n_splits} folds"
        )
    rng = np.random.default_rng(seed)
    order = rng.permutation(blocks)
    assignment = {int(b): i % n_splits for i, b in enumerate(order)}
    fold_of_point = np.array([assignment[int(b)] for b in labels])
    for k in range(n_splits):
        test = np.flatnonzero(fold_of_point == k)
        train = np.flatnonzero(fold_of_point != k)
        yield train, test


def leave_one_group_out(groups):
    """Yield (train_index, test_index) holding out one group at a time.

    Used for the cross-border question: with countries as groups, each fold
    trains on every country but one and tests on the country left out.
    """
    groups = np.asarray(groups)
    for g in np.unique(groups):
        test = np.flatnonzero(groups == g)
        train = np.flatnonzero(groups != g)
        if train.size == 0:
            raise ValueError("leaving out this group empties the training set")
        yield train, test


def folds_are_disjoint(splits, n_samples):
    """Check that no index appears in both sides of any split."""
    for train, test in splits:
        if np.intersect1d(train, test).size:
            return False
        if np.union1d(train, test).size > n_samples:
            return False
    return True
