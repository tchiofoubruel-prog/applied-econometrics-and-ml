"""Fit the model, validate it spatially, and attach prediction intervals.

    python scripts/03_model.py --features data/features.csv --target sharp_score

Three things are reported, in the order the call asks for them: accuracy under
a spatial block split rather than a random one, transferability under a
leave-one-country-out split, and the empirical coverage of conformal
prediction intervals on the held-out points.
"""

from __future__ import annotations

import argparse
import csv
import pathlib

import numpy as np

from eo_resilience import uncertainty, validation


def read_table(path):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"{path} holds no row")
    return rows


def as_matrix(rows, feature_names):
    X = np.array(
        [[float(r[name]) if r[name] not in ("", "nan") else np.nan
          for name in feature_names] for r in rows],
        dtype="float64",
    )
    return X


def fit_predict(X_train, y_train, X_test, seed=0):
    """Random forest if scikit-learn is installed, ridge otherwise.

    The fallback keeps the script runnable in a bare environment, and the
    validation design is what matters here rather than the learner.
    """
    try:
        from sklearn.ensemble import RandomForestRegressor
    except ImportError:
        Xtr = np.column_stack([np.ones(len(X_train)), X_train])
        Xte = np.column_stack([np.ones(len(X_test)), X_test])
        ridge = np.linalg.solve(
            Xtr.T @ Xtr + 1e-3 * np.eye(Xtr.shape[1]), Xtr.T @ y_train
        )
        return Xte @ ridge
    model = RandomForestRegressor(n_estimators=300, random_state=seed, n_jobs=-1)
    model.fit(X_train, y_train)
    return model.predict(X_test)


def r2(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - y_true.mean()) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=pathlib.Path, required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--block-degrees", type=float, default=0.25)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = read_table(args.features)
    reserved = {"lon", "lat", "region", "country", args.target}
    feature_names = sorted(k for k in rows[0] if k not in reserved)
    if not feature_names:
        raise SystemExit("no feature column left once the reserved names are removed")

    X = as_matrix(rows, feature_names)
    y = np.array([float(r[args.target]) for r in rows])
    lon = np.array([float(r["lon"]) for r in rows])
    lat = np.array([float(r["lat"]) for r in rows])

    # A feature that is missing everywhere, typically a season with too few
    # cloud-free scenes to composite, would otherwise empty the whole table.
    usable_col = np.isfinite(X).any(axis=0)
    if not usable_col.all():
        dropped = [n for n, u in zip(feature_names, usable_col) if not u]
        print(f"dropping {len(dropped)} feature(s) missing at every point: "
              f"{', '.join(dropped)}")
        X = X[:, usable_col]
        feature_names = [n for n, u in zip(feature_names, usable_col) if u]
    if not feature_names:
        raise SystemExit("every feature is missing at every point")

    keep = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X, y, lon, lat = X[keep], y[keep], lon[keep], lat[keep]
    rows = [r for r, k in zip(rows, keep) if k]
    print(f"{keep.sum()} points with complete features, {len(feature_names)} features")
    if keep.sum() < 50:
        raise SystemExit("too few complete points to validate anything")

    labels, _ = validation.spatial_blocks(lon, lat, args.block_degrees)
    print(f"{np.unique(labels).size} spatial blocks of {args.block_degrees} degrees")

    scores, coverages, widths = [], [], []
    for train, test in validation.block_folds(labels, n_splits=5, seed=args.seed):
        # Half the training fold calibrates the intervals, so the model never
        # sees the residuals used to set their width.
        rng = np.random.default_rng(args.seed)
        shuffled = rng.permutation(train)
        cut = len(shuffled) // 2
        fit_idx, cal_idx = shuffled[:cut], shuffled[cut:]
        pred_cal = fit_predict(X[fit_idx], y[fit_idx], X[cal_idx], seed=args.seed)
        pred_test = fit_predict(X[fit_idx], y[fit_idx], X[test], seed=args.seed)
        lo, hi = uncertainty.split_conformal_intervals(
            y[cal_idx], pred_cal, pred_test, alpha=args.alpha
        )
        scores.append(r2(y[test], pred_test))
        coverages.append(uncertainty.empirical_coverage(y[test], lo, hi))
        widths.append(uncertainty.mean_interval_width(lo, hi))

    print(f"spatial block CV   R2 = {np.mean(scores):.3f} "
          f"(sd {np.std(scores):.3f} over 5 folds)")
    print(f"interval coverage     = {np.mean(coverages):.3f} "
          f"for a target of {1 - args.alpha:.2f}")
    print(f"mean interval width   = {np.mean(widths):.3f}")

    if "country" in rows[0]:
        groups = np.array([r["country"] for r in rows])
        if np.unique(groups).size > 1:
            print("leave-one-country-out:")
            for train, test in validation.leave_one_group_out(groups):
                pred = fit_predict(X[train], y[train], X[test], seed=args.seed)
                print(f"  held out {groups[test][0]:<4} "
                      f"n = {test.size:<5} R2 = {r2(y[test], pred):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
