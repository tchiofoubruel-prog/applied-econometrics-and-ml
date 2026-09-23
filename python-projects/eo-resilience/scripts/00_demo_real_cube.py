"""Read the real Togo cube and plot the season its four sources describe.

    python scripts/00_demo_real_cube.py --out figures/togo_phenology.png

The cube is downloaded from the CropHarvest repository on first use and cached
outside this repository; it is not redistributed here. See `sample.py` for the
licence and the citation.
"""

from __future__ import annotations

import argparse
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from eo_resilience import phenology, sample

MONTH_LABELS = ["F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D", "J"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path,
                        default=pathlib.Path("figures/togo_phenology.png"))
    args = parser.parse_args()

    cube = sample.togo_cube()
    lon = (cube.bounds.left + cube.bounds.right) / 2
    lat = (cube.bounds.bottom + cube.bounds.top) / 2
    print(f"{cube} at {lon:.4f}E {lat:.4f}N, {cube.crs}")

    series = {
        "NDVI": np.nanmean(cube.ndvi(), axis=(1, 2)),
        "NDMI": np.nanmean(cube.ndmi(), axis=(1, 2)),
        "NDWI": np.nanmean(cube.ndwi(), axis=(1, 2)),
    }
    temp = np.nanmean(cube.band("temperature_2m"), axis=(1, 2)) - 273.15
    rain = np.nanmean(cube.band("total_precipitation"), axis=(1, 2)) * 1000
    vv = np.nanmean(cube.band("VV"), axis=(1, 2))

    months = np.arange(cube.n_timesteps)
    fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.4), sharex=True,
                             gridspec_kw={"height_ratios": [1.25, 1, 1]})

    ax = axes[0]
    for name, values in series.items():
        ax.plot(months, values, marker="o", markersize=3.5, linewidth=1.6, label=name)
    peak = phenology.peak_month(series["NDVI"])
    greenup = phenology.greenup_month(series["NDVI"])
    ax.axvline(greenup, color="0.55", linestyle=":", linewidth=1)
    ax.axvline(peak, color="0.25", linestyle="--", linewidth=1)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.18)
    ax.annotate("green-up", (greenup, hi + 0.04), xytext=(3, 0),
                textcoords="offset points", fontsize=8, color="0.35")
    ax.annotate("peak", (peak, hi + 0.04), xytext=(-24, 0),
                textcoords="offset points", fontsize=8, color="0.2")
    ax.set_ylabel("Sentinel-2 index")
    ax.legend(frameon=False, ncols=3, fontsize=9, loc="lower left",
              bbox_to_anchor=(0.0, -0.02))
    ax.set_title(
        f"One smallholder plot in Togo, {lat:.3f}N {lon:.3f}E, Feb 2019 to Feb 2020\n"
        "Sentinel-1, Sentinel-2, ERA5 and SRTM read from a single CropHarvest cube",
        fontsize=10.5, loc="left")

    ax = axes[1]
    ax.bar(months, rain, color="#4C78A8", alpha=0.75, width=0.6, label="ERA5 rainfall")
    ax.set_ylabel("rainfall (mm day$^{-1}$)")
    twin = ax.twinx()
    twin.plot(months, temp, color="#E45756", marker="s", markersize=3.5,
              linewidth=1.5, label="ERA5 2 m temperature")
    twin.set_ylabel("temperature (°C)")
    handles = ax.get_legend_handles_labels()[0] + twin.get_legend_handles_labels()[0]
    labels = ax.get_legend_handles_labels()[1] + twin.get_legend_handles_labels()[1]
    ax.set_ylim(0, max(rain) * 1.45)
    ax.legend(handles, labels, frameon=False, fontsize=9, loc="upper left",
              ncols=2)

    ax = axes[2]
    ax.plot(months, vv, color="#54A24B", marker="^", markersize=4, linewidth=1.6)
    ax.set_ylabel("Sentinel-1 VV (dB)")
    ax.set_xlabel("month of the season")
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_LABELS)

    for a in axes:
        a.spines[["top", "right"]].set_visible(True)
        a.grid(axis="y", alpha=0.25, linewidth=0.6)

    fig.text(0.005, 0.005,
             "Cube from CropHarvest (Tseng et al. 2021), CC BY-SA 4.0, "
             "downloaded rather than redistributed.", fontsize=7.5, color="0.4")
    fig.tight_layout(rect=(0, 0.02, 1, 1))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=170)
    print(f"figure written to {args.out}")

    stats = phenology.summarise(series["NDVI"], prefix="ndvi")
    for key in ("ndvi_peak", "ndvi_amplitude", "ndvi_peak_month",
                "ndvi_greenup_month", "ndvi_season_length"):
        print(f"  {key:<22} {stats[key]:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
