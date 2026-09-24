"""Print the five frozen Table I rows without recalculating experiments."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper_results/table1.csv"


def main():
    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 5
    expected = [("D3U", "Raw"), ("D3U", "IID"), ("D3U", "Retrieval"),
                ("TMDM", "Raw"), ("TMDM", "IID")]
    assert [(r["Forecaster"], r["Route"]) for r in rows] == expected
    assert abs(float(rows[2]["Brier"]) - .0394807157368658) < 1e-14
    assert abs(float(rows[2]["CRPS_kW"]) - 210.51989184626524) < 1e-12
    print("Forecaster  Route       Brier      CRPS (kW)  Severity-CRPS  ES (kW)   Invalid mass")
    for r in rows:
        print(f"{r['Forecaster']:<11} {r['Route']:<11} {float(r['Brier']):.6f}  "
              f"{float(r['CRPS_kW']):10.4f}  {float(r['Severity_CRPS']):13.6f}  "
              f"{float(r['Energy_Score_kW']):8.4f}  {float(r['Invalid_probability_mass']):.6f}")
    print("\nLaTeX rows:")
    for r in rows:
        print(f"{r['Forecaster']} & {r['Route']} & {float(r['Brier']):.4f} & "
              f"{float(r['CRPS_kW']):.2f} & {float(r['Severity_CRPS']):.4f} & "
              f"{float(r['Energy_Score_kW']):.2f} & "
              f"{float(r['Invalid_probability_mass']):.4f}" + " \\\\")


if __name__ == "__main__":
    main()
