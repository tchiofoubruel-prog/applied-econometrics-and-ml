"""Crop mapping across nine African countries, validated the way the call asks.

    python scripts/04_africa_benchmark.py --arrays /path/to/features/arrays

Three questions are answered in turn. Does the model work when neighbouring
points are kept out of training, rather than scattered across the folds? Does
it survive being moved to a country it never saw? And can it say when it does
not know?

The data is CropHarvest (Tseng et al. 2021, CC BY-SA 4.0), which is not
redistributed with this repository.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score

from eo_resilience import cropharvest, uncertainty, validation

SEED = 0


def build(arrays, cache):
    if cache is not None and cache.exists():
        z = np.load(cache, allow_pickle=True)
        return (z["X"], list(z["names"]), z["y"], z["lat"], z["lon"], z["country"])
    data = cropharvest.load_directory(arrays)
    X, names = cropharvest.feature_table(data["X"])
    if cache is not None:
        np.savez_compressed(cache, X=X, names=np.array(names), y=data["y"],
                            lat=data["lat"], lon=data["lon"], country=data["country"])
    return X, names, data["y"], data["lat"], data["lon"], data["country"]


def forest(seed=SEED):
    return RandomForestClassifier(
        n_estimators=400, min_samples_leaf=2, random_state=seed, n_jobs=-1
    )


def fit_predict_proba(X_train, y_train, X_test, seed=SEED):
    model = forest(seed)
    model.fit(X_train, y_train)
    return model.predict_proba(X_test), model


def evaluate(y_true, proba):
    pred = proba[:, 1] >= 0.5
    out = {"accuracy": float((pred == (y_true == 1)).mean())}
    out["auc"] = (
        float(roc_auc_score(y_true, proba[:, 1]))
        if len(np.unique(y_true)) > 1 else float("nan")
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arrays", type=pathlib.Path, required=True)
    parser.add_argument("--cache", type=pathlib.Path, default=None)
    parser.add_argument("--block-degrees", type=float, default=0.5)
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("figures/africa_results.json"))
    args = parser.parse_args()

    t0 = time.time()
    X, names, y, lat, lon, country = build(args.arrays, args.cache)
    keep = np.isfinite(X).all(axis=1)
    X, y, lat, lon, country = X[keep], y[keep], lat[keep], lon[keep], country[keep]
    print(f"{len(y)} labelled points, {X.shape[1]} season features, "
          f"{len(np.unique(country))} countries, loaded in {time.time() - t0:.0f}s")
    for c in sorted(set(country)):
        m = country == c
        print(f"  {c:<10} {m.sum():>5}   cropped {y[m].mean():.2f}")

    results = {"n": int(len(y)), "n_features": int(X.shape[1]),
               "countries": {c: int((country == c).sum()) for c in sorted(set(country))}}

    # 1. Random folds against spatial blocks, on the same data.
    print("\n1. what the split does to the score")
    rng = np.random.default_rng(SEED)
    order = rng.permutation(len(y))
    random_scores = []
    for k in range(5):
        test = order[k::5]
        train = np.setdiff1d(order, test)
        proba, _ = fit_predict_proba(X[train], y[train], X[test])
        random_scores.append(evaluate(y[test], proba))
    labels, _ = validation.spatial_blocks(lon, lat, args.block_degrees)
    block_scores = []
    for train, test in validation.block_folds(labels, n_splits=5, seed=SEED):
        proba, _ = fit_predict_proba(X[train], y[train], X[test])
        block_scores.append(evaluate(y[test], proba))
    for name, scores in (("random 5-fold", random_scores),
                         (f"spatial blocks of {args.block_degrees} deg", block_scores)):
        auc = np.mean([s["auc"] for s in scores])
        acc = np.mean([s["accuracy"] for s in scores])
        print(f"   {name:<28} AUC {auc:.3f}   accuracy {acc:.3f}")
        results[name] = {"auc": float(auc), "accuracy": float(acc)}
    results["n_blocks"] = int(np.unique(labels).size)

    # 2. Transferability across a border.
    print("\n2. leave one country out")
    transfer = {}
    for train, test in validation.leave_one_group_out(country):
        held = country[test][0]
        if len(np.unique(y[test])) < 2 or test.size < 100:
            print(f"   {held:<10} skipped, {test.size} points, "
                  f"{len(np.unique(y[test]))} class(es) present")
            continue
        proba, _ = fit_predict_proba(X[train], y[train], X[test])
        scores = evaluate(y[test], proba)
        transfer[held] = scores
        print(f"   {held:<10} n {test.size:>5}   AUC {scores['auc']:.3f}   "
              f"accuracy {scores['accuracy']:.3f}")
    if transfer:
        mean_auc = np.mean([s["auc"] for s in transfer.values()])
        print(f"   {'mean':<10} {'':>5}   AUC {mean_auc:.3f}")
        results["leave_one_country_out"] = transfer
        results["transfer_mean_auc"] = float(mean_auc)

    # 3. Saying when the model does not know.
    print(f"\n3. conformal prediction sets at {1 - args.alpha:.0%} coverage")
    for split_name, splits in (
        ("spatial blocks", list(validation.block_folds(labels, n_splits=5, seed=SEED))),
        ("across borders", list(validation.leave_one_group_out(country))),
    ):
        coverages, sizes, singleton_acc = [], [], []
        for train, test in splits:
            if test.size < 100 or len(np.unique(y[test])) < 2:
                continue
            shuffled = np.random.default_rng(SEED).permutation(train)
            cut = len(shuffled) // 2
            fit_idx, cal_idx = shuffled[:cut], shuffled[cut:]
            model = forest()
            model.fit(X[fit_idx], y[fit_idx])
            sets = uncertainty.conformal_label_sets(
                y[cal_idx], model.predict_proba(X[cal_idx]),
                model.predict_proba(X[test]), alpha=args.alpha
            )
            coverages.append(uncertainty.set_coverage(y[test], sets))
            sizes.append(uncertainty.mean_set_size(sets))
            single = sets.sum(axis=1) == 1
            if single.any():
                picked = sets[single].argmax(axis=1)
                singleton_acc.append(float((picked == y[test][single]).mean()))
        print(f"   {split_name:<16} coverage {np.mean(coverages):.3f}   "
              f"mean set size {np.mean(sizes):.2f}   "
              f"accuracy where the model commits {np.mean(singleton_acc):.3f}")
        results[f"conformal_{split_name.replace(' ', '_')}"] = {
            "coverage": float(np.mean(coverages)),
            "mean_set_size": float(np.mean(sizes)),
            "accuracy_on_singletons": float(np.mean(singleton_acc)),
        }

    # 4. Which source of information carries the signal.
    print("\n4. permutation importance grouped by source")
    train, test = next(validation.block_folds(labels, n_splits=5, seed=SEED))
    proba, model = fit_predict_proba(X[train], y[train], X[test])
    base = evaluate(y[test], proba)["auc"]
    groups = {"sentinel1": [], "sentinel2": [], "era5": [], "srtm": []}
    for j, name in enumerate(names):
        root = name.split("_")[0]
        if root in ("VV", "VH"):
            groups["sentinel1"].append(j)
        elif root in ("ndvi", "ndwi", "ndmi"):
            groups["sentinel2"].append(j)
        elif root in ("temperature", "total"):
            groups["era5"].append(j)
        elif name in ("elevation", "slope"):
            groups["srtm"].append(j)
    rng = np.random.default_rng(SEED)
    importance = {}
    for source, cols in groups.items():
        if not cols:
            continue
        drops = []
        for _ in range(5):
            Xp = X[test].copy()
            Xp[:, cols] = Xp[rng.permutation(len(test))][:, cols]
            drops.append(base - evaluate(y[test], model.predict_proba(Xp))["auc"])
        importance[source] = float(np.mean(drops))
        print(f"   {source:<12} AUC drop {importance[source]:+.4f}")
    results["grouped_permutation_importance"] = importance
    results["baseline_auc_for_importance"] = float(base)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(results, indent=1))
    print(f"\nresults written to {args.out}  ({time.time() - t0:.0f}s total)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
