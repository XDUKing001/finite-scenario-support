# Finite-Scenario Support for Rare-Event Probabilistic Forecasting

A lightweight implementation and minimal reproduction package for finite-scenario support analysis in rare-event probabilistic forecasting.

The repository contains the core support-analysis code, candidate-acquisition procedure, and scripts for reproducing the main figures and table.

## Overview

A probabilistic forecaster may assign a rare-event probability `q_X`, while its finite trajectory pool contains too few event or non-event samples to represent that probability without excessive weight concentration.

This repository focuses on the distinction between:

1. the target event probability; and
2. the support available in the realized finite trajectory pool.

The effective sample size (ESS) is

```text
ESS(w) = 1 / Σ_i w_i²
```

The implementation includes:

- exact ESS-based support analysis;
- a sufficient two-sided event/non-event quota;
- KL event-mass reweighting;
- same-source IID acquisition analysis;
- residual candidate acquisition with nearest or random donor ordering.

## Repository structure

```text
finite-scenario-support/
├── examples/
│   └── minimal_demo.py
├── paper_results/
│   ├── fig2_support.csv
│   ├── fig3_effort.csv
│   ├── fig3_quality.csv
│   ├── random_vs_nearest.csv
│   └── table1.csv
├── scripts/
│   ├── reproduce_fig2.py
│   ├── reproduce_fig3.py
│   └── reproduce_table1.py
├── src/
│   ├── __init__.py
│   ├── finite_support.py
│   └── residual_acquisition.py
├── LICENSE
├── README.md
└── requirements.txt
```

## Quick start

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the minimal synthetic example:

```bash
python examples/minimal_demo.py
```

Reproduce the main paper-level outputs:

```bash
python scripts/reproduce_fig2.py
python scripts/reproduce_fig3.py
python scripts/reproduce_table1.py
```

Generated figures are written to `outputs/`.

## Main support results

| Evaluation | Initial support | Final support |
|---|---:|---:|
| TMDM, same-source IID | 21.3% | 99.9% |
| D3U, same-source IID | 11.9% | 12.6% |
| D3U, alternative residual source | 11.9% | 99.70% |

These values correspond to the KWF1 protocol reported in the accompanying study.

A donor-order control further indicates that switching the candidate source accounts for most of the D3U support recovery, while history-based nearest ordering mainly improves trajectory-level forecast quality.

## Reproduction scope

This is a lightweight reproduction package.

It reproduces:

- finite-support calculations;
- ESS and quota examples;
- the main support-recovery figure;
- the forecast-quality and retrieval-effort figure;
- the main results table;
- a compact nearest-versus-random donor-order comparison.

It does not include:

- D3U or TMDM training code;
- model checkpoints;
- raw diffusion trajectory tensors;
- target-probability model training;
- raw Kelmarsh SCADA preprocessing.

The released CSV files contain derived aggregate results used for paper-level figure and table reproduction.

## Data

The experiments use 10-minute public SCADA data from the Kelmarsh wind farm, with the KWF1 turbine corresponding to a Senvion MM92 unit rated at 2050 kW.

Dataset:

https://zenodo.org/records/16807551

Raw SCADA data are not redistributed in this repository.

## Notes

ESS measures probability-weight concentration. It does not measure geometric trajectory diversity, statistical independence, or physical realism.

The empirical results in this repository correspond to the KWF1 evaluation protocol and should not be interpreted as universal performance guarantees.

## Citation

If you use this repository, please cite the accompanying manuscript:

*When More Samples Are Not Enough: Support-Adaptive Inference for Rare-Event Diffusion Forecasting.*

Publication details will be updated after review.

## License

This repository is released under the MIT License.
