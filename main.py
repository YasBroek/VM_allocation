import json
import os
import time as timer
from copy import deepcopy
from classes import Server, VM
from lower_bound import *
from heuristics.first_fit_decreasing import first_fit_decreasing
from heuristics.fit_to_server import fit_to_server
from heuristics.best_fit_decreasing import best_fit_decreasing
from heuristics.local_search import local_search
from heuristics.integer_solution import integer_solution

def load_instance(path):
    """
    Load JSON instance files
    """
    with open(path) as f:
        data = json.load(f)

    vms = [VM(**v) for v in data["vms"]]
    servers = [Server(**s) for s in data["servers"]]
    return vms, servers

def heuristic(fn, vms, servers):
    from copy import deepcopy
    result = fn(vms, deepcopy(servers))
    if result is None:
        return None, None
    allocations, cost = result
    if allocations is None or cost is None:
        return None, None
    return allocations, cost

def run_instance(path, run_exact=True):
    vms, servers = load_instance(path)
    results = {}
    times = {}

    # Lower bounds
    results["lb_resource"] = resource_lower_bound(vms, servers)
    t0 = timer.perf_counter()
    lb_lp = continuous_solution(vms, deepcopy(servers))
    times["lb_lp"] = timer.perf_counter() - t0
    results["lb_lp"] = lb_lp if lb_lp is not None else 0
    results["lb"] = max(results["lb_resource"], results["lb_lp"])

    # Heuristics
    for name, fn in [("ffd", first_fit_decreasing),
                     ("bfd", best_fit_decreasing),
                     ("fts", fit_to_server),
                     ("ls",  local_search)]:
        t0 = timer.perf_counter()
        _, results[name] = heuristic(fn, vms, servers)
        times[name] = timer.perf_counter() - t0

    # Exact
    if run_exact:
        t0 = timer.perf_counter()
        ilp = integer_solution(vms, deepcopy(servers))
        times["ilp"] = timer.perf_counter() - t0
        results["ilp"] = ilp if ilp is not None else None
    else:
        results["ilp"] = None
        times["ilp"] = None

    # Gaps
    ref = results["ilp"] if (run_exact and results["ilp"] is not None) else results["lb"]
    for h in ["ffd", "bfd", "fts", "ls"]:
        val = results[h]
        results[f"gap_{h}"] = (val - ref) / ref if (val is not None and ref is not None and ref > 0) else None

    results["times"] = times
    return results

def run_all(instances_dir):
    categories = {
        "small":  True,
        "medium": True,
        "large":  False,
    }

    def fmt(val, width=6, pct=False):
        if val is None:
            return f"{'N/A':>{width}}"
        if pct:
            return f"{val:>{width}.2%}"
        return f"{val:>{width}.1f}"

    def fmt_t(val, width=7):
        if val is None:
            return f"{'N/A':>{width}}"
        return f"{val:>{width}.3f}s"

    for category, run_exact in categories.items():
        folder = os.path.join(instances_dir, category)
        print(f"\n=== {category.upper()} ===")
        print(
            f"{'Instance':<20} {'LB':>6} {'ILP':>6} {'FFD':>6} {'BFD':>6} {'FTS':>6} {'LS':>6}"
            f" {'gap_FFD':>9} {'gap_BFD':>9} {'gap_FTS':>9} {'gap_LS':>9}"
            f" {'t_ILP':>8} {'t_FFD':>8} {'t_BFD':>8} {'t_FTS':>8} {'t_LS':>8}"
        )

        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(folder, fname)
            r = run_instance(path, run_exact=run_exact)
            t = r["times"]

            print(
                f"{fname:<20}"
                f" {fmt(r['lb'])}"
                f" {fmt(r['ilp'])}"
                f" {fmt(r['ffd'])}"
                f" {fmt(r['bfd'])}"
                f" {fmt(r['fts'])}"
                f" {fmt(r['ls'])}"
                f" {fmt(r['gap_ffd'], width=9, pct=True)}"
                f" {fmt(r['gap_bfd'], width=9, pct=True)}"
                f" {fmt(r['gap_fts'], width=9, pct=True)}"
                f" {fmt(r['gap_ls'],  width=9, pct=True)}"
                f" {fmt_t(t['ilp'])}"
                f" {fmt_t(t['ffd'])}"
                f" {fmt_t(t['bfd'])}"
                f" {fmt_t(t['fts'])}"
                f" {fmt_t(t['ls'])}"
            )

def run_variant2(instances_dir):
    for category in ["small", "medium"]:
        folder = os.path.join(instances_dir, category)
        print(f"\n=== VARIANT 2 — {category.upper()} ===")
        print(f"{'Instance':<20} {'Nominal':>8} {'Splitting':>10} {'Reduction':>10}")

        for fname in sorted(os.listdir(folder)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(folder, fname)
            vms, servers = load_instance(path)

            nominal   = integer_solution(vms, deepcopy(servers))
            splitting = continuous_solution(vms, deepcopy(servers))

            if nominal and splitting:
                reduction = (nominal - splitting) / nominal
                print(f"{fname:<20} {nominal:>8.1f} {splitting:>10.1f} {reduction:>9.1%}")
            else:
                print(f"{fname:<20} {'N/A':>8} {'N/A':>10} {'N/A':>10}")


run_variant2("instances")