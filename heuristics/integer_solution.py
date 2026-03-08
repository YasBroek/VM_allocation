from pulp import *

def integer_solution(vms, servers):
    x = {}
    y = {}

    # Variables
    for k, server in enumerate(servers):
        for j in range(server.qty):
            y[j, k] = LpVariable(f"y_{j}_{k}", cat="Binary") # Binary
            for i in range(len(vms)):
                x[i, j, k] = LpVariable(f"x_{i}_{j}_{k}", cat="Binary") # Binary

    # Problem definition
    prob = LpProblem("VM_Alocation_cont", LpMinimize)

    # Objective
    prob += lpSum(y[j, k] for j in range(server.qty) for k, server in enumerate(servers))

    # Constraint: One server per VM
    for i in range(len(vms)):
        prob += lpSum(x[i, j, k] for j in range(server.qty) for k, server in enumerate(servers)) == 1

    # Constraints: VMs must use less than servers' capacity
    for k, server in enumerate(servers):
        for j in range(server.qty):
            prob += lpSum(vm.vCPU * x[i, j, k] for i, vm in enumerate(vms)) <= server.vCPU * y[j, k]
            prob += lpSum(vm.RAM * x[i, j, k] for i, vm in enumerate(vms)) <= server.RAM * y[j, k]
            prob += lpSum(vm.disk * x[i, j, k] for i, vm in enumerate(vms)) <= server.disk * y[j, k]

    prob.solve(PULP_CBC_CMD(msg=0))

    return value(prob.objective)