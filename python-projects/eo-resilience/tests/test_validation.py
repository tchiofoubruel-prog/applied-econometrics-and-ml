import numpy as np
import pytest

from eo_resilience import validation


def test_points_in_the_same_square_share_a_block():
    labels, _ = validation.spatial_blocks([0.1, 0.9, 2.5], [0.1, 0.9, 2.5], 1.0)
    assert labels[0] == labels[1]
    assert labels[2] != labels[0]


def test_block_labels_are_stable_across_runs():
    xs, ys = np.linspace(0, 5, 40), np.linspace(0, 5, 40)
    first, _ = validation.spatial_blocks(xs, ys, 1.0)
    second, _ = validation.spatial_blocks(xs, ys, 1.0)
    assert np.array_equal(first, second)


def test_block_folds_never_put_a_block_on_both_sides():
    rng = np.random.default_rng(1)
    xs, ys = rng.uniform(0, 10, 200), rng.uniform(0, 10, 200)
    labels, _ = validation.spatial_blocks(xs, ys, 1.0)
    for train, test in validation.block_folds(labels, n_splits=5, seed=0):
        assert not set(labels[train]) & set(labels[test])


def test_block_folds_cover_every_point_exactly_once():
    labels = np.repeat(np.arange(10), 5)
    seen = np.concatenate(
        [test for _, test in validation.block_folds(labels, n_splits=5)]
    )
    assert np.array_equal(np.sort(seen), np.arange(labels.size))


def test_block_folds_refuse_more_folds_than_blocks():
    with pytest.raises(ValueError):
        list(validation.block_folds(np.array([0, 0, 1]), n_splits=5))


def test_leave_one_group_out_holds_back_one_country_at_a_time():
    groups = np.array(["MW", "MW", "ZM", "ZM", "MZ"])
    folds = list(validation.leave_one_group_out(groups))
    assert len(folds) == 3
    for train, test in folds:
        assert len(set(groups[test])) == 1
        assert set(groups[test]).isdisjoint(set(groups[train]))


def test_the_helper_catches_a_leaking_split():
    good = [(np.array([0, 1]), np.array([2, 3]))]
    bad = [(np.array([0, 1, 2]), np.array([2, 3]))]
    assert validation.folds_are_disjoint(good, 4)
    assert not validation.folds_are_disjoint(bad, 4)


def test_a_random_split_leaks_where_the_block_split_does_not():
    # Neighbouring points share a block, so a random split would place some of
    # them on both sides; the block splitter cannot.
    rng = np.random.default_rng(2)
    xs = np.repeat(np.arange(20), 10) + rng.uniform(0, 0.1, 200)
    ys = np.zeros(200)
    labels, _ = validation.spatial_blocks(xs, ys, 1.0)
    random_test = rng.choice(200, size=40, replace=False)
    random_train = np.setdiff1d(np.arange(200), random_test)
    assert set(labels[random_train]) & set(labels[random_test])
    for train, test in validation.block_folds(labels, n_splits=4, seed=3):
        assert not set(labels[train]) & set(labels[test])
