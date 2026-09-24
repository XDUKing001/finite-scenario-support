# Finite-Scenario Support for Rare-Event Probabilistic Forecasting

This repository contains a lightweight implementation and paper-level
reproduction package for the finite-scenario support analysis used in our
ICASSP 2027 submission, *When More Samples Are Not Enough:
Support-Adaptive Inference for Rare-Event Diffusion Forecasting*.

It is a compact scientific companion, not a full backbone-training release.

## Motivation

A forecaster can provide a target severe-event probability $q_X$, while its
finite set of sampled future trajectories may contain too few event or
non-event paths to represent that target without concentrating nearly all
weight on a few samples. The probability target and the realized candidate
support are different objects.

We measure weight concentration with effective sample size (ESS):

$$
\mathrm{ESS}(w)=\left(\sum_i w_i^2\right)^{-1}.
$$

For $n_E$ valid event paths and $n_N$ valid non-event paths, assigning event
mass $q$ uniformly within each stratum gives

$$
\mathrm{ESS}(q)=
\left(q^2/n_E+(1-q)^2/n_N\right)^{-1}.
$$

Missing strata with positive target mass cannot be repaired by reweighting.
Invalid physical paths receive zero final weight.

## Core idea

The exact ESS-feasible interval describes which event masses are representable
at an ESS floor for a *fixed* pool. The two-sided operational quota requires
$n_E\geq\lceil Kq-10^{-12}\rceil$ and
$n_N\geq\lceil K(1-q)-10^{-12}\rceil$. This quota is sufficient, not
necessary, for ESS at least $K$; it is not the feasible interval.

When the quota fails, the paper first considers cumulative same-source IID
acquisition. For the D3U route, a history-based alternative candidate source
translates a training residual to the current point forecast:
$Y_{\mathrm{cand}}=Y_{\mathrm{point,query}}+r_{\mathrm{train}}$.
Only physically valid candidates enter the augmented pool. Candidate
acquisition stops when both quota sides hold or the proposal budget is spent.
Each proposal consumes budget before physical filtering. The public source
offers stable Euclidean-nearest and seeded random donor orderings.

Given sufficient support, minimum-KL event-mass transport places
$q/n_E$ on every valid event trajectory and $(1-q)/n_N$ on every valid
non-event trajectory. The generic function does not silently project an
unrepresentable target. Scalar projection is provided separately for
explicitly defined fallback policies.

## What this release reproduces

- Finite-pool ESS, exact feasible intervals, sufficient quotas, and KL weights.
- A self-contained synthetic support and residual-acquisition example.
- Paper Figure 2 from frozen aggregate support summaries.
- Paper Figure 3 from frozen aggregate score and effort summaries.
- Table I from its exact five-row score summary.
- A compact nearest-versus-random donor-order control.

The derived CSV files permit figure and table reproduction, not independent
recalculation of the underlying experimental metrics. This release does **not**
include D3U or TMDM training, diffusion trajectory generation, target-risk
model fitting, donor-bank construction from raw data, or Kelmarsh SCADA
preprocessing. It contains no checkpoints, trajectory tensors, or raw SCADA.

## Quick start

Python 3.10 or newer is recommended.

    python -m venv .venv

Activate with .venv\Scripts\activate on Windows or
source .venv/bin/activate on Linux/macOS, then run:

    pip install -r requirements.txt
    python examples/minimal_demo.py
    python scripts/reproduce_fig2.py
    python scripts/reproduce_fig3.py
    python scripts/reproduce_table1.py

Figure outputs are written to outputs/ as vector PDF and 600-dpi PNG.
The table script prints readable and LaTeX rows without editing a manuscript.
The synthetic example does not need data files, model weights, or network
access.

## Paper setting

| Setting | Value |
|---|---:|
| Initial trajectories per case | 200 |
| Maximum cumulative IID budget | 3,200 |
| ESS floor $K$ | 10 |
| Alternative-source proposal budget | 128 |
| Forecast horizon | 6 × 10 min |
| Rated power | 2,050 kW |
| Severe-event threshold | 0.4259847508 p.u. |

The event severity uses the seven-point path from the last observed power
value through the six forecast values. With power divided by rated capacity,
it is the largest absolute increment over spans of 1, 2, 3, or 6 steps.
The severe event occurs when this value reaches the threshold above.
All empirical summaries refer to the paper's chronologically contiguous KWF1
evaluation protocol. The IID route uses cumulative acquisition up to its
maximum budget, stopping on support success and using the paper-defined
fallback when necessary; it is
**not** a uniform 3,200-trajectory pool for every case.

## Headline support results

| Evaluation | Initial | Route endpoint |
|---|---:|---:|
| TMDM, same-source IID | 21.3% | 99.9% |
| D3U, same-source IID | 11.9% | 12.6% |
| D3U, alternative residual source | 11.9% | 99.70% |

The D3U alternative-source endpoint is 14,676 / 14,720 cases.
Figure 2's retrieval horizontal axis counts **attempted donor proposals**,
including physically invalid proposals, not accepted trajectories. Its
vertical axis uses overall test-case support success. The Figure 3 effort
groups include all 12,964 retrieval-invoked cases, including unresolved
attempts; the separate $q_X=0$ group has only four invoked cases.
Group positions in that panel are categorical and labels show median $q_X$.

A donor-order control indicates that switching to the severe-residual
candidate source accounts for most support recovery. History-based nearest
ordering adds a smaller support gain and improves trajectory-level CRPS and
Energy Score relative to random ordering. Random ordering has a slightly
lower mean Brier score, so nearest ordering is chiefly a trajectory-quality
refinement here, not a universally superior ordering.

## Data and forecasting backbones

The empirical setting uses 10-minute public SCADA data from Kelmarsh wind
farm's Kelmarsh 1 turbine (Senvion MM92, 2,050 kW). The dataset is
available from the [Zenodo v4 record cited by the paper](https://zenodo.org/records/16807551)
(DOI: 10.5281/zenodo.16807551).
Raw data are not redistributed here.

The paper evaluates two frozen probabilistic forecasting backbones: the
Diffusion-based Decoupled Deterministic and Uncertain framework (D3U) and the
Transformer-Modulated Diffusion Model (TMDM). Their training code, model
weights, and checkpoints are not included.
This repository focuses on downstream finite-scenario support analysis and
paper-level derived results.

ESS controls probability-weight concentration; it does not measure geometric
diversity, statistical independence, or physical realism among trajectories.
The empirical findings should not be generalized beyond the KWF1 protocol
reported in the paper without additional evaluation. The chronological KWF1
evaluation is treated as development evidence rather than as a fully untouched
external confirmation set.

## Citation

If you use this code, please cite the accompanying manuscript:

Haonan Zhao, Jiangkun Tian, Jitao Shen, Jian Wu, and Jing Li,
*When More Samples Are Not Enough: Support-Adaptive Inference for Rare-Event
Diffusion Forecasting*, ICASSP 2027 submission, 2026.

Final publication metadata will be updated after publication.

## License

The code in this repository is released under the MIT License.
