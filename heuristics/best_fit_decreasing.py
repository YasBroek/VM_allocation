from utils import *
import math

def best_fit_decreasing(vms, server_types):
    vms_sorted = sort_vm(vms, server_types)
    servers = extend_and_sort(server_types)
    allocations = []
    used_servers = set()

    for vm in vms_sorted:
        best_server = None
        best_slack = math.inf

        for server in servers:
            if (server.vCPU >= vm.vCPU and
                server.RAM  >= vm.RAM  and
                server.disk >= vm.disk):
                # slack = how much space is wasted after placing this VM
                slack = (server.vCPU - vm.vCPU) + (server.RAM - vm.RAM) + (server.disk - vm.disk)
                if slack < best_slack:
                    best_slack = slack
                    best_server = server

        if best_server is None:
            print("No feasible solution with BFD")
            return None

        best_server.vCPU -= vm.vCPU
        best_server.RAM  -= vm.RAM
        best_server.disk -= vm.disk
        allocations.append((vm.ID, best_server.ID))
        used_servers.add(best_server.ID)

    return allocations, len(used_servers)