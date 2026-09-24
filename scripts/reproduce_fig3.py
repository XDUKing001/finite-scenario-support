"""Reproduce quality and proposal-effort panels from derived summaries."""

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import paper_plot_style

GREEN, ORANGE = "#307A61", "#C46D4F"
METRICS = ["Brier", "CRPS", "Severity-CRPS", "Energy Score"]


def read(name):
    with (ROOT / "paper_results" / name).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main():
    quality, effort = read("fig3_quality.csv"), read("fig3_effort.csv")
    assert len(quality) == 12 and len(effort) == 9
    for metric in METRICS:
        selected = {r["route"]: r for r in quality if r["metric"] == metric}
        assert set(selected) == {"Raw", "IID", "Retrieval"}
        raw = float(selected["Raw"]["score"])
        for route in ("IID", "Retrieval"):
            reduction = (raw - float(selected[route]["score"])) / raw * 100
            assert abs(reduction - float(selected[route]["relative_reduction_percent"])) < 1e-9
    assert sum(int(r["invoked_n"]) for r in effort) == 12964
    assert int(effort[0]["invoked_n"]) == 4 and float(effort[0]["q_median"]) == 0

    paper_plot_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.15))
    fig.subplots_adjust(left=.14, right=.98, bottom=.30, top=.91, wspace=.37)
    y = np.arange(4)[::-1]
    a.axvline(0, color="#9BA4A9", linestyle="--", linewidth=.9)
    for route, color, marker, offset in (("IID", ORANGE, "o", .12),
                                          ("Retrieval", GREEN, "^", -.12)):
        values = [float(next(r["relative_reduction_percent"] for r in quality
                             if r["metric"] == metric and r["route"] == route))
                  for metric in METRICS]
        a.scatter(values, y + offset, color=color, marker=marker, s=32, label=route, zorder=3)
        for x, yy in zip(values, y + offset):
            a.annotate(f"{x:.1f}%", (x, yy), xytext=(4, 0), textcoords="offset points",
                       va="center", fontsize=7.4, color=color)
    a.set_yticks(y, METRICS)
    a.set_xlim(-2, 51)
    a.set_ylim(-.5, 3.5)
    a.set_xlabel("Relative score reduction vs. Raw (%)")
    a.legend(loc="center right")

    x = np.arange(len(effort))
    q1 = np.array([float(r["q1_attempts"]) for r in effort])
    median = np.array([float(r["median_attempts"]) for r in effort])
    q3 = np.array([float(r["q3_attempts"]) for r in effort])
    p90 = np.array([float(r["p90_attempts"]) for r in effort])
    b.errorbar(x[1:], median[1:], yerr=[median[1:] - q1[1:], q3[1:] - median[1:]],
               fmt="none", ecolor=GREEN, capsize=2, linewidth=.9)
    b.plot(x[1:], median[1:], color=GREEN, marker="o", linewidth=1.45,
           markersize=4.5, label="Median (IQR)")
    b.plot(x[1:], p90[1:], color=ORANGE, linestyle="--", marker="^",
           linewidth=1.1, markersize=4.5, label="p90")
    b.errorbar([0], [median[0]], yerr=[[median[0] - q1[0]], [q3[0] - median[0]]],
               fmt="o", color="#90B6A7", capsize=2, markersize=4)
    b.scatter([0], [p90[0]], marker="^", color="#DEAC98", s=25)
    b.axvline(.5, color="#C9CFD3", linestyle="--", linewidth=.7)
    b.annotate("n=4", (0, p90[0]), xytext=(3, 7), textcoords="offset points", fontsize=7)
    b.set_xticks(x, ["0"] + [f"{float(r['q_median']):.4f}" for r in effort[1:]],
                 rotation=38, ha="right")
    b.set_xlim(-.35, 8.35)
    b.set_ylim(0, 130)
    b.set_ylabel("Attempted donor proposals")
    b.set_xlabel(r"Target-probability regime $q_X$")
    b.legend(loc="upper right")
    for ax, letter in ((a, "a"), (b, "b")):
        ax.text(.5, -.38, f"({letter})", transform=ax.transAxes,
                ha="center", va="top", fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    fig.savefig(output / "figure3_quality_effort.pdf")
    fig.savefig(output / "figure3_quality_effort.png", dpi=600)
    plt.close(fig)
    print("Figure 3: four exact score reductions and nine frozen probability regimes reproduced")


if __name__ == "__main__":
    main()
