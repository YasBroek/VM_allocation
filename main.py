import json
import os
from classes import Server, VM
from lower_bound import *
from heuristics.first_fit_decreasing import first_fit_decreasing
from heuristics.fit_to_server import fit_to_server
from heuristics.best_fit_decreasing import best_fit_decreasing
from heuristics.local_search import local_search

def load_instance(path):
    with open(path) as f:
        data = json.load(f)

    vms = [VM(**v) for v in data["vms"]]
    servers = [Server(**s) for s in data["servers"]]
    return vms, servers


def run_instance(path, run_exact=True):
    vms, servers = load_instance(path)

    results = {}

    # Lower bounds
    results["lb_resource"] = resource_lower_bound(vms, servers)
    results["lb_lp"]       = continuous_solution(vms, servers)
    results["lb"]          = max(results["lb_resource"], results["lb_lp"])

    # Heuristics (each needs a fresh copy of servers since they mutate state)
    _, results["ffd"] = first_fit_decreasing(vms, load_instance(path)[1])
    _, results["fts"] = fit_to_server(vms, load_instance(path)[1])
    _, results["bfd"] = best_fit_decreasing(vms, load_instance(path)[1])
    _, results["ls"]  = local_search(vms, load_instance(path)[1])

    # Exact (only for small instances)
    if run_exact:
        results["ilp"] = integer_solution(vms, servers)

    # Optimality gaps
    ref = results["ilp"] if run_exact else results["lb"]
    for h in ["ffd", "fts", "bfd", "ls"]:
        results[f"gap_{h}"] = (results[h] - ref) / ref if ref > 0 else 0

    return results


def run_all(instances_dir):
    categories = {
        "small":  True,   # run exact
        "medium": True,   # run exact (will be slower)
        "large":  False,  # heuristics only
    }

    for category, run_exact in categories.items():
        folder = os.path.join(instances_dir, category)
        print(f"\n=== {category.upper()} ===")
        print(f"{'Instance':<20} {'LB':>6} {'ILP':>6} {'FFD':>6} {'FTS':>6} {'BFD':>6} {'LS':>6} {'gap_FFD':>9} {'gap_BFD':>9} {'gap_LS':>9}")

        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(folder, fname)
            r = run_instance(path, run_exact=run_exact)

            ilp_str = f"{r['ilp']:>6.1f}" if run_exact else f"{'N/A':>6}"
            print(
                f"{fname:<20} "
                f"{r['lb']:>6.2f} "
                f"{ilp_str} "
                f"{r['ffd']:>6} "
                f"{r['fts']:>6}"
                f"{r['bfd']:>6} "
                f"{r['ls']:>6} "
                f"{r['gap_ffd']:>9.2%} "
                f"{r['gap_fts']:>9.2%} "
                f"{r['gap_bfd']:>9.2%} "
                f"{r['gap_ls']:>9.2%}"
            )


run_all("instances")