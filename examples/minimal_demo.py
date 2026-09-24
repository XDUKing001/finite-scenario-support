"""Self-contained synthetic example of support and residual acquisition."""

from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.finite_support import (effective_sample_size, ess_feasible_interval,
                                kl_reweight, quota_requirements, quota_satisfied)
from src.residual_acquisition import (build_residuals, is_physically_valid,
                                      rank_donors_nearest, reconstruct_candidate,
                                      standardize_histories)


def main():
    q, k = 0.08, 10
    event = np.array([True] * 2 + [False] * 18 + [True])
    valid = np.array([True] * 20 + [False])
    ne, nn = int((event & valid).sum()), int((~event & valid).sum())
    weights = kl_reweight(event, valid, q)
    print(f"Target event probability: {q:.2f}")
    print(f"Event count: {ne}; non-event count: {nn}")
    print(f"ESS-feasible interval: {ess_feasible_interval(ne, nn, k)}")
    print(f"Quota requirement: {quota_requirements(q, k)}")
    print(f"Quota satisfied: {quota_satisfied(ne, nn, q, k)}")
    print(f"Reweighted event mass: {weights[event & valid].sum():.2f}")
    print(f"ESS after reweighting: {effective_sample_size(weights):.3f}")

    histories = np.array([[4., 5.], [1., 2.], [8., 9.]])
    query = np.array([1.2, 2.1])
    mean, std = histories.mean(axis=0), histories.std(axis=0)
    donor_z = standardize_histories(histories, mean, std)
    query_z = standardize_histories(query, mean, std)
    order = rank_donors_nearest(query_z, donor_z)
    residuals = build_residuals(np.array([[2., 3.]]), np.array([[1., 2.]]))
    candidate = reconstruct_candidate(np.array([4., 5.]), residuals[0])
    print(f"Nearest donor ordering: {order.tolist()}")
    print(f"Reconstructed future: {candidate.tolist()}")
    print(f"Physical validity [0, 10]: {is_physically_valid(candidate, 0, 10)}")


if __name__ == "__main__":
    main()
