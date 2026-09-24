"""History-ordered residual proposals, independent of forecasting backbones."""

from __future__ import annotations

import numpy as np

from .finite_support import quota_satisfied


def build_residuals(train_truth, train_point_forecast) -> np.ndarray:
    truth = np.asarray(train_truth, dtype=float)
    point = np.asarray(train_point_forecast, dtype=float)
    if truth.shape != point.shape or truth.ndim != 2 or not np.all(np.isfinite(truth - point)):
        raise ValueError("train truth and point forecasts must be matching finite matrices")
    return truth - point


def standardize_histories(histories, mean, std) -> np.ndarray:
    """Use supplied training-set statistics; never fit on query histories."""
    x, mu, sigma = map(lambda a: np.asarray(a, dtype=float), (histories, mean, std))
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(mu)) or not np.all(np.isfinite(sigma)):
        raise ValueError("histories and training statistics must be finite")
    if np.any(sigma <= 0):
        raise ValueError("training standard deviations must be positive")
    try:
        return (x - mu) / sigma
    except ValueError as exc:
        raise ValueError("training statistics cannot broadcast over histories") from exc


def rank_donors_nearest(query_history, donor_histories) -> np.ndarray:
    """Stable ascending Euclidean order; ties preserve original bank indices."""
    q = np.asarray(query_history, dtype=float)
    donors = np.asarray(donor_histories, dtype=float)
    if donors.ndim != 2 or q.ndim != 1 or donors.shape[1] != q.size:
        raise ValueError("query and donor histories have incompatible shapes")
    if not np.all(np.isfinite(q)) or not np.all(np.isfinite(donors)):
        raise ValueError("histories must be finite")
    distance = np.linalg.norm(donors - q[None, :], axis=1)
    return np.argsort(distance, kind="stable")


def rank_donors_random(n_donors: int, seed: int) -> np.ndarray:
    """Seeded, without-replacement donor order for a control comparison."""
    if isinstance(n_donors, bool) or int(n_donors) != n_donors or n_donors < 0:
        raise ValueError("n_donors must be a nonnegative integer")
    return np.random.default_rng(seed).permutation(int(n_donors))


def reconstruct_candidate(query_point_forecast, donor_residual) -> np.ndarray:
    point, residual = map(lambda a: np.asarray(a, dtype=float),
                          (query_point_forecast, donor_residual))
    if point.ndim != 1 or point.shape != residual.shape or not np.all(np.isfinite(point + residual)):
        raise ValueError("point forecast and residual must be matching finite vectors")
    return point + residual


def is_physically_valid(candidate, lower: float, upper: float) -> bool:
    path = np.asarray(candidate, dtype=float)
    if path.ndim != 1 or not path.size or lower > upper:
        raise ValueError("candidate must be a nonempty vector and bounds ordered")
    return bool(np.all(np.isfinite(path)) and np.all((path >= lower) & (path <= upper)))


def acquire_until_quota(query_point_forecast, donor_residuals, donor_order,
                        initial_event: int, initial_nonevent: int,
                        q: float, k_min: int, max_attempts: int,
                        event_predicate, lower: float, upper: float):
    """Count proposals before filtering; insert all valid candidates; stop on both quotas.

    The event predicate must use the proposed path and origin-time information,
    never the query's realized future. The caller supplies the initial counts.
    """
    residuals = np.asarray(donor_residuals, dtype=float)
    order = np.asarray(donor_order)
    if residuals.ndim != 2 or order.ndim != 1 or max_attempts < 0:
        raise ValueError("invalid residual matrix, order, or attempt budget")
    if len(np.unique(order)) != len(order) or np.any(order < 0) or np.any(order >= len(residuals)):
        raise ValueError("donor order must contain distinct valid bank indices")
    ne, nn = int(initial_event), int(initial_nonevent)
    acquired, attempts = [], 0
    if quota_satisfied(ne, nn, q, k_min):
        return acquired, attempts, True
    for index in order[:max_attempts]:
        attempts += 1
        candidate = reconstruct_candidate(query_point_forecast, residuals[index])
        if not is_physically_valid(candidate, lower, upper):
            continue
        acquired.append(candidate)
        if bool(event_predicate(candidate)):
            ne += 1
        else:
            nn += 1
        if quota_satisfied(ne, nn, q, k_min):
            break
    return acquired, attempts, quota_satisfied(ne, nn, q, k_min)
