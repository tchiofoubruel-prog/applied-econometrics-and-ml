"""Result figures for the Africa benchmark.

Reads figures/africa_results.json (written by 04_africa_benchmark.py) and
writes figures/africa_results.png plus the four panels separately.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
FIGDIR = HERE.parent / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8983"
GRID = "#e6e5e1"
BLUE = "#2a78d6"
ORANGE = "#eb6834"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK_3,
        "text.color": INK,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.titlepad": 14,
    }
)


def fr(value: float, digits: int = 3) -> str:
    """Format a number the French way, with a comma for the decimal mark."""
    return f"{value:.{digits}f}".replace(".", ",")


def thousands(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def fr_ticks(digits: int = 2) -> FuncFormatter:
    return FuncFormatter(lambda v, _pos: fr(v, digits))


def strip(ax, axis="x"):
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    if axis == "x":
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.xaxis.set_major_formatter(fr_ticks())
    else:
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.yaxis.set_major_formatter(fr_ticks())
    ax.set_axisbelow(True)


def panel_split(ax, res):
    rnd = res["random 5-fold"]
    blk = res["spatial blocks of 0.5 deg"]
    labels = ["AUC", "Exactitude"]
    y = [1.0, 0.0]
    h = 0.30
    gap = 0.035
    for i, key in enumerate(("auc", "accuracy")):
        ax.barh(y[i] + h / 2 + gap / 2, rnd[key], height=h, color=BLUE)
        ax.barh(y[i] - h / 2 - gap / 2, blk[key], height=h, color=ORANGE)
        ax.text(rnd[key] - 0.014, y[i] + h / 2 + gap / 2, fr(rnd[key]),
                va="center", ha="right", color="white", fontsize=8.5, fontweight="bold")
        ax.text(blk[key] - 0.014, y[i] - h / 2 - gap / 2, fr(blk[key]),
                va="center", ha="right", color="white", fontsize=8.5, fontweight="bold")
        drop = rnd[key] - blk[key]
        ax.text(rnd[key] + 0.018, y[i], f"−{fr(drop)}", va="center", ha="left",
                color=INK_2, fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, color=INK, fontsize=9.5)
    ax.set_xlim(0, 1.08)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylim(-0.45, 1.45)
    strip(ax, "x")
    ax.set_title("Le découpage aléatoire gonfle le score", loc="left")
    ax.legend(
        handles=[Patch(color=BLUE, label="5 blocs aléatoires"),
                 Patch(color=ORANGE, label="blocs spatiaux de 0,5°")],
        loc="upper left", bbox_to_anchor=(0.0, -0.10), ncol=2, frameon=False,
        fontsize=8.5, handlelength=1.1, handleheight=0.9, labelcolor=INK_2,
        borderpad=0.0, columnspacing=1.4, handletextpad=0.5,
    )


def panel_countries(ax, res):
    loco = res["leave_one_country_out"]
    counts = res["countries"]
    items = sorted(loco.items(), key=lambda kv: kv[1]["auc"])
    names = [k for k, _ in items]
    aucs = [v["auc"] for _, v in items]
    ypos = list(range(len(names)))
    ax.barh(ypos, aucs, height=0.58, color=BLUE)
    mean = res["transfer_mean_auc"]
    ax.set_ylim(-0.7, len(names) - 0.2)
    ax.axvline(mean, color=ORANGE, linewidth=2, zorder=3,
               ymin=0.0, ymax=(len(names) - 0.45) / (len(names) + 0.5))
    ax.text(mean, -0.62, f"moyenne {fr(mean)}", color=ORANGE, fontsize=8.5,
            va="center", ha="center")
    for i, auc in enumerate(aucs):
        ax.text(auc - 0.014, i, fr(auc), va="center", ha="right",
                color="white", fontsize=8.5, fontweight="bold")
    ax.set_yticks(ypos)
    ax.set_yticklabels([f"{n}  ({thousands(counts[n])})" for n in names],
                       color=INK, fontsize=9)
    ax.set_xlim(0, 1.05)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    strip(ax, "x")
    ax.set_title("Transfert d'un pays à l'autre, AUC hors échantillon", loc="left")
    ax.set_xlabel("pays retiré de l'entraînement (nombre de points)", fontsize=8,
                  labelpad=8)


def panel_conformal(ax, res):
    blk = res["conformal_spatial_blocks"]
    brd = res["conformal_across_borders"]
    x = [0, 1]
    vals = [blk["coverage"], brd["coverage"]]
    sizes = [blk["mean_set_size"], brd["mean_set_size"]]
    ax.bar(x, vals, width=0.42, color=[BLUE, ORANGE])
    ax.axhline(0.90, color=INK_2, linewidth=1.6, linestyle=(0, (4, 3)), zorder=3)
    ax.text(1.55, 0.912, "cible 0,90", color=INK_2, fontsize=8.5,
            va="bottom", ha="right")
    for xi, v in zip(x, vals):
        ax.text(xi, v - 0.025, fr(v), va="top", ha="center", color="white",
                fontsize=10, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"blocs spatiaux\ntaille moyenne {fr(sizes[0], 2)}",
         f"entre pays\ntaille moyenne {fr(sizes[1], 2)}"],
        color=INK, fontsize=9.5,
    )
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    strip(ax, "y")
    ax.set_title("La garantie conforme se dégrade sous déplacement", loc="left")
    ax.set_xlabel("couverture observée des ensembles de prédiction", fontsize=8,
                  labelpad=8)


def panel_importance(ax, res):
    imp = res["grouped_permutation_importance"]
    pretty = {"sentinel1": "Sentinel-1 (radar)", "sentinel2": "Sentinel-2 (optique)",
              "era5": "ERA5 (climat)", "srtm": "SRTM (relief)"}
    items = sorted(imp.items(), key=lambda kv: kv[1])
    names = [pretty[k] for k, _ in items]
    vals = [v for _, v in items]
    ypos = list(range(len(names)))
    ax.barh(ypos, vals, height=0.58, color=BLUE)
    for i, v in enumerate(vals):
        inside = v > 0.03
        ax.text(v - 0.003 if inside else v + 0.003, i, fr(v, 4),
                va="center", ha="right" if inside else "left",
                color="white" if inside else INK_2, fontsize=8.5,
                fontweight="bold" if inside else "normal")
    ax.set_yticks(ypos)
    ax.set_yticklabels(names, color=INK, fontsize=9)
    ax.set_xlim(0, 0.135)
    ax.set_xticks([0, 0.04, 0.08, 0.12])
    ax.xaxis.set_major_formatter(fr_ticks(2))
    strip(ax, "x")
    ax.xaxis.set_major_formatter(fr_ticks(2))
    ax.set_title("Perte d'AUC quand une source est permutée", loc="left")
    ax.set_xlabel(f"AUC de référence {fr(res['baseline_auc_for_importance'])}",
                  fontsize=8, labelpad=8)


PANELS = [
    ("split", panel_split),
    ("countries", panel_countries),
    ("conformal", panel_conformal),
    ("importance", panel_importance),
]


def main() -> None:
    res = json.loads((FIGDIR / "africa_results.json").read_text())
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.4))
    for ax, (_, fn) in zip(axes.ravel(), PANELS):
        fn(ax, res)
    fig.suptitle(
        "Cartographie des parcelles paysannes par télédétection multi-capteurs",
        x=0.045, y=0.975, ha="left", fontsize=13.5, fontweight="bold", color=INK,
    )
    fig.text(
        0.045, 0.937,
        f"{thousands(res['n'])} points étiquetés dans 9 pays africains, "
        f"{res['n_features']} variables saisonnières tirées de Sentinel-1, "
        "Sentinel-2, ERA5 et SRTM (CropHarvest)",
        ha="left", fontsize=9.5, color=INK_2,
    )
    fig.tight_layout(rect=(0.02, 0.02, 0.99, 0.915), h_pad=5.0, w_pad=5.0)
    out = FIGDIR / "africa_results.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    print("wrote", out)

    for name, fn in PANELS:
        f, ax = plt.subplots(figsize=(6.2, 4.1))
        fn(ax, res)
        f.tight_layout()
        p = FIGDIR / f"africa_{name}.png"
        f.savefig(p, dpi=200)
        plt.close(f)
        print("wrote", p)


if __name__ == "__main__":
    main()
