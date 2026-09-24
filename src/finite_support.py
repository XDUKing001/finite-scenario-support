"""Exact finite-pool ESS, sufficient quotas, and KL event-mass transport."""

from __future__ import annotations

import math

import numpy as np


def _probability(q: float) -> float:
    q = float(q)
    if not math.isfinite(q) or not 0.0 <= q <= 1.0:
        raise ValueError("event probability must be finite and in [0, 1]")
    return q


def _count(value: int, name: str) -> int:
    if isinstance(value, (bool, np.bool_)) or int(value) != value or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return int(value)


def _floor(k_min: int) -> int:
    k = _count(k_min, "k_min")
    if k == 0:
        raise ValueError("k_min must be positive")
    return k


def effective_sample_size(weights) -> float:
    """Return 1 / sum(w_i**2) for probability weights summing to one."""
    w = np.asarray(weights, dtype=float)
    if w.ndim != 1 or w.size == 0 or not np.all(np.isfinite(w)) or np.any(w < 0):
        raise ValueError("weights must be a nonempty, finite, nonnegative vector")
    if not np.isclose(w.sum(), 1.0, rtol=0, atol=1e-10):
        raise ValueError("probability weights must sum to one")
    return float(1.0 / np.dot(w, w))


def ess_from_event_mass(q: float, n_event: int, n_nonevent: int) -> float:
    """ESS under uniform within-stratum weights for target event mass q."""
    q = _probability(q)
    ne, nn = _count(n_event, "n_event"), _count(n_nonevent, "n_nonevent")
    if ne == 0 and q > 0 or nn == 0 and q < 1:
        raise ValueError("target mass requires a missing support stratum")
    denominator = (q * q / ne if ne else 0.0) + ((1 - q) ** 2 / nn if nn else 0.0)
    if denominator == 0:
        raise ValueError("no valid support")
    return 1.0 / denominator


def ess_feasible_interval(n_event: int, n_nonevent: int, k_min: int):
    """Return the exact ESS-feasible interval for a fixed finite pool, or None."""
    ne, nn, k = _count(n_event, "n_event"), _count(n_nonevent, "n_nonevent"), _floor(k_min)
    nv = ne + nn
    if nv < k:
        return None
    if ne == 0:
        return (0.0, 0.0)
    if nn == 0:
        return (1.0, 1.0)
    p = ne / nv
    delta = math.sqrt(max(0.0, (nv / k - 1.0) * p * (1.0 - p)))
    return (max(0.0, p - delta), min(1.0, p + delta))


def quota_requirements(q: float, k_min: int) -> tuple[int, int]:
    """Return the paper's conservative, two-sided integer support quota."""
    q, k = _probability(q), _floor(k_min)
    return (math.ceil(max(0.0, k * q - 1e-12)),
            math.ceil(max(0.0, k * (1.0 - q) - 1e-12)))


def quota_satisfied(n_event: int, n_nonevent: int, q: float, k_min: int) -> bool:
    """The two-sided quota is sufficient, but not necessary, for satisfying the ESS floor."""
    ne, nn = _count(n_event, "n_event"), _count(n_nonevent, "n_nonevent")
    me, mn = quota_requirements(q, k_min)
    return ne >= me and nn >= mn


def kl_reweight(event_mask, valid_mask, q: float) -> np.ndarray:
    """Minimum-KL weights: equal within each valid stratum, zero on invalid paths.

    The caller must provide a realizable q. This function never projects q.
    """
    q = _probability(q)
    event, valid = np.asarray(event_mask), np.asarray(valid_mask)
    if event.ndim != 1 or valid.ndim != 1 or event.shape != valid.shape or not event.size:
        raise ValueError("event and valid masks must be same-length nonempty vectors")
    if event.dtype != np.bool_ or valid.dtype != np.bool_:
        raise ValueError("event and valid masks must be boolean")
    e, n = event & valid, ~event & valid
    ne, nn = int(e.sum()), int(n.sum())
    if ne == 0 and q > 0 or nn == 0 and q < 1:
        raise ValueError("target mass requires a missing support stratum")
    weights = np.zeros(event.size, dtype=float)
    if ne:
        weights[e] = q / ne
    if nn:
        weights[n] = (1 - q) / nn
    if not np.isclose(weights.sum(), 1.0, atol=1e-12):
        raise ValueError("no realizable probability distribution")
    return weights


def project_event_mass_to_interval(q: float, lower: float, upper: float) -> float:
    """Scalar projection for a separately specified projected-fallback rule."""
    q = _probability(q)
    lo, hi = _probability(lower), _probability(upper)
    if lo > hi:
        raise ValueError("lower bound exceeds upper bound")
    return min(max(q, lo), hi)
