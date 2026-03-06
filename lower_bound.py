import math
from classes import Server, VM
from pulp import *

def resource_lower_bound(vms, server_types):
    max_cpu = max(s.vCPU for s in server_types)
    max_ram = max(s.RAM for s in server_types)
    max_disk = max(s.disk for s in server_types)
    return max(math.ceil(sum(vm.vCPU for vm in vms) / max_cpu), math.ceil(sum(vm.RAM for vm in vms) / max_ram), math.ceil(sum(vm.disk for vm in vms) / max_disk))

def continuous_solution(vms, servers):
    x = {}
    y = {}
    for k, server in enumerate(servers):
        for j in range(server.qty):
            y[j, k] = LpVariable(f"y_{j}_{k}", 0, 1)
            for i in range(len(vms)):
                x[i, j, k] = LpVariable(f"x_{i}_{j}_{k}", 0, 1)

    prob = LpProblem("VM_Alocation_cont", LpMinimize)

    # Objective
    prob += lpSum(server.cost * y[j, k] for j in range(server.qty) for k, server in enumerate(servers))

    for i in range(len(vms)):
        prob += lpSum(x[i, j, k] for j in range(server.qty) for k, server in enumerate(servers)) == 1

    for k, server in enumerate(servers):
        for j in range(server.qty):
            prob += lpSum(vm.vCPU * x[i, j, k] for i, vm in enumerate(vms)) <= server.vCPU * y[j, k]
            prob += lpSum(vm.RAM * x[i, j, k] for i, vm in enumerate(vms)) <= server.RAM * y[j, k]
            prob += lpSum(vm.disk * x[i, j, k] for i, vm in enumerate(vms)) <= server.disk * y[j, k]

    prob.solve()

    return value(prob.objective)

def integer_solution(vms, servers):
    x = {}
    y = {}
    for k, server in enumerate(servers):
        for j in range(server.qty):
            y[j, k] = LpVariable(f"y_{j}_{k}", cat="Binary")
            for i in range(len(vms)):
                x[i, j, k] = LpVariable(f"x_{i}_{j}_{k}", cat="Binary")

    prob = LpProblem("VM_Alocation_cont", LpMinimize)

    # Objective
    prob += lpSum(server.cost * y[j, k] for j in range(server.qty) for k, server in enumerate(servers))

    for i in range(len(vms)):
        prob += lpSum(x[i, j, k] for j in range(server.qty) for k, server in enumerate(servers)) == 1

    for k, server in enumerate(servers):
        for j in range(server.qty):
            prob += lpSum(vm.vCPU * x[i, j, k] for i, vm in enumerate(vms)) <= server.vCPU * y[j, k]
            prob += lpSum(vm.RAM * x[i, j, k] for i, vm in enumerate(vms)) <= server.RAM * y[j, k]
            prob += lpSum(vm.disk * x[i, j, k] for i, vm in enumerate(vms)) <= server.disk * y[j, k]

    prob.solve()

    return value(prob.objective)