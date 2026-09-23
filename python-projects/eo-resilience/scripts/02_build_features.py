"""Turn the downloaded scenes into one feature table at the survey points.

    python scripts/02_build_features.py --raw data/raw --points points.csv \
        --out data/features.csv

The points file needs the columns `lon`, `lat` and, for the transferability
test, `region` and `country`.
"""

from __future__ import annotations

import argparse
import csv
import json
import pathlib

import numpy as np
import rasterio

from eo_resilience import compositing, extraction, indices, masking

SEASONS = {"rains": (11, 12, 1, 2, 3), "dry": (5, 6, 7, 8, 9)}


def read_points(path):
    lons, lats, extra = [], [], []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            lons.append(float(row["lon"]))
            lats.append(float(row["lat"]))
            extra.append({k: v for k, v in row.items() if k not in ("lon", "lat")})
    return np.array(lons), np.array(lats), extra


def scene_index(raw, scene):
    """Masked NDVI, NDWI and NDMI for one scene, as full arrays."""
    folder = raw / "sentinel2" / scene["id"]
    bands = {}
    for name in ("green", "red", "nir", "swir16"):
        with rasterio.open(folder / f"{name}.tif") as src:
            bands[name] = src.read(1).astype("float64")
            profile = src.profile
    with rasterio.open(folder / "scl.tif") as src:
        scl = src.read(1)
    valid = masking.scl_mask(scl)
    for name in bands:
        bands[name] = masking.apply_mask(bands[name], valid)
    return (
        {
            "ndvi": indices.ndvi(bands["nir"], bands["red"]),
            "ndwi": indices.ndwi(bands["green"], bands["nir"]),
            "ndmi": indices.ndmi(bands["nir"], bands["swir16"]),
        },
        profile,
        masking.valid_fraction(valid),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=pathlib.Path, default=pathlib.Path("data/raw"))
    parser.add_argument("--points", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, default=pathlib.Path("data/features.csv"))
    parser.add_argument("--buffer-px", type=int, default=1)
    parser.add_argument("--min-obs", type=int, default=3)
    args = parser.parse_args()

    scenes = json.loads((args.raw / "sentinel2_scenes.json").read_text())
    if not scenes:
        raise SystemExit("no scene listed; run 01_fetch_scenes.py first")

    stacks = {"ndvi": [], "ndwi": [], "ndmi": []}
    months, profile = [], None
    for scene in scenes:
        values, profile, share = scene_index(args.raw, scene)
        for key in stacks:
            stacks[key].append(values[key])
        months.append(int(scene["date"][5:7]))
        print(f"  {scene['id']}: {share:.0%} of pixels usable")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    composite_paths = {}
    for key, slices in stacks.items():
        per_season = compositing.seasonal_composites(
            np.stack(slices), months, SEASONS, min_obs=args.min_obs
        )
        for season, grid in per_season.items():
            name = f"{key}_{season}"
            path = args.out.parent / f"{name}.tif"
            extraction.write_raster(
                path, grid.astype("float32"), profile["transform"],
                crs=profile["crs"], nodata=float("nan"),
            )
            composite_paths[name] = path

    # Landscape structure: heterogeneity of the rains-season NDVI composite.
    with rasterio.open(composite_paths["ndvi_rains"]) as src:
        texture = indices.local_std(src.read(1).astype("float64"), window=3)
        texture_path = args.out.parent / "ndvi_texture.tif"
        extraction.write_raster(
            texture_path, texture.astype("float32"), src.transform,
            crs=src.crs, nodata=float("nan"),
        )
    composite_paths["ndvi_texture"] = texture_path

    lons, lats, extra = read_points(args.points)
    features = extraction.stack_features(
        composite_paths, lons, lats, buffer_px=args.buffer_px
    )

    columns = ["lon", "lat"] + sorted(extra[0]) + sorted(features)
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for i in range(len(lons)):
            row = [lons[i], lats[i]]
            row += [extra[i][k] for k in sorted(extra[0])]
            row += [features[k][i] for k in sorted(features)]
            writer.writerow(row)
    print(f"{len(lons)} points and {len(features)} features written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
