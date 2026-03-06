from copy import deepcopy
from utils import *

def first_fit_decreasing(vms, server_types):

    vms_sorted = sort_vm(vms, server_types)

    servers = extend_and_sort(server_types)

    attributions = []
    used_servers = set()

    for vm in vms_sorted:
        placed = False

        for s in servers:
            if (s.vCPU >= vm.vCPU and
                s.RAM >= vm.RAM and
                s.disk >= vm.disk):

                s.vCPU -= vm.vCPU
                s.RAM -= vm.RAM
                s.disk -= vm.disk

                attributions.append((vm.ID, s.ID))
                used_servers.add(s.ID)
                placed = True
                break

        if not placed:
            print("No feasible solution with FFD")
            return None

    return attributions, len(used_servers)