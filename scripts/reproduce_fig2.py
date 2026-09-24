"""Reproduce the paper's support-recovery panels from aggregate CSV values."""

import csv
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import paper_plot_style

BLUE, ORANGE, GREEN = "#376A9E", "#D36B3D", "#307A61"
LIGHT_GREEN, LIGHT_BLUE, GRAY = "#89C8B5", "#7CA8CC", "#B8BEC3"


def load():
    with (ROOT / "paper_results/fig2_support.csv").open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main():
    rows = load()
    iid = [r for r in rows if r["panel"] == "a"]
    missing = [r for r in rows if r["panel"] == "b"]
    recovery = sorted((r for r in rows if r["panel"] == "c"), key=lambda r: int(r["x"]))
    assert len(iid) == 10 and len(recovery) == 129
    budgets = [200, 400, 800, 1600, 3200]
    for model in ("D3U", "TMDM"):
        selected = sorted((r for r in iid if r["model"] == model), key=lambda r: int(r["x"]))
        assert [int(r["x"]) for r in selected] == budgets
        assert all(int(r["n_if_needed"]) <= 14720 for r in selected)
        assert all(abs(float(r["value"]) - 100 * int(r["n_if_needed"]) / 14720) < 1e-9 for r in selected)
    assert [int(r["x"]) for r in recovery] == list(range(129))
    assert int(recovery[0]["n_if_needed"]) == 1756
    assert int(recovery[-1]["n_if_needed"]) == 14676
    for model, deficient in (("D3U", 12964), ("TMDM", 11581)):
        selected = [r for r in missing if r["model"] == model]
        assert sum(int(r["n_if_needed"]) for r in selected) == deficient
        assert abs(sum(float(r["value"]) for r in selected) - 100) < 1e-9

    paper_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.65))
    fig.subplots_adjust(left=.07, right=.98, bottom=.25, top=.91, wspace=.42)
    a, b, c = axes
    for model, color, marker, linestyle in (("D3U", BLUE, "o", "-"), ("TMDM", ORANGE, "s", "--")):
        selected = sorted((r for r in iid if r["model"] == model), key=lambda r: int(r["x"]))
        a.plot(budgets, [float(r["value"]) for r in selected], color=color,
               marker=marker, linestyle=linestyle, linewidth=1.6, markersize=4.5, label=model)
    a.set_xscale("log", base=2)
    a.set_xticks(budgets, [str(x) for x in budgets], rotation=35)
    a.set_xlim(185, 3500)
    a.set_ylim(0, 102)
    a.set_xlabel("Total IID samples")
    a.set_ylabel("Support success (%)")
    a.legend(loc="center right")

    category_style = {"Event deficit": (LIGHT_GREEN, "///"),
                      "Non-event deficit": (LIGHT_BLUE, "\\\\"),
                      "Both deficits": (GRAY, "...")}
    for y, model in enumerate(("D3U", "TMDM")):
        offset = 0.0
        for category in category_style:
            row = next((r for r in missing if r["model"] == model and r["category"] == category), None)
            width = float(row["value"]) if row else 0.0
            if width:
                color, hatch = category_style[category]
                b.barh(y, width, left=offset, height=.45, color=color, edgecolor="white", hatch=hatch)
                if width > 8:
                    b.text(offset + width / 2, y, f"{width:.1f}%", va="center", ha="center")
            offset += width
    b.set_yticks([0, 1], ["D3U", "TMDM"])
    b.invert_yaxis()
    b.set_xlim(0, 101)
    b.set_xlabel("Composition among S=200 deficient cases (%)")
    b.legend(handles=[Patch(facecolor=color, hatch=hatch, label=cat)
                      for cat, (color, hatch) in category_style.items()],
             loc="center", bbox_to_anchor=(.52, .5), ncol=2, fontsize=6.2,
             columnspacing=.7, handlelength=1.0, handletextpad=.35)

    c.plot([int(r["x"]) for r in recovery], [float(r["value"]) for r in recovery],
           color=GREEN, linewidth=1.7)
    c.scatter([0, 128], [float(recovery[0]["value"]), float(recovery[-1]["value"])],
              color=GREEN, marker="^", s=25)
    c.set_xlim(0, 133)
    c.set_xticks([0, 32, 64, 96, 128])
    c.set_ylim(0, 102)
    c.set_xlabel("Attempted donor proposals")
    c.set_ylabel("Overall support success (%)")
    for ax, letter in zip(axes, "abc"):
        ax.text(.5, -.31, f"({letter})", transform=ax.transAxes,
                ha="center", va="top", fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#D9D9D9", linewidth=.45, alpha=.4)
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    fig.savefig(output / "figure2_support_recovery.pdf")
    fig.savefig(output / "figure2_support_recovery.png", dpi=600)
    plt.close(fig)
    print("Figure 2: D3U 11.929% -> 12.582%; TMDM 21.325% -> 99.905%; retrieval 99.701%")


if __name__ == "__main__":
    main()
